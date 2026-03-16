# AGENTS.md — Guia rápido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## TL;DR

- **Branch padrão:** trabalhe em `feature/long-change` (evite commits diretos na `main`).
- **Fluxo operacional atual:** Workflow DB/Postgres = fonte runtime; Kanban = interface principal; OpenSpec = artefatos/documentação.
- **Legado proibido para operação ativa:** não usar `docs/coordination/*.md` como superfície operacional para tracking ativo, evidências de QA, handoffs ou progresso corrente; tratar esses arquivos como espelho/auditoria e usar workflow DB + Kanban comments/work items como superfície viva, com OpenSpec como camada de artefatos.
- **Playbook operacional canônico (Phase 1):** seguir `docs/multiagent-operating-playbook.md` para responsabilidades por papel, contrato padrão de handoff, Definition of Done por coluna e regra de fechamento com runtime + handoff.
- **Criação de change:** use `scripts/create_change_and_seed.sh <change-name>` para garantir OpenSpec + coordination + workflow DB/Kanban no mesmo passo.
- **QA UI/browser:** preferir **Microsoft Playwright CLI** (`playwright-cli`) em vez de MCP para automação de interface; usar como base a skill oficial local `skills/playwright-cli-official/`; salvar evidências por fluxo (screenshots e, quando útil, trace/video), registrar os caminhos/links no card/tracking e abrir work item do tipo `bug` quando houver problema real.
- **Gates:** PO → DESIGN (quando UI) → Alan approval → DEV → QA → Alan homologation → archive.
- **Testes UI/E2E:** QA é o dono da validação; Playwright é a ferramenta principal de automação; Codex CLI entra como apoio para escrever/ajustar/depurar/rodar os testes, sem substituir a decisão de QA.
- **Design de interface em Codex CLI:** usar `skills/interface-design-codex/` como referência padrão para trabalho de DESIGN e apoio de revisão visual.
- **Playwright headed neste servidor:** preferir `/usr/local/bin/playwright-cli-headed` e um único `run-code` com `goto + interações + screenshot` no mesmo fluxo.
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
- **PO:** define escopo, taxonomia de work items (`change`, `story`, `bug`) e dependências. Só libera DEV depois de approval. **Quando não há change ativa (todas arquivadas), o PO deve puxar automaticamente o card de maior prioridade da coluna Pending para iniciar o planejamento no próximo turno.**
- **DEV:** implementa com base no workflow DB/Kanban como runtime. Respeita taxonomia `change`/`story`/`bug`, ownership, locks e dependências; só paraleliza quando o work item permitir com isolamento claro.
- **QA:** valida regressões, consistência do workflow DB/Kanban e critérios de aceite; bugs reais devem virar `bug` rastreável e bugs filhos bloqueiam o fechamento da story.

### Regras operacionais dos agentes
- O **Kanban** é o hub principal de consulta e handoff.
- O **workflow DB** é a fonte operacional de verdade.
- **OpenSpec** serve como camada de artefatos/documentação.
- `docs/coordination/*.md` é espelho/auditoria; se divergir do runtime/Kanban, vence o runtime/Kanban.
- Comentários do Kanban são o canal padrão entre agentes, com menções `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`.
- Nenhum agente (PO/DESIGN/DEV/QA) pode considerar sua etapa concluída só com OpenSpec/arquivos; é obrigatório atualizar o runtime/Kanban e deixar comentário de handoff no mesmo turno.
- Toda etapa só fecha de verdade com **runtime + handoff**; se um dos dois faltar, o próximo turno deve reconciliar antes de seguir.
- O contrato operacional curto (papéis, handoff, DoD por coluna, bloqueios) fica consolidado em `docs/multiagent-operating-playbook.md`.
- Quando Alan homologar uma change em chat, o orquestrador deve fechar e arquivar no mesmo turno (runtime/Kanban + OpenSpec), sem deixar pendência operacional.
- `change` é o container raiz da entrega; `story` é a fatia padrão de execução quando houver ownership/dependência própria; `bug` representa defeito real. Não criar cards separados para micro-passos sem necessidade operacional.
- Múltiplas stories/agentes podem trabalhar em paralelo, desde que respeitem **locks**, **dependências** e **WIP**.
- Regra prática de WIP: por padrão, no máximo **2 stories ativas por change** e **1 story ativa por agent run**.
- **Regra de auto-trigger:** Quando um card muda de coluna, o agente responsável pela nova etapa deve ser automaticamente acionado. Ex: card vai para PO → acionar PO; vai para DEV → acionar DEV; vai para QA → acionar QA.
- Lock padrão fica no nível da **story**; bug filho herda esse lock salvo reassignment explícito.
- Uma **story** só pode ser fechada quando todos os **bugs filhos** estiverem concluídos.
- Antes de promover para `QA`, `Alan homologation` ou `Archived`, reconciliar runtime/Kanban + `tasks.md` + handoff; para archive, preferir `scripts/archive_change_safe.sh`.

## Engenharia de prompt

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no Kanban. Nunca altere agentes apenas via jobs sem documentar aqui.
