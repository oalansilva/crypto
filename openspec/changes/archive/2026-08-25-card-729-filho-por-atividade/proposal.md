## Why

O D8 do #673 manda abrir chat novo por coluna. Isso trava o operador e mistura o problema errado: o custo é contexto de **atividade**, não o título do transcript. Precisamos de um chat `#<id>` por card em que o pai só despacha e cada atividade corre num filho isolado, sem cruzar T1/T7 e sem gate novo na FSM.

Issue: [#729](https://github.com/oalansilva/crypto/issues/729).

## What Changes

- Um chat `#<id>` cobre Em Refinamento → Done técnico. Homologado e Release/lote ficam fora.
- O pai não executa grill / Design / Apply / Review / QA. Exceção: depois de A/B com zero P0/P1 o pai grava **somente** `## Design Critique` em `design.md`. Recusa de mistura = o pai não executa a outra atividade **no mesmo chat**, não “abra `#id Apply`”.
- Filho por atividade, inherit de modelo, sem inherit de transcript:
  - Em Refinamento: filho `grill-card` (bind Status + `#<id>`, **não** branch `card-<id>-*`); relaying de rodadas; filho edita o body; T1 só Alan.
  - Design: filho autor (OpenSpec + protótipo); onda A/B disparada pelo pai.
  - Em desenvolvimento: um filho apply (loop fatiado **dentro** do filho).
  - Code Review: onda de dois reviewers.
  - QA: um filho checks/evidência; T14 no pai.
- Pai dono de `process_event` e git. Filho não arrasta coluna. Apply só com `Status=Pronto para Dev`.
- Default global `inherit` permanece. Isolados = lista fechada (filhos de atividade + ondas).
- Sem estado/evento/hook/`enabled_tools` novo na FSM. `AGENTS.md` always-on não cresce.
- `UI impact: none`.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs de emissão/harness/grill já existentes.

### Modified Capabilities

- `llm-flow-emission`: troca “um chat por coluna / abra chat novo” por “um chat por card + filho/onda por atividade”; recusa = pai não executa; sem gate FSM.
- `cursor-harness`: runbook dos dois clientes; Design child autor; pai orquestra; Apply/Review/QA não pedem chat novo; Design gate: sessão pai não escreve `design.md`/protótipo.
- `grill-card`: precondição deixa de exigir branch `card-<id>-*`; bind = Status=Em Refinamento + id no prompt; o executor é o filho; o pai só faz relaying.

## Impact

- Skills: `.cursor/skills/alan-workflow`, `grill-card`, `openspec-apply-change`, `.agents/skills/design-critic`.
- Docs: `docs/backlog-operating-model.md`, `docs/decision-log.md` (entrada nova; não reescrever a do #673 além de apontar o sucessor).
- Specs acima. Sem `backend/` de produto, sem `frontend/src/`. Sem mudança de T0–T17, I1–I9 ou `process_event` alphabet.
- Não reabre #530, #569, #613, #667, #668. Não enfraquece dual critic/reviewer, T7, browser gate.
- `UI impact: none`. Prototype N/A. Impeccable N/A neste card.
