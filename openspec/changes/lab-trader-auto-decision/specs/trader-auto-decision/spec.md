# Spec: trader-auto-decision

## ADDED Requirements

### Requirement: Remove needs_user_confirm antes do trader_validation

**Description:** The system SHALL NOT set `needs_user_confirm: true` or `status: needs_user_confirm` before or during the trader validation phase. The graph flow SHALL proceed automatically from implementation to trader_validation without human intervention.

#### Scenario: Fluxo automático para trader

Given um Lab run em fase de implementation completa
When o dev_senior retorna um template válido com métricas
Then o sistema DEVE chamar _trader_validation_node automaticamente
And NÃO DEVE marcar needs_user_confirm=True

### Requirement: Agente trader avalia resultado da estratégia automaticamente

**Description:** The system MUST execute the "trader" persona via LLM to evaluate the strategy result and return a verdict. The trader SHALL analyze the backtest metrics (in_sample, holdout, all), strategy performance, and risk to decide: approved, rejected, or needs_adjustment.

#### Scenario: Trader avalia resultado da estratégia

Given o contexto com backtest metrics (walk_forward), strategy_draft, e template
When _trader_validation_node é executado
Then o agente trader DEVE retornar um JSON com:
  - verdict: "approved" | "rejected" | "needs_adjustment"
  - reasons: lista de justificativas
  - required_fixes: lista de ajustes necessários (se needs_adjustment)

### Requirement: Salvar estratégia e template automaticamente quando approved

**Description:** When the trader verdict is "approved", the system SHALL automatically save the strategy to favorites AND save the template, without requiring human confirmation.

#### Scenario: Trader aprova e salva automaticamente

Given trader_verdict == "approved"
When o sistema processa o veredito
Then a estratégia DEVE ser salva nos favoritos automaticamente
And o template DEVE ser salvo automaticamente
And o status DEVE ser "done"

### Requirement: Fluxo pós-trader automático

**Description:** The system SHALL automatically route the flow based on the trader verdict without human confirmation. If approved: save to favorites and go to END. If rejected: go to END (without saving). If needs_adjustment: return to dev_implementation for automatic fixes.

#### Scenario: Trader rejeita

Given trader_verdict == "rejected"
When _after_trader_validation é executado
Then o status DEVE ser "rejected"
And o fluxo DEVE ir para END
And NÃO DEVE salvar nos favoritos

#### Scenario: Trader pede ajustes

Given trader_verdict == "needs_adjustment"
And trader_retry_count < max_retries
When _after_trader_validation é executado
Then o status DEVE ser "needs_adjustment"
And o fluxo DEVE voltar para "dev_implementation"
And trader_retry_count DEVE incrementar
And NÃO DEVE salvar nos favoritos ainda

## MODIFIED Requirements

### Requirement: Remover verificação de trader_verdict em lab.py

**Description:** The system MUST NOT require manual trader_verdict confirmation in lab.py endpoints. The endpoint SHALL accept the trader LLM verdict as final and continue the autonomous flow.

#### Scenario: Endpoint não requer confirmação

Given um run com phase="trader_validation"
When o graph completa o _trader_validation_node
Then o endpoint NÃO DEVE setar needs_user_confirm=True
And DEVE permitir que o fluxo continue automaticamente
