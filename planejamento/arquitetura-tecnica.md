# Arquitetura técnica e critérios operacionais

## Abordagem

Aplicação de linha de comando com a **biblioteca padrão do Python**. `main()` coordena a leitura ou geração de `vendas.csv`, prepara os registros e usa as métricas e os segmentos para compor os relatórios.

```text
vendas.csv (gerado ou carregado)
   ↓ RF02: inspeção
   ↓ RF03: limpeza e relatório (datas inválidas/nulos/regex/tipos)
   ↓ RF04: colunas derivadas (receita/mês/ano/trimestre/faixa)
   ↓ RF05: métricas (mês/produto/categoria/região)
   ↓ RF06–RF07: segmentação com função de ordem superior
   ↓ RF08: exportação dos relatórios e conferência do JSON
   ↓ RF09: resumo da execução orquestrada por main()
```

## Interfaces implementadas

| Função | Entrada | Saída |
|---|---|---|
| `gerar_dataset_vendas(caminho_csv, n_registros, seed)` | caminho, volume, semente | grava `vendas.csv` |
| `carregar_dataset(caminho_csv)` | CSV | lista de dicionários |
| `inspecionar_dados(registros)` | lista bruta | resumo no console |
| `limpar_dados(registros)` | brutos | `(registros_limpos, relatorio)` |
| `criar_colunas_derivadas(registros)` | limpos | registros enriquecidos |
| `calcular_metricas(registros)` | enriquecidos | dicionário com `por_mes`, `top_produtos`, `por_categoria`, `por_regiao` |
| `segmentar_clientes(registros)` | enriquecidos | clientes, gastos e segmentos |
| `processar_coluna(registros, coluna, funcao_transformacao, nome_saida)` | registros, campo de entrada, função e campo de saída | novos dicionários com a transformação aplicada |
| `calcular_estatisticas(metricas, clientes, relatorio_limpeza)` | métricas, segmentos e contagens da limpeza | totais consolidados para o JSON |
| `exportar_resultados(metricas, clientes, estatisticas, pasta_saida="outputs")` | estruturas de saída e diretório | dois CSVs, um JSON e o dicionário relido e conferido |
| `main()` | `vendas.csv` no diretório de execução, com geração quando ausente | relatórios em `outputs/` e resumo no console |

## Contratos críticos

- CSV original contém `id_venda`, `data_venda`, `cliente`, `produto`, `categoria`, `regiao`, `quantidade`, `preco_unitario`.
- A geração de dados brutos insere incoerências intencionalmente; não limpar no gerador.
- RF03: descartar registros com datas inválidas e numéricos críticos faltantes; `strip()` e regex antes das métricas. **Não** imputar nulos nem remover outliers nesta versão.
- RF04: `receita_total = quantidade * preco_unitario`; `mes_nome` em português via dicionário; `trimestre` Q1–Q4; classificar faixa com condicionais.
- RF05: conferir somatórios gerais e por grupo; evitar dupla contagem; definir e explicar ticket médio por venda.
- RF06: Bronze abaixo R$ 5.000; Prata entre R$ 5.000 e R$ 15.000; Ouro acima R$ 15.000.
- RF07: uma `lambda` ordena produtos por receita decrescente e nome crescente. A outra classifica o gasto acumulado em `processar_coluna()`.
- RF08: os CSVs têm cabeçalhos fixos, inclusive se a entrada gerar zero vendas válidas. Os três arquivos são escritos em UTF-8 em uma pasta temporária antes da substituição. Uma reserva impede substituições simultâneas, e uma falha tratável nessa etapa ou na conferência do JSON aciona a restauração das saídas anteriores.
- RF09: `main()` carrega ou gera a entrada, inspeciona, limpa, deriva, agrega, segmenta, exporta e exibe o JSON conferido e o resumo final.

## Estratégia de testes

1. Dataset `seed=42` deve ser reproduzível (hash e linhas conferidos); relatório de limpeza deve fechar contagens.
2. Testar exemplos de datas inválidas, `""` em quantidade/preço, nomes de clientes com ruído e limites dos segmentos.
3. Conferir total de receita por grupo versus total geral de registros limpos.
4. Executar a partir de pasta nova com Python da `.venv` sem dependências adicionais.
5. Verificar idempotência de saídas e conteúdo do JSON relido; garantir ausência de arquivos privados no Git.

A validação local aprovou 29 testes em Python 3.12.10. O JSON e o CSV mensal reconciliaram 183 vendas válidas, 1.031 unidades e R$ 1.290.346,30. O CSV de segmentação listou 50 clientes, com 6 Bronze, 10 Prata e 34 Ouro. A suíte usa pastas temporárias para a execução integrada e cobre falha de escrita, falha de substituição e divergência na releitura.

## Decisões e ressalvas de fonte

- O PDF foi atualizado para **escopo reduzido**, mas contém páginas com cabeçalho T3 e sumário anterior de RF01–RF11. Adotar RF01–RF09 detalhados no corpo do PDF; não incluir NumPy, visualizações ou classes na entrega obrigatória.
- A pedagogia confirmou a aplicação do peso 25% para T4; a tabela de critérios do PDF ainda contém uma referência anterior a 30%.
- O prazo excepcional exibido no AVA é **30/11/2026 às 23h59**; manter meta interna 30/11 até 12h.
