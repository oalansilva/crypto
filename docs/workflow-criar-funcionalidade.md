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

## Passo a passo

### 0) Pré-check

- Verificar changes abertas:
  - `openspec list --json`
- Verificar branch e working tree:
  - `git branch --show-current`
  - `git status --porcelain` (deve estar vazio)

### 1) Criar a change

- `openspec new change <change-name>`

### 2) Planning (sem Codex)

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

### 4) Revisão do Alan (antes de implementar)

Enviar links do viewer do OpenSpec e aguardar o “ok” do Alan.

Viewer (exemplo):
- `http://72.60.150.140:5173/openspec/changes/<change-name>/proposal`

> Importante: usar sempre o prefixo `/openspec/changes/`.

### 5) Implementação (com Codex)

- Garantir branch + working tree limpos
- Rodar:
  - `codex exec --full-auto --cd /root/.openclaw/workspace/crypto "Implementar as tasks da change <change-name> seguindo specs/design."`

### 6) Gate obrigatório de testes

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
