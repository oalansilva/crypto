## 1. Infraestrutura do Agente Kaizen

- [x] 1.1 Criar subagent auditor `.opencode/agent/kaizen.md` (read-only, herança de modelo, fontes: board, Git, OpenSpec, CI, sessões opencode via SQL mode=ro, tech debt)
- [x] 1.2 Criar command `.opencode/commands/kaizen.md` com modos `/kaizen`, `/kaizen card <id>`, `/kaizen release` (fluxo: coleta → log → cards PO → report)
- [x] 1.3 Criar `docs/kaizen-log.md` (append-only, template de entrada, regra de recorrência, histórico de mudanças de processo)

## 2. Registro e rastreabilidade no board

- [x] 2.1 Criar label `kaizen` no repo oalansilva/crypto
- [x] 2.2 Registrar melhorias como 1 card PO por melhoria com `Status=Todo`, campos preenchidos (`Prioridade`, `Tipo`, `Frente`, `Responsavel`, `Semana`) e dependências linkadas
- [x] 2.3 Aplicar limite de 3 cards kaizen por release (priorização P0/P1/P2 define os que entram; resto no backlog)

## 3. Regras de processo

- [x] 3.1 Adicionar papel Kaizen em `AGENTS.md` (responsabilidades, read-only, sessões, PO, priorização, propõe/Alan aprova, segurança) e atualizar contagem de agentes
- [x] 3.2 Adicionar regra 14 em `rules.md` (pós-release obrigatório `/kaizen release`, cards `Status=Todo`, máx. 3/release, propõe/Alan aprova, segurança de output)
- [x] 3.3 Referenciar `docs/kaizen-log.md` nos caminhos de documentação do AGENTS.md

## 4. Validação de teste (prova real)

- [x] 4.1 Executar auditoria real na release 2026-08-08 (`/kaizen release`) via subagent (board, Git, OpenSpec, CI, sessões do pacote 361/384/395/399)
- [x] 4.2 Anexar relatório com 9 achados (F-1..F-9) em `docs/kaizen-log.md` com métricas e trechos de sessão
- [x] 4.3 Criar cards kaizen do teste: #421 (P0, gate de Design), #422 (P1, release-guard), #423 (P2, gist/retrigger) — todos `Status=Todo`
- [x] 4.4 Validar `openspec validate --all` com a change card-420-kaizen-agent verde (executar em Code Review/QA)

## 5. Publicação de artefatos no card

- [x] 5.1 Publicar artefatos OpenSpec da change no card #420 (Gist secreto `crypto openspec card-420-kaizen-agent` + comentário com arquivos/links)
- [ ] 5.2 Criar View "Kaizen" no Project 1 (agrupada por Prioridade, filtro label `kaizen`) — **ação manual de Alan no board** (não automatizável via CLI; ver review card #420)
