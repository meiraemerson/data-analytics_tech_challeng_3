# Narrativa executiva

Identidade visual: preto, branco e rosa FIAP `#ED145B`, confirmado no [SVG oficial](https://www.fiap.com.br/svg/fiap.svg), consultado em 02/11/2026. Logos dos serviços mantêm suas marcas.

A apresentação tem 15 slides, dos quais os três últimos compõem o apêndice técnico. As notas dos slides incluem sugestões de transição para a fala.

| Slides | Papel na narrativa |
|---|---|
| 1–2 | Contexto e problema de expansão de uma área de Dados |
| 3–4 | Perfis e senioridade no Brasil, com evolução do remoto entre edições |
| 5–6 | Recorte financeiro e referências de remuneração por nível |
| 7–8 | Diversidade, regiões e modelos de trabalho |
| 9–10 | Uso de cloud e BI, preferência por Python e adoção declarada de IA |
| 11–12 | Recomendações e conclusão para a instituição |
| 13–15 | Fluxo AWS, qualidade das bases e arquitetura Draw.io |

## Evidências complementares

`results/perfil_nacional.csv` contém contagens por cargo, nível, modelo e região, incluindo ausência de informação. A conferência local usou os CSVs originais e os contratos de tratamento do projeto. `sql/perfil_nacional.sql` reproduz esses agrupamentos sobre a Silver no Athena. Essas consultas complementares não foram reexecutadas na AWS nesta revisão.

Na edição recente, cargos informados somam 2.500 respostas, nível informado soma 3.227 e modelos de trabalho informados somam 3.227. Denominadores diferentes são explícitos nos slides. Comparações temporais são entre amostras independentes. O remoto diminui na última edição nos níveis exibidos, sem uma causa identificada pela pesquisa. Uso de AWS e Power BI cresce entre os extremos, sem medir tamanho do mercado ou proficiência. A pergunta de preferência por Python permanece separada de uso no trabalho.

Nenhum ganho de produtividade, retorno financeiro ou efeito de contratação foi estimado. As recomendações são propostas para validação interna.
