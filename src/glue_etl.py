
import sys,json,csv,io,hashlib,functools
import boto3
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F, types as T
args=getResolvedOptions(sys.argv,['JOB_NAME','BUCKET','PREFIX','DATABASE'])
bucket,prefix,db=args['BUCKET'],args['PREFIX'],args['DATABASE']
s3=boto3.client('s3'); catalog=boto3.client('glue')
ctx=GlueContext(SparkContext.getOrCreate());spark=ctx.spark_session
job=Job(ctx);job.init(args['JOB_NAME'],args)
def read_json(name):
    return json.loads(s3.get_object(Bucket=bucket,Key=f'{prefix}/config/{name}')['Body'].read())
cfg=read_json('campos.json');multi=read_json('multiplas.json')
try:catalog.create_database(DatabaseInput={'Name':db})
except catalog.exceptions.AlreadyExistsException:pass
def write_table(df,layer,name):
    location=f's3://{bucket}/{prefix}/{layer}/{name}/'
    df.coalesce(2).write.mode('overwrite').option('compression','snappy').parquet(location)
    table={'Name':f'{layer}_{name}','TableType':'EXTERNAL_TABLE',
      'Parameters':{'classification':'parquet','EXTERNAL':'TRUE'},
      'StorageDescriptor':{'Columns':[{'Name':f.name,'Type':f.dataType.simpleString()} for f in df.schema.fields],
      'Location':location,'InputFormat':'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
      'OutputFormat':'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
      'SerdeInfo':{'SerializationLibrary':'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe','Parameters':{'serialization.format':'1'}}}}
    try:catalog.create_table(DatabaseName=db,TableInput=table)
    except catalog.exceptions.AlreadyExistsException:catalog.update_table(DatabaseName=db,TableInput=table)
def union(frames):return functools.reduce(lambda a,b:a.unionByName(b),frames)
responses=[];choices=[];audit=[]
for base in cfg['edicoes']:
    ed=base['edicao'];key=f"{prefix}/bronze/edicao={ed}/{base['arquivo']}"
    content=s3.get_object(Bucket=bucket,Key=key)['Body'].read()
    assert hashlib.sha256(content).hexdigest()==base['sha256'],'Hash divergente'
    header=next(csv.reader(io.StringIO(content.decode('utf-8-sig'))))
    schema=T.StructType([T.StructField(f'c{i}',T.StringType(),True) for i in range(len(header))])
    raw=(spark.read.schema(schema).option('header',True).option('multiLine',True)
         .option('quote','"').option('escape','"').option('mode','FAILFAST')
         .csv(f's3://{bucket}/{key}')).cache()
    original=raw.count();assert original==base['linhas']
    clean=raw.dropDuplicates().cache();n=clean.count()
    indexes={h:f'c{i}' for i,h in enumerate(header)}
    def col(h):return F.col(indexes[h])
    selected=[F.lit(ed).alias('edicao'),F.lit(base['ano_coleta']).alias('ano_coleta'),
              F.lit(base['sha256']).alias('fonte_sha256')]
    for name,definition in cfg['campos'].items():
        source=col(definition['colunas'][ed])
        if name=='respondente_id':expr=source
        else:
            mapping=cfg['mapas_valores'][name][ed]
            allowed=list(mapping)
            assert not clean.filter(source.isNotNull() & ~source.isin(allowed)).limit(1).count(),f'Categoria desconhecida: {name}'
            typ={'boolean':'boolean','integer':'int'}.get(definition['tipo'],'string')
            pairs=[]
            for old,new in mapping.items():pairs.extend([F.lit(old),F.lit(new).cast(typ)])
            expr=F.create_map(*pairs)[source]
        selected.append(expr.alias(name))
        if name in ('salario_faixa','tamanho_empresa'):
            selected.append(source.alias(name+'_original'))
    resp=clean.select(*selected)
    assert resp.select('respondente_id').distinct().count()==n,'IDs conflitantes'
    resp=resp.withColumn('nivel_analitico',F.when(F.col('gestor')==True,F.lit('Gestor')).otherwise(F.col('senioridade')))
    resp=resp.withColumn('nivel_comparavel',F.when(F.col('nivel_analitico').isin('Sênior','Especialista/Staff+'),F.lit('Senior/Especialista')).otherwise(F.col('nivel_analitico')))
    for target,source in [('cargo_grupo','cargo_atual'),('experiencia_grupo','tempo_experiencia_dados'),('modelo_trabalho_grupo','modelo_trabalho_atual')]:
        pairs=[]
        for old,new in cfg['mapas_derivados'][target][ed].items():pairs.extend([F.lit(old),F.lit(new).cast('string')])
        resp=resp.withColumn(target,F.create_map(*pairs)[F.coalesce(F.col(source),F.lit(''))])
    responses.append(resp)
    for family,definition in multi.items():
        entry=definition['edicoes'][ed]
        if not entry['pergunta_disponivel']:continue
        opts=entry['opcoes']; vals=[F.when(F.trim(col(o['coluna_original']))!='',col(o['coluna_original']).cast('int')).otherwise(F.lit(None).cast('int')) for o in opts]
        for o in opts:
            assert not clean.filter(col(o['coluna_original']).isNotNull() & ~col(o['coluna_original']).isin('0','1','')).limit(1).count(),'Indicador fora do dominio'
        complete=functools.reduce(lambda a,b:a&b,[v.isNotNull() for v in vals])
        answered=functools.reduce(lambda a,b:a|b,[v.isNotNull() for v in vals])
        positive=functools.reduce(lambda a,b:a|b,[F.coalesce(v==1,F.lit(False)) for v in vals])
        conflict=F.lit(False)
        ex=definition['exclusividade']
        for i,o in enumerate(opts):
            if o['opcao_canonica'] in ex['opcoes_exclusivas']:
                others=[F.coalesce(v==1,F.lit(False)) for j,v in enumerate(vals) if j!=i and opts[j]['opcao_canonica'] not in ex['opcoes_compativeis_com_exclusiva']]
                conflict=conflict | (F.coalesce(vals[i]==1,F.lit(False)) & functools.reduce(lambda a,b:a|b,others,F.lit(False)))
        status=(F.when(~answered,'sem_resposta').when(conflict,'contraditoria')
                .when(~complete,'parcial').when(~positive,'sem_selecao').otherwise('valida'))
        array=F.array(*[F.struct(F.lit(o['opcao_canonica']).alias('opcao'),vals[i].alias('selecionado'),F.lit(o['rotulo_original']).alias('rotulo_original')) for i,o in enumerate(opts)])
        long=clean.select(F.lit(ed).alias('edicao'),col(cfg['campos']['respondente_id']['colunas'][ed]).alias('respondente_id'),F.lit(family).alias('familia'),status.alias('status_resposta'),F.explode(array).alias('item')).select('edicao','respondente_id','familia','status_resposta','item.*')
        choices.append(long)
    audit.append({'edicao':ed,'bronze':original,'duplicatas':original-n,'silver':n})
    # Os DataFrames derivados sao avaliados antes de liberar o cache no fim do job.
resp=union(responses).cache();opts=union(choices).cache()
assert resp.count()==14002
write_table(resp,'silver','respostas');write_table(opts,'silver','opcoes')
perfil_fields=['genero','raca','pcd','regiao','formacao_nivel','situacao_trabalho','setor_empresa','nivel_analitico','cargo_grupo','modelo_trabalho_grupo']
perfil=resp.select('edicao',F.explode(F.array(*[F.struct(F.lit(c).alias('campo'),F.coalesce(F.col(c),F.lit('Sem informacao')).alias('categoria')) for c in perfil_fields])).alias('item')).select('edicao','item.*').groupBy('edicao','campo','categoria').count()
write_table(perfil,'gold','perfil')
from pyspark.sql.window import Window
tech=opts.filter(F.col('status_resposta')=='valida').groupBy('edicao','familia','opcao').agg(F.sum('selecionado').alias('selecionaram'),F.count('*').alias('denominador')).withColumn('percentual',F.col('selecionaram')/F.col('denominador')*100)
write_table(tech,'gold','tecnologias_ia')
salary=resp.filter((F.col('vive_no_brasil')==True)&F.col('salario_faixa').isNotNull()&F.col('situacao_trabalho').isNotNull()&~F.col('situacao_trabalho').contains('empresa de fora do Brasil')).groupBy('edicao','cargo_grupo','nivel_comparavel','situacao_trabalho','salario_faixa').count()
write_table(salary,'gold','remuneracao')
quality=opts.filter(F.col('familia')=='ia_produtividade').select('edicao','respondente_id','status_resposta').distinct().groupBy('edicao','status_resposta').count()
write_table(quality,'gold','qualidade_ia')
checks=opts.filter((F.col('familia')=='ia_produtividade')&(F.col('status_resposta')=='valida')).select('edicao','respondente_id').distinct().groupBy('edicao').count().collect()
assert {r['edicao']:r['count'] for r in checks}=={'2023-2024':3746,'2024-2025':3604,'2025-2026':2100}
s3.put_object(Bucket=bucket,Key=f'{prefix}/auditoria/ultima_execucao.json',Body=json.dumps({'contagens':audit,'silver_total':14002,'job_run_id':sys.argv[sys.argv.index('--JOB_RUN_ID')+1] if '--JOB_RUN_ID' in sys.argv else None}).encode())
job.commit()
