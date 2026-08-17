# Tasks: card-580-release-doc-same-day

## Design (este turno)

- [x] 0. OpenSpec superset do issue #580 (crítica + Gist antes de Aprovação de Design)

## Apply (após Pronto para Dev)

- [x] 1. `pre` Release docs: classificar pelo diff (release-* usa HEAD; senão origin/develop); allowlist closeout; fail-closed; não usar develop==main
- [x] 2. `post`: evidência ancestral de `origin/main`; `evidence..origin/main` ⊆ allowlist; abreviação ≥7 pelo menos uma vez na doc
- [x] 3. `AGENTS.md`: uma doc por data; segundo pacote atualiza o mesmo arquivo após o deploy; PR documental continua gated
- [x] 4. Evidência: PASS código+doc existente sem evidência; FAIL documental develop≠main sem evidência; FAIL post evidência de lote anterior mesmo SHA na doc; PASS post evidência=ponta de código com main à frente só de closeout
