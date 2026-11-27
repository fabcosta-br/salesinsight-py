# Matriz de rastreabilidade — SalesInsight PY (T4)

**Fonte:** enunciado M1S08, versão reduzida 10/09/2026, seções 4.2 e 5.  
**Status:** RF01–RF09 implementados e validados com Python 3.12.10. O Gate 04 (RF07–RF09) foi publicado em `feat/exportacao-fluxo` no commit `6f4ac6c` e integrado em `develop` no merge `adf9233`. A suíte tem 29 testes aprovados. [PR nº 4](https://github.com/fabcosta-br/salesinsight-py/pull/4)

| ID | Obrigação verificável | Evidência | Aceite técnico | Branch |
|---|---|---|---|---|
| RF01 | Gerar `vendas.csv` sintético determinístico (`seed=42`, ~200 registros) ou carregar CSV com campos exigidos | Dataset e função geradora/leitura | 8 campos originais; valores deliberadamente inconsistentes conforme referência; regeneração reproduzível | `feat/dados-inspecao` |
| RF02 | Exibir número de registros, colunas, nulos por coluna e primeiras 5 linhas | Saída de console de inspeção | Contagens consistentes com os registros originais | `feat/dados-inspecao` |
| RF03 | `strip`, datas inválidas via `datetime.strptime` com exceção, descarte de críticos ausentes, conversão de tipos, regex em cliente, relatório de remoções | Registros limpos + relatório | `iniciais = removidos + finais` (200 = 17 + 183 no CSV oficial). Datas válidas e críticos preenchidos entre os finais. Variantes de cliente normalizadas e demais nomes sinalizados. | `feat/limpeza-transformacao` |
| RF04 | `receita_total`, `mes`, `mes_nome` em português, `trimestre` Q1–Q4, `ano`, `faixa_receita_item` | Registros derivados | Receita = quantidade × preço. Faixas oficiais com limites em 500 e 5000. Calendário e valores derivados conferidos nos 183 registros válidos. | `feat/limpeza-transformacao` |
| RF05 | Agregar receita/quantidade/nº vendas por mês; Top 5 produtos; receita por categoria; receita e ticket médio por região | Estrutura dicionário de listas + console | Receita de R$ 1.290.346,30 reconciliada com os 183 registros válidos. Top 5 em ordem decrescente. Ticket médio por registro válido da região. | `feat/metricas-segmentacao` |
| RF06 | Gastos acumulados por cliente, Bronze (<5000), Prata (5000–15000), Ouro (>15000); lambda; Top 10 e contagem por segmento | Lista de segmentos + console | Limiares inclusivos de Prata verificados. Top 10 ordenado e 50 clientes classificados (6 Bronze, 10 Prata e 34 Ouro). | `feat/metricas-segmentacao` |
| RF07 | Funções com parâmetros, retornos e docstrings, duas aplicações de `lambda` e função de ordem superior | `processar_coluna()` classifica clientes com uma função recebida. O ranking de produtos usa outra `lambda`. | Aplicação da função recebida, limites dos segmentos e desempate do ranking verificados em testes | `feat/exportacao-fluxo` |
| RF08 | Exportar CSV de mês e segmentos, gravar e reler JSON de estatísticas | `outputs/metricas_por_mes.csv`, `outputs/segmentacao_clientes.csv`, `outputs/estatisticas_gerais.json` | Cabeçalhos e UTF-8 verificados. Totais dos relatórios conferidos com os cálculos e JSON relido. | `feat/exportacao-fluxo` |
| RF09 | `main()` e `if __name__ == "__main__":` executam o fluxo completo | Execução local e testes em diretório temporário | Limpeza antes da transformação e das agregações. Duas execuções reproduzem os três relatórios e preservam a entrada existente. | `feat/exportacao-fluxo` |

## Critérios transversais da rubrica (10 pontos)

| Critério | Pontuação máxima | Evidência |
|---|---:|---|
| README com objetivo, instalação, execução, conceitos e link do vídeo | 1,00 | `README.md` revisado no Gate 05. Link do vídeo pendente. |
| GitHub: branches descritivas e commits que reflitam evolução lógica | 1,00 | `main`/`develop`, features e PRs, pelo menos 5 commits individuais |
| Vídeo até cinco minutos: execução, decisão técnica e oportunidades de melhoria | 2,00 | URL pública funcional |
| RF01–RF03 | 2,00 | Dados/limpeza + relatório |
| RF04–RF06 | 2,50 | Derivação/agregação/segmentação |
| RF07 | 1,00 | Funções, lambda, ordem superior |
| RF08–RF09 | 0,50 | CSV/JSON, leitura e `main()` |
| **Total** | **10,00** | |

A revisão preventiva de RF08 no Gate 05 foi publicada em `docs/readme` no commit `8b1a4b1` e integrada em `develop` no commit `6ac11d3`. A auditoria final do Gate 06 está em andamento. A integração em `main`, a gravação do vídeo e a submissão no AVA seguem pendentes. [PR nº 5](https://github.com/fabcosta-br/salesinsight-py/pull/5)

**Atenção ao enunciado:** o sumário anterior enumera RF01–RF11 com NumPy/gráficos/classes, mas a versão reduzida vigente detalha RF01–RF09 como obrigatórios. Os itens opcionais não pontuam nesta versão. O professor deve poder distinguir implementação e revisão a partir do histórico.
