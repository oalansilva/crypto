# AGENTS.md — Guia rápido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## TL;DR

- **Branch padrão:** trabalhe em `feature/long-change` (evite commits diretos na `main`).
- **Fluxo OpenSpec ("Criar Funcionalidade"):** Proposal → validate → Alan: **Go** → implementar → testes → push → **deploy na VPS (stop/start backend+frontend)** → validar URLs → (opcional) archive.
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
