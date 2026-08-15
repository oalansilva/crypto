## 1. Canonicalização da prova OOS

- [x] 1.1 Adicionar em `backend/app/services/oos_promotion_proof.py` uma normalização pura e recursiva dos valores do payload antes de `json.dumps`
- [x] 1.2 Converter somente floats finitos e integrais para `int`, preservando floats fracionários, `None`, strings, booleans, estrutura de dicts e ordem de listas
- [x] 1.3 Manter emissão e verificação usando a mesma `_canonical_digest`, sem alterar JWT HS256, propósito, TTL ou autorização do override

## 2. Testes unitários

- [x] 2.1 Cobrir igualdade do digest para `8953.0` na emissão e `8953` após round-trip, inclusive em dict/list aninhados
- [x] 2.2 Cobrir verificação end-to-end: prova emitida com float integral é aceita contra payload equivalente com inteiro
- [x] 2.3 Cobrir que float fracionário/conteúdo realmente diferente não é normalizado para o mesmo valor e invalida a prova
- [x] 2.4 Cobrir preservação de `None`, strings e booleans e comportamento fail-closed de prova expirada ou assinada com payload diferente

## 3. Regressão funcional do gate walk-forward

- [x] 3.1 Validar candidato NO-GO com prova válida: admin + `override_oos: true` salva favorito sem falso 422 de prova (coberto por teste unitário e2e do digest; fluxo de rota sem alteração)
- [x] 3.2 Validar candidato NO-GO sem override: permanece bloqueado com motivo explícito e não salva (regra existente em favorites.py inalterada, coberta por integração)
- [x] 3.3 Validar candidato GO com prova válida e sem override: permanece salvável
- [x] 3.4 Confirmar que usuário não-admin não ganha permissão de override e que prova ausente, inválida ou expirada continua rejeitada (testes e2e do digest: tampered/expired/ausente rejeitadas)

## 4. Validação e handoff

- [x] 4.1 Executar os testes unitários focados do serviço/gate e registrar resultado terminal (11/11 digest + 50/50 walk-forward/favoritos)
- [x] 4.2 Validar a change OpenSpec e reconciliar os critérios com a implementação
- [x] 4.3 Executar `qa-gate` e a cobertura visual padrão do projeto para card sem mudança visual, ou registrar dispensa válida de Alan conforme a política
- [x] 4.4 Registrar no handoff o risco transitório de provas pré-deploy (TTL de seis horas) e orientar nova otimização quando necessário

> As seções 1–4 registram a entrega original já executada. A regra concluída em 1.2 foi superada pela evidência pós-implementação para números acima de `Number.MAX_SAFE_INTEGER`; o rework pendente está definido abaixo sem apagar o histórico.

## 5. Rework pós-implementação — precisão transportável

- [x] 5.1 Restringir a conversão de floats finitos e integrais para `int` ao intervalo inclusivo `±(2^53-1)`, mantendo floats integrais fora desse intervalo como `float`
- [x] 5.2 Preservar booleans antes da regra de inteiros e converter inteiros fora do intervalo seguro para o `float` IEEE-754 mais próximo
- [x] 5.3 Implementar falha fechada para NaN/Infinity, `OverflowError` e qualquer conversão de inteiro que não resulte em double finito
- [x] 5.4 Manter a normalização recursiva e a mesma `_canonical_digest` na emissão e verificação, sem alterar assinatura, propósito, TTL, autorização ou gate GO/NO-GO

## 6. Testes do rework

- [x] 6.1 Reproduzir o caso homologado: emissão com `calmar_ratio=3.290195462758171e16` e save com `32901954627581710` devem produzir o mesmo digest e validar a prova
- [x] 6.2 Manter a regressão do caso seguro `8953.0` → `8953`, inclusive em dicionários e listas aninhados
- [x] 6.3 Cobrir `±(2^53-1)`, valores imediatamente fora dos limites, inteiros inseguros que convergem ao mesmo double e um valor inseguro ainda distinguível
- [x] 6.4 Cobrir preservação de booleans e floats fracionários, além de falha fechada para NaN, Infinity e inteiro com overflow na conversão para float
- [x] 6.5 Confirmar que payload distinguível alterado, prova expirada, assinatura inválida e propósito incorreto continuam rejeitados

## 7. Validação e QA do rework

- [x] 7.1 Executar os testes focados do serviço de prova e do gate/favoritos após a implementação e registrar resultado terminal
- [x] 7.2 Validar a change OpenSpec e reconciliar proposal, design, spec e tasks com a implementação final
- [x] 7.3 Executar novamente o `qa-gate` e a cobertura visual padrão para card sem mudança visual, ou registrar dispensa válida de Alan conforme a política
- [x] 7.4 Registrar no handoff a limitação inevitável de que inteiros distintos acima de `2^53` que colapsam no mesmo `Number` não são distinguíveis pelo fluxo browser
