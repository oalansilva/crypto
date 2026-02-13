# Spec: dev-trader-feedback

## ADDED Requirements

### Requirement: Passar trader_verdict com required_fixes para dev no retry

**Description:** When the Dev node is executed in a retry scenario (`dev_needs_retry=True`), the system SHALL pass the `trader_verdict` with `required_fixes` in the context/message. The Dev persona MUST receive explicit feedback from the Trader about what structural changes are needed.

#### Scenario: Dev recebe feedback do trader no retry

Given um run com `dev_needs_retry=True` e `trader_verdict` existente
When o `_implementation_node` é executado novamente (retry)
Then o contexto DEVE incluir o `trader_verdict` e `required_fixes`
And o Dev Senior DEVE receber essas instruções na mensagem

### Requirement: Dev Senior implementa mudanças estruturais solicitadas

**Description:** The Dev Senior persona SHALL implement structural changes requested by the Trader in `required_fixes`, not just optimize parameters. This includes changes like: pivoting strategy type, adding indicators, modifying logic thresholds, etc.

#### Scenario: Dev implementa mudanças estruturais

Given o Dev recebe `required_fixes` = ["mudar para momentum", "adicionar filtro de volume"]
When o Dev gera o novo template
Then o template DEVE refletir as mudanças solicitadas
And NÃO DEVE apenas otimizar parâmetros existentes (RSI 14→11)

### Requirement: Mensagem customizada no retry incluindo feedback do trader

**Description:** When calling the Dev Senior persona for a retry, the system SHALL use a custom message that includes the Trader's feedback (verdict, reasons, required_fixes) instead of the default context-only message.

#### Scenario: Mensagem inclui instruções do trader

Given um retry após rejeição do trader
When `_run_persona` é chamado para o dev_senior
Then a mensagem DEVE conter:
  - Veredicto do trader (rejected/needs_adjustment)
  - Razões da rejeição
  - Lista de ajustes requeridos (required_fixes)
  - Instrução clara para implementar mudanças estruturais

## MODIFIED Requirements

### Requirement: Modificar _implementation_node para detectar retry

**Description:** The system MUST detect when this is a retry scenario (previous trader rejection with required fixes) and adjust the Dev Senior call accordingly. If `dev_needs_retry=True` and `trader_verdict` exists with actionable feedback, construct and pass a custom message to the Dev.

#### Scenario: Retry detectado e mensagem customizada construída

Given `outputs.get("dev_needs_retry")` is True
And `outputs.get("trader_verdict")` exists with required_fixes
When `_implementation_node` chama `_run_persona` para dev_senior
Then o sistema DEVE:
  1. Extrair `verdict`, `reasons`, `required_fixes` do trader_verdict
  2. Construir mensagem customizada com feedback
  3. Passar mensagem customizada no `_run_persona`
