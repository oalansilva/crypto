## Why

Card #416 ficou com título divergente no board ("Substituir gpt-5.6-luna por MiMo-V2.5") vs issue ("…Qwen3.7 Plus") vs implementação (`qwen3.7-plus`) (F-3); e após o merge que trocou o modelo do vision, spawns ainda usaram o modelo antigo porque a configuração é lida no spawn a partir da sessão/worktree antiga (F-4).

## What Changes

- Regra de fechamento: título do board == título da issue no momento do `Done` (ou comentário registrando divergência aprovada).
- Documentação: mudança de modelo de subagent exige nova sessão; auditoria kaizen adiciona sinal "modelo antigo pós-merge" nas sessões da release.

## Capabilities

### New Capabilities

- `board-issue-title-sync`: sincronização obrigatória de título board/issue no fechamento de card.

### Modified Capabilities

- `multiagent-operating-standard`: troca de modelo de subagent exige sessão nova; sessões/spawns em voo permanecem no modelo antigo.
- `kaizen-continuous-improvement`: a auditoria detecta o sinal "modelo antigo pós-merge" nas sessões da release.

## Impact

- `AGENTS.md`/`rules.md` (regra de fechamento e documentação de modelo).
- Subagent `kaizen` (`.opencode/agent/kaizen.md`): novo sinal de auditoria.
- Sem mudanças de runtime, banco ou frontend.
