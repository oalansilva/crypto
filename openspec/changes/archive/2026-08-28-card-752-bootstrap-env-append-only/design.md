## Context

Card #752 (Kaizen P0, `Operacao`, `Prioridade P0`, `Status=Design`) nasce do outage PROD na release 2026-08-27 (#747): um bootstrap ad-hoc fez `grep` sem permissão (`root:root 600` em `/srv/apps/prod/criptofarol/source/backend/.env` → `Permission denied`) e `mv` de um tmp só com 4 chaves Telegram sobre o dotenv do backend, apagando `DATABASE_URL` / `JWT_SECRET` e deixando o backend em loop (health 502). Restore manual: `.env.bak-20260809` + `JWT_SECRET` do DEV + chaves Telegram; cópia do wiped em `.env.wiped-20260827`.

Estado atual:
- `ops/` não tem bootstrap versionado; operador improvisa `cat >` / `mv` do snippet.
- `backend/app/config.py:7-18` faz `load_dotenv(backend/.env, override=False)` e `load_dotenv(root/.env, override=False)`; o unit `criptofarol-prod-*` faz `source` do dotenv do backend (não lê o da raiz). #687 fixou `BINANCE_*` no home raiz; #747 fixou Telegram no home backend.
- Guard `fail_closed` em `q_git=develop`/`main` bloqueia Agent de escrever dotenv; o script é para operador (ou Apply em branch de card), não para CI tocar paths reais.
- Doc `docs/monitor-telegram-alerts.md` ainda não registra DEV vs PROD para webhook único (`setWebhook` para PROD tira o DEV) e que vars Telegram vivem no dotenv do backend.

Stakeholders: operador (DEV/PROD), backend em PROD, QA/CI.

**UI impact: none.** Script CLI + doc operacional. Nenhuma rota, shell, componente ou copy de produto. Prototype N/A. Pipeline Impeccable desta coluna Design = N/A.

## Goals / Non-Goals

**Goals:**
- Entregar script versionado em `ops/` fail-closed, append-only por chave, que nunca substitua o ficheiro destino pelo patch.
- `--file` obrigatório sem default; destino ausente → exit ≠0 sem criar ficheiro.
- Patch via `--from-file` e/ou stdin (`KEY=VALUE`), sem `--set`; `--from-file` primeiro, stdin por cima (stdin ganha no patch interno).
- Merge por chave: `destino ∪ patch`; nenhuma chave do destino some; piso `DATABASE_URL`+`JWT_SECRET` imutável (valor diferente no patch → exit ≠0 sem backup/mv).
- Preservar comentários, linhas vazias e ordem do destino; update só valor na linha (sufixo `# comment` permanece); chaves novas no fim na ordem efetiva do patch.
- Backup timestamped antes de escrever (mesmo dir, `.env.bak-YYYYMMDD-HHMMSS`, `chmod 600` no bak); replace atómico via tmp no mesmo filesystem; recusar se destino antes ou resultado não tiver piso; `chmod 600` no destino após escrita; idempotência sem backup/mv quando merge idêntico.
- Testes só em tmp; nunca tocar dotenv reais; saída só nomes/contagens/paths, nunca valores.
- Doc curta em `docs/monitor-telegram-alerts.md` (DEV vs PROD, um bot = um webhook, vars no dotenv do backend).

**Non-Goals:**
- Rotacionar `JWT_SECRET` agora (dívida: DEV/PROD partilham secret; bak 20260809 não tinha JWT).
- Bot Telegram separado DEV/PROD neste card.
- Secret manager, `Environment=` com valor, mudar loader/units, unificar homes, copiar chaves entre os dois dotenv.
- Restore de destino já wiped (usar bak / `.env.wiped-20260827`); este script recusa.
- Restart de services.
- Colar valores de secret em issue/chat/evidência/log.

## Decisions

1. **Linguagem: Python 3 em `ops/bootstrap_env.py` (não `sh`).**
   Alternativa `sh`/`awk`/`sed` rejeitada: preservar comentários/ordem/sufixo, tratar quoting, validar piso, EACCES, e garantir testes determinísticos é frágil em shell. Python permite parser alinhado ao `source` do unit, `argparse` estrito, e `pytest` tmp sem subshell. Nome `bootstrap_env.py` (PEP 8) com symlink opcional `bootstrap-env` documentado; `chmod +x` com shebang. Alternativa `bootstrap-env.sh` não cobre #752 sem reimplementar parsing.

2. **CLI: `argparse` estrito, sem `default` para `--file`.**
   `parser.add_argument('--file', required=True)`; `--from-file` opcional; nenhuma flag `--set`. Sem `--file` → `parser.error` exit 2. Destino inexistente ou não-regular → exit ≠0 sem criar. Sem default de path para não adivinhar DEV vs PROD. Alternativa com default `/srv/apps/.../backend/.env` rejeitada (issue Q1).

3. **Patch sources: `--from-file` + stdin, merge interno `file` → `stdin` (stdin ganha).**
   Ler `--from-file` se fornecido; ler stdin se não for TTY **ou** se pipe tiver bytes (detectar via `sys.stdin.isatty()` e `select` não-bloqueante; se TTY sem pipe → stdin vazio). Parsear cada fonte em `OrderedDict` preservando última ocorrência por chave no mesmo ficheiro (último valor efetivo vence, alinhado ao `source`). Depois merge: `patch = {**from_file_dict, **stdin_dict}`. Se patch vazio (sem nenhuma `KEY=VALUE`) → exit ≠0 sem escrita (cobre Q6). Alternativa “stdin sempre” rejeitada (exige pipe mesmo para `--from-file`).

4. **Parser `KEY=VALUE` alinhado ao `source` do unit, com preservação.**
   Regex chave: `^\\s*([A-Za-z_][A-Za-z0-9_]*)\\s*=`. Linhas com `^\\s*#` ou vazias → comentário/vazia, ignoradas para patch e preservadas no destino. Chaves comentadas (`# DATABASE_URL=`) não contam para piso. Valor = resto da linha após primeiro `=`, com `strip` só para detetar vazio mas preservado literal para comparação (whitespace-only = vazio → destino inválido). `export KEY=VALUE` suportado strippando prefixo `export\\s+`. Quoting: valor comparado literal; não fazer `shlex` unwrap para não divergir do `source`. Sufixo ` # comment` ou `; comment` após valor em linha do destino: detetado via regex `^(\\s*KEY\\s*=)([^#;]*?)(\\s*[#;].*)?$` para preservar grupo 3 ao reescrever. Alternativa “reemitir sem sufixo” rejeitada (Q7).

5. **Piso imutável `DATABASE_URL` + `JWT_SECRET`.**
   Após parse, validar destino antes: para cada chave do piso, último valor não vazio (strip) deve existir; ausente/vazio/whitespace → exit ≠0, destino inalterado, sem bak (AC2/AC3). Na validação do patch: se patch contém piso e `patch[piso] != destino[piso]` (comparação strip) → exit ≠0 sem bak/mv (AC5). Omitir piso no patch ou repetir mesmo valor → ok (AC4). Também recusar merge cujo resultado não tenha piso (defesa após merge). Alternativa “permitir update de piso com flag” rejeitada.

6. **Preservação de comentários/ordem + append.**
   Ler destino linha-a-linha, manter `list[str]`. Para cada chave do patch não-piso: se chave existe no destino (último índice), substituir só `valor` na linha (grupo 2), mantendo prefixo e sufixo; se não existe, append `KEY=VALUE` no fim na ordem efetiva do patch (ordem de `OrderedDict`). Chaves só no destino permanecem. Valor update usa `patch_val` literal (sem re-quoting). Alternativa “reordenar alfabeticamente” rejeitada.

7. **Backup timestamped + replace atómico + perms.**
   Antes de escrever, `stat` destino; se EACCES → exit ≠0 sem truncar. Criar bak: `destino.bak-YYYYMMDD-HHMMSS` (hora com segundos, `datetime.now().strftime("%Y%m%d-%H%M%S")`); se colidir (duas corridas no mesmo segundo) → acrescentar `-<n>` incremental. `shutil.copy2` + `chmod 0o600` no bak. Escrita: `tempfile.mkstemp(dir=destino.parent)` → escrever resultado mergeado (`\\n` join, sem adicionar newline extra além do existente), `fsync`, `chmod 0o600`, `os.replace(tmp, destino)` (atómico mesmo filesystem). Recusar se destino antes ou resultado não tiver piso (já validado). `chmod 600` no destino só no caminho de escrita; no-op idempotente não toca. Alternativa `cp` + `mv` do patch rejeitada ( `_Avoid`).

8. **Idempotência sem mutação.**
   Comparar `resultado_bytes` com `destino_bytes` antes de backup/mv: se idêntico (merge não mudou nada) → exit 0 sem backup novo, sem `mv`, sem `chmod` (AC1 segunda corrida). Comparação binária (inclui comentários/ordem) para não reescrever à toa. Alternativa “sempre bak” rejeitada (Q4).

9. **EACCES e atomicidade.**
   Qualquer `open` com `PermissionError` → exit ≠0 sem criar/truncar destino nem bak. `mkstemp` em `destino.parent` garante mesmo filesystem para `replace`. Alternativa tmp em `/tmp` rejeitada (cross-fs não atómico).

10. **Saída sem valores + testes em tmp.**
    Stdout/stderr só nomes de chaves, contagens e paths; nunca `VALUE`. Testes em `backend/tests/test_bootstrap_env.py` (ou `tests/`) usando `tmp_path` fixtures; asserts cobrem AC1–AC11; nenhum teste abre `backend/.env` ou `/srv/apps/...` real para escrita. CI já roda `pytest` com `DATABASE_URL` fake; este card não muda loader.

11. **Doc `docs/monitor-telegram-alerts.md`.**
    Secção curta DEV vs PROD: um bot = um `setWebhook`; `setWebhook` para PROD invalida DEV; vars `MONITOR_TELEGRAM_BOT_TOKEN` / `TELEGRAM_WEBHOOK_SECRET` / `MONITOR_TELEGRAM_BOT_USERNAME` / `MONITOR_TELEGRAM_ALERTS_ENABLED` vão para `<checkout>/backend/.env` (o que o unit faz `source`); home raiz `BINANCE_*` não é usado para Telegram. Link para #747 e para unit `source`.

## Risks / Trade-offs

- [Operador passa `--file` ao home errado (raiz vs backend)] → Mitigação: `--file` explícito + doc dos dois homes; script não adivinha nem dual-write; Telegram no home errado não chega ao unit (aceito).
- [Destino wiped: script recusa; restore manual] → Mitigação: mensagem “piso ausente; restore via bak/.env.wiped-20260827” sem valores; não auto-restaura.
- [Backup colisão no mesmo segundo] → Mitigação: sufixo `.<n>` incremental; `chmod 600` no bak.
- [Parser `KEY=VALUE` com `export`/`quotes` diverge de `source` em casos raros] → Mitigação: suite cobre `export`, `# comment`, `;`, quoting simples, chave repetida; documentar limitação.
- [Stdin TTY vs pipe vazio ambíguo] → Mitigação: `isatty` + `select`; TTY sem dados = patch vazio → exit ≠0 sem escrita (Q6).
- [EACCES `root:root 600` em PROD] → Mitigação: fail-closed sem truncar; operador roda com `sudo -u root` ou owner correto.
- [Idempotência binária vs semântica] → Mitigação: comparação inclui comentários; segunda corrida com mesmo patch não reescreve mesmo se valor já igual.

## Migration Plan

Apply (branch `card-752-*` em `Status=Pronto para Dev`):
1. Criar `ops/bootstrap_env.py` + `chmod +x`, sem tocar dotenv reais.
2. Criar `backend/tests/test_bootstrap_env.py` (tmp fixtures, AC1–AC11).
3. Atualizar `docs/monitor-telegram-alerts.md` (secção DEV vs PROD, webhook único, home backend).
4. `pytest backend/tests/test_bootstrap_env.py -q` + `openspec validate`.
5. Code Review local (`diff-reviewer`+`code-reviewer` no diff `origin/develop...HEAD`), commit SHA, push, `Status=QA`→`Done` após `qa-gate` verde, `./restart` e validação URL; `Pronto` só em release lote com `release-guard`.

Rollback: apagar `ops/bootstrap_env.py` e reverter doc; sem migração de banco.

## Open Questions

Nenhuma bloqueante (fronteira vazia após Round 2). Residual: nome final `bootstrap_env.py` vs `bootstrap-env.py` fica fechado neste design (`bootstrap_env.py`); symlink `bootstrap-env` opcional no Apply se `ops/` precisar de hífen.

## UI impact

**none** — script CLI operacional + doc. Sem rota, componente ou estado visual.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite é CLI exit codes, preservação de ficheiro, backup e doc.

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Harness de processo não exige pipeline Impeccable nesta coluna; `DESIGN.md`/`DESIGN.md` canónico permanece autoridade visual para telas futuras.

## Design Critique

- P0: nenhum — fail-closed, piso, merge append-only, backup atómico e idempotência cobrem outage; `q_git` Guard permanece bloqueando Agent em `develop`/`main`.
- P1: nenhum — parser `export`/`#`/`;`/repetida last-wins alinhado ao `source`; EACCES sem truncar; stdin TTY vs pipe tratado.
- P2 (accepted-residual): operador pode apontar `--file` ao home errado (raiz vs backend) — mitigado por `--file` explícito + doc dos dois homes; destino wiped exige restore manual via bak (por desenho).
- P3 (accepted-residual): nome `bootstrap_env.py` vs `bootstrap-env.py` — fechado em `bootstrap_env.py` com symlink opcional; não afeta contrato.

Riscos não bloqueantes: nenhum P0/P1 aberto; UI impact `none` sem superfície visual; Impeccable/Snapshot N/A justificado abaixo.

Referências: `openspec/changes/card-752-bootstrap-env-append-only/proposal.md` + `specs/bootstrap-env-append-only/spec.md` + issue #752 (DoD completo).
Prototype: N/A — `UI impact: none`, script CLI + doc (ver `## Prototype`).
Snapshot (git-tracked; Gist não envia esta pasta): N/A justificado para `UI impact: none`.

Design Agent verdict: PASS

## Apply contract

- Editar só: `ops/bootstrap_env.py`, `backend/tests/test_bootstrap_env.py` (ou `tests/` mirror), `docs/monitor-telegram-alerts.md`, `openspec/changes/card-752-bootstrap-env-append-only/specs/**`, `openspec/specs/**` via archive.
- Zero `frontend/src/`, zero `backend/app/config.py` loader, zero `ops/systemd/*`, zero `main` direto, zero `Environment=` com secret.
- Script MUST: `--file` required, `--from-file`/`stdin` com merge file→stdin, exit ≠0 sem escrita quando patch sem `KEY=VALUE`, merge `destino∪patch`, piso imutável, preservar comentários/ordem/sufixo, bak timestamped `chmod 600`, tmp `mkstemp` no mesmo dir + `os.replace` + `chmod 600`, idempotência sem bak/mv, só nomes/contagens/paths na saída.
- Testes MUST usar `tmp_path` e cobrir AC1–AC11 sem tocar dotenv reais.
- Doc MUST registar um bot = um webhook e home backend para Telegram.
