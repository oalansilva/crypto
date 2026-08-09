# Design — card-422-release-guard-prod-deploy-orphan-refs

## Context

A release 2026-08-08 foi inicialmente fechada com cards em `Pronto` sem deploy em PROD (F-7), e refs de releases anteriores permanecem sem classificação (F-5: `runtime-card-362-develop`, `rollback-card-362-369`, `runtime-develop-card369`, `release-post-20260802`, `sync-main-into-develop-20260803`, `release-20260803-cards-366-374`) além de worktrees `preserve/*` com WIP não commitado. O guard atual não detecta nenhum dos dois estados.

## Escopo

- `release-guard pre`: check de evidência de deploy PROD antes de liberar `Pronto` (commit publicado no source PROD + services reiniciados + URL pública validada).
- `release-guard post`: inventário de refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*` e worktrees `preserve/*` com exigência de classificação e sinalização de WIP não commitado.
- Docs/AGENTS atualizados conforme necessário.
- Fora de escopo: limpeza automática de refs (exige autorização humana por card/ref).

## UI impact

`UI impact: none` — script bash de guard de release; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — Evidência de deploy PROD como variáveis de ambiente/arquivo de evidência no fechamento.** O guard `pre` verifica a existência de evidência registrada (ex.: commit PROD + serviços + URL validada documentados no pacote/ambiente) antes de liberar `Pronto`; em modo estrito, ausência = blocker. Alternativa (inspeção remota do source PROD via SSH) mais frágil: depende de credenciais e rede do guard.
- **D2 — Inventário no `post` como blocker estrito, não auto-limpeza.** Refs/worktrees órfãs e WIP não commitado são listados com instrução de classificação (integrar/preservar/limpar com autorização); a limpeza permanece manual/humana. Alternativa (auto-delete) rejeitada por risco de perda de conteúdo não classificado.
- **D3 — Sinalização de WIP não commitado via `git status --porcelain` nas worktrees `preserve/*`.** Reutiliza lógica existente do guard (`dirty worktree`) sem nova dependência.

## Riscos

- [Falso blocker por evidência mal formatada] → Mitigação: aceitar formato simples e documentado (commit PROD publicado + services reiniciados + URL validada), validado na próxima release.
- [Refs legítimas não órfãs marcadas como órfã] → Mitigação: classificação exigida (não auto-exclusão); guard apenas sinaliza e aguarda decisão humana.

## Design Critique

- **Escopo**: fecha os dois gaps de evidência da auditoria 08-08 (deploy PROD e refs órfãs) sem introduzir limpeza automática perigosa.
- **Regressão de produto**: nenhuma — guard é ferramenta de processo.
- **Riscos operacionais**: guard `pre` mais estrito pode bloquear fechamentos sem evidência; mitigado pela documentação do fluxo de deploy obrigatório e pela classificação manual.
- **Pendências não bloqueantes**: refs antigas já existentes serão sinalizadas no primeiro `post` — esperado e alinhado ao critério de aceite.
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
