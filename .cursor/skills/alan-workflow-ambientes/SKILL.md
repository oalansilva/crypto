---
name: alan-workflow-ambientes
description: "Use esta skill junto com alan-workflow quando trabalhar no ambiente Oracle do Alan com DEV e PROD separados: Cripto Farol, Clara Voice, Hermes, bancos, URLs, services systemd, Caddy, releases, homologacao e validacao de runtime. Use sempre que a tarefa puder afetar DEV, PROD, publicacao, release, deploy, banco, servico, dominio, Hermes ou validacao publica."
---

# Alan Workflow Ambientes

## Papel

Canônico neste repo: `.cursor/skills/alan-workflow-ambientes/` no GitHub (não `~/.codex` nem hermes). Drive/Docs do cripto: siga o `AGENTS.md` do repo.

Esta skill complementa `alan-workflow`. Ela decide **onde agir**: `DEV`, `PROD` ou `DEV->PROD`.

`alan-workflow` continua mandando em cards, status, OpenSpec, Git, review, release e evidencia.
Esta skill manda em ambiente, paths, services, URLs, bancos e guardrails de producao.

## Regra Central

Antes de qualquer acao em Cripto, Clara ou Hermes, resolva o alvo:

```text
Ambiente alvo: DEV | PROD | DEV->PROD
Projeto: criptofarol | clara | hermes
Tipo: implementacao | correcao | release | operacao | diagnostico
```

Se Alan nao disser `producao`, `prod`, `release`, `publicar`, `subir lote`, `corte`, `dominio final` ou `hotfix em producao`, assuma **DEV**.

Nunca altere PROD a partir de um pedido generico como `implemente`, `corrija`, `faça o card` ou `teste`.

OpenClaw **nao** e runtime ativo. Nao operar `openclaw-gateway.service` nem a porta `18789` como caminho corrente. Referencias a OpenClaw nesta skill sao historicas.

## Mapa Atual

Inventario conferido no host (systemctl/ss, 2026-08-17). Portas internas DEV do Cripto **nao** sao 8003/5173 — essas pertencem ao PROD neste host.

### Hermes (runtime de agente)

Hermes e o runtime ativo de agente. Componentes sao independentes; reinicie so o unit afetado.

| Componente | Unit | Notas |
| --- | --- | --- |
| API Server | processo em `127.0.0.1:8642` | `POST /v1/responses` (OpenAI Responses). Auth opcional via bearer. |
| Telegram | `hermes-telegram.service` | Gateway Telegram |
| SemParar | `hermes-semparar.service` | Gateway Telegram profissional |
| Clara DEV API | `hermes-clara-dev-api.service` | `hermes gateway run --accept-hooks`; `HERMES_HOME=/root/.hermes-clara-dev-api` |
| Dashboard | `hermes-dashboard.service` | `127.0.0.2:9119`; `HERMES_HOME=/root/.hermes` |
| Second Brain sync | `hermes-second-brain-sync.service` + timer | Ingestao; inativo por padrao |
| Second Brain alert | `hermes-second-brain-sync-alert.service` | Alerta Telegram de falha de sync |
| Gateway (ubuntu) | `hermes-gateway.service` | Template instalado; `HERMES_HOME=/home/ubuntu/.hermes` |

CLI: `/usr/local/bin/hermes`. Homes: `/root/.hermes` (dashboard), `/root/.hermes-clara-dev-api` (Clara DEV), `/home/ubuntu/.hermes` (gateway ubuntu). Nao usar `/root/.openclaw`.

### Cripto Farol DEV

- Source: `/srv/apps/dev/criptofarol/source`
- URL: `https://dev.criptofarol.com.br`
- Banco app: `crypto_app_dev`
- Banco workflow: `crypto_workflow_dev`
- Backend: `criptofarol-dev-backend.service` (interno `127.0.0.1:8004`)
- Frontend: `criptofarol-dev-frontend.service` (interno `127.0.0.1:5175`)
- Discovery dispatcher: `criptofarol-dev-runtime-worker.service` (`RUN_DISCOVERY_OUTBOX_DISPATCHER=1`)
- Discovery Celery: `criptofarol-dev-discovery-worker.service` (fila `discovery`)
- Candle writer: `criptofarol-dev-candle-writer.service` + timer
- Uso: implementacao, validacao tecnica, teste de Alan e homologacao.
- Unico source DEV canonico. Nao recriar nem usar `/root/crypto`.

### Cripto Farol PROD

- Source: `/srv/apps/prod/criptofarol/source`
- URL: `https://criptofarol.com.br`
- Banco app: `crypto_app`
- Backend: `criptofarol-prod-backend.service` (interno `127.0.0.1:8003`)
- Frontend: `criptofarol-prod-frontend.service` (interno `127.0.0.1:5173`)
- Leads: `criptofarol-prod-leads.service`
- Runtime worker: `criptofarol-prod-runtime-worker.service` (refresh de favoritos; dispatcher de discovery so quando o card/release correspondente ligar a flag)
- Candle writer: `criptofarol-prod-candle-writer.service` + timer
- Uso: somente release, publicacao, operacao autorizada ou hotfix explicitamente autorizado.

### Clara DEV

- Source: `/srv/apps/dev/clara-realtime/source`
- URL: `https://dev-clara.criptofarol.com.br`
- Service: `clara-dev.service`
- Porta interna: `13001`
- Consultas de agente: Hermes API Server (`127.0.0.1:8642`), nao OpenClaw Gateway.

### Clara PROD

- Source: `/srv/apps/prod/clara-realtime/source`
- URL: `https://clara.criptofarol.com.br`
- Service: `clara-prod.service`
- Porta interna: `3001`

## Fluxo Padrao

### Antes de escolher o workspace

1. Para Cripto Farol, manter somente dois caminhos operacionais: DEV e PROD.
2. DEV: usar `/srv/apps/dev/criptofarol/source` para implementacao, validacao, documentacao versionada, funil, analytics e assets sociais.
3. PROD: usar `/srv/apps/prod/criptofarol/source` somente com pedido explicito de release/producao.
4. Nao recriar nem usar `/root/crypto` como clone auxiliar, social archive ou workspace temporario.
5. Se aparecer trabalho temporario do Cripto Farol fora de DEV/PROD, inventariar e **nao apagar** o path sem autorizacao explicita de Alan. Mover o que nao pode ser perdido para o ambiente canonico; delete so depois da autorizacao.
6. Para o procedimento detalhado de unificacao, leia `references/criptofarol-two-path-workspace.md`.
7. Para funil, UTMs, leads, PostHog, Metabase ou analytics social-site-lead, leia `references/criptofarol-funnel-attribution.md` antes de mexer.

### Implementacao

1. Resolver ambiente como DEV.
2. Usar repo/source DEV conforme regra do projeto.
3. Seguir `alan-workflow`: card, OpenSpec, branch/worktree, review e testes.
4. Validacao intermediaria: reiniciar somente o unit DEV afetado.
5. Validar em URL/service DEV.
6. Fechamento tecnico (`Done`): no Cripto Farol DEV usar o `./restart` canonico em `/srv/apps/dev/criptofarol/source` (migrations, build, workers de discovery, backend/frontend). Nao usar restart parcial da era OpenClaw como prova de Done.
7. Aguardar teste de Alan para `Homologado`.

### Validacao Tecnica / Done

1. Ambiente padrao: DEV.
2. Done do Cripto Farol: `./restart` no source DEV canonico.
3. Validar checks, OpenSpec quando aplicavel, services e URL DEV (`https://dev.criptofarol.com.br` e health interno 8004/5175).
4. QA visual versionado: seguir `alan-workflow` Visual QA no DEV Linux.
5. Nao reiniciar PROD.
6. Nao mover para `Pronto`.

### Homologacao

1. Ambiente: DEV.
2. Nao reiniciar por padrao.
3. Reiniciar DEV somente se uma correcao nova for aplicada para o teste de Alan.
4. Quando Alan aprovar, mover para `Homologado`; isso nao autoriza PROD automaticamente.

### Release DEV->PROD

Fail-closed. Exigir pedido explicito de Alan: `release`, `publicar`, `subir para producao`, `subir lote` ou equivalente.

Evidencia minima antes de `Pronto`:

1. Inventario Git/worktrees/stash/PRs/OpenSpec/board.
2. Pacote so com cards `Homologado` (ou excecao explicita).
3. SHA publicado em `main`.
4. Source PROD no commit publicado (`git fetch && git reset --hard origin/main` no path PROD).
5. `alembic upgrade head` no banco PROD.
6. Build do frontend com `VITE_APP_ENV=production`.
7. Restart somente dos services PROD afetados.
8. URL publica `https://criptofarol.com.br` validada.
9. Registrar evidencia (`<commit> services=<svcs> url=<url>`).

### Realinhamento Pos-Release

1. alinhar DEV depois da publicacao;
2. reiniciar somente services DEV afetados (Done posterior usa `./restart`);
3. validar URL/service DEV;
4. reportar PROD e DEV separadamente.

### Operacao/Incidente em PROD

PROD pode ser tocado diretamente somente se Alan pedir explicitamente ou se houver incidente operacional claro.

Mesmo em incidente: leia antes; preserve backup; menor ponto reversivel; reinicie so services PROD afetados; valide endpoint PROD; backporte para DEV depois.

## Politica De Restart

Nunca reinicie DEV e PROD por habito. Reinicie somente o que foi afetado.

### Cripto Farol — intermediario (nao e Done)

- Frontend DEV: `criptofarol-dev-frontend.service`
- Backend DEV: `criptofarol-dev-backend.service`
- Discovery dispatcher DEV: `criptofarol-dev-runtime-worker.service`
- Discovery Celery DEV: `criptofarol-dev-discovery-worker.service`
- Frontend PROD: `criptofarol-prod-frontend.service`
- Backend/API PROD: `criptofarol-prod-backend.service`
- Leads PROD: `criptofarol-prod-leads.service`
- Runtime worker PROD: `criptofarol-prod-runtime-worker.service`

### Cripto Farol — Done tecnico em DEV

`/srv/apps/dev/criptofarol/source/restart` (canonico). Cobre migrations, build, candle-writer timer, discovery workers, backend e frontend.

### Clara

- Clara DEV: `clara-dev.service`
- Clara PROD: `clara-prod.service`

### Hermes (por componente)

- API Server / `8642`: o processo que serve `POST /v1/responses`
- Telegram: `hermes-telegram.service`
- SemParar: `hermes-semparar.service`
- Clara DEV API: `hermes-clara-dev-api.service`
- Dashboard: `hermes-dashboard.service`
- Second Brain: `hermes-second-brain-sync.service` / alert
- Gateway ubuntu: `hermes-gateway.service` somente se esse unit for o afetado

Nao reiniciar "Hermes inteiro" por habito. Nao reiniciar OpenClaw.

### Caddy

Caddy e borda unica. Preferir `reload` a restart completo. Validar so os dominios afetados; DEV e PROD se o bloco for compartilhado.

### Quando Os Dois Ambientes Entram

- Caddy ou TLS comum;
- segredo/config global usado pelos dois;
- dependencia global do host;
- release que exige realinhar DEV depois;
- hotfix PROD que precisa ser aplicado tambem em DEV;
- componente Hermes compartilhado (Telegram, dashboard, API 8642).

## Evidencia Minima Por Ambiente

### DEV

- `git status -sb` classificado;
- comando de teste/check executado;
- `./restart` no Done do Cripto, ou unit direcionado no meio do card;
- service local ativo;
- URL DEV respondendo;
- OpenSpec da change validado quando aplicavel.

### PROD

- inventario de release;
- SHA publicado;
- migrations + build de producao;
- services PROD afetados reiniciados (ou justificativa);
- URL publica validada;
- `Pronto` so apos prova em PROD.

## Linguagem De Status

- `validado em DEV`: tecnico, ainda nao publicado.
- `aguardando homologacao`: Alan ainda precisa testar/aprovar.
- `homologado`: Alan aprovou em DEV.
- `publicado em PROD`: release aplicada e endpoint PROD validado.
- `Pronto`: publicado em PROD com evidencia e card atualizado.

## Smoke read-only (sem secrets)

```bash
systemctl is-active \
  criptofarol-dev-backend.service criptofarol-dev-frontend.service \
  criptofarol-prod-backend.service criptofarol-prod-frontend.service \
  clara-dev.service clara-prod.service \
  hermes-telegram.service hermes-dashboard.service hermes-clara-dev-api.service
ss -ltn | grep -E '8004|5175|8003|5173|13001|3001|8642|9119'
curl -fsS -o /dev/null -w 'dev-health:%{http_code}\n' https://dev.criptofarol.com.br/api/health
curl -fsS -o /dev/null -w 'prod-health:%{http_code}\n' https://criptofarol.com.br/api/health
```

Nao imprimir Environment=, tokens, `.env` ou journal completo.

## Bloqueios

Pare e reporte se:

- o ambiente alvo estiver ambiguo e a acao puder afetar PROD;
- PROD e DEV apontarem para o mesmo banco, env ou volume sem justificativa clara;
- um agente tratar OpenClaw/`18789` como runtime ativo;
- houver escrita concorrente em DEV e PROD no mesmo recurso;
- uma validacao publica contradisser o service local;
- um segredo aparecer em output;
- um path temporario for candidato a delete sem autorizacao explicita de Alan.
