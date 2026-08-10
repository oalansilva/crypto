---
description: Kaizen — auditoria de melhoria contínua de processo e tech debt (board, Git, OpenSpec, CI, sessões opencode). Uso: /kaizen, /kaizen card <id>, /kaizen release.
---

# Kaizen — Melhoria Contínua

Audita o processo de execução do projeto, detecta fricções (incluindo sessões do opencode onde o modelo se perde ou alucina) e cadastra melhorias como cards PO no board.

## Modos

| Comando | Uso |
| --- | --- |
| `/kaizen` | Auditoria completa (processo + tech debt + sessões recentes) |
| `/kaizen card <id>` | Mini-análise pós-card: sessões/CI/higiene daquele card |
| `/kaizen release` | Auditoria profunda pós-release (obrigatório no fechamento de lote) |

## Fluxo de execução

1. **Coletar evidências**: acionar o subagent `kaizen` (`.opencode/agent/kaizen.md`) para coletar e analisar:
   - Board: `gh project item-list 1 --owner oalansilva --format json --limit 200` (paginar se >200; Status vs Fluxo, cards presos, gates, evidência em Done/Homologado/Pronto)
   - Git: inventory completo + `scripts/release-guard audit`
   - OpenSpec: `openspec validate --all` e status das changes ativas
   - CI: checks recentes de PRs merged (falhas/cancelled, qa-gate, visual)
   - Sessões: SQL read-only em `~/.local/share/opencode/opencode.db` — em `/kaizen release`, escopo = sessões dos cards do pacote (`#<id>`/`card-<id>`) entre a release anterior e a atual, incluindo subagents (`parent_id`)
   - Tech debt (full/release): coverage, `pip-audit`/`npm audit`, padrões do reviewer
2. **Consolidar relatório**: anexar achados em `docs/kaizen-log.md` (append-only, com trechos curtos de evidência de sessão permitidos APENAS neste relatório local).
3. **Registrar cards (atuar como PO)**: cada melhoria acionável vira **1 issue separada** no repo `oalansilva/crypto`:
   - Formato PO: `## Proposta (PO)` com Contexto (evidência + link `docs/kaizen-log.md`), Escopo, Critérios de aceite, classificação change/story/bug
   - Labels: `kaizen` + `enhancement` (ou `bug` quando for defeito de processo)
   - Campos do Project 1: `Status=Em Refinamento` (obrigatório — cards kaizen nascem na primeira coluna, entrada obrigatória de todo card novo, e seguem o fluxo normal do board; nunca criar direto em coluna de execução), `Prioridade` (regra abaixo), `Tipo` (Operacao/Codigo/QA/Seguranca/Metrica), `Frente`, `Responsavel` (Codex/Clara/Alan), `Semana` (alvo de execução)
   - Dependências entre melhorias: issue filha/linkada
   - **Limite de capacidade: máximo 3 cards kaizen por release.** A priorização (P0/P1/P2) define os 3 que entram; o restante fica no backlog kaizen para releases seguintes. Vaga só libera com `Pronto`/`Cancelado`.
4. **Reportar**: resumo gerencial curto com os cards criados e links.

## Regra de priorização (P0/P1/P2)

Calculada na criação do card pelo PO (Kaizen), com override humano sempre possível:

| Prioridade | Enquadramento |
| --- | --- |
| P0 | Risco de segurança/dados/produção; falha recorrente que bloqueia entregas (CI flaky, gates pulados); alucinação/loop de modelo com custo alto repetido; correção rápida → semana atual |
| P1 | Quick win (ganho médio-alto, esforço baixo); higiene anti-retrabalho; falha mensal → próxima semana |
| P2 | Desejável, retrospectiva acumulada, sem urgência → backlog |

## Regras de segurança e autonomia

- O Kaizen (subagent) é read-only e **nunca implementa**: propõe e cadastra cards. Alan tria (aprovado/recusado/pendente) nos comentários das issues; o agente principal (main) executa o aprovado.
- Issues públicas: apenas métricas agregadas e IDs. Trechos de raciocínio/texto de sessões somente em `docs/kaizen-log.md`.
- Evolução de skills: o Kaizen pode propor melhorias de skills em uso e pesquisar alternativas (busca read-only em GitHub/docs/CLIs, comparação de fit com evidência). Troca/criação de skill só após aprovação de Alan, respeitando herança de modelo/roteamento.
- `/kaizen release` é obrigatório no fechamento de lote: rodar após deploy PROD validado e antes de mover cards para `Pronto`, com evidência no `kaizen-log.md`.
