# Coordination / Change Notes

This folder stores lightweight coordination notes for each OpenSpec change.

Notas de execução atual ficam em `docs/coordination/<change>.md`.
Notas históricas e fechadas foram movidas para `docs/coordination/archive/`.

## Why

Use estes arquivos para manter a trilha de decisão, estado e evidências fora do chat, de forma versionada.

## Rules

- Se o dado importa para trabalho ativo, registre em `openspec` ou em `docs/coordination/<change>.md`.
- Mantenha arquivos curtos, objetivos e atualizados.
- Prefira links de evidência (PR, CI, OpenSpec viewer, testes) em vez de logs longos no texto.
- O fluxo vivo hoje é: OpenSpec + nota em `docs/coordination/<change>.md` + GitHub PR/Merge.

### Fluxo operacional (solista)

- Você conduz discovery, planejamento, implementação, validação e encerramento.
- Atualize o status do change no `docs/coordination/<change>.md` a cada avanço relevante.
- Registre decisões de escopo, risco, limitações e "what changed" no resumo.

### Comunicação com Alan

- Encaminhe apenas ações necessárias de decisão, bloqueio ou aprovação final.
- Use formato mínimo:
  - `Status`: pass / blocked / needs-review
  - `Próximo passo`: dono e ação
  - `Evidência`: PR/CI/links

### Arquivos ativos

Use um arquivo por change:

- `docs/coordination/<change-name>.md`

Arquivos de referência histórica:

- `docs/coordination/archive`

Template padrão em `docs/coordination/template.md`.
