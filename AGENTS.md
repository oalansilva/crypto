# AGENTS.md — Guia rápido para operação local neste repo

Este arquivo organiza o fluxo de trabalho para evitar retrabalho e manter padrão operacional no repo.

## TL;DR

- **Branch padrão:** trabalhe direto em `main` para mudanças de rotina.
- **Fluxo simplificado:** implemente, valide e confirme; se quiser revisão formal, abra PR `main <- feature/<nome>` e merge no mesmo repositório antes de fechar.
- **Referência operacional:** `docs/workflow-criar-funcionalidade.md`.
- `docs/workflow-criar-funcionalidade.md` define onde registrar decisão e evidência por change (via PR e resumo no chat).
- OpenSpec é a camada de especificação técnico (artifacts).
- Validação humana final permanece com Alan antes de homologação.

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

## Convenções de UI/UX

- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs, limites e risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Regras de operação

- Fluxo único (sem divisão por agentes): você conduz descoberta, planejamento, implementação, validação e fechamento.
- Registre em `docs/workflow-criar-funcionalidade.md` e no PR:
  - status atual
  - decisões de escopo
  - evidências de teste/PR
- Para promover produção, trabalhe em `main` e abra PR de revisão se quiser validação externa.

## Ferramentas

- **QA UI/browser:** preferir Microsoft Playwright CLI (`playwright-cli`) em vez de MCP.
- Para interfaces com evidência visual, usar `/usr/local/bin/playwright-cli-headed` no fluxo de captura.
- Use `skills/playwright-cli-official/` e `skills/interface-design-codex/` como referência.
