## Context

Card [#631](https://github.com/oalansilva/crypto/issues/631). O Guard (`scripts/process-fsm/guard.py` + fallback `.cursor/hooks/process-fsm-guard.sh`) protege o sidecar `.design-digest` (escrito só por `process_event` T5). Hoje `sidecar_in_command` é `".design-digest" in command`: qualquer Shell que cite o nome — `git add` do archive, `git commit -m "...design-digest..."`, `git status`/`git reset` — recebe `permission: deny` sem mutar o ficheiro.

**UI impact: none.** Guard/hooks/pytest. Prototype N/A. Impeccable N/A.

Estado atual relevante:

- `board_status.sidecar_in_command` — substring ingenua
- `guard.decide` — `is_sidecar_path(path) or sidecar_in_command(command)` → `_sidecar_deny`
- fallback bash — mesmo substring em `command` antes do early-return
- testes: `test_sidecar_write_denied_in_design`, `test_python_c_sidecar_command_denied` (true deny); falta falso positivo git-cite

## Goals / Non-Goals

**Goals:**

- Deny aplica-se a `Write`/`StrReplace`/`Delete` no path do sidecar e a Shell que **muta** o sidecar.
- `git add` / `git commit` / `git status` / `git reset` que só citam o filename MUST NOT deny por substring.
- Fixtures `beforeShellExecution`: falso positivo (allow) + true deny (deny); `pytest scripts/process-fsm` verde.
- Fallback bash alinhado à mesma semântica.

**Non-Goals:**

- Alterar quem escreve o sidecar (`process_event` T5) ou o formato do digest.
- Negar/permitir `git commit`/`git push`/`./restart` como hooks de produto (permanecem out of scope do Guard de produto).
- UI, board, release, `process_event` transitions.
- Parser shell completo / AST Python — heurística determinística suficiente para os padrões do PO.

## Decisions

1. **Substituir substring por detecção path-aware de mutação.**  
   Alternativa A: manter substring e allowlist `^git ` — frágil (`git ... && python -c open(...w...)`).  
   Alternativa B (escolhida): se `command` contém `.design-digest`, negar só quando classificado como mutação do sidecar; citação pura → não aplica `_sidecar_deny`.  
   `Write`/`StrReplace`/`Delete` continuam via `is_sidecar_path(path)` (path do tool), classificado antes de `design_globs`.

2. **API: evoluir `sidecar_in_command` (ou renomear) para “mutação do sidecar”.**  
   Preferência: renomear semanticamente (`sidecar_mutation_in_command` ou equivalente) e atualizar imports em `guard.py` + testes; manter `is_sidecar_path` intacto.  
   Contrato: `False` se command vazio ou sem `.design-digest`; `True` só se mutação.

3. **Heurísticas de mutação (deny quando `.design-digest` presente e…):**  
   - redirect / `tee` com destino cujo path termina em `.design-digest` (`>`, `>>`, `tee`)  
   - `rm` / `unlink` / `shred` com argumento sidecar  
   - `cp` / `mv` / `install` com destino sidecar  
   - `sed -i` / `perl -i` sobre path sidecar  
   - `python`/`python3` `-c` que abre o sidecar em modo escrita (`'w'`/`"w"`/`'a'`/`'x'`/`'wb'` etc.) ou `Path(...).write_text` / `.write_bytes` no sidecar  
   - path extraído por `MUTATION_RE` + path ending `.design-digest` (já coberto por `is_sidecar_path` se `extract_path` devolver o path)  
   True deny pinado: fixture existente `python -c "open('.../.design-digest','w').write('x')"`.

4. **Allow (não sidecar-deny) quando só citam:**  
   Exemplos pinados em fixtures `beforeShellExecution`:  
   - `git add openspec/changes/<change>/.design-digest`  
   - `git commit -m "chore: archive .design-digest"`  
   - `git status -- openspec/changes/<change>/.design-digest`  
   - `git reset HEAD -- .../.design-digest`  
   Leituras (`cat`, `ls`, `git show`) que só citam também MUST NOT deny por esta regra.  
   Outras regras do Guard (Status item-edit, product write) permanecem independentes.

5. **Fallback bash espelha a heurística, não a substring.**  
   Remover `if ".design-digest" in command: deny` ingénuo. Aplicar a mesma classificação de mutação (stdlib no heredoc Python já usado no fallback, ou checks equivalentes). Path de tool que `endswith(".design-digest")` permanece deny.

6. **Testes no job `process-fsm` existente.**  
   - Manter true deny: Write tools + `python -c` write.  
   - Adicionar allow: pelo menos um `git add` e um `git commit`/`git status` que citam `.design-digest`.  
   - Opcional: um redirect `> .../.design-digest` como true deny adicional.  
   Sem GitHub; `status` injetado.

7. **Escopo de ficheiros.**  
   `board_status.py`, `guard.py`, `process-fsm-guard.sh`, `test_guard.py` e/ou `test_process_event.py`. Sem mudança de yaml FSM nem de paging.

## Risks / Trade-offs

- [Heurística incompleta: novo vetor `node -e` / `printf` sem `>`] → aceitar residual; padrões PO + `python -c` / redirect / rm cobrem o uso Agent atual; expandir só com fixture.
- [Falso negativo: `git add` + `&&` mutação no mesmo command] → se a mutação for detetável no mesmo string, deny; se só `git add`, allow (correto).
- [Falso positivo residual em mensagem `git commit` com redirect colado] → improvável; fixtures pinam allow de cite.
- [Fallback bash divergir do Python] → D5: mesma semântica; teste pode exercitar `decide()` (path principal); fallback documentado nas tasks.
- [Rename quebra imports externos] → só `scripts/process-fsm` + hook; grep no apply.

## Migration Plan

Aditivo no Guard. Rollback = reverter os três ficheiros + testes. Sem banco, sem deploy de produto. Hooks locais passam a permitir archive git do sidecar após merge em `develop`.

## Open Questions

Nenhuma bloqueante. Aceite PO: cite ≠ mutate.

## UI impact

**none** — correção do Guard/hook/pytest. Nenhuma tela, rota ou componente.

## Prototype

N/A — `UI impact: none`. Sem superfície visual nova ou alterada.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none` (Guard sidecar; sem superfície visual).

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit (read-only). Fontes: `proposal.md`, `design.md` (D1–D7), `tasks.md`, `specs/process-fsm-guard/spec.md`, `board_status.sidecar_in_command`, `guard.decide`, fallback bash substring. Card #631, change `card-631-guard-sidecar-git-cite`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Task id `c58734aa-2aa4-411e-8252-45b03bf09ecc` — **PASS** (P0/P1 nenhum).

### Dimensões

- **Escopo:** só Guard/hook/pytest sidecar cite-vs-mutate; `process_event` T5 e UI fora.
- **Produto / processo:** deny Write tools + Shell mutante; git cite MUST NOT deny por substring; fixtures false positive + true deny.
- **Operação:** residual heurística (`node -e`, `git restore`) e paridade fallback bash documentados; apply deve remover substring no hook.
- **UI / a11y / responsivo / estados visuais:** N/A — Guard.

### Achados

- **P0 / P1:** nenhum.
- **P2 (aceitos):** (1) task 2.1 endurecida pós-crítica para exigir fixtures `git add` + `git commit` + `git status`; (2) sem assert dedicado do fallback bash — residual, D5 + task 1.3; (3) redirect true-deny opcional; (4) falsos negativos pouco tipados (`git restore`) — expandir só com fixture.

### Pendências não bloqueantes

Apply segue D1–D6 + tasks. Board **não** movido nesta sessão (pedido explícito). Aprovação humana (`Aprovação de Design → Pronto para Dev`) permanece de Alan.

Design Agent verdict: PASS
