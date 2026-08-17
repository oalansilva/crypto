## 1. Contrato de Code Review

- [ ] 1.1 Atualizar `AGENTS.md` para exigir dois Tasks `generalPurpose` read-only `inherit` em todo `Status=Code Review` (`.cursor/agents/diff-reviewer.md` no diff; `.cursor/agents/code-reviewer.md` no processo), com pré-commit vs HEAD e fechamento `origin/develop...HEAD` na branch do card; `/review-bugbot` e `/review-security` só se Alan pedir; spawn vazio com 1 retry + residual explícito.
- [ ] 1.2 Atualizar `rules.md` com o mesmo gate pré-commit, Bugbot Off de propósito, e a proibição de Autofix na branch existente / Agent Review automático pós-commit.
- [ ] 1.3 Atualizar `docs/backlog-operating-model.md` para descrever Code Review como reviewers locais vs `develop`, não Bugbot obrigatório nem “revisão Cursor” genérica.
- [ ] 1.4 Atualizar o bloco canônico de Done (`AGENTS.md` / helper) para citar `diff-reviewer` e `code-reviewer`; `--review` continua obrigatório em `--transition done`.

## 2. Regras e subagent versionados

- [ ] 2.1 Manter `.cursor/BUGBOT.md` (raiz) como regras lidas pelo reviewer local (PostgreSQL, sem SQLite, Design/`Pronto para Dev`, secrets, testes, Playwright).
- [ ] 2.2 Manter `backend/.cursor/BUGBOT.md` e `frontend/.cursor/BUGBOT.md` com regras do tree.
- [ ] 2.3 Criar `.cursor/agents/diff-reviewer.md` e atualizar `.cursor/agents/code-reviewer.md`, ambos `readonly: true`, `model: inherit`.

## 3. Evidência operacional e log

- [ ] 3.1 Registrar Bugbot Off de propósito (chat Alan 2026-08-17: não ligar por custo). Não exigir Autofix Off no dashboard.
- [ ] 3.2 Append em `docs/kaizen-log.md` do pivot #569 (Bugbot obrigatório → reviewers locais).
- [ ] 3.3 Append em `docs/decision-log.md` da decisão que substitui `/review-bugbot` obrigatório.

## 4. Validação

- [ ] 4.1 `openspec validate --change card-569-code-review-bugbot` (ou specs afetados) verde.
- [ ] 4.2 Conferir que nenhum arquivo de produto (`backend/app/**`, `frontend/src/**`) mudou.
- [ ] 4.3 Publicar/republicar OpenSpec no card #569 (mesmo Gist); UI impact none; Prototype N/A.
- [ ] 4.4 Code Review deste card: `diff-reviewer` no uncommitted vs HEAD; depois do commit, `diff-reviewer` em `origin/develop...HEAD` na branch do card; `code-reviewer` de processo. Sem `/review-bugbot` obrigatório.
