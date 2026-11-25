# Checklist de aprovação e entrega — SalesInsight PY

**Rubrica oficial da versão reduzida: total 10 pontos.** Marcar apenas quando a evidência existir no repositório.

## Avaliação (10/10)

- [ ] README completo: objetivo, instalação/execução, conceitos e link do vídeo — **1,00**.
- [ ] Branches por funcionalidade, commits claros e evolução lógica demonstrada — **1,00**.
- [ ] Vídeo até 5 min: execução do início ao fim, decisão técnica e melhorias; também Kanban, ambiente e branches — **2,00**.
- [x] RF01–RF03: carregar, inspecionar, limpar datas e nulos, normalizar texto com regex e apresentar relatório. Evidência validada localmente — **2,00**.
- [ ] RF04–RF06: derivar colunas, 4 agregações e segmentação com lambda — **2,50**.
- [ ] RF07: funções com parâmetros, retorno e docstrings; função de ordem superior — **1,00**.
- [ ] RF08–RF09: CSV e JSON, releitura JSON, `main()` executando do zero — **0,50**.

## Evidências adicionais de robustez

- [ ] `vendas.csv` gerado com seed fixa e preservado em `main` (ou gerado automaticamente com instruções explícitas).
- [x] RF03: relatório validado com 200 entradas, 17 exclusões e 183 registros válidos.
- [x] RF04: receita por linha, calendário e limites das faixas validados com Python 3.12.10.
- [ ] Testes dos limiares Bronze/Prata/Ouro.
- [ ] Saídas finais em `outputs/` conferidas, CSV legível e JSON válido.
- [ ] Pelo menos 5 commits, convenção de mensagens clara, PRs revisados.
- [ ] Execução limpa reproduzida com Python local.
- [ ] Vídeo abre em janela privada sem senha, áudio/sincronismo legíveis.
- [ ] GitHub público e vídeo acessível; links submetidos no AVA antes de 30/11 23h59.
- [ ] Status **Enviado para avaliação** ou equivalente e comprovante salvos.

## Política de integridade

- Não marcar etapas ainda não executadas.
- Não publicar credenciais, paths locais privados, nomes de terceiros ou dados pessoais reais.
- Utilizar dados sintéticos de vendas; compreender e explicar integralmente as escolhas e a implementação.
