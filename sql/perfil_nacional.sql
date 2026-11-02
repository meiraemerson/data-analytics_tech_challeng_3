SELECT edicao, 'cargo_grupo' AS campo, COALESCE(cargo_grupo, 'Sem informacao') AS categoria, COUNT(*) AS n FROM silver_respostas GROUP BY edicao, cargo_grupo
UNION ALL
SELECT edicao, 'nivel_comparavel' AS campo, COALESCE(nivel_comparavel, 'Sem informacao') AS categoria, COUNT(*) AS n FROM silver_respostas GROUP BY edicao, nivel_comparavel
UNION ALL
SELECT edicao, 'modelo_trabalho_grupo' AS campo, COALESCE(modelo_trabalho_grupo, 'Sem informacao') AS categoria, COUNT(*) AS n FROM silver_respostas GROUP BY edicao, modelo_trabalho_grupo
UNION ALL
SELECT edicao, 'regiao' AS campo, COALESCE(regiao, 'Sem informacao') AS categoria, COUNT(*) AS n FROM silver_respostas GROUP BY edicao, regiao
ORDER BY edicao, campo, n DESC;
