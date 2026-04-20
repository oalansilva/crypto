# Tasks

## PO
- [x] Enquadrar a mudança como regra de produto do Monitor ligada à integração Binance.
- [x] Definir escopo, dependências, riscos e critérios de aceite testáveis.
- [x] Publicar pacote de review com paths diretos de OpenSpec.

## DESIGN
- [ ] Criar protótipo obrigatório do estado de `Portfolio` bloqueado para ativo cripto com Binance conectada.
  - Critério de aceite: `prototype/prototype.html` ou `prototype.html` mostra claramente estado bloqueado, estado derivado da carteira e mensagem/indicação de origem.
- [ ] Definir linguagem visual para diferenciar controle editável vs controle bloqueado por integração.
  - Critério de aceite: usuário entende que o estado vem da carteira e não pode ser alterado manualmente.

## DEV
- [ ] Detectar no Monitor quando o ativo é do tipo criptomoeda e existe conexão Binance configurada.
  - Critério de aceite: a regra só ativa para ativos elegíveis.
- [ ] Integrar o estado de `Portfolio` com holdings/carteira do usuário.
  - Critério de aceite: o estado exibido reflete se o ativo está ou não na carteira.
- [ ] Bloquear interação manual do controle `Portfolio` enquanto Binance estiver conectada.
  - Critério de aceite: nenhuma ação do usuário altera manualmente o estado nesse cenário.
- [ ] Preservar o comportamento atual para ativos não cripto ou sem Binance conectada.
  - Critério de aceite: a regra nova não causa regressão fora do cenário definido.
- [ ] Garantir refresh consistente quando holdings mudarem.
  - Critério de aceite: após atualizar dados, o Monitor reflete o estado correto da carteira.

## QA
- [ ] Validar ativo cripto com Binance conectada e holdings positivos.
  - Critério de aceite: `Portfolio` aparece ativo e bloqueado.
- [ ] Validar ativo cripto com Binance conectada e sem holdings.
  - Critério de aceite: `Portfolio` aparece inativo e bloqueado.
- [ ] Validar tentativa de edição manual com Binance conectada.
  - Critério de aceite: o estado não muda manualmente.
- [ ] Validar ativo não cripto.
  - Critério de aceite: regra nova não interfere no comportamento esperado.
- [ ] Validar cenário sem Binance conectada.
  - Critério de aceite: o comportamento segue a lógica atual não bloqueada.
- [ ] Anexar evidência reproduzível, preferencialmente Playwright.
  - Critério de aceite: QA entrega prova do estado bloqueado e da preservação dos cenários fora da regra.

## Notes
- Próximo owner esperado: DESIGN.
- Protótipo é obrigatório antes de qualquer avanço para approval, por envolver comportamento de UI no Monitor.
- Regra principal: para cripto com Binance conectada, `Portfolio` deixa de ser decisão manual e passa a refletir a carteira.
- Insumo obrigatório absorvido do Party Mode: a regra vale apenas para ativos do tipo criptomoeda e deve vir dos ativos comprados do usuário.
