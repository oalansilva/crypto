## Why

Alan no T7 do #792 abriu o Monitor real (`SOL/USDT`, cabeçalhos Status / Preço / Distância / 7d / Risco até stop / Tags) e o protótipo r1 era uma **galeria de estados** com tokens Binance. Assessment A/B e `design.md` mesmo assim emitiram PASS (“fidelidade shell”). A regra já proíbe layout paralelo, mas o teste observável live ainda é só chrome (sidebar 224px, `--bg-*`). Sem landmarks da rota viva e sem `copied` no `G_design`, o furo volta no próximo Design UI affected.

## What Changes

- Endurecer o harness de Design: fidelidade bloqueante = **landmarks da rota viva** (listagem, cabeçalhos, ações, expand), não só shell/nav/tokens/densidade.
- `openspec/specs/impeccable-design-gate`: tela existente MUST ser **clone da rota** + patch do delta; **galeria de estados** (N cards para N cenários quando o produto é lista+detalhe) = P0.
- Prompt A/B: abrir URL viva da rota e URL do protótipo quando houver sessão; P0 se landmark da listagem faltar. Sem sessão, `/login` **não** é “a rota”.
- Toggle Antes/Depois, se existir: Antes = clone sem delta, Depois = clone+delta; botão morto (`aria-pressed` sem script) não conta.
- **Q1=A:** skill + A/B **e** `G_design`. `UI impact: affected` + rota existente ⇒ T5 recusa se landmarks ou `copied` falharem.
- **Q2=A:** catálogo versionado de landmarks por rota + leitura **estática** do HTML do proto. T5 offline (sem Playwright autenticado em `submeter_design`).
- **Q3=A:** `copied` = soma dos bytes entre `COPIED:start` e `COPIED:end`. Ausência de marcadores ou soma 0 ⇒ T5 recusa.
- **Q4=A:** fail-closed — rota declarada sem entrada no catálogo ⇒ T5 recusa. O autor **não** acrescenta a chave na mesma change para furar o gate.
- **Q5=A:** `design.md` MUST ter campo parseável `live_route:` e/ou `surface: existing|new`. `surface: existing` (ou `live_route:` de rota conhecida) exige chave + landmarks + `copied`. `surface: new` (ou `live_route: N/A` justificado) isenta catálogo/`copied`. `UI impact: affected` + proto **sem** o campo ⇒ T5 recusa.
- Catálogo semeado para rotas existentes (Monitor, Favoritos, Descoberta, Combo), não só `table.signals`.
- Fixture de regressão: bytes do r1 #792 (`068581d6…`, sem `table.signals`) MUST ser classificados BLOCKED. Path live r2 **não** é essa fixture e **não** se pacha.

Não é **BREAKING** para produto: nenhuma rota, shell ou copy de Cripto muda. É **BREAKING** para o predicado `G_design` em cards `UI impact: affected` com proto de tela existente — T5 deixa de passar só com 3 md + specs.

## Capabilities

### New Capabilities

- `design-route-clone-gate`: predicado composto de `G_design` — parse de `live_route:` / `surface:` no `design.md`, catálogo versionado por rota, leitura estática do HTML do proto, soma `copied`, fail-closed sem chave, isenção `surface: new`, fixture r1 BLOCKED.

### Modified Capabilities

- `impeccable-design-gate`: clone+delta passa a exigir landmarks da rota viva; galeria de estados = P0; A/B compara URL viva vs proto; chrome/tokens não substituem clone da página.
- `process-fsm-event`: `files_g_design` / `G_design` deixa de ser só presença de 3 md + specs; T5 (`submeter_design`) recusa quando o gate de clone falha.
- `llm-flow-emission`: folha de tokens continua chrome; MUST NOT substituir clone da página; `design.md` ganha campos parseáveis `live_route:` / `surface:`.

## Impact

- Apply (após Pronto para Dev), só harness: `scripts/process-fsm/process_event.py` (`files_g_design` / predicado composto), catálogo versionado, testes/fixture r1, `.agents/skills/design-critic/SKILL.md`, delta em `openspec/specs/impeccable-design-gate`, `process-fsm-event`, `llm-flow-emission`.
- Não toca `backend/`, `frontend/src/`, protótipo live do #792 (`frontend/public/prototypes/card-792-monitor-risco-explicito/`), `DESIGN.md`, pipeline Impeccable HTML, Playwright autenticado dentro de T5.
- Não reabre #792 (Pronto), #673, #530 como Apply. Não faz fork do vendor `$impeccable critique`. Sem credencial de produção no `process_event`.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Sem HTML de produto.
- Origem: issue #799 (DoD grelhado; Q1–Q5=A, 2026-08-29). Relacionado e **não** reaberto: #792 Pronto; #673; #530.
