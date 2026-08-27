## 1. Script fail-closed `ops/bootstrap_env.py`

- [ ] 1.1 Criar `ops/bootstrap_env.py` com `argparse` (`--file` required, `--from-file` opcional, sem `--set`), shebang + `chmod +x`, leitura de `--from-file` e stdin (file→stdin, stdin ganha), parser `KEY=VALUE` alinhado ao `source` (strip `export`, ignora `#`/vazias, último valor vence, chaves comentadas não contam para piso)
- [ ] 1.2 Implementar validação de piso (`DATABASE_URL`+`JWT_SECRET` presente e não-vazio após strip no destino antes e no resultado; patch com piso diferente → exit ≠0 sem bak/mv; patch vazio → exit ≠0 sem escrita; EACCES → exit ≠0 sem truncar)
- [ ] 1.3 Implementar merge `destino ∪ patch` com preservação de comentários/linhas vazias/ordem, update só valor na linha com sufixo `#`/`;` preservado, chaves novas append no fim na ordem do patch
- [ ] 1.4 Implementar backup timestamped `.env.bak-YYYYMMDD-HHMMSS[.<n>]` no mesmo dir + `chmod 600` no bak, tmp `mkstemp(dir=destino.parent)` + `fsync` + `chmod 600` + `os.replace` atómico, idempotência binária (sem bak/mv/chmod quando idêntico), `chmod 600` no destino após escrita, saída só nomes/contagens/paths (nunca valores)

## 2. Testes em tmp (nunca dotenv reais)

- [ ] 2.1 Criar `backend/tests/test_bootstrap_env.py` usando `tmp_path` fixtures cobrindo AC1–AC11: AC1 dupla corrida + preservação de `WORKFLOW_DATABASE_URL`, AC2/AC3 destino sem piso, AC4 patch sem piso, AC5 piso diferente, AC6 destino inexistente/sem `--file`, AC7 file+stdin mesma chave, AC8 patch vazio, AC9 comentários/ordem/sufixo, AC10 modo 600 + bak timestamped, AC11 só tmp (nenhum teste escreve dotenv real DEV/PROD)
- [ ] 2.2 Rodar `pytest backend/tests/test_bootstrap_env.py -q` e `openspec validate --all` (ou `openspec status --change`); garantir `pytest` verde sem abrir `backend/.env` reais

## 3. Doc operacional

- [ ] 3.1 Atualizar `docs/monitor-telegram-alerts.md` com secção DEV vs PROD: um bot = um `setWebhook` (PROD tira DEV), vars `MONITOR_TELEGRAM_BOT_TOKEN`/`TELEGRAM_WEBHOOK_SECRET`/`MONITOR_TELEGRAM_BOT_USERNAME`/`MONITOR_TELEGRAM_ALERTS_ENABLED` no `<checkout>/backend/.env` (home que o unit faz `source`), home raiz para `BINANCE_*`; `UI impact: none` (sem protótipo)

## 4. Portas de design (skill alan-workflow / design-critic)

- [ ] 4.1 Declarar `UI impact: none` com justificativa (script CLI + doc, sem superfície visual) e registar `Prototype: N/A` / `Impeccable: N/A` justificado; não pedir browser gate
- [ ] 4.2 Publicar Gist `crypto openspec card-752-bootstrap-env-append-only` via `publish-openspec-card-artifacts.sh` (sem HTML no Gist) e comentar card #752 com change + gist_url + comentário do board
