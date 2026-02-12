# Spec: Dev Template Notation (Backend)

**Capability:** backend  
**Type:** enhancement  
**Change:** dev-template-notation

---

## MODIFIED Requirements

### Requirement: Dev prompt enforces valid notation

**Description:** The system SHALL update the Dev prompt to require `entry_logic` and `exit_logic` in valid boolean notation (no free text).

#### Scenario: Valid boolean syntax
- **Given** Dev generates a template
- **When** prompt is applied
- **Then** entry/exit logic MUST be boolean expressions (ex: `rsi14 > 55 AND close > ema50`)
- **And** free-text phrases are not allowed

---

### Requirement: stop_loss numeric

**Description:** The system SHALL require `stop_loss` to be numeric (float), not a string.

#### Scenario: stop_loss enforced
- **Given** Dev outputs template
- **When** stop_loss is present
- **Then** stop_loss MUST be a float (e.g., 0.03)

---

## ADDED Requirements

### Requirement: Dev auto-corrects invalid logic

**Description:** The system SHALL instruct the Dev to detect invalid logic and correct it before returning output.

#### Scenario: Invalid expression detected
- **Given** Dev drafts an invalid expression (e.g., "cruza acima")
- **When** Dev validates output
- **Then** Dev MUST rewrite into a valid boolean expression
- **And** output returned is valid
