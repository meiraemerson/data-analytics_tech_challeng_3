SELECT
    edicao,
    regiao,
    nivel_comparavel,
    COUNT(*) AS respondentes,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (PARTITION BY edicao, regiao), 2
    ) AS percentual_na_regiao
FROM silver_respostas
WHERE regiao IS NOT NULL
  AND TRIM(regiao) <> ''
  AND regiao <> 'Sem informacao'
  AND nivel_comparavel IS NOT NULL
  AND TRIM(nivel_comparavel) <> ''
GROUP BY edicao, regiao, nivel_comparavel
ORDER BY edicao, regiao, respondentes DESC;
