# Workflow: Criar Funcionalidade (CX)

Este documento descreve o fluxo padrão para criar funcionalidades no projeto **crypto** usando OpenSpec + Codex, com **gate obrigatório de testes** para reduzir dependência de validação manual.

## Regras Globais

### Definition of Done (DoD)
Uma change só é considerada **Done** quando:
- CI está **verde**
- QA validou critérios de aceitação e atualizou/criou testes necessários
- Alan homologou (UI/fluxo real)
- Change foi arquivada no OpenSpec

Regra operacional de stage: uma etapa intermediária só conta como concluída quando o runtime/Kanban foi atualizado **e** o handoff correspondente foi publicado no card no mesmo turno.

### Regras de qualidade (obrigatórias)
- Mudou schema de DB? Deve ter migração (SQLite `ALTER TABLE`/startup migration) + teste de integração.
- Endpoints de UI devem ter limites e não podem fazer backfill histórico gigante por padrão (ex: candles sempre bounded por `timeframe+limit`).
- Qualquer endpoint novo/alterado deve ter pelo menos 1 **teste de contrato** (integration) validando status + schema mínimo.
- Tasks devem ser pequenas (ideal 30–90 min) para permitir execução em turnos.

### Políticas operacionais
- Merge: padrão é **merge commit** (preserva rastreio). Squash só quando explicitamente desejado.
- Deploy: produção = `main` (deploy via `./stop.sh` + `./start.sh`).
- Rollback: se quebrou produção, preferir **revert no main** primeiro.

1) **Nunca iniciar planning se existir change aberta (não arquivada)**
- Antes de criar uma nova change, liste as changes e arquive as pendentes.

2) **Artefatos de change em inglês**
- `proposal/specs/design/tasks` sempre em inglês.

3) **Trabalhar em branch**
- Evitar commitar direto no `main`.

4) **UI é validada pelo Alan**
- O bot não “aprova” UI sozinho.

5) **Testing é parte do DoD**
- Para cada change, adicionar/atualizar testes conforme `docs/testing-playbook.md`.

## Papéis (multi-agente)

- **Alan (Stakeholder)**: valida a ideia (antes) e homologa o final (depois).
- **main**: mantém o chat gerencial e consulta Kanban/runtime como superfície principal.
- **PO**: discovery, escopo/restrições, critérios de aceitação, artefatos OpenSpec (EN) + `review-ptbr.md`.
- **DESIGN**: quando houver UI/UX, protótipo, decisões visuais e notas de aceite para DEV/QA.
- **DEV**: implementação + commits/PR/merge/deploy.
- **QA**: testes (unit/integration/E2E), valida critérios de aceitação, garante CI verde. **Tudo passa por QA.**

Contrato operacional curto por papel, handoff padrão e DoD por coluna: `docs/multiagent-operating-playbook.md`.

## Passo a passo

### 0) Pré-check

- Verificar changes abertas:
  - `openspec list --json`
  - Se existir change aberta, **arquivar antes** de criar outra.
- Verificar branch e working tree:
  - `git branch --show-current`
  - `git status --porcelain` (deve estar vazio)

### 1) Criar o Kanban da change (obrigatório)

- Criar `docs/coordination/<change-name>.md` usando `docs/coordination/template.md`.
- Preencher o mínimo: Status + Links do viewer + Next actions.

### 2) Criar a change

- `openspec new change <change-name>`

### 3) Discovery (PO) — perguntas e decisões (obrigatório)

O PO deve fechar (por escrito) antes do planning:
- objetivo
- defaults
- regras
- escopo e não-escopo
- performance/limites (ex: candles limit)
- persistência (backend/local)
- critérios de aceitação

Registrar no kanban `docs/coordination/<change-name>.md` em "Decisions (locked)".

### 4) Planning (sem Codex)

Gerar instruções e escrever os artefatos:

- Proposal:
  - `openspec instructions proposal --change <change-name>` → `proposal.md`
- Specs:
  - `openspec instructions specs --change <change-name>` → `specs/<capability>/spec.md`
- Design:
  - `openspec instructions design --change <change-name>` → `design.md`
- Tasks:
  - `openspec instructions tasks --change <change-name>` → `tasks.md`

### 5) Validar a change

- `openspec validate <change-name> --type change`

### 6) Aprovação do PO (antes do Alan)

- PO revisa os artefatos, garante que decisões e critérios de aceitação estão travados.
- PO atualiza o kanban (`docs/coordination/<change>.md`) marcando PO como **done**.

### 7) Revisão do Alan (antes de implementar)

Enviar links do viewer do OpenSpec e aguardar o “ok” do Alan.

**Camada de revisão PT-BR (obrigatória):**
- Enviar um resumo curto em PT-BR no chat.
- Criar o arquivo **não-canônico** `openspec/changes/<change-name>/review-ptbr.md`.
- Incluir também o link do viewer para esse resumo PT-BR.

Viewer (exemplos):
- Proposal: `http://72.60.150.140:5173/openspec/changes/<change-name>/proposal`
- Review PT-BR: `http://72.60.150.140:5173/openspec/changes/<change-name>/review-ptbr`

> Importante: usar sempre o prefixo `/openspec/changes/`. O artifact `review-ptbr` precisa estar allowlisted no backend (`backend/app/routes/openspec.py`).

### 8) Implementação (DEV)

- Garantir branch + working tree limpos
- Rodar:
  - `codex exec --full-auto --cd /root/.openclaw/workspace/crypto "Implementar as tasks da change <change-name> seguindo specs/design."`

### 9) QA Gate (obrigatório)

Antes de mover a change para `QA`, rode o guard de upstream:
- `./scripts/verify_upstream_published.py --for-status QA`

O QA deve:
- adicionar/atualizar testes conforme `docs/testing-playbook.md`
- rodar suites relevantes (integration + E2E quando aplicável)
- garantir CI verde
- registrar evidências no kanban (Links + Notes)

**Checklist mínimo (PASSOU/FALHOU):**
- Backend integration: `./backend/.venv/bin/python -m pytest -q backend/tests/integration`
- Frontend E2E (quando aplicável): `npm --prefix frontend run test:e2e`

> Se o E2E não rodar localmente (deps), registrar e confiar no CI.

Só após QA OK a change pode ser considerada pronta para homologação.

### 9) Deploy

- `git push origin <branch>`
- (Se usando PR) abrir PR, aguardar CI verde, e fazer merge (padrão: merge commit)
- Deploy produção:
  - `./stop.sh`
  - `./start.sh`
- Pós-deploy: checar `/api/health`.

### 10) Homologação (Alan)

Antes de mover a change para `Alan homologation`, rode:
- `./scripts/verify_upstream_published.py --for-status "Alan homologation"`

- Alan testa e confirma “ok”.

### 11) Arquivar a change

Antes de arquivar, rode:
- `./scripts/verify_upstream_published.py --for-status Archived`

Use o helper seguro (recomendado), que também revalida o guard:
- `./scripts/archive_change_safe.sh <change-name>`

### 12) Evidência

- Registrar hash do commit/PR associado no fechamento/arquivo.
