WITH base AS (
    SELECT
        edicao,
        CASE
            WHEN setor_empresa = 'Finanças ou Bancos' THEN 'Financeiro'
            ELSE 'Demais setores'
        END AS recorte_setor,
        COALESCE(cargo_grupo, 'Sem informacao') AS cargo_grupo
    FROM silver_respostas
    WHERE setor_empresa IS NOT NULL
)
SELECT
    edicao, recorte_setor, cargo_grupo,
    COUNT(*) AS respondentes,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (PARTITION BY edicao, recorte_setor), 2
    ) AS percentual_no_setor
FROM base
GROUP BY edicao, recorte_setor, cargo_grupo
ORDER BY edicao, recorte_setor, respondentes DESC;
