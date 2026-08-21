## Why

O Guard `beforeShellExecution` trata qualquer ocorrência de `>` / `>>` / `tee` como mutação e, se o comando também cita um path em `product_globs`, aplica `write_produto` mesmo quando o destino real do redirect é `/dev/null` ou um arquivo sob `/tmp`. Isso gera falso positivo: listagens, deploys e testes que só descartam stdout/stderr passam a deny fora de I1. O card #625 fecha esse buraco de classificação sem afrouxar o deny de redirect/`tee` real sobre árvores de produto.

## What Changes

- Em `scripts/process-fsm/guard.py` (e fallback bash simétrico em `.cursor/hooks/process-fsm-guard.sh`), a classificação de shell mutante passa a distinguir o **alvo** do redirect/`tee` do path citado no comando.
- Redirects cujo alvo é exatamente `/dev/null` (ou equivalente canônico) **ou** um path sob `/tmp` **não** disparam deny de produto, mesmo que o comando cite `backend/` / `frontend/src/`.
- Redirect/`tee`/`cp`/`mv`/`sed -i` cujo alvo cai em `product_globs` continua deny fora de I1 (comportamento atual preservado).
- Fixtures `beforeShellExecution` em `test_guard.py` cobrem falso positivo (null/`/tmp`) e true deny (produto).
- Aceite: `pytest scripts/process-fsm` verde; **UI impact: none**.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `process-fsm-guard`: requisito de shell mutante — allowlist de redirect/`tee` para `/dev/null` e sob `/tmp`; deny permanece para alvos em `product_globs`.

## Impact

- Código: `scripts/process-fsm/guard.py`, `scripts/process-fsm/test_guard.py`, `.cursor/hooks/process-fsm-guard.sh` (fallback).
- Spec: delta em `openspec/specs/process-fsm-guard/spec.md` (via change).
- Sem mudança de UI, board, yaml de colunas, `process_event`, ou `hooks.json` (já registra `beforeShellExecution`).
- Sem breaking change de API de produto; só corrige policy de hook.
