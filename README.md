# SalesInsight PY — Análise de Dados de Vendas

**Projeto acadêmico:** SCTEC/SENAI — Desenvolvimento de IA para Análise Preditiva — Turma T4, Módulo 1 (Mini-Projeto da Semana 08).  
**Responsável acadêmico:** Fabiano Rodrigo Costa.

> **Status: RF01 e RF02 implementados.** O projeto completo segue em desenvolvimento.

## Objetivo

Construir, em Python, um fluxo reprodutível de análise de vendas para uma empresa de varejo: carregar um CSV, inspecionar e limpar registros, criar colunas derivadas, agregar métricas, segmentar clientes e exportar resultados para CSV e JSON.

O escopo obrigatório segue a **versão reduzida do enunciado de 10/09/2026**, correspondente aos conteúdos do Módulo 1 até a Semana 05. Não exige Pandas, NumPy, Matplotlib, Seaborn, classes ou modelos preditivos.

## Escopo e rastreabilidade

- [Matriz RF01–RF09 e critérios de aceitação](planejamento/matriz-requisitos.md)
- [Kanban operacional](planejamento/tarefas-kanban.md)
- [Arquitetura e decisões técnicas](planejamento/arquitetura-tecnica.md)
- [Checklist de avaliação e entrega](planejamento/checklist-rubrica.md)

## Origem dos dados

A opção A, recomendada no enunciado, gera dados sintéticos em Python. A opção B permite usar um dataset externo, mediante adaptação aos campos e critérios de qualidade exigidos. A opção A foi adotada pela reprodutibilidade, pelo controle das inconsistências inseridas e pelo alinhamento ao gerador fornecido nas páginas 5 e 6 do enunciado.

## Jornada do dataset

```mermaid
flowchart TD
    origem["Escolha da origem dos dados (opção A selecionada)"]
    geracao["RF01 — Geração (concluída)"]
    inspecao["RF02 — Inspeção (concluída)"]
    tratamento["RF03/RF04 — Limpeza e transformação (futuras)"]
    analise["RF05–RF09 — Análise e exportação (futuras)"]
    origem --> geracao
    geracao --> inspecao
    inspecao --> tratamento
    tratamento --> analise
```

## Estrutura

```text
salesinsight-py/
├── README.md
├── salesinsight.py           # geração, leitura e inspeção
├── vendas.csv               # dados sintéticos de RF01
├── test_salesinsight.py      # testes de RF01 e RF02
├── outputs/                 # relatórios CSV/JSON produzidos em RF08
└── planejamento/
    ├── matriz-requisitos.md
    ├── tarefas-kanban.md
    ├── arquitetura-tecnica.md
    └── checklist-rubrica.md
```

## Ambiente previsto (Windows / PowerShell)

Recomendação: Python 3.12, VS Code com extensão Python e GitHub Desktop. O trabalho obrigatório utiliza apenas a biblioteca padrão do Python; **não requer instalações de bibliotecas externas**.

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe --version
```

Para executar RF01 e RF02, rode na raiz do repositório:

```powershell
.\.venv\Scripts\python.exe -X utf8 salesinsight.py
```

O script carrega `vendas.csv` do diretório atual. Se o arquivo estiver ausente, ele executa o gerador da opção A e grava 200 registros sintéticos em UTF-8 com `seed=42`. A inspeção exibe as dimensões, os nomes das colunas, as ausências por coluna e as primeiras cinco linhas.

Para rodar os testes de RF01 e RF02:

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

## Versionamento planejado

- `main`: versão estável, com integração final.
- `develop`: integração e validação das funcionalidades.
- `feat/dados-inspecao`: RF01–RF02.
- `feat/limpeza-transformacao`: RF03–RF04.
- `feat/metricas-segmentacao`: RF05–RF06.
- `feat/exportacao-fluxo`: RF07–RF09, revisando a organização das funções ao longo do fluxo.
- `docs/readme`: documentação final, verificações e link do vídeo.

Cada feature será criada a partir de `develop` atualizada, integrada mediante revisão e registrada por commits pequenos com mensagens descritivas.

## Resultados e demonstração

A execução de referência com Python 3.12.10 e `seed=42` produziu **200 registros e 8 colunas**. A inspeção identificou **10 ausências em `quantidade`**, **4 em `preco_unitario`** e zero nas demais colunas. O CSV contém ainda 4 datas marcadas como `DATA INVALIDA`, 11 produtos com espaços extras e 19 nomes de cliente com ruído.

O registro 2 tem quantidade vazia, o registro 11 contém `DATA INVALIDA` e o registro 12 contém o produto `" Headset "`. O preço unitário está vazio no registro 18.

A geração com os mesmos parâmetros produz o mesmo arquivo. O SHA-256 do CSV gerado em Python 3.12.10 é `5d8b1e07856f3b1ad4c433840cb1845643de3175450908f919cf83f7c21f0859`.

A demonstração do fluxo completo e o link público do vídeo permanecem previstos para a entrega final. Ferramentas de IA foram utilizadas como apoio à implementação e à verificação técnica.

## Referência

Enunciado do AVA: *Desenvolvedor(a) em IA para Análise Preditiva [T4] — M1S08 — Mini-Projeto Avaliativo — SalesInsight PY*, versão reduzida datada de 10/09/2026. Prazo excepcional confirmado pela pedagogia no AVA: **30/11/2026, 23h59**. A versão consultada possui inconsistências de cabeçalho (T3) e de peso (30% em uma seção); o peso **25%** foi confirmado por Andrezza Finco para a T4.
