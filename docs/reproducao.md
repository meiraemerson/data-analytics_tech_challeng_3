# Reprodução no Jupyter e AWS Academy

## Ambiente local

Python 3.11 é a versão de referência para a organização deste pacote. As faixas de dependências estão em `requirements.txt`; não constituem um lock do ambiente original.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Abra `notebooks/Tech_Challenge_Fase3.ipynb`. O notebook detecta a raiz do repositório quando aberto na raiz ou em `notebooks/`.

## Credenciais e configuração

Inicie o laboratório AWS Academy e configure fora do repositório o perfil local `default`, com `aws_access_key_id`, `aws_secret_access_key` e `aws_session_token` temporários, conforme o arquivo de credenciais mostrado no laboratório. Renove os três campos quando a sessão expirar. Nunca os inclua em células ou commits.

Na primeira célula de configuração, ajuste somente `PERFIL_AWS`, `REGIAO`, `BUCKET_EXISTENTE` (vazio para gerar um nome) e, se necessário, `ROLE_GLUE_ARN`. A LabRole é procurada automaticamente; permissões de criação de bucket, Glue e Athena dependem do laboratório. `WORKGROUP_ATHENA` deve corresponder ao workgroup disponível.

Execute as células em ordem. O notebook realiza o download e a validação das fontes, publica Bronze e contratos no S3, envia o script, cria/executa o job Glue, monitora a execução e consulta Athena. A execução provisiona e utiliza recursos da sua conta de laboratório. O processamento distribuído ocorre no Glue 5.0; não é necessário instalar PySpark ou `awsglue` localmente.

## Navegação

- Notebook: execução integrada e resultados salvos das análises.
- `src/glue_etl.py`: cópia extraída do script definido no notebook.
- `config/`: contratos extraídos do notebook, com campos e hashes das fontes.
- `sql/`: consultas SQL literais extraídas das etapas 6, 8 e 9.
- `results/`: agregados usados no relatório; nenhuma resposta individual.

O notebook é a fonte de execução. Ao alterar contratos ou o script extraído, atualize também suas definições no notebook. Arquivos SQL podem ser executados no Athena após selecionar o catálogo/banco criado pelo projeto.

## Validação local

```bash
python src/validar_projeto.py
```

Essa validação verifica estrutura do notebook, sintaxe Python e legibilidade dos agregados. Ela não executa o laboratório AWS. As saídas analíticas preservadas são evidências da execução anterior; logs com identificadores do laboratório foram removidos da versão pública.
