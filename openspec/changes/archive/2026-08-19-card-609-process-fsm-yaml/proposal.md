## Why

O processo de 12 colunas já é um grafo, mas vive em prosa (`AGENTS.md`, skill, harness). Sem uma tabela compilável, o Guard (#611) não tem o que executar e o Auto inventa arestas. O lote 1 começa aqui: versionar a EFSM do epic #608 como artefato testável, sem hook e sem GitHub.

## What Changes

- Adicionar `.cursor/process-fsm.yaml` com estados, T0–T17, arestas ilegais, `enabled_tools`, `enabled_events`, `context_file` (stubs), globs de produto/design e invariantes I1–I9.
- Adicionar validador (`scripts/process-fsm/`) que checa schema, determinismo das guardas e `request_implement` ∉ δ.
- Adicionar fixtures pytest **sem rede e sem hook**: transições legais e ilegais (Todo+Write, develop+Write, Done+Write, Agent+T7, unbound+Write).
- Não ligar Cursor hooks, `process_event` nem paging (`AGENTS.md`) — isso é #611/#612/#613.
- Não alterar código de produto (`backend/`, `frontend/src/`).

## Capabilities

### New Capabilities

- `process-fsm`: tabela EFSM versionada + validador + fixtures da δ (fonte da verdade do epic #608 para o lote 1).

### Modified Capabilities

- (nenhuma) — `cursor-harness` só passa a *consumir* este yaml no #611.

## Impact

- Novos paths: `.cursor/process-fsm.yaml`, `scripts/process-fsm/**`, testes do validador.
- Sem API, banco, UI ou dependências de runtime do produto.
- Desbloqueia #610 (resolver) e #611 (Guard Write).
- `UI impact: none`. Prototype N/A.
