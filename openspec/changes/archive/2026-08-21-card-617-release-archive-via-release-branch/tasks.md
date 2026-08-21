# Tasks: card-617-release-archive-via-release-branch

## Design (este turno)

- [x] 0.1 OpenSpec completo (proposal, design, specs, tasks) como superset do issue #617
- [x] 0.2 Design Critique isolada + veredito PASS no `design.md`
- [x] 0.3 Publicar Gist/comentário no card #617 (após crítica PASS)

## Apply (após Pronto para Dev)

## 1. Runbook

- [x] 1.1 Atualizar `docs/crypto-overlay.md`: caminho `release-*` quando push em `develop` é recusado por proteção/`qa-gate`, mesmo com pacote só Homologado; passo obrigatório sync `main → develop` + reexecutar `post`
- [x] 1.2 Atualizar `.cursor/skills/alan-workflow/` com a mesma regra curta (apontar overlay); não dual-write playbook completo em `AGENTS.md`
- [x] 1.3 Confirmar stub `AGENTS.md` ainda aponta overlay on-demand para release

## 2. release-guard pre

- [x] 2.1 Verificar `scripts/release-guard pre` em `release-*` com archive só no HEAD e ausente em `origin/develop`; ajustar só se houver FAIL indevido (D2)
- [x] 2.2 Garantir que a saída do `pre` não prescribe “publique archive em develop primeiro”
- [x] 2.3 Não expandir escopo ao #618 (ref local `develop`)

## 3. Evidência

- [x] 3.1 Registrar evidência: `pre` PASS no cenário archive-via-`release-*` sem archive em `origin/develop` → `evidence-apply.md`
- [x] 3.2 Registrar que o runbook cita sync `main → develop` e reexecução do `post` após sync
- [x] 3.3 `openspec validate --change card-617-release-archive-via-release-branch` (ou escopo equivalente) verde
