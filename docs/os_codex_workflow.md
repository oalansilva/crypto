# Fluxo OS+Codex (OpenSpec Change Proposal → Codex CLI)

Este projeto usa o workflow oficial do OpenSpec via **changes**.

Schema atual: `spec-driven` (proposal → specs → design → tasks)

## Atalho no chat
Use: **OS+Codex: <sua feature>**

## Passo a passo (humano + agente)

### 1) Criar change
```bash
openspec new change <change_id> --schema spec-driven --description "<resumo>"
```

### 2) Preencher artefatos do change
Arquivos típicos:
- `openspec/changes/<change_id>/proposal.md`
- `openspec/changes/<change_id>/specs/**/*.md`
- `openspec/changes/<change_id>/design.md`
- `openspec/changes/<change_id>/tasks.md`

(Use `openspec instructions <artifact> --change <change_id>` para obter instruções enriquecidas.)

### 3) Validar change
```bash
openspec validate <change_id>
```

### 4) Apply (implementação)
- Implementar tasks do `tasks.md`.
- Rodar testes.

Com wrapper (change-driven):
- o wrapper valida o change
- busca as tasks via `openspec instructions apply --change <change_id> --json`
- falha se não houver tasks
- injeta no prompt do Codex o contexto completo do change: `proposal.md`, `design.md`, `specs/**/*.md`, `tasks.md` (com truncamento por arquivo)

```bash
./scripts/openspec_codex_task.sh <change_id>
```

### 5) Verify
```bash
openspec validate <change_id>
./backend/.venv/bin/python -m pytest -q
```

### 6) Archive
Após deploy/teste manual OK:
```bash
openspec archive <change_id>
```

## Notas
- O wrapper OS+Codex aplica guardrails (working tree limpa, escopo de paths, testes).
- Limite de arquivos alterados default: 3 (ajustável via `MAX_FILES_CHANGED`).
- Limite de linhas alteradas está **desativado por padrão** (reative com `MAX_LINES_CHANGED=<n>`).
