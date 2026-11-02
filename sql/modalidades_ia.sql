SELECT edicao, opcao, selecionaram, denominador, percentual
FROM gold_tecnologias_ia
WHERE familia = 'ia_produtividade'
ORDER BY edicao, percentual DESC;
