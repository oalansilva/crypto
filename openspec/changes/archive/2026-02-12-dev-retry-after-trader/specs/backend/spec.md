# Spec: Auto-retry do Dev após feedback do Trader (Backend)

**Capability:** backend  
**Type:** enhancement  
**Change:** dev-retry-after-trader

---

## ADDED Requirements

### Requirement: Auto-retry do Dev após feedback do Trader

**Description:** The system SHALL re-run the Dev implementation when the Trader returns required_fixes and the run is not approved.

#### Scenario: Trader pede ajustes
- **Given** o Trader retorna verdict needs_adjustment ou rejected com required_fixes
- **When** o Dev recebe o feedback
- **Then** o sistema MUST aplicar correções e re-rodar o backtest antes de nova validação

---

### Requirement: Limite de tentativas

**Description:** The system MUST cap the number of Dev retries after Trader feedback to a configurable limit (default 2).

#### Scenario: Limite atingido
- **Given** o número de tentativas atingiu o limite
- **When** o Trader ainda rejeita
- **Then** o sistema MUST parar o retry e manter o status needs_adjustment

---

### Requirement: Trace de retries

**Description:** The system SHALL append trace events for each Dev retry triggered by Trader feedback.

#### Scenario: Auditoria
- **Given** uma tentativa automática foi executada
- **When** o run continua
- **Then** o trace MUST incluir o motivo, tentativa atual e limite
