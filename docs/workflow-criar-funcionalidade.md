# Workflow: Criar Funcionalidade (CX)

Este documento descreve o fluxo padrão para criar funcionalidades no projeto **crypto** usando OpenSpec + Codex, com **gate obrigatório de testes** para reduzir dependência de validação manual.

## Regras Globais

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
- **PO**: discovery, escopo/restrições, critérios de aceitação, artefatos OpenSpec (EN) + `review-ptbr.md`.
- **DEV**: implementação + commits/PR/merge/deploy.
- **QA**: testes (unit/integration/E2E), valida critérios de aceitação, garante CI verde. **Tudo passa por QA.**

## Passo a passo

### 0) Pré-check

- Verificar changes abertas:
  - `openspec list --json`
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

### 3) Validar a change

- `openspec validate <change-name> --type change`

### 5) Revisão do Alan (antes de implementar)

Enviar links do viewer do OpenSpec e aguardar o “ok” do Alan.

**Camada de revisão PT-BR (obrigatória):**
- Enviar um resumo curto em PT-BR no chat.
- Criar o arquivo **não-canônico** `openspec/changes/<change-name>/review-ptbr.md`.
- Incluir também o link do viewer para esse resumo PT-BR.

Viewer (exemplos):
- Proposal: `http://72.60.150.140:5173/openspec/changes/<change-name>/proposal`
- Review PT-BR: `http://72.60.150.140:5173/openspec/changes/<change-name>/review-ptbr`

> Importante: usar sempre o prefixo `/openspec/changes/`. O artifact `review-ptbr` precisa estar allowlisted no backend (`backend/app/routes/openspec.py`).

### 6) Implementação (DEV)

- Garantir branch + working tree limpos
- Rodar:
  - `codex exec --full-auto --cd /root/.openclaw/workspace/crypto "Implementar as tasks da change <change-name> seguindo specs/design."`

### 7) QA Gate (obrigatório)

O QA deve:
- adicionar/atualizar testes conforme `docs/testing-playbook.md`
- rodar suites relevantes (integration + E2E quando aplicável)
- garantir CI verde
- registrar evidências no kanban (Links + Notes)

Só após QA OK a change pode ser considerada pronta para homologação.

### 8) Gate obrigatório de testes (execução)

1) **Criar/atualizar testes** (obrigatório)
- Seguir `docs/testing-playbook.md`.

2) Rodar testes localmente:

- Backend (mínimo obrigatório):
  - `./backend/.venv/bin/python -m pytest -q backend/tests/integration`

- Frontend E2E (quando aplicável):
  - `npm --prefix frontend run test:e2e`

> Se o E2E não rodar localmente (deps), registrar e confiar no CI.

#### Checklist de testes (PASSOU/FALHOU)

Para cada change/feature:

- [ ] **Backend tests**: `pytest -q backend/tests/integration` **PASSOU**
  - Se falhou: corrigir e re-rodar até passar.

- [ ] **E2E (se aplicável)**: `npm --prefix frontend run test:e2e` **PASSOU**
  - Se falhou: corrigir e re-rodar.
  - Se CI-only: registrar que local não roda e validar no GitHub Actions.

- [ ] **Reportar no chat** (resumo obrigatório):

Exemplo (sucesso):
```
✅ Testes backend: PASSOU
✅ Testes E2E: PASSOU (quando aplicável)
```

Exemplo (falha):
```
❌ Testes backend: FALHOU
   - comando: ./backend/.venv/bin/python -m pytest -q backend/tests/integration
   - erro: <cole o trecho principal>
```

> Dica: quando o E2E falhar no CI, usar os artifacts do workflow (Playwright report/trace) para debug.

### 7) Deploy

- `git push origin <branch>`
- `./stop.sh`
- `./start.sh`

### 8) Validação UI (Alan)

- Alan testa e confirma “ok”.

### 9) Arquivar a change

- `openspec archive <change-name> --yes`

### 10) Evidência

- Registrar hash do commit/PR associado no fechamento/arquivo.
