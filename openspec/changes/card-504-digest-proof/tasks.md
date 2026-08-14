## 1. Canonicalização da prova OOS

- [ ] 1.1 Adicionar em `backend/app/services/oos_promotion_proof.py` uma normalização pura e recursiva dos valores do payload antes de `json.dumps`
- [ ] 1.2 Converter somente floats finitos e integrais para `int`, preservando floats fracionários, `None`, strings, booleans, estrutura de dicts e ordem de listas
- [ ] 1.3 Manter emissão e verificação usando a mesma `_canonical_digest`, sem alterar JWT HS256, propósito, TTL ou autorização do override

## 2. Testes unitários

- [ ] 2.1 Cobrir igualdade do digest para `8953.0` na emissão e `8953` após round-trip, inclusive em dict/list aninhados
- [ ] 2.2 Cobrir verificação end-to-end: prova emitida com float integral é aceita contra payload equivalente com inteiro
- [ ] 2.3 Cobrir que float fracionário/conteúdo realmente diferente não é normalizado para o mesmo valor e invalida a prova
- [ ] 2.4 Cobrir preservação de `None`, strings e booleans e comportamento fail-closed de prova expirada ou assinada com payload diferente

## 3. Regressão funcional do gate walk-forward

- [ ] 3.1 Validar candidato NO-GO com prova válida: admin + `override_oos: true` salva favorito sem falso 422 de prova
- [ ] 3.2 Validar candidato NO-GO sem override: permanece bloqueado com motivo explícito e não salva
- [ ] 3.3 Validar candidato GO com prova válida e sem override: permanece salvável
- [ ] 3.4 Confirmar que usuário não-admin não ganha permissão de override e que prova ausente, inválida ou expirada continua rejeitada

## 4. Validação e handoff

- [ ] 4.1 Executar os testes unitários focados do serviço/gate e registrar resultado terminal
- [ ] 4.2 Validar a change OpenSpec e reconciliar os critérios com a implementação
- [ ] 4.3 Executar `qa-gate` e a cobertura visual padrão do projeto para card sem mudança visual, ou registrar dispensa válida de Alan conforme a política
- [ ] 4.4 Registrar no handoff o risco transitório de provas pré-deploy (TTL de seis horas) e orientar nova otimização quando necessário
