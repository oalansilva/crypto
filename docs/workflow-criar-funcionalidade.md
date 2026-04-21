# Workflow: Criar Funcionalidade (CX)

Este documento descreve o fluxo padrão para criar funcionalidades no projeto **crypto** usando OpenSpec + Codex, com gate obrigatório de testes para reduzir dependência de validação manual.

## Regras Globais

### Definition of Done (DoD)
Uma change só é considerada **Done** quando:
- CI está **verde**
- QA validou critérios de aceitação e atualizou/criou testes necessários
- Alan homologou (UI/fluxo real)
- Change foi arquivada no OpenSpec

Regra operacional de stage: uma etapa intermediária só conta como concluída quando o runtime foi atualizado **e** o handoff correspondente foi registrado em `docs/coordination/<change>.md` no mesmo turno.

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
- Padrão operacional: trabalhar diretamente em `develop`.
- Commits diretos em `develop` são aceitos.
- Use PR `develop -> main` para promoção a produção.
- Criar branch por tarefa apenas quando houver isolamento explícito necessário.

4) **UI é validada pelo Alan**
- O bot não “aprova” UI sozinho.

5) **Testing é parte do DoD**
- Para cada change, adicionar/atualizar testes conforme `docs/testing-playbook.md`.

## Papéis (multi-agente)

- **Alan (Stakeholder)**: valida a ideia (antes) e homologa o final (depois).
- **main**: mantém o chat gerencial e consulta runtime + coordenação como superfície principal.
- **PO**: discovery, escopo/restrições, critérios de aceitação, artefatos OpenSpec (EN) + `review-ptbr.md`.
- **DESIGN**: quando houver UI/UX, protótipo, decisões visuais e notas de aceite para DEV/QA.
- **DEV**: implementação + commits/PR/merge/deploy.
- **QA**: testes (unit/integration/E2E), valida critérios de aceitação, garante CI verde. **Tudo passa por QA.**

Contrato operacional curto por papel, handoff padrão e DoD por estágio: `docs/multiagent-operating-playbook.md`.

Nota: o OpenSpec oficial define os artefatos do change, mas não define ownership por papel. Neste repositório, o `PO` gera os artefatos do change e o `DESIGN` complementa com protótipo visual e decisões de UX.

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

### 3) Discovery (PO) — perguntas e decisões (obrigatório)

O PO deve fechar (por escrito) antes do planning:
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

### 6) Encerrar PO e disparar DESIGN

- PO revisa os artefatos, garante que decisões e critérios de aceitação estão travados.
- PO atualiza status da change para `DESIGN` no runtime (se necessário) e registra handoff em `docs/coordination/<change-name>.md`.
- PO registra handoff com o status de saída da etapa: artifacts prontos (`proposal/specs/tasks/design`). DESIGN responsável por prototipar UI quando aplicável.
- **PO dispara o agente DESIGN** (via spawn ou mensagem interna) após registrar os artefatos.
- Somente após DESIGN finalizar (protótipo + links publicados) o handoff avança para `Alan approval`.

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

### 8) Implementação (DEV)

- Garantir branch + working tree limpos
- Rodar:
  - `codex exec --full-auto --cd /root/.openclaw/workspace/crypto "Implementar as tasks da change <change-name> seguindo specs/design."`

### 9) QA Gate (obrigatório)

Antes de mover a change para `QA`, **não use o upstream guard como bloqueio padrão da própria change**.
- Sequência preferida: `DEV implementa -> QA valida -> commit/publish depois`.
- Mudanças locais da própria change não devem bloquear por si só `DEV -> QA`.
- Só rode `./scripts/verify_upstream_published.py --for-status QA` se houver necessidade operacional fora desse fluxo.

O QA deve:
- adicionar/atualizar testes conforme `docs/testing-playbook.md`
- rodar suites relevantes (integration + E2E quando aplicável)
- garantir CI verde
- registrar evidências no `docs/coordination/<change-name>.md` (Links + Notes)

Checklist mínimo (PASSOU/FALHOU):
- Backend integration: `./backend/.venv/bin/python -m pytest -q backend/tests/integration`
- Frontend E2E (quando aplicável): `npm --prefix frontend run test:e2e`

Só após QA OK a change pode ser considerada pronta para homologação.

### 10) Deploy

- `git checkout develop`
- `git push origin develop`
- Se ainda não houver PR aberta de `develop -> main`, abra com:
  - `gh pr create --base main --head develop --title "chore: promote develop to main" --body "Sincronização de mudanças consolidadas em develop."`
- Se já houver PR, ela se atualiza automaticamente com o novo commit.
- Aguardar CI verde e fazer merge em `main` (merge commit padrão).
- Deploy produção:
  - `./stop.sh`
  - `./start.sh`
- Pós-deploy: checar `/api/health`.

### 11) Homologação (Alan)

Antes de mover a change para `Homologation`, rode:
- `./scripts/verify_upstream_published.py --for-status "Homologation"`
- Alan testa e confirma “ok”.

### 12) Arquivar a change

Antes de arquivar, rode:
- `./scripts/verify_upstream_published.py --for-status Archived`
- `./scripts/archive_change_safe.sh <change-name>`

### 13) Evidência

- Registrar hash do commit/PR associado no fechamento/arquivo.
