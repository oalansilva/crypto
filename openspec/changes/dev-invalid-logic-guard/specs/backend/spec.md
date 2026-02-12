# Spec: Guard de Lógica Inválida (Backend)

**Capability:** backend  
**Type:** enhancement  
**Change:** dev-invalid-logic-guard

---

## ADDED Requirements

### Requirement: Preflight de lógica antes do backtest

**Description:** The system SHALL validate `entry_logic` and `exit_logic` deterministically before running any backtest job.

#### Scenario: lógica inválida
- **Given** a candidate template with invalid logic syntax
- **When** the Dev is about to run the backtest
- **Then** the system MUST detect invalid logic and block the backtest

---

### Requirement: Auto-correção e retry

**Description:** The system SHALL auto-correct invalid logic and retry the backtest up to a limited number of attempts.

#### Scenario: correção automática
- **Given** invalid logic detected on preflight
- **When** Dev applies auto-correction
- **Then** the system MUST retry backtest with corrected logic

---

### Requirement: Registro de ajustes

**Description:** The system SHALL append trace events describing invalid logic and corrections applied.

#### Scenario: auditável
- **Given** an auto-correction was executed
- **When** the run continues
- **Then** the trace MUST include the reason and attempt count
