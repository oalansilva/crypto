# Design — harden-multiagent-kadro-execution-model

## Overview

This is the follow-up execution-hardening change that should happen only after the operating contract has been standardized.

## Design principle

> Do not harden the execution engine until the role contract, handoff contract, and stage-completion rules are already clear.

## Main design decisions

### 1. Preserve the current structure
This change keeps:
- current Kadro / Kanban flow
- current persistent agents
- workflow DB as runtime truth
- OpenSpec as artifact layer

### 2. Align instructions to the standardized model
Once the operating model is defined, agent instructions should be aligned to it so the intended process becomes repeatable behavior.

### 3. Improve execution discipline inside the current stage flow
The change should improve the practical use of:
- `change`
- `story`
- `bug`
- ownership
- locks
- dependencies
- practical WIP / parallelism expectations

### 4. Harden closure behavior
Homologation and archive flows should become more reliable end-to-end with less post-hoc reconciliation.

### 5. Reduce drift instead of masking it
The goal is to reduce drift across runtime, OpenSpec, and metadata rather than normalizing manual reconciliation as the default operating mode.
