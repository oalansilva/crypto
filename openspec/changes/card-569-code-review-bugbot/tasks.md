## 1. Contrato de Code Review

- [ ] 1.1 Atualizar `AGENTS.md` para exigir `/review-bugbot` em todo `Status=Code Review` com os dois prompts canônicos (`uncommitted changes` sem Base Branch; `branch changes` + `Base Branch: develop` no SHA de fechamento), `/review-security` nos globs do design, spawn vazio com 1 retry + fallback explícito, invocação do revisor de processo via Task `generalPurpose` read-only, e remover “bugbot só se Alan pedir”.
- [ ] 1.2 Atualizar `rules.md` com o mesmo gate pré-commit e a proibição de Autofix na branch existente / Agent Review automático pós-commit.
- [ ] 1.3 Atualizar `docs/backlog-operating-model.md` para descrever Code Review como `/review-bugbot` vs `develop`, não “revisão Cursor” genérica.
- [ ] 1.4 Atualizar o bloco canônico de Done (`AGENTS.md` / helper se necessário) para citar o resultado do `/review-bugbot`.

## 2. Regras e subagent versionados

- [ ] 2.1 Criar `.cursor/BUGBOT.md` (raiz) com PostgreSQL obrigatório, sem SQLite, Design/`Pronto para Dev` não puláveis, secrets fora, testes se `backend/**` muda, Playwright visual se UI muda.
- [ ] 2.2 Criar `backend/.cursor/BUGBOT.md` e `frontend/.cursor/BUGBOT.md` com regras do tree.
- [ ] 2.3 Criar `.cursor/agents/code-reviewer.md` com `readonly: true`, `model: inherit`, focado em processo/contrato (OpenSpec, Design evidence, não regressão de status).

## 3. Evidência operacional e log

- [ ] 3.1 Registrar Autofix Off (screenshot/settings). Se o dashboard não estiver acessível, deixar o item aberto até comentário de Alan aceitando o residual; não fechar 3.1 só com nota.
- [ ] 3.2 Append em `docs/kaizen-log.md` da origem do card #569 (proposta → implementação).
- [ ] 3.3 Append em `docs/decision-log.md` da decisão de Code Review nativo vs `develop`.

## 4. Validação

- [ ] 4.1 `openspec validate --change card-569-code-review-bugbot` (ou specs afetados) verde.
- [ ] 4.2 Conferir que nenhum arquivo de produto (`backend/app/**`, `frontend/src/**`) mudou.
- [ ] 4.3 Publicar/republicar OpenSpec no card #569; UI impact none; Prototype N/A.
- [ ] 4.4 Code Review deste card: `/review-bugbot` `uncommitted changes` (sem Base Branch) antes do commit; depois do commit, `/review-bugbot` `branch changes` + `Base Branch: develop`; Task de processo read-only com `.cursor/agents/code-reviewer.md`.
