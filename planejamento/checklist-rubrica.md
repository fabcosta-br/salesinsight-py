# Checklist de aprovação e entrega — SalesInsight PY

**Rubrica oficial da versão reduzida: total de 10 pontos.** O Gate 04 foi publicado em `6f4ac6c` e integrado em `develop` em `adf9233`. [PR nº 4](https://github.com/fabcosta-br/salesinsight-py/pull/4)

## Avaliação (10/10)

- [ ] README com objetivo, instalação, execução e conceitos revisados no Gate 05. Link público do vídeo pendente — **1,00**.
- [x] Branches por funcionalidade, commits descritivos e evolução registrada nos PRs nº 1 a 4 — **1,00**.
- [ ] Vídeo até 5 min: execução do início ao fim, decisão técnica e melhorias; também Kanban, ambiente e branches — **2,00**.
- [x] RF01–RF03: carregar, inspecionar, limpar datas e nulos, normalizar texto com regex e apresentar relatório. Evidência validada localmente — **2,00**.
- [x] RF04–RF06: derivar colunas, calcular as quatro agregações e segmentar clientes com lambda. Evidência validada localmente — **2,50**.
- [x] RF07 — Funções com parâmetros, retornos e docstrings, dois usos de `lambda` e função de ordem superior verificados em testes — **1,00**.
- [x] RF08–RF09 — CSVs, JSON relido e conferido e execução de `main()` em pasta temporária — **0,50**.

## Evidências adicionais de robustez

- [x] Geração automática de `vendas.csv` com seed fixa e instruções no README. A execução em pasta temporária reproduziu os 200 registros.
- [x] RF03: relatório validado com 200 entradas, 17 exclusões e 183 registros válidos.
- [x] RF04: receita por linha, calendário e limites das faixas validados com Python 3.12.10.
- [x] RF05: contagem de 183 vendas e receita de R$ 1.290.346,30 reconciliadas com os registros válidos.
- [x] RF06: limites Bronze/Prata/Ouro, Top 10 e distribuição dos 50 clientes conferidos.
- [x] Três saídas em `outputs/` conferidas. CSVs com 12 linhas mensais e 50 clientes, e JSON reconciliado com os totais.
- [x] Pelo menos cinco commits de trabalho individual, com mensagens descritivas e integração por PR.
- [x] Execução limpa e saídas idênticas em duas rodadas com Python 3.12.10. Suíte de 29 testes aprovada.
- [ ] Auditoria do Gate 05 e integração final em `main`.
- [ ] Vídeo abre em janela privada sem senha, áudio/sincronismo legíveis.
- [ ] GitHub público e vídeo acessível; links submetidos no AVA antes de 30/11 23h59.
- [ ] Status **Enviado para avaliação** ou equivalente e comprovante salvos.

## Política de integridade

- Não marcar etapas ainda não executadas.
- Não publicar credenciais, paths locais privados, nomes de terceiros ou dados pessoais reais.
- Utilizar dados sintéticos de vendas; compreender e explicar integralmente as escolhas e a implementação.
