# SalesInsight PY — Análise de Dados de Vendas

**Projeto acadêmico:** SCTEC/SENAI — Desenvolvimento de IA para Análise Preditiva — Turma T4, Módulo 1 (Mini-Projeto da Semana 08).  
**Responsável acadêmico:** Fabiano Rodrigo Costa.

> **Status: estrutura inicial / planejamento.** A implementação, o dataset, as saídas e a gravação serão produzidos e validados nas próximas etapas. Este repositório não deve ser apresentado como projeto funcional até a conclusão de RF01–RF09.

## Objetivo

Construir, em Python, um fluxo reprodutível de análise de vendas para uma empresa de varejo: carregar um CSV, inspecionar e limpar registros, criar colunas derivadas, agregar métricas, segmentar clientes e exportar resultados para CSV e JSON.

O escopo obrigatório segue a **versão reduzida do enunciado de 10/09/2026**, correspondente aos conteúdos do Módulo 1 até a Semana 05. Não exige Pandas, NumPy, Matplotlib, Seaborn, classes ou modelos preditivos.

## Escopo e rastreabilidade

- [Matriz RF01–RF09 e critérios de aceitação](planejamento/matriz-requisitos.md)
- [Kanban operacional](planejamento/tarefas-kanban.md)
- [Arquitetura e decisões técnicas](planejamento/arquitetura-tecnica.md)
- [Checklist de avaliação e entrega](planejamento/checklist-rubrica.md)

## Estrutura

```text
salesinsight-py/
├── README.md
├── salesinsight.py           # implementação a desenvolver
├── vendas.csv               # será produzido em RF01
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

Quando RF01–RF09 estiverem implementados, a execução deverá funcionar com:

```powershell
.\.venv\Scripts\python.exe salesinsight.py
```

Esse comando está documentado como **instrução futura**; o arquivo inicial é somente uma estrutura de planejamento e ainda não executa o projeto.

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

**Ainda pendentes.** Após a implementação, esta seção incluirá exemplos de saída, decisões técnicas verificadas, limitações, resultados e o link público do vídeo (máximo de cinco minutos), conforme a rubrica oficial.

## Referência

Enunciado do AVA: *Desenvolvedor(a) em IA para Análise Preditiva [T4] — M1S08 — Mini-Projeto Avaliativo — SalesInsight PY*, versão reduzida datada de 10/09/2026. Prazo excepcional confirmado pela pedagogia no AVA: **30/11/2026, 23h59**. A versão consultada possui inconsistências de cabeçalho (T3) e de peso (30% em uma seção); o peso **25%** foi confirmado por Andrezza Finco para a T4.
