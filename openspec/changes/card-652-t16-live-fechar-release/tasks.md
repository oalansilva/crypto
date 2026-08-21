## 1. Tabela e validator

- [x] 1.1 T16 no yaml: `actor: Agent`; I2 sem T16; `enabled_tools[Homologado]` inclui `process_event`; stub Homologado cita T16 live
- [x] 1.2 `ALAN_GATES` só T1/T7/T15; validator falha se T16 for Alan-only ou omitir Agent
- [x] 1.3 `harness.mdc` e skill `alan-workflow`: Alan único T1/T7/T15; Homologado→Pronto via `process_event fechar_release`
- [x] 1.4 Fixture `evaluate`: Agent+M_lote→Pronto T16; Agent¬M_lote→reject; Alan `homologar` inalterado

## 2. Medir M_lote e closer

- [x] 2.1 `measure_m_lote()`: `scripts/release-guard post` exit 0 ⇒ True; ≠0/timeout/erro ⇒ False
- [x] 2.2 `process_event fechar_release` live chama o measurer quando `m_lote` não foi injetado; CLI **sem** `--m-lote`
- [x] 2.3 Pacote = `RELEASE_CARDS` ou `--card` solo; Homologado ou já Pronto (Pronto=skip); qualquer outro Status/ausente ⇒ I9; unbound `develop`/`release-*` permitido só neste evento; após membership, `evaluate(state=Homologado)` e mover por id do pacote
- [x] 2.4 Closer: `comment_pronto` (`--card <id>` por Homologado) e então `set_status(Pronto)`; closer/measurer None ⇒ I9, mover vazio; token yaml `deploy_prod` não é passo Mealy
- [x] 2.5 `--dry-run` não comenta nem move; `main()` injeta measurer+closer reais
- [x] 2.6 Fixtures: measurer True + closer ok ⇒ mover Pronto por Homologado; ¬M_lote ⇒ reject `guard:M_lote`; membro Done/QA ⇒ I9; mix Homologado+Pronto ⇒ skip Pronto e move o resto; closer omitido ⇒ I9; comment falha antes do move ⇒ I9; T15 reject; testes **não** chamam GitHub nem `release-guard` real

## 3. Fora de escopo

- [x] 3.1 Diff NÃO faz deploy PROD, archive, PR `main`, nem altera `backend/` / `frontend/src/`
- [x] 3.2 `priorizar` / `aprovar_design` / `homologar` continuam reject Agent
- [x] 3.3 `pytest scripts/process-fsm -q` verde
