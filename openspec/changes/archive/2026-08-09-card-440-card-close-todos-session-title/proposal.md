## Why

Sessão "Casual greeting" com 4.1M tokens ($0.38) sem título descritivo (F-4), e reincidência (2ª auditoria) de todos `in_progress` eternos (card-399) e comentário OpenSpec duplicado no card #413/#385 (família #423, F-5). A evidência operacional não é íntegra/auditável sem esses fechamentos.

## What Changes

- `/opsx:verify`/Done exige todos `completed` (0 todos `in_progress`/`pending` em sessões de cards Done).
- Helper `publish-openspec-card-artifacts` atualiza gist/comentário existente em vez de republicar (sinergia com #423).
- Sessões com custo > $0.10 têm título descritivo (card/contexto).
- Elevar #423 de P2 para P1.

## Capabilities

### New Capabilities

- `card-close-evidence-integrity`: fechamento de card exige todos completed e título de sessão descritivo em sessões caras.

### Modified Capabilities

- `kaizen-continuous-improvement`: a auditoria valida todos completos em sessões de cards Done e títulos descritivos em sessões caras.
- `developer-tooling`: `/opsx:verify` valida todos completos; helper atualiza gist/comentário existente.

## Impact

- Fluxo `/opsx:verify`/`/opsx:apply` (skills OpenSpec), subagent `kaizen`.
- Helper `publish-openspec-card-artifacts.sh`.
- Board: prioridade do card #423 elevada a P1 (ação de PO).
- Sem mudanças de runtime, banco ou frontend.
