# Workflow: Criar Funcionalidade (CX)

Este documento descreve o fluxo padrão para criar funcionalidades no projeto **crypto** usando OpenSpec + Codex CLI, com gate obrigatório de testes para reduzir dependência de validação manual.

## Regras Globais

### Definition of Done (DoD)
Uma change só é considerada **Done** quando:
- CI está **verde**
- Critérios de aceitação foram validados e testes atualizados quando necessário
- Alan homologou (UI/fluxo real)
- Change foi arquivada no OpenSpec

Regra operacional de etapa: uma etapa só conta como concluída quando houve atualização no `docs/coordination/<change>.md` e o commit/PR correspondente.

### Regras de qualidade (obrigatórias)
- Mudou schema de DB? Deve ter migração (SQLite `ALTER TABLE`/startup migration) + teste de integração.
- Endpoints de UI devem ter limites e não podem fazer backfill histórico gigante por padrão (ex: candles bounded por `timeframe+limit`).
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
- Padrão operacional: trabalhar diretamente em `main`.
- Commits diretos em `main` são aceitos.
- PR de revisão é opcional: `feature/<slug> -> main`.
- Criar branch por tarefa apenas quando houver isolamento explícito necessário.

4) **UI é validada pelo Alan**
- O bot não “aprova” UI sozinho.

5) **Testing é parte do DoD**
- Para cada change, adicionar/atualizar testes conforme `docs/testing-playbook.md`.

## Responsável

Você é o único operador.  
O fluxo usa OpenSpec + Codex CLI + revisão humana no fim pelo Alan.

Checklist de controle:
- manter `docs/coordination/<change>.md` atualizado com o status e decisões;
- registrar links de artefatos de aprovação e evidências de teste;
- garantir revisão final com Alan antes de promover.

Nota: use `docs/coordination/<change>.md` para manter trilha operacional de decisão e evidência.

## Passo a passo

### 0) Pré-check

- Verificar changes abertas:
  - `openspec list --json`
  - Se existir change aberta, **arquivar antes** de criar outra.
- Verificar branch e working tree:
  - `git branch --show-current`
  - `git status --porcelain` (deve estar vazio)

### 1) Criar trilha da change (obrigatório)

- Criar `docs/coordination/<change-name>.md` usando `docs/coordination/template.md`.
- Preencher o mínimo: Status + Links do viewer + Next actions.

### 2) Criar a change

- `openspec new change <change-name>`

### 3) Discovery — perguntas e decisões (você)

Feche (por escrito) antes do planning:
- objetivo
- defaults
- regras
- escopo e não-escopo
- performance/limites (ex: candles limit)
- persistência (backend/local)
- critérios de aceitação

Registrar no `docs/coordination/<change-name>.md` em "Decisions (locked)".

### 4) Planning (sem Codex)

- Proposal:
  - `openspec instructions proposal --change <change-name>` → `proposal.md`
- Specs:
  - `openspec instructions specs --change <change-name>` → `specs/<capability>/spec.md`
- Tasks:
  - `openspec instructions tasks --change <change-name>` → `tasks.md`
- Design:
  - `openspec instructions design --change <change-name>` → `design.md`

### 5) Validar a change

- `openspec validate <change-name> --type change`

### 6) Handoff para implementação

- Consolidar `proposal/specs/tasks` (e `design.md` quando houver UI) e registrar em `docs/coordination/<change-name>.md`.
- Avançar para aprovação do Alan apenas após critérios e decisões estarem fechados.

### 7) Revisão do Alan (antes de implementar)

Enviar links do viewer do OpenSpec e aguardar o “ok” do Alan.

**Camada de revisão PT-BR (obrigatória):**
- Enviar um resumo curto em PT-BR no chat.
- Criar `openspec/changes/<change-name>/review-ptbr.md`.
- Incluir também o link do viewer para esse resumo PT-BR.

Viewer (exemplos):
- Proposal: `http://72.60.150.140:5173/openspec/changes/<change-name>/proposal`
- Review PT-BR: `http://72.60.150.140:5173/openspec/changes/<change-name>/review-ptbr`

> Importante: usar sempre o prefixo `/openspec/changes/`. O artifact `review-ptbr` precisa estar allowlisted no backend (`backend/app/routes/openspec.py`).

### 8) Implementação

- Garantir branch + working tree limpos
- Rodar:
  - `codex exec --full-auto --cd /root/.openclaw/workspace/crypto "Implementar as tasks da change <change-name> seguindo specs/design."`

### 9) Validação (obrigatório)

Sequência preferida: implementação -> validação -> merge.
- Mudanças locais da própria change não devem bloquear por si só a revisão.
- Controle de progresso é feito por commit/PR + validação em `docs/coordination/<change-name>.md`.

A validação deve:
- adicionar/atualizar testes conforme `docs/testing-playbook.md`
- rodar suites relevantes (integration + E2E quando aplicável)
- garantir CI verde
- registrar evidências no `docs/coordination/<change-name>.md` (Links + Notes)

Checklist mínimo (PASSOU/FALHOU):
- Backend integration: `./backend/.venv/bin/python -m pytest -q backend/tests/integration`
- Frontend E2E (quando aplicável): `npm --prefix frontend run test:e2e`

Só após validação OK a change pode ser considerada pronta para homologação.

### 10) Deploy

- `git checkout main`
- `git push origin main`
- Se preferir, crie PR de revisão:
  - `git checkout -b feature/<slug>`
  - implemente
  - `git push -u origin feature/<slug>`
  - `gh pr create --base main --head feature/<slug> --title "<resume>" --body "Resumo curto da mudança"`
  - aguardar CI verde e fazer merge em `main`
- No fluxo mais simples (sem revisão prévia), faça `git push origin main` após validação.
- Deploy produção:
  - `./stop.sh`
  - `./start.sh`
- Pós-deploy: checar `/api/health`.

### 11) Homologação (Alan)

Alan testa e confirma “ok”.

### 12) Arquivar a change

Antes de arquivar, rode:
- `./scripts/archive_change_safe.sh <change-name>`

### 13) Evidência

- Registrar hash do commit/PR associado no fechamento/arquivo.
