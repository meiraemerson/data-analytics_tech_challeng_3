WITH base AS (
    SELECT
        edicao,
        CASE
            WHEN setor_empresa = 'Finanças ou Bancos' THEN 'Financeiro'
            ELSE 'Demais setores'
        END AS recorte_setor,
        nivel_comparavel,
        salario_faixa
    FROM silver_respostas
    WHERE setor_empresa IS NOT NULL
      AND vive_no_brasil = TRUE
      AND salario_faixa IS NOT NULL
      AND situacao_trabalho IS NOT NULL
      AND situacao_trabalho NOT LIKE '%empresa de fora do Brasil%'
      AND nivel_comparavel IS NOT NULL
)
SELECT
    edicao, recorte_setor, nivel_comparavel, salario_faixa,
    COUNT(*) AS respondentes,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (
              PARTITION BY edicao, recorte_setor, nivel_comparavel
          ), 2
    ) AS percentual_no_grupo
FROM base
GROUP BY edicao, recorte_setor, nivel_comparavel, salario_faixa
ORDER BY edicao, recorte_setor, nivel_comparavel, respondentes DESC;
