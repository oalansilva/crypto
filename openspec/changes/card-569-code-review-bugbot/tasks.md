## 1. Contrato de Code Review

- [x] 1.1 Atualizar `AGENTS.md` para exigir dois Tasks `generalPurpose` read-only `inherit` em todo `Status=Code Review`
- [x] 1.2 Atualizar `rules.md` com o mesmo gate pré-commit, Bugbot Off de propósito, Autofix/Agent Review
- [x] 1.3 Atualizar `docs/backlog-operating-model.md`
- [x] 1.4 Atualizar o bloco canônico de Done / helper `--review`

## 2. Regras e subagent versionados

- [x] 2.1 `.cursor/BUGBOT.md` na raiz
- [x] 2.2 `backend/.cursor/BUGBOT.md` e `frontend/.cursor/BUGBOT.md`
- [x] 2.3 `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md` (`readonly`, `inherit`)

## 3. Evidência operacional e log

- [x] 3.1 Bugbot Off de propósito (chat Alan 2026-08-17)
- [x] 3.2 Append `docs/kaizen-log.md`
- [x] 3.3 Append `docs/decision-log.md`

## 4. Validação

- [x] 4.1 `openspec validate card-569-code-review-bugbot`
- [x] 4.2 Nenhum arquivo de produto (`backend/app/**`, `frontend/src/**`) mudou
- [x] 4.3 OpenSpec no card #569 (Gist `aed5b632eeaf406221d83787a83cbec4`)
- [ ] 4.4 Code Review deste card: `diff-reviewer` uncommitted + vs `origin/develop...HEAD`; `code-reviewer` de processo
