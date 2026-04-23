# AGENTS.md — Guia rápido para agentes (e humanos) neste repo

Este arquivo existe para reduzir retrabalho e evitar mudanças fora de escopo.

## TL;DR

- **Branch padrão:** trabalhe em `develop` para trabalho diário de implementação e validações.
- **Fluxo de produção:** implemente e valide diretamente em `develop`; para liberar produção, abra PR `develop -> main`.
- **Regra de fluxo:** use somente `develop` e `main`; sem criação de branches por tasks usuais.
- **Banco padrão:** PostgreSQL é obrigatório em runtime, QA e scripts operacionais (`DATABASE_URL` e `WORKFLOW_DATABASE_URL` em formato PostgreSQL).
- **Não usar SQLite** como banco de operação. Em runtime/QA/Homologação, use apenas PostgreSQL (`DATABASE_URL` e `WORKFLOW_DATABASE_URL`).
- OpenSpec é a camada de especificação técnico (artifacts).
- Workflow DB e OpenSpec são fontes de operação e evidência.

## Fluxo Git operacional (sempre)

- Trabalhe sempre em `develop`; não crie `feature/*`, `bugfix/*` ou outras branches para tarefas isoladas.
- Commite cada ajuste em `develop`.
- Abra PR de `develop` para `main` para liberar produção.
- O merge em `main` é o passo final e de homologação da mudança.
- Após merge em `main`, atualize `develop` para refletir o estado da produção.

Exemplo mínimo:
```bash
git switch develop
git pull
# ...alterações locais...
git add .
git commit -m "feat: descrição da mudança"
git push
gh pr create --base main --head develop --title "..."

# após merge:
git pull
```

Checklist de rotina (diária/por mudança):

1. `git switch develop`
2. `git pull`
3. aplicar alteração
4. `git add .`
5. `git commit -m "tipo: mensagem"`
6. `git push`
7. `gh pr create --base main --head develop --title "<titulo>" --body "descricao breve"`
8. Mescle o PR em `main` (passo final da mudança).
9. Após merge: `git pull`

Padrão de commit recomendado:
- `feat: adicionar fluxo de merge develop->main`
- `fix: corrigir validação de entrada no endpoint de backtest`
- `chore: atualizar documentação e scripts de desenvolvimento`
- `refactor: simplificar regra de configuração`
- `docs: registrar padrão operacional no AGENTS`

## Regras de operação

- Fluxo único (sem divisão por agentes): você conduz descoberta, planejamento, implementação, validação e fechamento.
- Registre em `openspec/changes/<change>/` e no PR:
  - status atual
  - decisões de escopo
  - evidências de teste/PR
- Para promover produção, trabalhe em `develop` (sem branch extra) e abra PR de `develop -> main`.

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
- Workflow OpenSpec/Codex: `openspec/changes/` e `openspec/specs/`

## Convenções de UI/UX (Lab)

- **Upstream** deve ser uma conversa fluida (Humano ↔ Trader) para clarificar inputs/constraints/risco.
- O label "validator" na UI/copy deve aparecer como **Trader**.

## Agentes e responsabilidades

O time é composto por 5 agentes, cada um com papel definido:

### main — Project Manager / Team Leader
**Template base:** Orion (productivity)

Orquestra o time, coordena workflow, delegation, status reports, prazos.
- Mantém conversa com Alan curta/gerencial
- Consulte workflow DB e OpenSpec como fonte principal.
- Move status de mudança no workflow, celebra marcos, identifica riscos proativamente
- Fornece próximo passo após completar tarefa
- Pede clarifying questions quando necessário
- Dá estimates de tempo quando possível

### PO — Product Manager
Define especificações, gerencia backlog, Requirements, escopo do produto.
- Define taxonomia de work items (`change`, `story`, `bug`) e dependências
- É dono dos artefatos OpenSpec da change: `proposal.md`, `specs/**`, `design.md`, `tasks.md` e `review-ptbr.md`
- Só libera DEV depois de approval
- **Quando não há change ativa (todas arquivadas), o PO deve puxar a change de maior prioridade no status `Pending` para iniciar planejamento no próximo turno.**

### DESIGN — UX/UI Researcher
**Template base:** UX Researcher (creative)

Foca em UX/prototipação e pesquisa de usuário.
- Publica protótipos e decisões visuais na seção de handoff da change
- Complementa a planning package com protótipo visual e decisões de UX para DEV/QA
- Desenha pesquisas de usuário e scripts de entrevista
- Analisa feedback de usuários (tickets, reviews, pesquisas)
- Identifica problemas de usabilidade
- Gera relatórios com recomendações baseadas em evidências

### DEV — Software Engineer + Code Reviewer
**Template base:** Lens (development)

Implementa código +レビュー automática.
- Implementa com base no workflow DB + notas de handoff como runtime
- Respeita taxonomia `change`/`story`/`bug`, ownership, locks e dependências
- Faz code review: bugs, security issues, logic errors
- Scaneia vulnerabilidades (SQL injection, XSS, hardcoded secrets)
- Avalia qualidade (A-F), sugere melhorias

### QA — Tester + Bug Hunter
**Template base:** Trace (development)

Valida + análise profunda de bugs.
- Valida regressões, consistência do workflow DB e critérios de aceite
- Bugs reais viram `bug` rastreável; bugs filhos bloqueiam story
- Análise de erro: parse stack traces, identifica root cause vs symptoms
- Fornece steps de debug em ordem de probabilidade
- Cria bug reports com steps de reprodução e severidade

### Regras operacionais dos agentes
- O **workflow DB** é a fonte operacional de verdade.
- **OpenSpec** define artefatos e a trilha técnica.
- `openspec/changes/<change>/` é o canal padrão entre agentes, com menções `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`.
- Nenhum agente (PO/DESIGN/DEV/QA) pode considerar sua etapa concluída só com artefatos; é obrigatório atualizar o runtime e registrar handoff no mesmo turno.
- Toda etapa só fecha de verdade com **runtime + handoff registrado**; se um dos dois faltar, o próximo turno deve reconciliar antes de seguir.
- O contrato operacional curto (papéis, handoff, DoD por status, bloqueios) fica consolidado no fluxo operacional do projeto.
- Quando Alan homologar uma change em chat, o orquestrador deve fechar e arquivar no mesmo turno (runtime + OpenSpec + handoff), sem pendência operacional.
- `change` é o container raiz da entrega; `story` é a fatia padrão de execução quando houver ownership/dependência própria; `bug` representa defeito real. Não criar cards separados para micro-passos sem necessidade operacional.
- Múltiplas stories/agentes podem trabalhar em paralelo, desde que respeitem **locks**, **dependências** e **WIP**.
- Regra prática de WIP: por padrão, no máximo **2 stories ativas por change** e **1 story ativa por agent run**.
- **Regra de auto-trigger:** Quando o status da change avança no runtime, o agente responsável pela nova etapa deve ser acionado. Ex: status vira PO → acionar PO; vira DEV → acionar DEV; vira QA → acionar QA.
- **Regra de validação QA:** Antes de enviar para homologação Alan, QA deve rodar testes E2E (`frontend/tests/*.spec.ts`) e revisar evidências registradas no fluxo operacional.
- Lock padrão fica no nível da **story**; bug filho herda esse lock salvo reassignment explícito.
- Uma **story** só pode ser fechada quando todos os **bugs filhos** estiverem concluídos.
- Antes de promover para `QA`, `Homologation` ou `Archived`, reconciliar runtime + `openspec/changes/<change>/tasks.md` + handoff.

## Engenharia de prompt

Se for necessário mudar o tom de um agente (ex: deixar o design mais exploratório ou o DEV mais cauteloso), primeiro atualiza este arquivo com o novo prompt/personalidade e registra no `openspec/changes/<change>/` do fluxo ativo. Nunca altere agentes apenas via jobs sem documentar aqui.
