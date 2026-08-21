# AGENTS.md — stub (não always-on)

Este arquivo **não** é o playbook de 12 colunas nem o closeout de release.

Board: https://github.com/users/oalansilva/projects/1

Quando a tarefa precisar de portas/URLs, Drive, PostgreSQL ou release/lote/PROD:

`Read docs/crypto-overlay.md`

Fora desses tópicos, não carregue o overlay.

PostgreSQL obrigatório (`DATABASE_URL`). Não usar SQLite em runtime/QA.

Cliente: Cursor Agent. Skills: `.cursor/skills/` neste repo.
