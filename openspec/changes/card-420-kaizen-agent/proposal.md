## Why

O projeto possui processo maduro (alan-workflow, OpenSpec, Project 1, Playwright visual, release-guard), mas nada mede nem melhora o processo em si: fricções se repetem, sessões do opencode custam caro sem chegar a `Done` e melhorias não têm trilha. Criar o papel Kaizen de melhoria contínua para que quanto mais o processo é usado, melhor ele fique.

## What Changes

- Novo subagent auditor `.opencode/agent/kaizen.md` (read-only): coleta evidências de board, Git hygiene, OpenSpec, CI, tech debt e sessões do opencode (SQL `mode=ro` em `~/.local/share/opencode/opencode.db`), detectando onde o modelo se perde ou alucina.
- Novos commands `/kaizen`, `/kaizen card <id>` e `/kaizen release` (`.opencode/commands/kaizen.md`).
- Novo `docs/kaizen-log.md`: relatório local versionado (append-only) com achados, métricas agregadas, trechos curtos de sessão e histórico de mudanças de processo.
- Label `kaizen` no repo para rastrear melhorias no Project 1.
- Regras de processo: papel Kaizen em `AGENTS.md`, regra 14 em `rules.md` (pós-release obrigatório, cards `Status=Todo`, máx. 3 cards kaizen por release, priorização P0/P1/P2, propõe/Alan aprova, segurança de output).
- Kaizen atua como PO ao registrar melhorias: 1 card por melhoria, formato `## Proposta (PO)`, campos do board preenchidos, dependências linkadas.

## Capabilities

### New Capabilities
- `kaizen-continuous-improvement`: auditoria de melhoria contínua de processo — coleta de evidências (board, Git, OpenSpec, CI, sessões), detecção de fricção/alucinação de modelo, registro em `docs/kaizen-log.md` e criação de cards kaizen no board com priorização.

### Modified Capabilities
- `developer-tooling`: adiciona os novos artefatos opencode (subagent kaizen, command `/kaizen`) ao escopo de configuração versionada de ferramenta de desenvolvimento.
- `multiagent-operating-standard`: adiciona o papel Kaizen ao modelo operacional (responsabilidades, limite de 3 cards/release, aprovação humana para mudanças).

## Impact

- `.opencode/agent/kaizen.md`, `.opencode/commands/kaizen.md`, `docs/kaizen-log.md`, `AGENTS.md`, `rules.md`.
- Board Project 1 (label `kaizen`, campo `Prioridade`, View "Kaizen" a criar manualmente no board — não automatizável via CLI).
- Sem impacto em runtime (backend/frontend) — mudança exclusiva de processo/tooling (`UI impact: none`).
