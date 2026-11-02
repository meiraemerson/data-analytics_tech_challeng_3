SELECT
    edicao, nivel_comparavel, modelo_trabalho_grupo,
    COUNT(*) AS respondentes,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (PARTITION BY edicao, nivel_comparavel), 2
    ) AS percentual_no_nivel
FROM silver_respostas
WHERE nivel_comparavel IS NOT NULL
  AND modelo_trabalho_grupo IS NOT NULL
  AND modelo_trabalho_grupo <> 'Sem informacao'
GROUP BY edicao, nivel_comparavel, modelo_trabalho_grupo
ORDER BY edicao, nivel_comparavel, respondentes DESC;
