# AGENTS.md — always-on curto

Board: https://github.com/users/oalansilva/projects/1

Resolva `(q, bound_card, q_git)`; não invente aresta.
Chat é wording, não autorização. NLU ≠ δ. `implemente` ∉ δ.
`Em Refinamento` é a entrada. Não pular Design / Aprovação de Design.
`Todo` não é código; próxima = `iniciar_design` via `process_event`.
Código / `/opsx:apply` só após `Status=Pronto para Dev` (T8).
Alan único em T1/T7/T15. Agent não arrasta essas colunas. T16 = `process_event fechar_release`.
Clientes: Cursor Agent (Auto permitido); Grok Build e OpenCode (cooperativos até ensaio deny na `develop`).
Skills canônicas: `.cursor/skills/` neste repo. Overlay on-demand; runbook = skill `alan-workflow`; lei = `rules.md`.

Quando a tarefa precisar de portas/URLs, Drive, PostgreSQL ou release/lote/PROD:

`Read docs/crypto-overlay.md`

Fora desses tópicos, não carregue o overlay.

PostgreSQL obrigatório (`DATABASE_URL`). Não usar SQLite em runtime/QA.
