SELECT
    edicao,
    cargo_grupo,
    COUNT(*) AS genero_informado,
    SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) AS mulheres,
    ROUND(100.0 * SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS percentual_feminino
FROM silver_respostas
WHERE genero IN ('Feminino', 'Masculino', 'Outro')
  AND cargo_grupo IS NOT NULL
  AND cargo_grupo <> 'Sem informacao'
GROUP BY edicao, cargo_grupo
ORDER BY edicao, genero_informado DESC;
