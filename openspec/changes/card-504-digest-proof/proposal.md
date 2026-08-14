## Why

O fluxo de otimização com split emite uma prova assinada para vincular o resultado walk-forward ao payload que pode ser promovido a favorito. Ao salvar pelo navegador, números JSON sem parte fracionária podem voltar como `int` embora tenham sido emitidos pelo backend como `float` (por exemplo, `8953.0` volta como `8953`). O conteúdo é numericamente equivalente, mas a serialização usada pelo digest é diferente; a verificação rejeita a prova e o admin recebe 422 ao tentar salvar um candidato NO-GO com override válido.

## Root Cause

`_canonical_digest` calcula SHA-256 diretamente sobre `json.dumps` dos objetos Python. A emissão em `POST /api/combos/optimize` inclui objetos como `metrics.trades` com floats integrais, enquanto `POST /api/favorites/` reconstrói o payload depois do round-trip JSON do browser. Como `8953.0` e `8953` têm representações textuais distintas, o digest emitido diverge do digest verificado, apesar de não haver alteração semântica do valor.

## What Changes

- Normalizar recursivamente os valores do payload antes da serialização canônica: todo `float` finito e integral passa a `int`.
- Aplicar a mesma função canônica à emissão e à verificação da prova, preservando ordenação de chaves, codificação compacta e SHA-256 existentes.
- Cobrir por teste unitário o round-trip `8953.0` → `8953`, inclusive dentro de dicionários e listas aninhados.
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

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `walk-forward-validation`: a prova de promoção deve permanecer verificável quando o único delta do round-trip JSON for a representação de floats integrais como inteiros.

## Acceptance Criteria

1. Após otimização com split e veredito NO-GO, um admin com `override_oos: true` e prova válida salva o favorito sem o falso 422 de prova inválida.
2. Um candidato NO-GO sem override continua bloqueado, com motivo explícito do gate, e não é salvo.
3. Um candidato GO com prova válida continua salvável sem override.
4. Teste unitário demonstra que payloads equivalentes antes/depois do round-trip JSON (`8953.0` ↔ `8953`), inclusive em estruturas aninhadas, produzem o mesmo digest e preservam a verificação da prova.
5. Valores realmente diferentes continuam produzindo digests diferentes e provas expiradas ou inválidas continuam rejeitadas.
6. Validações proporcionais da change e `qa-gate` terminam verdes.

## Impact

- **Backend:** correção localizada na canonicalização da prova OOS.
- **Segurança:** não amplia autorização nem reduz validação de assinatura/expiração; apenas define equivalência canônica para duas representações JSON do mesmo número integral.
- **Compatibilidade:** novas provas serão estáveis no round-trip descrito. Provas ainda válidas emitidas antes do deploy podem exigir nova otimização; provas expiradas permanecem inválidas.
- **UI impact: none:** não há superfície visual nova ou alterada; o comportamento corrigido pertence ao digest e à validação backend.
