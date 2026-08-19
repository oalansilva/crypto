## 1. Tabela

- [x] 1.1 Criar `.cursor/process-fsm.yaml` copiando a matriz T0–T17 do design.md (T17a+T17b), states, enabled_tools, enabled_events, context_file stubs, product_globs/design_globs do Decision 7, I1–I9, `fail_closed_asymmetric: true`
- [x] 1.2 `illegal_events` = request_implement, pular_coluna, Agent.aprovar_design; `write_produto` NÃO entra nessa lista
- [x] 1.3 `illegal_edges` inclui Todo+write_produto, develop+write_produto, Done+write_produto, unbound+write_produto, Agent+aprovar_design
- [x] 1.4 T2 `from: Vivo` (validador expande); T0 `from: null`

## 2. Validador

- [x] 2.1 Implementar `scripts/process-fsm/` (load yaml, schema, expansão Vivo, determinismo T4/T5, T10/T11, T12–T14)
- [x] 2.2 Falhar se T1, T7, T15 ou T16 omitir ator Alan
- [x] 2.3 Falhar se `write_produto` estiver em `illegal_events` ou se Σ divergir da matriz

## 3. Fixtures

- [x] 3.1 Pytest em `scripts/process-fsm/test_*.py`: T0–T17 legais + I1 allow (Em desenvolvimento + write_produto com binding)
- [x] 3.2 Pytest arestas ilegais: Todo+Write, develop+Write, Done+Write, Agent+T7, unbound+Write
- [x] 3.3 Ligar `pytest scripts/process-fsm -q` no job de CI de testes (sem GitHub)

## 4. Fora de escopo (verificar no diff)

- [x] 4.1 Diff NÃO altera `.cursor/hooks.json`, `backend/`, `frontend/src/`
