# AGENTS.md — Guia rápido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## TL;DR

- **Branch padrão:** trabalhe em `feature/long-change` (evite commits diretos na `main`).
- **Fluxo operacional atual:** Workflow DB/Postgres = fonte runtime; Kanban = interface principal; OpenSpec = artefatos/documentação.
- **Criação de change:** use `scripts/create_change_and_seed.sh <change-name>` para garantir OpenSpec + coordination + workflow DB/Kanban no mesmo passo.
- **Gates:** PO → DESIGN (quando UI) → Alan approval → DEV → QA → Alan homologation → archive.
- **Escopo de mudanças:** prefira mexer apenas em `backend/`, `frontend/`, `src/`, `tests/`, `openspec/`.

## Como rodar (VPS / dev)

### Backend (FastAPI)
- Porta padrão: **8003**
- Logs (quando usamos nohup): `/tmp/uvicorn-8003.log`

Exemplo:
```bash
cd backend
nohup ../backend/.venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn-8003.log 2>&1 &
```

### Frontend (Vite)
- Porta padrão: **5173**
- Logs (quando usamos nohup): `/tmp/vite-5173.log`

Exemplo:
```bash
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/vite-5173.log 2>&1 &
```

## Testes / checks

- Backend:
```bash
./backend/.venv/bin/python -m pytest -q
```

- Frontend build:
```bash
npm --prefix frontend run build
```

## Documentos úteis

- Visão geral: `README.md`
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Workflow OpenSpec/Codex: `docs/os_codex_workflow.md`

## Convenções de UI/UX (Lab)

- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs/constraints/risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Agentes e responsabilidades

O orquestrador controla cinco agentes virtuais (main, design, PO, DEV, QA). Cada um segue uma persona clara:

- **main:** orquestrador. Mantém a conversa com Alan curta/gerencial, consulta Kanban como fonte principal e aciona os demais agentes. Não deve virar a fonte de verdade do processo.
- **design:** foca em UX/prototipação. Publica protótipos e decisões visuais no Kanban/artefatos, especialmente quando houver UI.
- **PO:** define escopo, taxonomia de work items (`change`, `story`, `bug`) e dependências. Só libera DEV depois de approval.
- **DEV:** implementa com base no workflow DB/Kanban como runtime. Respeita locks/dependências e pode trabalhar em paralelo com outros agentes quando o work item permitir.
- **QA:** valida regressões, consistência do workflow DB/Kanban e critérios de aceite; bugs filhos bloqueiam o fechamento da story.

### Regras operacionais dos agentes
- O **Kanban** é o hub principal de consulta e handoff.
- O **workflow DB** é a fonte operacional de verdade.
- **OpenSpec** serve como camada de artefatos/documentação.
- Comentários do Kanban são o canal padrão entre agentes, com menções `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`.
- Múltiplas stories/agentes podem trabalhar em paralelo, desde que respeitem **locks**, **dependências** e **WIP**.
- Uma **story** só pode ser fechada quando todos os **bugs filhos** estiverem concluídos.

## Engenharia de prompt

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no Kanban. Nunca altere agentes apenas via jobs sem documentar aqui.
