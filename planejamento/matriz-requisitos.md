# Matriz de rastreabilidade — SalesInsight PY (T4)

**Fonte:** enunciado M1S08, versão reduzida 10/09/2026, seções 4.2 e 5.  
**Status:** RF01–RF04 implementados e validados localmente com Python 3.12.10. RF05–RF09 previstos.

| ID | Obrigação verificável | Evidência prevista | Aceite técnico | Branch prevista |
|---|---|---|---|---|
| RF01 | Gerar `vendas.csv` sintético determinístico (`seed=42`, ~200 registros) ou carregar CSV com campos exigidos | Dataset e função geradora/leitura | 8 campos originais; valores deliberadamente inconsistentes conforme referência; regeneração reproduzível | `feat/dados-inspecao` |
| RF02 | Exibir número de registros, colunas, nulos por coluna e primeiras 5 linhas | Saída de console de inspeção | Contagens consistentes com os registros originais | `feat/dados-inspecao` |
| RF03 | `strip`, datas inválidas via `datetime.strptime` com exceção, descarte de críticos ausentes, conversão de tipos, regex em cliente, relatório de remoções | Registros limpos + relatório | `iniciais = removidos + finais` (200 = 17 + 183 no CSV oficial). Datas válidas e críticos preenchidos entre os finais. Variantes de cliente normalizadas e demais nomes sinalizados. | `feat/limpeza-transformacao` |
| RF04 | `receita_total`, `mes`, `mes_nome` em português, `trimestre` Q1–Q4, `ano`, `faixa_receita_item` | Registros derivados | Receita = quantidade × preço. Faixas oficiais com limites em 500 e 5000. Calendário e valores derivados conferidos nos 183 registros válidos. | `feat/limpeza-transformacao` |
| RF05 | Agregar receita/quantidade/nº vendas por mês; Top 5 produtos; receita por categoria; receita e ticket médio por região | Estrutura dicionário de listas + console | Somatórios consistentes com dados limpos; Top 5 ordenado; ticket médio definido explicitamente | `feat/metricas-segmentacao` |
| RF06 | Gastos acumulados por cliente, Bronze (<5000), Prata (5000–15000), Ouro (>15000); lambda; Top 10 e contagem por segmento | Lista de segmentos + console | Limiares corretos e receita consolidada por cliente | `feat/metricas-segmentacao` |
| RF07 | Funções com parâmetros, retornos e docstrings; duas aplicações de lambda em contextos distintos; função de ordem superior que recebe função | `salesinsight.py` | Todas as etapas encapsuladas; `processar_coluna(...)` ou equivalente com função como parâmetro | `feat/exportacao-fluxo` e revisão transversal |
| RF08 | Exportar CSV de mês e segmentos; JSON de estatísticas; reler JSON | `outputs/metricas_por_mes.csv`, `outputs/segmentacao_clientes.csv`, `outputs/estatisticas_gerais.json` | Arquivos não vazios e leitura de retorno consistente | `feat/exportacao-fluxo` |
| RF09 | `main()` e `if __name__ == '__main__':`; fluxo completo de ponta a ponta | Execução do script em ambiente limpo | Saída sem exceções; limpeza antes de transformação e agregações; outputs regenerados | `feat/exportacao-fluxo` |

## Critérios transversais da rubrica (10 pontos)

| Critério | Pontuação máxima | Evidência |
|---|---:|---|
| README com objetivo, instalação, execução, conceitos e link do vídeo | 1,00 | `README.md` completo |
| GitHub: branches descritivas e commits que reflitam evolução lógica | 1,00 | `main`/`develop`, features e PRs, pelo menos 5 commits individuais |
| Vídeo até cinco minutos: execução, decisão técnica e oportunidades de melhoria | 2,00 | URL pública funcional |
| RF01–RF03 | 2,00 | Dados/limpeza + relatório |
| RF04–RF06 | 2,50 | Derivação/agregação/segmentação |
| RF07 | 1,00 | Funções, lambda, ordem superior |
| RF08–RF09 | 0,50 | CSV/JSON, leitura e `main()` |
| **Total** | **10,00** | |

**Atenção ao enunciado:** o sumário anterior enumera RF01–RF11 com NumPy/gráficos/classes, mas a versão reduzida vigente detalha RF01–RF09 como obrigatórios. Os itens opcionais não pontuam nesta versão. O professor deve poder distinguir implementação e revisão a partir do histórico.
