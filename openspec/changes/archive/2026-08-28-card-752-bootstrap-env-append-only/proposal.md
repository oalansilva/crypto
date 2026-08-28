## Why

O operador e os utilizadores de PROD sofrem outage (backend em loop, health público 502) quando um bootstrap de secrets substitui o ficheiro dotenv por um tmp incompleto — como no closeout da release 2026-08-27 (#747), em que `grep` sem permissão + `mv` de 4 linhas Telegram apagou `DATABASE_URL` / `JWT_SECRET` em `/srv/apps/prod/criptofarol/source/backend/.env`. É necessário um bootstrap que só acrescente/atualize chaves sem substituir o ficheiro, para não derrubar PROD ao ligar Telegram ou qualquer env nova.

## What Changes

- Script versionado em `ops/` (fail-closed) com `--file` obrigatório: operador aponta o dotenv concreto (DEV ou PROD), sem default de path; destino ausente → exit ≠ 0 e não cria dotenv do zero.
- Patch via `--from-file` e/ou stdin (`KEY=VALUE`); sem `--set` na argv; se `--from-file` e stdin vêm juntos, aplicar ficheiro primeiro e stdin por cima (stdin ganha no patch dentro do patch).
- Patch sem nenhuma chave `KEY=VALUE` (ficheiro vazio, só comentários/linhas vazias, ou stdin TTY/pipe vazio) → exit ≠ 0, sem escrita.
- Merge por chave: resultado = destino ∪ patch; nenhuma chave do destino desaparece; piso imutável: se o patch trouxer `DATABASE_URL` ou `JWT_SECRET` com valor diferente do destino → exit ≠ 0, sem backup, sem `mv`; omitir piso no patch ou repetir mesmo valor é válido; demais chaves do patch: update-or-insert.
- Preservar comentários, linhas vazias e ordem do destino; chaves já presentes mudam só o valor na linha (sufixo de comentário na mesma linha permanece); chaves novas no fim, na ordem efetiva do patch.
- Backup timestamped do destino antes de qualquer escrita (mesmo diretório; padrão `.env.bak-YYYYMMDD…` com hora para não colidir no mesmo dia; `chmod 600` no bak).
- Replace atómico só do resultado mergeado (tmp no mesmo filesystem); recusar `mv` se o destino antes ou o resultado não tiverem o piso (presente e não vazio); `chmod 600` no destino após escrita (não no no-op).
- Merge idêntico ao destino (segunda corrida com mesmo patch já aplicado) → exit 0, sem backup novo, sem `mv`, sem mutação.
- Testes em tmp; nunca tocar nos dotenv reais de DEV/PROD no CI/pytest; saída só nomes de chaves / contagens / paths, nunca valores.
- Doc curta em `docs/monitor-telegram-alerts.md`: DEV vs PROD; um bot = um webhook (`setWebhook` para PROD tira o DEV); vars Telegram vão para o dotenv do backend (o que o unit faz `source`).
- `UI impact: none`.

## Capabilities

### New Capabilities

- `bootstrap-env-append-only`: bootstrap de dotenv fail-closed, append-only por chave, com piso `DATABASE_URL`+`JWT_SECRET` imutável, preservação de comentários/ordem, backup timestamped e replace atómico; cobre o script em `ops/` e o contrato de CLI descrito acima.

### Modified Capabilities

- (nenhuma) — doc em `monitor-telegram-alerts` é atualização de documentação operacional, não mudança de REQUIREMENTS de spec existente; demais specs permanecem inalteradas.

## Impact

- Cria `ops/bootstrap-env.py` (ou `ops/bootstrap-env.sh` — decisão no design; nome final em `ops/` e documentado no spec) e testes em `backend/tests/` ou `tests/` usando fixtures tmp.
- Altera `docs/monitor-telegram-alerts.md` (seção DEV vs PROD, webhook único, home backend para vars Telegram).
- Não toca `backend/app/config.py` loader (`load_dotenv` com `override=False`), units systemd (`Environment=`), `.env` reais, banco, frontend, nem rotaciona `JWT_SECRET` ou cria bot separado (fora do escopo).
- Riscos: operador pode passar `--file` ao home errado (raiz vs backend); destino wiped requer restore manual via bak; EACCES no destino (não-owner) → exit ≠ 0 sem truncar.
