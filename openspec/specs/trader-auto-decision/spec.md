# trader-auto-decision Specification

## Purpose
TBD - created by archiving change lab-trader-auto-decision. Update Purpose after archive.
## Requirements
### Requirement: Remover verificação de trader_verdict em lab.py

**Description:** The system MUST NOT require manual trader_verdict confirmation in lab.py endpoints. The endpoint SHALL accept the trader LLM verdict as final and continue the autonomous flow.

#### Scenario: Endpoint não requer confirmação

Given um run com phase="trader_validation"
When o graph completa o _trader_validation_node
Then o endpoint NÃO DEVE setar needs_user_confirm=True
And DEVE permitir que o fluxo continue automaticamente

