## Regra operacional deste workspace

- O agente DEV deve implementar código via Codex usando ACP como canal operacional padrão.
- O acesso direto via `acpx` é o caminho preferencial do DEV; `scripts/dev-via-acpx.sh` é opcional.
- Usar sessão nomeada por work item: `dev-change-<id>`, `dev-story-<id>`, `dev-bug-<id>`.
- A permissão padrão operacional deve ser `approve-all` para evitar bloqueios em sessões não interativas.
- Desvios desse fluxo só devem ocorrer com justificativa explícita registrada no runtime/Kanban.
