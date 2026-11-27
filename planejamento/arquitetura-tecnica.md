# Arquitetura técnica e critérios operacionais

## Abordagem

Aplicação de linha de comando com a **biblioteca padrão do Python**. `main()` coordena a leitura ou geração de `vendas.csv`, prepara os registros e usa as métricas e os segmentos para compor os relatórios.

RF07–RF09 foram publicados no commit `6f4ac6c` de `feat/exportacao-fluxo` e integrados em `develop` no commit `adf9233`. [PR nº 4](https://github.com/fabcosta-br/salesinsight-py/pull/4)

A revisão preventiva do Gate 05 foi publicada em `docs/readme` no commit `8b1a4b1`. A integração em `develop` segue pendente pelo PR nº 5, que está aberto. [PR nº 5](https://github.com/fabcosta-br/salesinsight-py/pull/5)

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
- RF08: os CSVs têm cabeçalhos fixos, inclusive se a entrada gerar zero vendas válidas. A reserva exclusiva sob `outputs/` contém a preparação em UTF-8 e as cópias de recuperação. Uma falha tratável na substituição ou na conferência do JSON aciona a restauração das saídas anteriores.
- RF09: `main()` carrega ou gera a entrada, inspeciona, limpa, deriva, agrega, segmenta, exporta e exibe o JSON conferido e o resumo final.

## Estratégia de testes

1. Dataset `seed=42` deve ser reproduzível (hash e linhas conferidos); relatório de limpeza deve fechar contagens.
2. Testar exemplos de datas inválidas, `""` em quantidade/preço, nomes de clientes com ruído e limites dos segmentos.
3. Conferir total de receita por grupo versus total geral de registros limpos.
4. Executar a partir de pasta nova com Python da `.venv` sem dependências adicionais.
5. Verificar idempotência de saídas e conteúdo do JSON relido; garantir ausência de arquivos privados no Git.

A validação local aprovou 29 testes em Python 3.12.10. O JSON e o CSV mensal reconciliaram 183 vendas válidas, 1.031 unidades e R$ 1.290.346,30. O CSV de segmentação listou 50 clientes, com 6 Bronze, 10 Prata e 34 Ouro. A suíte usa pastas temporárias para a execução integrada e cobre falha de escrita, falha de substituição e divergência na releitura.

## Permissões dos relatórios no Windows

No Windows com Python 3.12.10, o diagnóstico em pasta temporária mostrou que a área criada por `TemporaryDirectory` tinha ACL restrita. Os arquivos preparados receberam essa ACL e `Path.replace()` a manteve ao movê-los para o destino no mesmo volume NTFS. Com isso, a conta usada pelo Git perdeu acesso a relatórios publicados por outra identidade local. [Documentação da Microsoft sobre permissões em cópias e movimentações](https://learn.microsoft.com/en-us/troubleshoot/windows-client/windows-security/permissions-on-copying-moving-files)

O Gate 05 prepara os arquivos e as cópias de recuperação na própria reserva, criada com `Path.mkdir()` sob o diretório de saída. A reserva recebe a herança de `outputs/`. O fluxo mantém a substituição por arquivo, a recuperação em falhas tratáveis e a conferência do JSON. A limpeza remove apenas os arquivos temporários previstos e suas duas pastas de trabalho.

## Referência de escopo

Os requisitos RF01–RF09 detalhados na versão reduzida do enunciado de 10/09/2026 são a referência desta entrega. O prazo oficial registrado no AVA é **30/11/2026 às 23h59**.
