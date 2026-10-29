## ADDED Requirements

### Requirement: Guard nega captura e disparo do executor fora do process_event
A Guard SHALL negar comando de shell do agente que chame o caminho `capturar` do cliente do executor ou o endpoint `dispatches` do repositório do executor, a menos que o comando seja só uma invocação de `scripts/process-fsm/process_event.py` com evento nomeado e flags. A negação SHALL dizer ao agente para usar `process_event`. A regra de `item-edit`/GraphQL de Status SHALL continuar como está. Esta regra é cooperativa e MUST NOT ser apresentada como garantia contra forja.

#### Scenario: Agente tenta capturar um comando do Alan
- **WHEN** o comando de shell chama `portao_client.py capturar` ou `gh api repos/<repo do executor>/dispatches`
- **THEN** a Guard devolve `deny` e aponta `process_event`

#### Scenario: process_event continua permitido
- **WHEN** o comando é só `python3 scripts/process-fsm/process_event.py pedir_review --card N`
- **THEN** esta regra não nega
