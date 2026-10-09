## 1. Guard — excepção de archive em release-*

- [x] 1.1 Em `scripts/process-fsm/guard.py`, na ramificação `kind == "design"` com `q is None` e `q_git` não `card-<id>-*`, aplicar a excepção só quando `q_git` casa `release-*` e **todos** os paths de design do envelope mapeiam `openspec/changes/<change>/` ou `openspec/changes/archive/<YYYY-MM-DD>-<change>/` com `<change>` `^(card|issue)-(\d+)`. Não alterar `resolve.py`, `.cursor/process-fsm.yaml`, `process_event.py` nem `enabled_tools`.
- [x] 1.2 Para cada id mapeado, chamar o `status_provider` injectável com esse id (não com `bound_card`). Allow só se Status for exactamente `Homologado`. Sem id, Status unread/None/quota, ou path de `frontend/public/prototypes/` → deny `fail_closed`. Card resolvido que não é Homologado → deny `outside_package`. `agent_message` nomeia reason e o id mapeado quando existir.
- [x] 1.3 Se `RELEASE_CARDS` estiver definido, validar com `t16.parse_package_cards` e exigir que o id mapeado pertença à lista **e** continue Homologado. Lista inválida ou id fora da lista → deny. Lista vazia/ausente não é token de allow. Produto, sidecar, Status `item-edit` e allow de design em `card-<id>-*` inalterados.

## 2. Regressão

- [x] 2.1 Fixture de replay: `Write` em `openspec/changes/` sem prefixo `card-<id>`/`issue-<id>`, `q_git=release-2026-08-26`, sessão sem status, `bound_card=⊥` → deny `fail_closed` (deny registado).
- [x] 2.2 Fixtures de allow: path activo `openspec/changes/card-1017-…` e destino `openspec/changes/archive/2026-09-22-card-1017-…` em `release-*` unbound com `status_provider("1017")=Homologado` → allow, sem `evaluate(write_produto)`.
- [x] 2.3 Fixtures de deny: Status unread → `fail_closed`; Status `Design`/`Todo` → `outside_package` mesmo com `RELEASE_CARDS=1017`; `RELEASE_CARDS=999` com 1017 Homologado → `outside_package`; `q_git=develop` design → `fail_closed`; produto em `release-*` → deny; protótipo em `release-*` → `fail_closed`; envelope misto protótipo+archive → deny. Provider injectado; pytest MUST NOT chamar GitHub.
- [x] 2.4 Correr `pytest scripts/process-fsm/test_guard.py -q` e confirmar que os casos anteriores de design em `card-*` e produto em develop/I1/I3 continuam verdes.

## 3. Runbook

- [x] 3.1 Em `docs/crypto-overlay.md` (publicação / caminho B), declarar o archive OpenSpec do pacote Homologado **na** `release-*` como passo normal, sem worktree-do-card + cherry-pick e sem exigir `bound_card` de sessão.
- [x] 3.2 Na secção Release de `.cursor/skills/covenant-flow/SKILL.md`, nomear o mesmo caminho, recusar confirmação operacional extra de Alan, apontar #1059 como consumidor de `decide()` (sem segunda allow-list), e não crescer `AGENTS.md` nem stubs dsh/Grok/OpenCode.
- [x] 3.3 No overlay/skill, exigir que o próximo `/kaizen release` aplicável registre se a recorrência F-1/#1022 (fail_closed em `release-*` unbound) encerrou. Não executar release neste card.

## 4. Validação da change

- [x] 4.1 `openspec validate --change card-1022-release-archive-guard` (e `openspec status --change card-1022-release-archive-guard --json`) verdes para esta change. Falhas de changes alheias não bloqueiam este item.
