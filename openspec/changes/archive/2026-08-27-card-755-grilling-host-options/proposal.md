## Why

Ao grelhar, o card da ferramenta do host (`ask_user_question` no Grok, `AskUserQuestion` no Cursor) pode mostrar só a opção recomendada. O operador nos dois clientes não vê as alternativas da fronteira: só confirma a seta ou escreve Other. A original do Matt lista as escolhas no **corpo** da pergunta e a `➡️` é só a recomendação; o furo é o mapeamento para `options[]` da TUI e o relaying do pai que colapsa à recomendada.

Issue: [#755](https://github.com/oalansilva/crypto/issues/755).

## What Changes

- Lei nos dois clientes; o vendor Matt (`.cursor/skills/grilling/SKILL.md`) **não** é reescrito.
- Canônico `.cursor/skills/grill-card/SKILL.md`: Q fechada lista **todas** as alternativas reais em `options[]` (N≥2); recomendada primeiro com `(Recommended)`; Other não conta no N; Q aberta = markdown e/ou Other, **proibido** `options[]` fictícias.
- Uma linha extra na seção Grill-card de `.cursor/skills/alan-workflow/SKILL.md`: o **pai** chama a ferramenta do host com **todas** as options da Q fechada e não colapsa à recomendada.
- Relaying: o filho devolve cada Q fechada com as N opções listadas; o pai mapeia 1:1 para `options[]` (mesma ordem, recomendada primeiro). O filho isolado não chama a ferramenta do host.
- Fallback markdown Matt (`❓` + `➡️`) só se a ferramenta do host não estiver disponível: o **corpo** lista as escolhas; a seta é só a recomendação.
- Comentário canônico **idempotente**: no máximo um `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` por issue; reabertura da fronteira não duplica; texto já exato = deixar; texto errado = editar/minimizar o existente.
- Stubs Grok (`.grok/skills/grilling/`, `.grok/skills/grill-card/`) e gerador `grok_stubs.py` **intactos** — não nomeiam a ferramenta.
- Apply/QA: needles no pytest (`scripts/process-fsm`). Sessão real nos dois clientes = Homologado (Alan), **não** gate de QA.
- `UI impact: none`. Sem gate, hook ou evento novo na FSM. `AGENTS.md` always-on não cresce.

Não entra: reescrever grilling vendor; mudar TUI vendor; FSM; reabrir #667/#668; nomear ferramenta nos stubs; options fictícias; dual-write Hermes / `~/.codex`; sessão real como gate de QA.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs `grill-card` e `cursor-harness` já existentes.

### Modified Capabilities

- `grill-card`: Q fechada N≥2 na ferramenta do host; Q aberta sem options fictícias; fallback markdown com escolhas no corpo; comentário canônico idempotente; dump filho→pai com as N opções listadas (não só a seta).
- `cursor-harness`: mínimo — o pai, via linha de relay no `alan-workflow`, chama a ferramenta do host com **todas** as options da Q fechada e não colapsa à recomendada. Sem delta de `process-harness` / gerador de stubs.

## Impact

- Skills: `.cursor/skills/grill-card/SKILL.md` e **uma linha** na seção Grill-card de `.cursor/skills/alan-workflow/SKILL.md`.
- Specs: delta `grill-card` + delta mínimo `cursor-harness`. Sem `process-harness`, sem `.cursor/process-fsm.yaml`, sem `scripts/process-fsm/grok_stubs.py`, sem stubs `.grok/skills/*`.
- Testes: needles em `scripts/process-fsm/test_grill_card.py` (e/ou arquivo novo no mesmo dir).
- Sem `backend/` de produto, sem `frontend/src/`. Não reabre #667 (porta) nem #668 (adapters / gerador).
- `UI impact: none`. Prototype N/A. Impeccable N/A neste card.
