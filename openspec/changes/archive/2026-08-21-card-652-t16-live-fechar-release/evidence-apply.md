# Evidence apply — card #652

- `pytest scripts/process-fsm -q`: 169 passed
- T16 live: `process_event fechar_release` mede `release-guard post`, fecha `RELEASE_CARDS` Homologado→Pronto
- T15/`homologar` continua reject Agent
- Sem deploy PROD no evento; yaml `deploy_prod` não é Mealy
