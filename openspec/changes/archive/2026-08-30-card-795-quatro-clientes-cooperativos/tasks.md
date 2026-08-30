## 1. Produto: render_agents hardcode cooperativo

- [x] 1.1 Em `oalansilva/covenant-flow` `scripts/process-fsm/overlay.py`, `render_agents()` emite exactamente: `Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).` e `Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.`
- [x] 1.2 `render_agents()` MUST NOT interpolar `clients.*.auto`; MUST NOT conter `Auto permitido`; `SCHEMA_MAJOR` permanece 1; `CLIENT_KEYS` permanece `("cursor", "grok", "opencode")`; `validate_overlay` continua a não ler o boolean `auto`
- [x] 1.3 Não editar Guard, `process-fsm.yaml`, T0–T17, `install.sh` copy list, adapters, `docs/crypto-overlay.md`, `backend/**` nem `frontend/src/**`; não tocar config local IDE/CLI Cursor

## 2. Produto: README bloco do estranho

- [x] 2.1 Substituir só a secção **Clientes** pelas frases D6 do `design.md` (quatro nomes; os quatro cooperativos; yaml não conduz o stub; Auto não autoriza cruzar colunas; MUST NOT reivindicar Auto em Grok/OpenCode/dsh)
- [x] 2.2 O bloco MUST NOT afirmar que Auto é Cursor `clients.cursor.auto: true`; MUST NOT mencionar `approvalMode` / Run Everything; resto do README (O que é, 12 colunas, Install, Layout) inalterado salvo 2.3
- [x] 2.3 Exemplo `--pin` = tag deste card (esperado `v1.1.5`); MUST NOT `latest` nem placeholder; MUST NOT reabrir #787 como Apply; MUST NOT `gh repo edit` da description

## 3. Goldens pytest `scripts/process-fsm`

- [x] 3.1 `test_agents_md_is_stub` e/ou teste de `render_agents()`: quatro nomes; as duas linhas D5; `"Auto permitido" not in text`; sem Auto Grok/OpenCode/dsh; ensaio deny só nos três; ≤40 linhas não vazias
- [x] 3.2 Fixture com `clients.cursor.auto: true` MAY permanecer — o stub gerado continua cooperativo (prova Q2=A)
- [x] 3.3 Pin-tests (`test_pin_copies_dsh_without_injecting_clients_dsh` e needle em `test_grill_card.py`) sobem o esperado de `v1.1.4` para a tag deste card; `clients.dsh.auto: false` permanece
- [x] 3.4 `pytest scripts/process-fsm` sem GitHub verde; Guard / T0–T17 inalterados

## 4. Tag produto

- [x] 4.1 Confirmar `gh api repos/oalansilva/covenant-flow/tags`; se `v1.1.5` livre, usá-la; senão o próximo patch livre (nunca major)
- [x] 4.2 Commit no produto (`render_agents` + README + goldens) e tag patch; `install.sh --pin` continua a copiar `.dsh/` sempre

## 5. Pin Cripto

- [x] 5.1 Overlay Cripto: `clients.cursor.auto: false` (grok/opencode/dsh continuam `false`); `validate_overlay` PASS
- [x] 5.2 `implantar --pin` da tag deste card; overlay `pin:` = essa tag; `AGENTS.md` regenerado coincide com o `render_agents()` novo (sem hand-edit; sem `Auto permitido`)
- [x] 5.3 Não reabrir #787 como Apply; não alterar Guard, T0–T17, `CLIENT_KEYS`, `SCHEMA_MAJOR`; não tocar config local IDE/CLI; zero diff `backend/` / `frontend/src/` de produto

## 6. Verificação

- [x] 6.1 `openspec validate` da change verde; UI impact none
- [x] 6.2 `AGENTS.md` ≤40; quatro nomes; sem `Auto permitido`; sem Auto Grok/OpenCode/dsh; README produto no mesmo tag/pin com D6
