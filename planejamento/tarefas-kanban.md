# Kanban — SalesInsight PY

**Responsável acadêmico** — Fabiano Rodrigo Costa

**Prazo oficial no AVA** — 30/11/2026 às 23h59.

## A fazer

- [ ] **D1 — README:** inserir o link público do vídeo.
- [ ] **D2 — Integração final:** comparar `develop` e `main` e solicitar aprovação para a versão de entrega.
- [ ] **D3 — Auditoria:** execução independente do zero e revisão da rubrica linha a linha.
- [ ] **V1 — Roteiro:** máximo de 5 minutos e cobertura integral dos tópicos.
- [ ] **V2 — Gravação:** demonstração real, câmera, voz, explicação do Kanban/branches.
- [ ] **S1 — Submissão:** links públicos testados em janela privada e comprovante do AVA.

## Em andamento

- [ ] **Gate 05 — Qualidade e documentação.** Revisão executiva do README, atualização da rastreabilidade e correção preventiva da exportação em `docs/readme`. Auditoria e autorização para versionamento pendentes.

## Concluído

- [x] **P0.0 — Escopo:** matriz RF01–RF09, cronograma e estratégia Git documentados.
- [x] **P0.1 — Repositório:** criar `fabcosta-br/salesinsight-py` público com `main`.
- [x] **P0.2 — Git:** criar `develop` a partir de `main`; registrar snapshot inicial; confirmar autores, acesso público e branch padrão.
- [x] **P0.3 — Ambiente:** verificar Python 3.12, VS Code, GitHub Desktop e execução local básica.
- [x] **RF01–02 — Dados/inspeção:** gerador e inspeção validados. Integração em `origin/develop` pelo PR nº 1 (`e8f331d`).
- [x] **RF03–04 — Limpeza/derivação:** implementação validada com 12 testes aprovados. Publicação confirmada no commit `be2b37c`.
- [x] **RF05–RF06 — Métricas e segmentação.** Os 20 testes de referência passaram. Integração em `origin/develop` pelo PR nº 3 (`1f53ee1`).
- [x] **RF07–RF09 — Gate 04.** Fluxo integrado, CSVs e JSON relido validados com 29 testes. Publicação em `feat/exportacao-fluxo` (`6f4ac6c`) e integração em `origin/develop` (`adf9233`). [PR nº 4](https://github.com/fabcosta-br/salesinsight-py/pull/4)
- [x] Enunciado oficial consultado e divergências da versão reduzida registradas.

## Política de movimentação

1. Mover a tarefa para **Em andamento** somente quando iniciar a implementação.
2. Só marcar **Concluído** com teste verificável e commit correspondente.
3. Um commit por incremento lógico; evitar agrupar funcionalidades independentes.
4. Cada feature nasce de `develop` atualizado; revisar diff antes de PR/merge.
5. `main` só recebe versão validada; não excluir branches durante a avaliação.
6. Código executado e vídeo gravado pelo autor, com compreensão das decisões implementadas.
