# Arquitetura técnica e critérios operacionais

## Abordagem

Aplicação de linha de comando usando **somente a biblioteca padrão do Python** (`csv`, `json`, `os`, `re`, `random`, `datetime`, `collections`). Uma sequência de funções transforma a entrada `vendas.csv` em métricas, segmentação e arquivos exportados. Não usar modelos de Machine Learning nesta versão.

```text
vendas.csv (gerado ou carregado)
   ↓ RF02: inspeção
   ↓ RF03: limpeza e relatório (datas inválidas/nulos/regex/tipos)
   ↓ RF04: colunas derivadas (receita/mês/ano/trimestre/faixa)
   ├─ RF05: métricas (mês/produto/categoria/região)
   └─ RF06: segmentação Bronze/Prata/Ouro
        ↓ RF07: funções reutilizáveis/lambdas/ordem superior
        ↓ RF08: arquivos CSV, JSON e leitura de volta
        ↓ RF09: execução integrada main()
```

## Interfaces planejadas (a implementar e validar)

| Função | Entrada | Saída |
|---|---|---|
| `gerar_dataset_vendas(caminho_csv, n_registros, seed)` | caminho, volume, semente | grava `vendas.csv` |
| `carregar_dataset(caminho_csv)` | CSV | lista de dicionários |
| `inspecionar_dados(registros)` | lista bruta | resumo no console |
| `limpar_dados(registros)` | brutos | `(registros_limpos, relatorio)` |
| `criar_colunas_derivadas(registros)` | limpos | registros enriquecidos |
| `calcular_metricas(registros)` | enriquecidos | dicionário com `por_mes`, `top_produtos`, `por_categoria`, `por_regiao` |
| `segmentar_clientes(registros)` | enriquecidos | clientes, gastos, segmentos |
| `processar_coluna(registros, coluna, funcao_transformacao, nome_saida)` | registros/função | dados transformados |
| `exportar_resultados(metricas, clientes, estatisticas)` | estruturas de saída | CSV/JSON e conferência |
| `main()` | arquivos e funções | fluxo completo sem erro |

## Contratos críticos

- CSV original contém `id_venda`, `data_venda`, `cliente`, `produto`, `categoria`, `regiao`, `quantidade`, `preco_unitario`.
- A geração de dados brutos insere incoerências intencionalmente; não limpar no gerador.
- RF03: descartar registros com datas inválidas e numéricos críticos faltantes; `strip()` e regex antes das métricas. **Não** imputar nulos nem remover outliers nesta versão.
- RF04: `receita_total = quantidade * preco_unitario`; `mes_nome` em português via dicionário; `trimestre` Q1–Q4; classificar faixa com condicionais.
- RF05: conferir somatórios gerais e por grupo; evitar dupla contagem; definir e explicar ticket médio por venda.
- RF06: Bronze abaixo R$ 5.000; Prata entre R$ 5.000 e R$ 15.000; Ouro acima R$ 15.000.
- RF07: lambdas em **dois contextos distintos**; uma função recebe outra função como argumento.
- RF08: `outputs/metricas_por_mes.csv`, `outputs/segmentacao_clientes.csv`, `outputs/estatisticas_gerais.json`; reabrir JSON após escrita.
- RF09: geração/carregamento → inspeção → limpeza → derivação → métricas/segmentação → exportação, nunca as agregações antes da limpeza.

## Estratégia de testes

1. Dataset `seed=42` deve ser reproduzível (hash e linhas conferidos); relatório de limpeza deve fechar contagens.
2. Testar exemplos de datas inválidas, `""` em quantidade/preço, nomes de clientes com ruído e limites dos segmentos.
3. Conferir total de receita por grupo versus total geral de registros limpos.
4. Executar a partir de pasta nova com Python da `.venv` sem dependências adicionais.
5. Verificar idempotência de saídas e conteúdo do JSON relido; garantir ausência de arquivos privados no Git.

## Decisões e ressalvas de fonte

- O PDF foi atualizado para **escopo reduzido**, mas contém páginas com cabeçalho T3 e sumário anterior de RF01–RF11. Adotar RF01–RF09 detalhados no corpo do PDF; não incluir NumPy, visualizações ou classes na entrega obrigatória.
- A pedagogia confirmou a aplicação do peso 25% para T4; a tabela de critérios do PDF ainda contém uma referência anterior a 30%.
- O prazo excepcional exibido no AVA é **30/11/2026 às 23h59**; manter meta interna 30/11 até 12h.
- O código inicial deste pacote é intencionalmente incompleto. Planejamento não equivale a implementação verificada.
