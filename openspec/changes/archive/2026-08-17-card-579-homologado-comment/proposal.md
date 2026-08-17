# Proposal: card-579-homologado-comment

## Why

Na release 2026-08-17 o F-2 registrou cards Homologados sem comentário canônico até o closeout. No lote 2 do mesmo dia os 8 cards (#529/#530/#531/#553/#554/#566/#567/#568) chegaram de novo em Homologado sem o helper; o closeout postou retroativo. Recidiva no mesmo dia. O helper `scripts/post-card-evidence-comment.sh --transition homologado` já existe e deduplica; o agente não o chama no turno do arraste e o `release-guard pre` não falha por ausência.

## What Changes

- Processo: no mesmo turno em que o card entra em `Status=Homologado` (arraste de Alan ou confirmação em chat), o agente SHALL rodar o helper **antes** de qualquer ação de lote/release.
- Guard: `pre` verifica o comentário canônico quando `RELEASE_CARDS` está setado, via REST de comments (sem GraphQL/`item-list`). Falha do helper ou comentário ausente bloqueia o closeout; não esperar o `post`.
- Docs: `AGENTS.md` (e skill `alan-workflow` quando #585 aplicar) deixa explícito: arraste Homologado ⇒ helper no mesmo turno.

## UI impact

`none` — processo, `scripts/release-guard`, docs. Sem superfície visual do produto.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `release-worktree-hygiene`: `pre` passa a checar comentário canônico de homologação quando `RELEASE_CARDS` está setado.
- `card-close-evidence-integrity`: obriga o helper no mesmo turno do arraste/confirmação Homologado.

## Impact

`scripts/release-guard`, `scripts/post-card-evidence-comment.sh` (sem mudar o texto canônico), `AGENTS.md`. Sem webhook GitHub. Sem UI.
