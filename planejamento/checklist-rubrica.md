# Checklist de aprovação e entrega — SalesInsight PY

**Rubrica oficial da versão reduzida: total 10 pontos.** Marcar apenas quando a evidência existir no repositório.

## Avaliação (10/10)

- [ ] README completo: objetivo, instalação/execução, conceitos e link do vídeo — **1,00**.
- [ ] Branches por funcionalidade, commits claros e evolução lógica demonstrada — **1,00**.
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
- [ ] Pelo menos 5 commits, convenção de mensagens clara, PRs revisados.
- [x] Execução limpa e saídas idênticas em duas rodadas com Python 3.12.10. Suíte de 29 testes aprovada.
- [ ] Vídeo abre em janela privada sem senha, áudio/sincronismo legíveis.
- [ ] GitHub público e vídeo acessível; links submetidos no AVA antes de 30/11 23h59.
- [ ] Status **Enviado para avaliação** ou equivalente e comprovante salvos.

## Política de integridade

- Não marcar etapas ainda não executadas.
- Não publicar credenciais, paths locais privados, nomes de terceiros ou dados pessoais reais.
- Utilizar dados sintéticos de vendas; compreender e explicar integralmente as escolhas e a implementação.
