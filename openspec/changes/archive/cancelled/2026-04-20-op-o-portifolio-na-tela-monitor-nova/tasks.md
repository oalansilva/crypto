# Tasks

## PO Tasks
- [x] Enquadrar a mudança como regra de produto do Monitor ligada à carteira Binance.
- [x] Definir escopo, dependências, riscos e critérios de aceite testáveis.
- [x] Publicar pacote de review com os paths diretos de OpenSpec.

## DESIGN Tasks
- [x] Criar protótipo obrigatório do estado de `Portfolio` bloqueado para ativo criptomoeda com Binance válida.
  - Critério de aceite: `prototype/prototype.html` ou `prototype.html` mostra o estado bloqueado, a origem automática pela carteira e o fallback visual para sync indisponível/desatualizado.
- [x] Definir copy e diferenciação visual entre controle editável e controle derivado da carteira.
  - Critério de aceite: o usuário entende que o valor é automático e por que não pode alterá-lo manualmente.

## DEV Tasks
- [ ] Detectar de forma canônica quando o ativo do Monitor é do tipo criptomoeda.
  - Critério de aceite: a regra ativa apenas para ativos elegíveis.
- [ ] Detectar quando a conexão Binance do usuário está válida para leitura da carteira.
  - Critério de aceite: a regra não bloqueia contas sem conexão válida.
- [ ] Derivar o valor exibido de `Portfolio` a partir dos holdings atuais da carteira integrada.
  - Critério de aceite: o estado exibido reflete presença ou ausência do ativo na carteira.
- [ ] Bloquear interação manual do controle `Portfolio` enquanto a regra derivada estiver ativa.
  - Critério de aceite: nenhuma ação manual altera o valor nesse cenário.
- [ ] Exibir fallback de indisponibilidade/desatualização sem reabrir edição manual.
  - Critério de aceite: em falha de sync, o controle continua bloqueado e a UI informa o problema.
- [ ] Preservar o comportamento atual para ativos não cripto ou sem Binance válida.
  - Critério de aceite: a regra nova não causa regressão fora do escopo.

## QA Tasks
- [ ] Validar ativo cripto com Binance válida e holdings positivos.
  - Critério de aceite: `Portfolio` aparece ativo e bloqueado.
- [ ] Validar ativo cripto com Binance válida e sem holdings.
  - Critério de aceite: `Portfolio` aparece inativo e bloqueado.
- [ ] Validar tentativa de edição manual com Binance válida.
  - Critério de aceite: o valor não muda manualmente.
- [ ] Validar fallback de sync indisponível ou desatualizado.
  - Critério de aceite: o controle segue bloqueado e a indicação visual aparece.
- [ ] Validar ativo não cripto e cripto sem Binance válida.
  - Critério de aceite: o comportamento atual é preservado.
- [ ] Anexar evidência reproduzível, preferencialmente Playwright.
  - Critério de aceite: QA entrega prova do estado bloqueado e da preservação dos cenários fora da regra.

## Notes
- Próximo owner esperado: DESIGN.
- Protótipo é obrigatório antes de qualquer avanço para approval, por envolver mudança de UI no Monitor.
- Regra principal: para cripto com Binance válida, `Portfolio` deixa de ser decisão manual e passa a refletir a carteira.
