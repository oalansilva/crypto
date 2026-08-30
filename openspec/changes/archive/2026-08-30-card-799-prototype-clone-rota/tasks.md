## 1. Catálogo e helper

- [x] 1.1 Criar `scripts/process-fsm/route-landmarks.yaml` (`version: 1`) com chaves `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` e os selectors/texts de D6 do `design.md`
- [x] 1.2 Criar `scripts/process-fsm/design_clone_gate.py`: parse `UI impact` / `live_route` / `surface` (regex D5); soma UTF-8 `COPIED:start`/`COPIED:end`; match estático concatenando `frontend/public/prototypes/<q_git>/*.html`; lookup do catálogo em HEAD (D4)
- [x] 1.3 Materializar `scripts/process-fsm/fixtures/792-r1-gallery.html` com sha256 exacto `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` (histórico git se preciso). MUST NOT escrever em `frontend/public/prototypes/card-792-monitor-risco-explicito/`

## 2. G_design / process_event

- [x] 2.1 Em `scripts/process-fsm/process_event.py`, compor `files_g_design` = ficheiros OpenSpec **e** clone gate (D7). Resolver proto em `frontend/public/prototypes/<q_git>/`. Sem Playwright autenticado. Sem evento/Σ novo no yaml
- [x] 2.2 Manter override injectado `g_design=True` nos testes legais T5 existentes; o default (`g_design is None`) MUST medir o predicado composto

## 3. Testes

- [x] 3.1 `scripts/process-fsm/test_design_clone_gate.py`: existing + landmarks; `copied` ausente/0 recusa; chave ausente em HEAD recusa; worktree-only key não passa; affected + proto sem campo recusa; `surface: new` / `live_route: N/A` isenta; r1 sha256 `068581d6…` classificado BLOCKED contra `/monitor`
- [x] 3.2 Em `scripts/process-fsm/test_process_event.py`, T5 com `g_design is None` recusa galeria r1 + `live_route: /monitor`; T5 UI none + 3 md + specs continua a transitar. `pytest scripts/process-fsm -q` verde
- [x] 3.3 Usar skills de projeto quando couber (`.cursor/skills`, `.agents/skills`); Design → Aprovação de Design → Pronto para Dev já ocorreu antes deste Apply — não recodar produto

## 4. Skill

- [x] 4.1 Em `.agents/skills/design-critic/SKILL.md`, D10: fidelidade bloqueante = landmarks da rota viva (não sidebar 224px / `--bg-*`); galeria de estados = P0 em lista+detalhe; A/B abre URL viva + proto quando houver sessão; `/login` não é a rota; toggle Antes/Depois MUST mudar a vista

## 5. Fora de escopo (confirmação)

- [x] 5.1 Diff deste card sem `backend/`, `frontend/src/`, proto live #792, `DESIGN.md`, `.cursor/process-fsm.yaml` Σ, `CONTEXT.md`, `docs/adr/`
- [x] 5.2 `openspec validate --type change --strict` da change `card-799-prototype-clone-rota` verde; `UI impact: none` — zero HTML de protótipo de produto
