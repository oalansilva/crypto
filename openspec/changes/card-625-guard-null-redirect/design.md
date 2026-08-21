## Context

Card [#625](https://github.com/oalansilva/crypto/issues/625). O Guard Write (#611/#612) já classifica `beforeShellExecution` com `MUTATION_RE` (`>`, `>>`, `tee`, `sed -i`, …) e, se o comando também cita um path em `product_globs`, trata isso como `write_produto`. O falso positivo: comandos que só leem/listam/testam produto e descartam saída com `>/dev/null`, `2>/dev/null` ou `> /tmp/...` são deny fora de I1.

**UI impact: none.** Policy de hook/harness. Prototype N/A. Impeccable N/A.

Estado atual (worktree `card-625-guard-null-redirect`):

- `_path_from_command` em `scripts/process-fsm/guard.py`: se há token de mutação **e** regex acha `backend/`/`frontend/src/` em qualquer lugar do comando → path de produto → deny via `write_produto`.
- Fallback bash em `.cursor/hooks/process-fsm-guard.sh` replica a mesma heurística.
- Fixtures existentes: `test_shell_redirect_denied`, `test_shell_tee_denied`, `test_shell_absolute_and_glued_redirect_denied`, `test_pytest_backend_allowed`.

## Goals / Non-Goals

**Goals:**

- Redirect/`tee` cujo **alvo** é `/dev/null` (canônico) ou um path sob `/tmp` **MUST NOT** disparar deny de produto, mesmo citando árvores de produto no comando.
- Redirect/`tee` (e demais mutações) cujo alvo cai em `product_globs` continua deny fora de I1.
- Fixtures envelope `beforeShellExecution` cobrem falso positivo e true deny.
- `pytest scripts/process-fsm` verde.
- Fallback bash alinhado à mesma regra (sem divergência Python vs shell).

**Non-Goals:**

- Parser AST completo de shell / expansão de variáveis (`$TMPDIR`, `~`, process substitution).
- Alterar `product_globs` / colunas / `process_event` / board / `hooks.json` matcher.
- Allowlist de outros sinks (`/var/tmp`, pipes nomeados, fds arbitrários além de `/dev/null`).
- Código de produto backend/frontend; UI; commit; movimento de Status.

## Decisions

1. **Classificar pelo alvo do redirect/`tee`, não por qualquer path citado.**  
   Alternativa: remover `>` de `MUTATION_RE` (abre buraco real). Alternativa: allowlist só de comandos “read-only” (`pytest`, `ls`) — incompleto e frágil. Escolha: após detectar token de mutação, extrair o **destino** de `>`/`>>`/`tee` e só então decidir.

2. **Allowlist de alvo: `/dev/null` ou prefixo `/tmp/` (e o próprio `/tmp`).**  
   - `/dev/null` (e formas coladas `>/dev/null`, `2>/dev/null`, `>>/dev/null`).  
   - Destinos sob `/tmp` (absolutos; ex. `/tmp/out.log`, `/tmp/repo/...` que **não** sejam reinterpretados como produto só por conter a substring `backend/` no path absoluto fora do repo — ver Decision 4).  
   Se **todos** os alvos de redirect/`tee` no comando estiverem na allowlist, o Guard **não** promove um path de produto citado noutro token a `write_produto` por causa desse redirect.  
   Se **qualquer** alvo de redirect/`tee` cair em `product_globs` (relativo ou absoluto resolvido para prefixo de produto), deny fora de I1 (como hoje).

3. **Mutações não-redirect (`sed -i`, `cp`, `mv`, `install`, `perl -i`) inalteradas.**  
   Continuam a extrair path de produto/design no comando e a negar produto fora de I1. A allowlist null/`/tmp` aplica-se a redirects e a `tee` (incluindo `tee -a`).

4. **Não confundir `/tmp/.../backend/...` com write de produto do repo.**  
   O falso positivo clássico do card é `... backend/ ... >/dev/null`. Um `tee /tmp/scratch/backend/app/main.py` **não** é write no worktree: alvo allowlisted sob `/tmp` ⇒ não deny-produto por esse path. True deny continua sendo redirect/`tee` para `backend/...` ou `frontend/src/...` (relativo ao cwd do envelope) ou absoluto que `repo_relative` mapeia para esses prefixos **fora** de `/tmp` e `/dev/null`.

5. **Mesma regra no fallback bash do adapter.**  
   Sem isso, Python/PyYAML ausente reintroduz o falso positivo. Implementação espelhada (regex de alvo null/`/tmp` antes de promover path de produto).

6. **Fixtures no envelope Cursor `beforeShellExecution`.**  
   Mínimo:
   - falso positivo: comando que cita `backend/` (ou `frontend/src/`) e redireciona só para `/dev/null` e/ou `/tmp/...` com Status fora de I1 ⇒ `allow`;
   - true deny: `>> backend/...` ou `tee backend/...` (e variantes coladas/absolutas já cobertas) fora de I1 ⇒ `deny`;
   - regressão: `pytest backend/ -q` sem mutação ⇒ `allow`.  
   Sem rede GitHub; `status` injetado.

7. **Escopo de implementação só harness.**  
   Arquivos: `guard.py`, `test_guard.py`, `process-fsm-guard.sh`. Sem UI, sem OpenSpec de produto, sem board.

## Risks / Trade-offs

- [Shell ofuscado grava produto sem token/`tee` óbvio] → residual P2 já aceito no #611; fora do aceite #625.
- [`$TMPDIR` fora de `/tmp`, ou `>/dev/fd/3`] → não allowlist; pode deny se houver path de produto no comando — aceito; PO pediu só `/dev/null` e `/tmp`.
- [Múltiplos redirects mistos: um null e um produto] → qualquer alvo produto ⇒ deny (fail-closed).
- [Divergência Python vs bash fallback] → Decision 5 + fixture que exercita a regra (pytest no módulo Python; smoke de string no fallback se proporcional).
- [Allowlist `/tmp` usada para staging e depois `mv` para produto] → o `mv` para produto continua deny fora de I1.

## Migration Plan

Aditivo no Guard. Rollback = reverter os três paths de harness. Sem migration de banco. Sem mudança de `hooks.json`.

## Open Questions

Nenhuma bloqueante. `$TMPDIR` ≠ `/tmp` fica explicitamente fora (Non-Goal).

## UI impact

**none** — correção de classificação no Guard de shell; nenhuma tela de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. Sem superfície visual; policy de `beforeShellExecution`.

## Prototype Validation

N/A — sem protótipo.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

**Critic:** Task isolada inherit, read-only (sem editar arquivos / board / commit).  
**Fontes:** `proposal.md`, `design.md` (Decisions 1–7), `tasks.md`, `specs/process-fsm-guard/spec.md`; inspeção opcional de `scripts/process-fsm/guard.py` (`MUTATION_RE`, `_path_from_command`) e fallback `.cursor/hooks/process-fsm-guard.sh`.  
**Card / change:** #625 / `card-625-guard-null-redirect`.  
**UI impact:** none. **Prototype:** N/A — policy de hook; sem superfície visual. **Impeccable Brief/Critique/Audit/Trace:** N/A — `UI impact: none`.

### Achados por dimensão

- **Escopo:** Change limitada a classificação shell no Guard (Python + fallback bash) e fixtures. Sem UI, board, `hooks.json`, `process_event`, `product_globs`. Coerente com aceite e Non-Goals.
- **Regressão de produto / segurança do deny:** Decisão correta: classificar pelo **alvo** de redirect/`tee`, não por path citado. Allowlist `/dev/null` e sob `/tmp`; qualquer alvo em `product_globs` fora de I1 permanece deny; redirects mistos fail-closed. Mutações não-redirect inalteradas.
- **Confirmação UI:** Nenhuma tela/protótipo; Prototype Validation N/A justificado.
- **Riscos operacionais (não bloqueantes):** (1) Implementação MUST allowlistar o destino bruto antes do match/`repo_relative` que hoje promove `/tmp/.../backend/...` a produto. (2) Ajustar fixture `extract_path` de `tee /tmp/repo/backend/...`. (3) Residuais `$TMPDIR` / ofuscação / `&>` fora do aceite — já documentados.

### Pendências aceitas (P2)

Ordem allowlist-antes-remap; sync do assert `extract_path`; residual Non-Goals.

**Design Agent verdict: PASS**
