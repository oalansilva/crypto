## Context

Card [#968](https://github.com/oalansilva/crypto/issues/968) (Operação, P1). Briefing = issue grelhado. Q2=B, Q3=A, Q4=A — este Design não as reabre. Q1 ficou sem A/B («não percebi»); o *como* fecha aqui.

Factos no disco (worktree, 18/09): overlay PROD lista backend, frontend, leads, runtime-worker, candle-writer e telegram-alert-scan; **não** lista `criptofarol-prod-discovery-worker`. DEV lista o worker de varredura. Units em `ops/systemd/`: discovery-worker e runtime-worker `Type=simple`; candle-writer e telegram-alert-scan `Type=oneshot`. `./restart` é só o fecho DEV canónico e já reinicia o discovery-worker DEV. Docs de setembro (`docs/release-2026-09-*.md`) omitem discovery-worker em `services=`; agosto ainda o listava. `scripts/release-guard` exige `PROD_DEPLOY_EVIDENCE` não vazio no `post`; **não** recusa `services=` incompleto. Overlay `release.restart: ./restart` não é o caminho PROD.

UI impact: none
live_route: N/A operação de release/PROD (units systemd de longa duração); sem tela de produto
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar `/monitor` `/favorites` `/combo/discovery` `/combo/select` `landing`. Prototype N/A. Impeccable N/A.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

- **Longa duração:** unit `Type=simple` / processo persistente que mantém código do produto em memória (site, API, captação, worker de runtime, worker de varredura).
- **Job de uma execução / oneshot:** unit `Type=oneshot` disparado por timer; carrega código em cada corrida (escrita de candles, scan de alerta Telegram).
- **Inventário de produção:** `.covenant-flow/overlay.yaml` `environments.prod` — fonte da lista do publish e da nota do dia, não a memória do chat.
- **Janela do publish:** a mesma janela do deploy PROD (source no commit, migrate, build, restart, health).
- **Evidência:** `PROD_DEPLOY_EVIDENCE` no formato `<commit> services=<svc,...> url=<url-pública>`.

## Goals / Non-Goals

**Goals:**

- Completar o inventário PROD com o worker de varredura junto dos demais de longa duração.
- Na janela do publish, reiniciar **todos** os de longa duração desse inventário para a última versão.
- `post` recusa visível se `services=` omitir um de longa duração, ou se um de longa duração **a correr** ainda estiver no código velho; cards não vão a Pronto. Disco e o que já reiniciou ficam.
- Processo de longa duração que não fique a correr: fecho pode PASS se site e API respondem (Q2 B); incidente à parte.
- Nota `docs/release-<data>.md` lista os reiniciados a partir do inventário; oneshot constam como job/timer à espera, não como restart da janela.

**Non-Goals:**

- Mudar `./restart` DEV.
- Caminho novo de restart PROD fora do fecho de release.
- Reiniciar PostgreSQL, proxy, ou oneshot só por simetria.
- Cronometrar Descoberta / provar comportamento novo da varredura nesta janela (Q3 A).
- Desfazer disco ou rollback quando o fecho recusa.
- Produto `backend/**` / `frontend/src/**`. HTML de protótipo.

## Decisions

1. **Q1 *como* = lista canónica no overlay, classificada — não processo vivo fora da lista.** `environments.prod.services` continua o inventário de units de produto; **acrescenta** `criptofarol-prod-discovery-worker.service`. Chave irmã `environments.prod.oneshot_services` lista os jobs de uma execução já no overlay (`criptofarol-prod-candle-writer.service`, `criptofarol-prod-telegram-alert-scan.service`) e MUST ser subconjunto de `services`. Janela do publish = `services` − `oneshot_services` (hoje: backend, frontend, leads, runtime-worker, discovery-worker). O publish **não** varre o host à procura de `Type=simple` fora do overlay. Unit novo de produto entra primeiro no overlay, não no chat. Rejeitado: scanner vivo no fecho (caminho novo). Rejeitado: reiniciar `services` inteiro incluindo oneshot.

2. **Restart na janela usa o fecho já existente.** No source PROD, `systemctl restart` dos units da janela (mesmo gesto de setembro, lista agora completa). `./restart` DEV intocado. Sem script/comando novo de restart PROD fora do fecho. Overlay on-demand deixa de dizer «services PROD afetados» como lista memorizada; manda derivar a janela do inventário. Skill `covenant-flow-environments` só o recorte se o pin ainda mandar reiniciar `services[]` sem subtrair oneshot. `AGENTS.md` always-on MUST NOT crescer.

3. **`post` recusa evidência incompleta (Q4 A, primeiro corte).** Com overlay PROD presente, o `post` (e o `pre` quando já exige evidência) parseia `services=` (com ou sem sufixo `.service`). Falta de qualquer unit da janela = blocker visível; cards não são publicados. Nomes extra (oneshot) = aviso, não blocker. Evidência no estilo 16/09 (quatro units, sem varredura) MUST falhar depois deste card.

4. **`post` recusa código velho em processo a correr (Q4 A, segundo corte).** Para cada unit da janela que **está activo**, se o arranque do processo (`ExecMainStartTimestamp` ou equivalente systemd) for anterior à janela do deploy desta evidência, blocker visível. Não desfaz disco. P3: campo systemd exacto e âncora da janela (tempo do reset PROD / evidência). Consulta systemd no mesmo host do fecho; não é caminho novo de restart.

5. **Processo parado não bloqueia o fecho (Q2 B).** Unit da janela inactive/failed depois do restart: **não** é blocker do `post` se `release.health_url` (site/API) responder. Não exige o processo de volta. Incidente à parte. Continua a exigir o nome desse unit em `services=` (a janela declarou o restart).

6. **Nota do dia a partir do inventário.** `docs/crypto-overlay.md` (e o molde da doc canónica) manda listar os reiniciados = janela do overlay, e os oneshot = `oneshot_services` como job/timer à espera. Proibido copiar a lista do chat ou de um lote de setembro. Não reescrever as docs de 16/09 como entrega deste card.

## Risks / Trade-offs

- [Risco] Agente ainda reinicia `services[]` inteiro e dispara oneshot na janela → Mitigação: `oneshot_services` + overlay doc; recorte da skill só se o pin duplicar; `post` não exige oneshot em `services=`.
- [Risco] `oneshot_services` ausente ou dessincronizado do overlay → Mitigação: MUST ser subconjunto de `services`; janela vazia ou sem discovery-worker é blocker; P3 validação em `overlay.py`.
- [Risco] Consulta systemd no `post` falha (sem root) → Mitigação: fail-closed no corte de código velho **quando o unit está activo e o timestamp é ilegível**; Q2 B cobre o caso parado. P3: como o teste injeta o timestamp.
- [Risco] Fixtures do guard usam `services=app` sintético → Mitigação: testes deste card cobrem o overlay real da worktree; fixtures sintéticas passam a declarar janela mínima ou usam overlay de teste. P3.
- [Trade-off] Unit de longa duração a correr fora do overlay não é encontrado neste card — aceite Q1 (lista, não vivo); inventário 18/09: nenhum outro unit de produto.
- [P3 Apply] Nome exacto da chave YAML; normalização `.service`; campo systemd; âncora temporal da janela; recorte pin da skill; ajuste das fixtures `services=app`.

## Prototype

N/A — card sem tela: operação de release/PROD (units systemd de longa duração). Sem rota autenticada, sem landing, sem HTML, sem clonar catálogo, sem `frontend/public/prototypes/`. Impeccable / Playwright visual / `DESIGN.md` = N/A justificado. Nunca emprestar `/monitor` `/favorites` `/combo/discovery` `/combo/select` `landing`.

## Impeccable

N/A — `UI impact: none`; não há superfície visual nem pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana permanecem.

## Apply contract

- `.covenant-flow/overlay.yaml`: acrescentar `criptofarol-prod-discovery-worker.service` a `environments.prod.services`; declarar `environments.prod.oneshot_services` com candle-writer e telegram-alert-scan.
- `docs/crypto-overlay.md`: janela do publish = inventário longa duração; oneshot fora; nota do dia a partir do overlay; MUST NOT lista memorizada; MUST NOT crescer `AGENTS.md`.
- `scripts/release-guard`: `post` (e `pre` quando já exige evidência) recusa `services=` incompleto da janela; recusa unit da janela activo com arranque anterior à janela; Q2 B: parado + health ok não bloqueia; MUST NOT rollback / MUST NOT mutar refs.
- `backend/tests/integration/test_release_guard.py` (ou equivalente): evidência 16/09 incompleta falha; janela completa passa; oneshot extra = aviso; processo parado + health ok passa; activo em código velho falha.
- Skill `covenant-flow-environments` MAY recorte se o pin mandar reiniciar `services[]` sem subtrair oneshot. `./restart` DEV MUST NOT mudar. Zero `backend/` produto / `frontend/src/**`. Sem HTML.
- A secção de crítica fica para o pai depois do crítico. Autor não submete Design / Gist / T5.

## Migration / Rollout

N/A de dados. Depois de Pronto para Dev: Apply nesta branch; o **próximo** publish PROD usa a janela completa. Rollback deste card = reverter overlay + predicados do guard. Recusa de fecho **não** desfaz o que já foi ao disco.

## Open Questions

Nenhuma — Q2–Q4 fechadas no issue; Q1 fechada na decisão 1. P3 acima são detalhe de Apply.

## Design Critique

Crítico isolado (sem-tela, 1 critic, sem transcript). Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: sem rework (zero P0/P1 de produto/escopo). Snapshot: `.impeccable/critique/968-card-968-prod-restart-long-running.md`.

Token check:
- `UI impact: none` — linha própria.
- `live_route: N/A operação de release/PROD (units systemd de longa duração); sem tela de produto` — ausência + justificativa; nunca `/monitor` `/favorites` `/combo/discovery` `/combo/select` `landing`.
- `surface: new` — linha própria; isenta catálogo (par `live_route: N/A`).
- Prototype N/A justificado. Impeccable N/A justificado. clone_gate PASS.

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — chave YAML `oneshot_services` + subconjunto de `services`; campo systemd / âncora da janela; fixtures `services=app` e injecção de timestamp; recorte pin da skill `covenant-flow-environments` + `pre` quando já exige evidência.
- **Disposition:** Q2=B Q3=A Q4=A intactas. Q1 *como* = lista overlay classificada (`services` − `oneshot_services`), não scanner vivo. Janela do publish = mesmos units de longa duração no fecho já existente, com o worker de varredura no inventário PROD. `post` recusa `services=` incompleto e código velho em processo activo; processo parado + health ok não bloqueia. Sem DEV restart, caminho novo, oneshot por simetria, cronómetro da Descoberta, rollback, UI. Sem rework.
- **Riscos não bloqueantes:** P3 acima.

Design Agent verdict: PASS

- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: design-critic → Grok 4.6 (cursor-grok-4.6-high)`
- html generated vs copied: N/A vs N/A
- spawns: 2
