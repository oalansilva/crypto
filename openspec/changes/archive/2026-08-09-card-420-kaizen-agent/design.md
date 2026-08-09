# Design — card-420-kaizen-agent

## UI impact

**`UI impact: none`** — mudança exclusiva de processo/tooling (`.opencode/agent`, `.opencode/commands`, `docs/kaizen-log.md`, `AGENTS.md`, `rules.md`). Nenhuma superfície visual do produto é alterada; não há telas, componentes, rotas ou estilos. Impeccable: `N/A` (sem UI nova para críticar/auditar).

## Context

Processo maduro (alan-workflow, OpenSpec, Project 1, Playwright visual, release-guard) sem feedback loop do próprio processo: fricções se repetem, sessões do opencode custam caro sem `Done` e melhorias não têm trilha. O opencode persiste sessões completas em `~/.local/share/opencode/opencode.db` (sessions, messages, parts, todos, custos, erros de tool), viabilizando detecção objetiva de modelo perdido/alucinando via SQL read-only.

## Goals / Non-Goals

**Goals:**
- Auditoria read-only de processo (board, Git, OpenSpec, CI, tech debt, sessões opencode) com achados priorizados.
- Registro local versionado (`docs/kaizen-log.md`) e cards kaizen no board como PO (1 card por melhoria, `Status=Todo`, máx. 3/release, `Prioridade` P0/P1/P2).
- Detecção de sessões onde o modelo se perde/alucina (escopo = cards da release).
- Evolução de skills: propor melhorias e pesquisar alternativas (read-only); troca só com aprovação de Alan.

**Non-Goals:**
- Não implementar melhorias automaticamente (propõe, Alan aprova).
- Não automatizar a limpeza de refs/worktrees (exige autorização humana).
- Não mudar runtime backend/frontend.

## Decisions

1. **Subagent read-only (`edit: deny`) com herança de modelo da sessão principal.** Visão de imagem delegada ao subagent `vision` (única exceção de roteamento do projeto). Evidência: `.opencode/agent/kaizen.md` não fixa `model` (herda) e segue o contrato de herança do AGENTS.md.
2. **Escopo de sessões = release, não janela fixa:** correlacionar sessões por `#<id>`/`card-<id>` em títulos/mensagens de usuário, no diretório do projeto, entre a release anterior e a atual, incluindo subagents via `parent_id`. Evita custo e ruído de varrer 180MB.
3. **Sinais objetivos de alucinação/perda no DB:** caminho/URL inventado (erros `read`/`webfetch`), loop (mesmo erro ≥2x sem mudança de estratégia), `step-finish unknown`, custo alto sem `Done`, deriva de roteamento (`message.modelID ≠ session.model`), subagent falhando (`task` com erro), TODO eterno, tool mal usada (grep/read >64KB).
4. **Segurança de output em camadas:** issues públicas com métricas agregadas e IDs; trechos curtos (≤2-3 linhas) só em `docs/kaizen-log.md`; nunca prompts/raciocínio/tokens/credenciais.
5. **Registro PO com priorização visível:** campo `Prioridade` existente do board (P0/P1/P2) com regra severidade × frequência / esforço; View "Kaizen" agrupada por prioridade (criação manual no Project 1, fora do escopo automatizável); `Semana` para agendamento; override humano sempre.
6. **Limite 3 cards kaizen/release** com backlog para releases seguintes — evita Kaizen consumir capacidade de entrega (WIP sem limite na execução, mas entrada limitada).
7. **Gatilhos:** `/kaizen` e `/kaizen card <id>` sob demanda; `/kaizen release` obrigatório no fechamento de lote (após deploy PROD validado, antes de mover para `Pronto`).

## Risks / Trade-offs

- **Custo da auditoria de sessões**: mitigado por escopo = release + SQL filtrado (mode=ro); janela ampla só sob pedido explícito.
- **Falso positivo em deriva de roteamento**: `vision` (exceção) grava modelID diferente na sessão — tratar como sinal informativo, não bloqueio; correlacionar com `parent_id`/tool `task`.
- **Subagent `kaizen` não nativo em sessões iniciadas antes da criação do arquivo**: fallback operacional é usar o contrato via subagent `general` (mesmo modelo), registrado no handoff.
- **Board não expõe timestamps por item via `gh project item-list`**: métricas de ciclo dependem de heurísticas (Updated/Created) até v2 (workflow DB).
- **Cards kaizen competem com entrega de produto**: mitigado pelo limite de 3/release e triagem humana de prioridade.

## Design Agent verdict

**PASS** — decisão enxuta registrada, sem superfície visual nova (`UI impact: none`). Design Critique: sem achados bloqueantes no escopo. Impeccable: N/A justificado (ausência de superfície visual). Prototype: N/A (não há UI).

## Prototype Validation

N/A — sem superfície visual; nenhuma validação em navegador aplicável.
