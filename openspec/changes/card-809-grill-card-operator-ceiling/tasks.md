Skills canónicas deste repo (`.cursor/skills/`, `.agents/skills/`): `grill-card`, `covenant-flow`, `implantar`, `openspec-apply-change`. Apply só com `Status=Pronto para Dev` (gate Design → Aprovação de Design → Pronto para Dev; `UI impact: none` não pula colunas). Não editar o vendor `.cursor/skills/grilling/SKILL.md`.

## 1. Adapter canónico `grill-card`

- [x] 1.1 Em `oalansilva/covenant-flow` `.cursor/skills/grill-card/SKILL.md`, acrescentar o tecto de linguagem (Q1=A): Qs e options em português de operador em **todo** card em Em Refinamento; identificador do git → facto no body ou *como* em Riscos para Design, nunca option no host
- [x] 1.2 Alinhar o *quando* da fronteira vazia: 6 seções DoD **e** nenhuma decisão de operador em aberto; o texto do comentário permanece `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` (Q3=A; idempotente)
- [x] 1.3 Other vazio, silêncio e «não percebi» / «isto é técnico» (via Other ou texto livre) reclassificam; MUST NOT ficar como aceite da recomendada (Q2=A); Other do host #755 é automático e não é option listada; outras Qs da rodada continuam à espera
- [x] 1.4 Disparo «oferecer grill» permanece body sem as 6 seções; o tecto MUST NOT obrigar a re-grelhar um DoD já escrito; contrato N≥2 / D5 / ramos Cursor-Grok vs dsh intactos; vendor `grilling` intocado

## 2. Frase no bloco Grill-card de `covenant-flow`

- [x] 2.1 Inserir a frase exacta D5 do `design.md` no `## Grill-card` de `.cursor/skills/covenant-flow/SKILL.md`, depois do relay de options e antes de `Cliente dsh:`
- [x] 2.2 Manter a linha de disparo (body sem as 6 seções) e a de relay (`todas as options` / `não colapsa`); MUST NOT editar `process-fsm.yaml`, `AGENTS.md`, `grok_stubs.py`, `dsh_stubs.py`

## 3. Peles thin

- [x] 3.1 `.grok` / `.dsh` / `.opencode` `grill-card/SKILL.md` continuam MUST Read do canónico; body ≤8 linhas não-vazias; MUST NOT copiar o tecto para os stubs; Grok stub MUST NOT nomear host tools

## 4. Goldens pytest `scripts/process-fsm`

- [x] 4.1 Criar `fixtures/grill_ceiling/` com D4: quatro fail de identificador (`fail_795_q2`, `fail_799_q3`, `fail_801_q3`, `fail_monitor_path`); `pass_operator` MUST conter `Não priorizar ainda`, `acabada` e `20260830`; três fail de stamp (`fail_stamp_other_empty`, `fail_stamp_silence`, `fail_stamp_nao_percebi`) — MUST NOT pôr «não percebi» como label da option recomendada; MUST NOT `gh issue edit` #795/#799/#801
- [x] 4.2 Em `test_grill_card.py`: scanner `ceiling_violation` estreito (D4: SHA misto; eventos só `process_event`/`iniciar_design`; asserts unidade `Não priorizar ainda`/`acabada`/`20260830` passam e `process_event priorizar`/`94f8ed41` falham); fail dumps de identificador reprovam; `pass_operator` aprova; os três stamp dumps reprovam; needles da frase D5 (inclui Other/silêncio) na secção Grill-card; needles Q2/Q3 no canónico
- [x] 4.3 Pin-tests (`test_dsh_adapter.py` e needle em `test_grill_card.py`) sobem `v1.1.5` para a tag deste card; N1 (#755 host options / vendor Matt / stubs Grok) verdes; `pytest scripts/process-fsm` sem GitHub verde

## 5. Tag produto

- [x] 5.1 Confirmar `gh api repos/oalansilva/covenant-flow/tags`; se `v1.1.6` livre, usá-la; senão o próximo patch livre (nunca major); `SCHEMA_MAJOR` permanece 1
- [ ] 5.2 Commit no produto (adapter + frase covenant-flow + goldens) e tag patch; `install.sh --pin` continua a copiar nucleus/adapters

## 6. Pin Cripto

- [x] 6.1 `implantar --pin` da tag deste card no worktree Cripto; overlay `pin:` = essa tag
- [x] 6.2 Não reabrir #667/#755/#786; não reescrever #795/#799/#801; não promover `/opsx:explore`; zero diff `backend/` / `frontend/src/` de produto; peles grill-card continuam thin

## 7. Verificação

- [x] 7.1 `openspec validate` da change verde; UI impact none
- [x] 7.2 Canónico tem tecto; vendor `grilling` sem diff de tecto; frase D5 (Other/silêncio/«não percebi») no bloco Grill-card; goldens fail/pass + asserts de scanner estreito; stubs ≤8 + MUST Read
