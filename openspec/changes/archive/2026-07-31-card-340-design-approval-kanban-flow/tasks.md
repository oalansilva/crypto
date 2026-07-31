## 1. Workflow e persistência

- [x] 1.1 Centralizar os status, aliases e transições canônicas, removendo fallback silencioso para desenvolvimento.
- [x] 1.2 Migrar estados legados de forma idempotente e persistir impacto de UI, entrega de design e snapshot da aprovação.
- [x] 1.3 Proteger mutações do workflow por autenticação e restringir a aprovação de design ao aprovador configurado.
- [x] 1.4 Validar a entrega de design, o bypass sem UI e a invalidação de aprovação quando a evidência mudar.

## 2. Kanban e experiência de aprovação

- [x] 2.1 Atualizar o Kanban para as colunas canônicas e lentes Produto e Design, Entrega e Todas.
- [x] 2.2 Exibir design, protótipo, crítica, bypass e validade da aprovação no drawer do card.
- [x] 2.3 Implementar drag-and-drop e ação acessível equivalentes, com autenticação e feedback de erro/sucesso em desktop e mobile.
- [x] 2.4 Atualizar testes unitários, integração e Playwright/QA visual para o novo fluxo.

## 3. Agentes, board e documentação

- [x] 3.1 Versionar adaptadores OpenSpec oficiais para Codex e Cursor e documentar o de-para dos comandos.
- [x] 3.2 Atualizar AGENTS.md, rules.md, configuração OpenSpec e documentação operacional com o gate de design.
- [x] 3.3 Atualizar opções, ordem e readme do Status no GitHub Project 1 preservando cards existentes.

## 4. Verificação e entrega técnica

- [x] 4.1 Rodar validação OpenSpec, testes backend/frontend, build e QA visual, corrigindo falhas.
- [x] 4.2 Executar review Codex no diff exato, commit/push do SHA revisado e acompanhar qa-gate terminal verde.
- [x] 4.3 Integrar em develop, executar ./restart, validar a URL e registrar as evidências no card #340.

Evidência operacional: review final aprovado; SHAs `c44c1e3c` e `efe6631a`; PR #341 com `qa-gate` e Playwright verdes; squash `67c1b679` em `develop`; `./restart` concluído; backend `GET /api/health` e frontend `GET /kanban` responderam com sucesso.

Nota: usar as skills do projeto em `.codex/skills` para OpenSpec, testes, debugging e frontend quando aplicável.
