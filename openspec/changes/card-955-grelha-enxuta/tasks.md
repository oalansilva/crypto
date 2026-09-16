Skills canónicas (produto `oalansilva/covenant-flow`, depois pin no Cripto): `grill-card`, `covenant-flow`, `openspec-new-change`, `openspec-ff-change`, `kaizen`. Apply só com `Status=Pronto para Dev`. Não editar o vendor `.cursor/skills/grilling/SKILL.md`. MUST NOT dual-write lei em `.dsh/` / `.grok/` / `.opencode/`. MUST NOT `backend/**` nem `frontend/src/**`.

## 1. Adapter canónico `grill-card`

- [x] 1.1 Em `oalansilva/covenant-flow` `.cursor/skills/grill-card/SKILL.md`, DoD da grelha = 3 seções (`## Problema`, `## História`, `## Entra`; critérios dentro de Entra); MUST NOT exigir `## Vocabulário` / `## Riscos` em Em Refinamento
- [x] 1.2 Uma passagem, no máximo 5 perguntas de produto; sem segunda passagem; furos listados em Entra e/ou dump para o pai
- [x] 1.3 Delta do body: reconstruir REST PATCH com seções inalteradas byte-idênticas; needles `PATCH só das seções que mudaram` e `handoff lista o delta`
- [x] 1.4 Fronteira vazia = 3 seções **e** nenhuma decisão de operador em aberto; comentário T1 permanece `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` (idempotente); tecto #809: *como* de identificador git vai ao Design, nunca a `## Riscos` no issue; vendor `grilling` intocado; contrato N≥2 / D5 / ramos Cursor-Grok vs dsh intactos

## 2. Runbook `covenant-flow` e briefing OpenSpec

- [x] 2.1 Bloco `## Grill-card`: skip exacto `card nítido; sem grill`; disparo = body ainda não diz quem sofre e entra/não entra (ou pedido explícito); MUST NOT restar `6 seções do DoD`; tecto #809 e relay `todas as options` / `não colapsa` intactos
- [x] 2.2 «Card primeiro»: Gist = *superset* do issue (história copiada + *como*), não só o *como*; `G_design` continua a exigir pacote + comentário
- [x] 2.3 `.cursor/skills/openspec-new-change/SKILL.md` e `openspec-ff-change/SKILL.md`: briefing no *issue* = Problema, História, Entra/não entra; `proposal.md` MUST copiar essas seções do body (MUST NOT inventar); furo de seção no issue → comentar e permanecer em Design
- [x] 2.4 MUST NOT editar `process-fsm.yaml`, `AGENTS.md` always-on, `grok_stubs.py`, `dsh_stubs.py`

## 3. Kaizen release

- [x] 3.1 `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` reporta `sessões de grelha por card` e `Em Refinamento vs Design` (proxy transcript); skip `card nítido; sem grill` conta 0; MUST NOT parser de usage / dashboard

## 4. Peles thin

- [x] 4.1 `.grok` / `.dsh` / `.opencode` `grill-card` e `covenant-flow` continuam MUST Read do canónico; body ≤8 linhas não-vazias; MUST NOT copiar DoD 3 / skip / Gist *superset* para os stubs

## 5. Goldens pytest `scripts/process-fsm`

- [x] 5.1 `test_grill_card.py`: needles 3 seções, uma passagem teto 5, `card nítido; sem grill`, delta PATCH, Gist *superset* (fixture `proposal.md` **sem** `## Problema` / `## História` / `## Entra` falha; fixture que copia do issue passa); retunar assert `6 seções do DoD` na secção Grill-card
- [x] 5.2 Fixtures: body nítido (Problema+Entra) → skip; body oco → spawn; dump 6 Qs ou segunda passagem → fail; dump que reescreve seção inalterada → fail. MUST NOT `gh issue edit` de cards já grelhados
- [x] 5.3 Ceiling #809 e N1 (#755) verdes; pin-tests que cravam `v1.1.15` sobem para a tag deste card; `pytest scripts/process-fsm` sem GitHub verde

## 6. Tag produto

- [x] 6.1 Confirmar `gh api repos/oalansilva/covenant-flow/tags`; se `v1.1.16` livre, usá-la; senão o próximo patch livre (nunca major); `SCHEMA_MAJOR` permanece 1
- [x] 6.2 Commit no produto (adapter + runbook + openspec-new/ff + kaizen + goldens) e tag patch; `install.sh --pin` continua a copiar nucleus/adapters

## 7. Pin Cripto

- [x] 7.1 `implantar --pin` da tag deste card no worktree Cripto; overlay `pin:` = essa tag
- [x] 7.2 Não reabrir #667/#755/#809; não reescrever bodies já grelhados; zero diff `backend/` / `frontend/src/`; peles continuam thin

## 8. Verificação

- [x] 8.1 `openspec validate` da change verde; UI impact none; Prototype N/A
- [x] 8.2 Canónico tem DoD 3 + uma passagem + delta + skip; vendor `grilling` sem diff; runbook sem `6 seções do DoD` e com `card nítido; sem grill`; goldens verdes; stubs ≤8 + MUST Read
