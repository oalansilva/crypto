## Why

O fluxo de otimização com split emite uma prova assinada para vincular o resultado walk-forward ao payload que pode ser promovido a favorito. Ao salvar pelo navegador, números passam pelo tipo `Number` IEEE-754 do JavaScript antes de voltarem à API. Isso tanto remove a parte decimal de floats integrais seguros (`8953.0` volta como `8953`) quanto limita inteiros à precisão observável pelo transporte. A correção original cobriu o caso pequeno convertendo todo float integral para `int`, mas falha no payload homologado real: `calmar_ratio=3.290195462758171e16`, acima de `Number.MAX_SAFE_INTEGER`, é convertido por Python para `32901954627581712`, enquanto `JSON.stringify` envia `32901954627581710`. A prova legítima continua sendo rejeitada com 422.

## Root Cause

`_canonical_digest` calcula SHA-256 sobre `json.dumps` dos objetos Python. Emissão e verificação recebem tipos e representações diferentes depois do round-trip pelo browser. Canonicalizar todo float integral com `int(value)` pressupõe precisão inteira arbitrária que o transporte JavaScript não possui: para o `calmar_ratio` real, o digest da issue foi `2301a454...`, o digest no save foi `703a6548...` e `match=False`. A canonicalização precisa vincular a prova à precisão numérica efetivamente transportável, e não a uma expansão inteira que só existe em uma das pontas.

## What Changes

- Normalizar recursivamente os valores do payload segundo a precisão observável no transporte JSON/JavaScript.
- Converter floats finitos e integrais para `int` somente dentro de `±(2^53-1)`; floats integrais fora desse intervalo permanecem `float`.
- Converter inteiros fora do intervalo seguro para o `float` IEEE-754 mais próximo, falhando de forma fechada se a conversão exceder o domínio finito; preservar booleans antes da regra de inteiros.
- Aplicar a mesma função canônica à emissão e à verificação da prova, preservando ordenação de chaves, codificação compacta e SHA-256 existentes.
- Cobrir por teste unitário tanto o round-trip seguro `8953.0` → `8953` quanto o caso real `3.290195462758171e16` → `32901954627581710`, inclusive em estruturas aninhadas.
- Manter intactos o JWT, sua assinatura, propósito, expiração, autorização de admin e decisão GO/NO-GO.

## Scope

- `backend/app/services/oos_promotion_proof.py`: normalização recursiva usada por `_canonical_digest`.
- Testes unitários de canonicalização e verificação da prova, seguindo o padrão de `backend/tests/unit/test_walk_forward_gate.py`.
- Delta spec de estabilidade da prova walk-forward no round-trip JSON.

## Out of Scope

- Alterar telas, mensagens, payloads do frontend ou qualquer interação visual.
- Alterar os critérios walk-forward, a classificação GO/NO-GO ou conceder override a usuários sem permissão de admin.
- Alterar algoritmo/segredo do JWT, finalidade da prova ou duração atual de seis horas.
- Aceitar payload modificado, prova expirada, prova com assinatura inválida ou valores não equivalentes.
- Criar migração ou persistir uma nova versão de digest.
- Distinguir inteiros diferentes acima de `2^53` quando eles colapsam no mesmo `Number` JavaScript; essa informação já não existe no fluxo do browser.
- Dar suporte a NaN ou Infinity; valores não finitos permanecem inválidos/fail-closed.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `walk-forward-validation`: a prova de promoção deve permanecer verificável quando o único delta for a representação numérica produzida pelo round-trip JSON/JavaScript, respeitando o limite de inteiros seguros.

## Acceptance Criteria

1. Após otimização com split e veredito NO-GO, um admin com `override_oos: true` e prova válida salva o favorito sem o falso 422 de prova inválida.
2. Um candidato NO-GO sem override continua bloqueado, com motivo explícito do gate, e não é salvo.
3. Um candidato GO com prova válida continua salvável sem override.
4. Teste unitário demonstra que payloads equivalentes antes/depois do round-trip JSON seguro (`8953.0` ↔ `8953`), inclusive em estruturas aninhadas, produzem o mesmo digest e preservam a verificação da prova.
5. Teste unitário reproduz o payload homologado com `calmar_ratio=3.290195462758171e16` na emissão e `32901954627581710` no save, obtendo o mesmo digest e prova válida.
6. Floats fracionários não são arredondados; booleans são preservados; NaN, Infinity e conversão de inteiro fora do domínio finito falham de forma fechada.
7. Valores diferentes que continuam distinguíveis após o transporte produzem digests diferentes, e provas expiradas ou inválidas continuam rejeitadas.
8. Validações proporcionais da change e `qa-gate` terminam verdes.

## Impact

- **Backend:** correção localizada na canonicalização da prova OOS.
- **Segurança:** não amplia autorização nem reduz validação de assinatura/expiração; define equivalência canônica na precisão que o browser consegue transportar. Inteiros distintos que colapsam no mesmo `Number` JavaScript são inevitavelmente indistinguíveis nesse fluxo.
- **Compatibilidade:** novas provas serão estáveis no round-trip descrito. Provas ainda válidas emitidas antes do deploy podem exigir nova otimização; provas expiradas permanecem inválidas.
- **UI impact: none:** não há superfície visual nova ou alterada; o comportamento corrigido pertence ao digest e à validação backend.
