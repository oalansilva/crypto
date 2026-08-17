## Why

A skill global `alan-workflow-ambientes` ainda trata OpenClaw (`openclaw-gateway.service`, porta 18789) como runtime ativo e descreve um mapa DEV/PROD incompleto (portas, workers, timers e Hermes). Agentes que carregam a skill operam contra topologia falsa: restart errado, PROD mutável demais e OpenClaw como alvo.

## What Changes

- Reescrever o mapa da skill para a topologia real do Oracle: Cripto DEV/PROD, Clara DEV/PROD e Hermes (Telegram, SemParar, Clara DEV API, dashboard, Second Brain).
- OpenClaw sai do runtime ativo e fica só como histórico classificado.
- Matriz de restart: fechamento DEV usa `./restart` canônico; validação intermediária pode ser direcionada; restart Hermes é por componente.
- Mutação em PROD permanece fail-closed e só com autorização explícita de Alan.
- Runbook de release PROD exige inventário, SHA, migrations, build, services, URL pública e evidência.
- Caminhos temporários só são removidos com autorização explícita.
- Smoke read-only valida units, portas e URLs sem expor secrets.

## Capabilities

### New Capabilities

- `oracle-environment-map`: contrato da skill de ambientes (DEV/PROD/Hermes, ports, services, restart, fail-closed em PROD).

### Modified Capabilities

- `developer-tooling`: a skill global de ambientes deixa de mandar OpenClaw e passa a mandar Hermes + mapa real.
- `cursor-harness`: o harness Cursor carrega a skill de ambientes atualizada, sem gateway OpenClaw.

## Impact

- Skill global: `~/.codex/skills/alan-workflow-ambientes/SKILL.md` (e espelhos Cursor/opencode se existirem).
- Docs do repo: `AGENTS.md` só se ainda apontar OpenClaw como runtime ativo de ambientes; sem mudança de produto.
- Sem alteração de API, UI ou banco.
