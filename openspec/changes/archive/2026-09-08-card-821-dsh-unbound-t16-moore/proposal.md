## Why

No dsh web, Alan pede closeout explícito (`suba a release` / `fechar release` / `subir lote`) numa sessão **sem card** e o root recusa, lendo o stub Moore unbound `Não carregue playbook de release.` como deny de T16. Recidiva `session-35e78019`: ler a skill `covenant-flow` **não** chega enquanto o header continua a proibir o playbook. Cursor/Grok já carregam overlay no pedido explícito (#613); o quarto cliente não. P1: o lote fecha-se noutro cliente.

## What Changes

- O stub unbound compilado (`UNBOUND_PAGE` em `paging.py`) deixa de ser lido como “proibido fechar release”. Continua a negar Write de produto e **não** despeja Homologado/release always-on (#613).
- Pedido explícito de release em sessão sem card (`q=None`, `bound_card=⊥`, `q_git=develop`) passa a mandar carregar overlay on-demand e iniciar o playbook T16.
- O mesmo compilador alimenta os quatro injectores; o fallback fail-open do `sessionStart` Cursor fica alinhado ao stub novo.
- Uma linha no runbook `covenant-flow` (secção Release): `bound_card=⊥` / `enabled_events: (unbound)` é display do paging, não lei de T16.
- Goldens pytest em `scripts/process-fsm` cobrem idle unbound vs excepção de closeout explícito. DoD humano: **só o dsh** (dump autenticado `:3080`). Sem dump nos quatro clientes.
- `unread_page()` (Status unread com card bound) **não** muda neste card.
- **Não** muda Σ / `fechar_release` / `M_lote` / `backend/` / `frontend/src/`. **Não** cresce `AGENTS.md` com o runbook de 12 colunas. `clients.dsh.auto` permanece `false`. **Não** executa lote PROD neste card.

## Capabilities

### New Capabilities

- (nenhuma) — a excepção de closeout explícito unbound já está na lei T16 (`lote_git("develop")` avalia `fechar_release`); este card alinha o stub Moore para o modelo não tratar paging como deny.

### Modified Capabilities

- `process-fsm-paging`: stub unbound (`bound_card=⊥`) MUST negar Write de produto e MUST NOT despejar frames Homologado/release always-on; MUST NOT conter a ordem absoluta `Não carregue playbook de release.`; MUST nomear a excepção de pedido explícito (`suba a release` / `fechar release` / `subir lote`) para carregar overlay e iniciar T16. `enabled_events: (unbound)` continua display. Fallback `sessionStart` usa o mesmo stub. `unread_page()` fora.
- `covenant-flow`: uma linha na secção Release — paging unbound não é deny de T16 no pedido explícito; overlay on-demand. Pin = próximo patch livre após o `pin` vigente (`v1.1.13`) para o núcleo `paging.py` não reverter no próximo `--pin`. `clients.dsh.auto: false`. `AGENTS.md` não cresce.

## Impact

- Altera (Apply, após Pronto para Dev): `scripts/process-fsm/paging.py` (`UNBOUND_PAGE`), `.cursor/hooks/process-fsm-session-start.sh` (fallback), `scripts/process-fsm/test_paging.py`, uma linha em `.cursor/skills/covenant-flow/SKILL.md` secção Release. Nucleus via produto `oalansilva/covenant-flow` + `implantar --pin` no Cripto.
- Não toca `process-fsm.yaml` / Σ / `process_event.py` / `t16.py` / `guard.py` `decide()`, `backend/` / `frontend/src/`, Dual-write Hermes / `~/.codex/skills/`, vendor `deepseek-harness`, Auto dsh, `unread_page()`, `AGENTS.md` (tamanho/substância), HTML / `DESIGN.md` de produto.
- `UI impact: none`. Prototype N/A. Impeccable/Playwright desta coluna = N/A.
- Origem: issue #821. Homologação: dump autenticado `http://127.0.0.1:3080` de um turno `suba a release` **ou** `fechar release` unbound com ≥1 tool do playbook T16 (overlay / `covenant-flow-environments` / `release-guard` / board / `process_event fechar_release`). Só `skill` + `read` do runbook **falha** (recidiva `session-35e78019`). Pytest **não** substitui esse dump; dump nos outros clientes **não** é critério.
