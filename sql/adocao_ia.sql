WITH respostas AS (
    SELECT
        edicao,
        respondente_id,
        MAX(CASE WHEN opcao = 'nao_usa' AND selecionado = 1
                 THEN 1 ELSE 0 END) AS nao_usa,
        MAX(CASE WHEN opcao <> 'nao_usa' AND selecionado = 1
                 THEN 1 ELSE 0 END) AS usa_ia
    FROM silver_opcoes
    WHERE familia = 'ia_produtividade'
      AND status_resposta = 'valida'
    GROUP BY edicao, respondente_id
)
SELECT
    edicao,
    COUNT(*) AS respostas_validas,
    SUM(usa_ia) AS declararam_uso,
    SUM(nao_usa) AS declararam_nao_uso,
    ROUND(100.0 * SUM(usa_ia) / COUNT(*), 2) AS percentual_entre_validas
FROM respostas
GROUP BY edicao
ORDER BY edicao;
