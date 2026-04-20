---
spec: openspec.v1
id: op-o-portifolio-na-tela-monitor-7
title: Monitor Portfolio Option Derived from Wallet for Crypto Assets
card: "#110"
change_id: op-o-portifolio-na-tela-monitor-7
stage: PO
status: draft
owner: Alan
created_at: 2026-04-19
updated_at: 2026-04-19
---

# Proposal: Monitor Portfolio Option Derived from Wallet for Crypto Assets

**Card:** #110  
**change_id:** `op-o-portifolio-na-tela-monitor-7`  
**Stage:** PO

## 1. User Story

> As a user monitoring crypto assets, I want the Portfolio option in Monitor to become read-only when Binance is configured, so the displayed portfolio always reflects my wallet holdings instead of manual selection.

## 2. Product Decision

For assets classified as `cryptomoeda`, when the user has Binance configured, the Portfolio field in Monitor becomes derived data.

The UI must stop allowing manual edits and the value shown must come from Wallet data based on the user's bought assets.

For non-crypto assets, the current behavior remains unchanged.

## 3. Scope

### Scope In
- Apply the rule only to Monitor items classified as `cryptomoeda`
- Detect Binance-configured state as the trigger for read-only behavior
- Derive Portfolio from Wallet/Binance holdings instead of manual input
- Enforce the same rule in backend or business validation
- Show a clear fallback/informational state when wallet data is unavailable or empty

### Scope Out
- Changes to non-crypto asset behavior
- Support for brokers/providers other than Binance
- Broad Monitor redesign beyond read-only state and contextual explanation
- New portfolio composition logic outside current Wallet ownership data

## 4. Final Functional Rule

| Condition | Expected behavior |
| --- | --- |
| Asset is `cryptomoeda` + Binance configured + wallet data available | Portfolio is read-only and auto-filled from Wallet |
| Asset is `cryptomoeda` + Binance configured + no eligible holdings / sync failure | Portfolio stays read-only and shows fallback feedback |
| Asset is not `cryptomoeda` | Existing manual behavior remains |
| Binance not configured | Existing manual behavior remains |

## 5. Risks and Dependencies

### Risks
- Misapplying the rule to all Monitor assets instead of only `cryptomoeda`
- Frontend-only lock without backend protection
- Wallet/Binance sync delay creating stale Monitor values
- Missing fallback for empty holdings or sync failure

### Dependencies
- Canonical asset type classification available in Monitor payload or business layer
- Reliable Wallet/Binance integration status
- Wallet source able to resolve which bought assets define Portfolio

## 6. Acceptance Criteria

- Given a `cryptomoeda` asset and Binance configured, when the user opens Monitor, then Portfolio is shown as read-only.
- Given a `cryptomoeda` asset and Binance configured, when wallet data is available, then Portfolio is populated from Wallet data and not from manual input.
- Given a non-crypto asset, when the user opens Monitor, then Portfolio keeps the current editable behavior.
- Given Binance-configured crypto with empty or unavailable wallet data, when Monitor loads, then Portfolio remains blocked and the interface shows clear feedback about missing/unavailable data.
- Given a direct request attempting to manually persist Portfolio for Binance-configured crypto, when backend validation runs, then the manual value is ignored or rejected according to the derived rule.

## 7. Recommended Next Step

Hand off to DESIGN for the read-only state, fallback messaging, and field-origin clarity in Monitor.
