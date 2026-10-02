## Context

Card **#1075**, Status=Design. Briefing = issue grelhada (Problema, História, Entra, Não entra) copiada em `proposal.md`. Sem reentrevista.

O módulo Scalp BTCUSDT vive em `/monitor` (`ScalpModule` entre o `page-sub` e os KPIs). Em produção o interruptor nunca ligou (0 estados, 0 fills); as tabelas `scalp_user_states` e `scalp_fills` existem. No DEV o código do #1045 e do #1070 já está na `develop` (PRs mergeadas): diagnóstico, recalibração, 3 tabelas extra, laço a perguntar ao Jev, 0 fills. Alan já cancelou #1045 e #1070 no board; cancelar o card não apaga o código. O Jev só serve este scalper. Operar, Carteira, candles e o runtime-worker (fila da Descoberta e favoritos) são outra coisa.

Catálogo HEAD `/monitor`: `table.signals` + Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia.

Impeccable (Operate): audience = utilizador autenticado no Monitor (e visitante na landing / leitor de Ajuda / Perfil); outcome = o módulo do scalper não aparece e o resto da tela continua; direction = clone da página viva `/monitor` + delta = ausência do módulo; `DESIGN.md` permanece autoridade visual. Copy nas outras superfícies some sem anunciar a saída.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nessas regiões. Delta: o módulo do scalper não aparece; o resto (Em posição, Saída/cobertura, KPIs, filtros) continua. Extras na mesma pasta, cada um clone da página viva + delta de copy (zero menção a scalper/scalp, sem anunciar que saiu): `landing.html` (landing v4), `ajuda.html` (`/help`), `perfil.html` (Meu Perfil), `credenciais.html` (Credenciais da Binance). Essas N páginas **não** entram no index. Nunca painel de 6 estados nem ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Some o módulo do scalper em `/monitor` (desktop e mobile). Em posição, Saída/cobertura, KPIs e filtros ficam.
- Ajuda, Perfil, Credenciais da Binance e landing v4 deixam de mencionar scalper/scalp. Sem banner, Telegram ou texto de descontinuação.
- `/api/scalp/status` responde 404. Laço, serviços, ordens `cfscalp_` e classes de banco saem. Backend e runtime-worker sobem; fila da Descoberta e favoritos continuam.
- Migração nova apaga as 5 tabelas. Migrações antigas ficam no histórico.
- Saem flags `RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*`/`TYPESAFE_*`. Depois do `./restart` o DEV sobe sem elas e sem log de diagnóstico do scalper. O Farol não pergunta ao Jev.
- Saem scripts `scalp_*`, testes e protótipos dos cards de scalper. Snapshots do Monitor regravados. Capabilities `scalp-*` retiradas; specs partilhadas deixam de citar o scalper. Changes ativas #1045 e #1070 saem de `openspec/changes/`.
- Operar, Carteira, chave Spot, candles e runtime-worker ficam.

**Non-Goals:**

- Tratar ordens abertas ou saldo na Binance deixados pelo scalper.
- Remover o runtime-worker, a chave Spot, o envio de ordens de Operar ou o armazenamento de candles.
- Apagar ou reescrever migrações antigas, ou archives OpenSpec #1001–#1043.
- Mudar o card #1074 ou qualquer outra estratégia.
- Cancelar #1045 e #1070 no board (Alan já cancelou).
- Banner, Telegram ou texto de descontinuação.
- Cancelar a conta do Jev ou apagar chaves guardadas.

## Decisions

1. **A superfície canónica é o `/monitor` que já existe, sem o módulo.** O interruptor e o painel Scalp BTCUSDT saem. A board (Em posição, Saída/cobertura, KPIs, filtros, `table.signals`, Operar) não redesenha. Não há rota nova. O index não é um painel de estados nem ANTES/DEPOIS.
   Alternativa rejeitada — **página stub «o scalper saiu»**: o Entra manda some sem aviso.
   Alternativa rejeitada — **só esconder com CSS/`hidden`**: o critério é nenhum elemento do scalper; o módulo e a API saem de verdade.

2. **Copy nas outras superfícies: cortar a menção, não anunciar a saída.** Landing v4, `/help` (fora do `OnboardingGuide`), Meu Perfil e Credenciais da Binance perdem as cláusulas de scalp. Operar com confirmação, leitura da carteira e nunca saque ficam. `OnboardingGuide` já não cita scalp (Q7=B) e não muda.
   Alternativa rejeitada — **restaurar «não é bot 24/7» / «nunca envia ordem» como absoluto**: o Operar ainda envia após confirmação; mentir sobre isso não é o pedido.

3. **API e laço saem; o runtime-worker fica.** Desligar o router `/api/scalp/*`, o `scalp_loop` na API e no worker, e os serviços `scalp_*`. O worker continua a fila da Descoberta e a atualização de favoritos. Sem chave Spot nova; a de Meu Perfil continua só para Operar/Carteira.
   Alternativa rejeitada — **deixar o router a devolver 410 com mensagem**: o critério é 404; 410 ainda é superfície do scalper.

4. **Migração nova DROP das 5 tabelas; as antigas ficam.** `scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions`, `scalp_calibration_state`. Bancos que já aplicaram as creates (DEV e PROD) não quebram. Sem backfill. Sem apagar Alembic `20260921_0001`, `20260921_0002`, `20260927_0001`.
   Alternativa rejeitada — **downgrade das migrações antigas**: o Entra manda migração nova precisamente para não reescrever histórico.

5. **Flags e Jev saem do runtime; a conta Jev não se cancela.** Units, overlay e docs de operação perdem `RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*`/`TYPESAFE_*`. Depois do `./restart` o Farol não pergunta ao Jev. Chaves guardadas e a conta TypeSafe ficam (Não entra).
   P3 de Apply: lista exacta de ficheiros `ops/systemd/*`, `restart`, overlay.

6. **Specs: capability nova `scalper-removed` + REMOVED em todas as `scalp-*` vigentes + deltas nas partilhadas.** Changes ativas `card-1045-jev-diagnostico-recalibracao` e `card-1070-scalp-jev-lucro-liquido` saem de `openspec/changes/` (o código delas sai neste card; os archives #1001–#1043 ficam). Capabilities só existentes nessas changes (`scalp-jev-diagnostico-recalibracao`, `scalp-jev-offline-backtest`, `scalp-jev-geometry-apply`) nunca são promovidas a `openspec/specs/`.
   Alternativa rejeitada — **arquivar #1045/#1070 com sync para main**: isso promoveria o scalper; o Entra manda sair de `openspec/changes/`.

7. **Protótipos e testes dos cards de scalper saem; snapshots do Monitor regravados.** Apply apaga `frontend/public/prototypes/card-*scalp*` e irmãos #1045/#1070, testes e2e desses cards, e regrava `visual-critical` do Monitor sem o módulo.
   P3 de Apply: inventário exacto de paths.

## Risks / Trade-offs

- [Ordem `cfscalp_` ainda no livro da Binance] → Aceite: Não entra tratar saldo/ordens na exchange.
- [DEV com interruptor ligado e 3 tabelas extra] → Mitigação: migração nova DROP as 5; laço e flags saem no mesmo Apply; `./restart` como critério.
- [Apagar changes ativas #1045/#1070 deixa `openspec validate --all` a apontar specs órfãs] → Mitigação: este change traz os REMOVED das `scalp-*` vigentes; as capabilities só da change activa nunca entram em main.
- [Copy a anunciar a saída] → Mitigação: proto extras + critério de zero menção e zero descontinuação; crítico verifica.
- [Regressão Operar/Carteira/worker] → Mitigação: critério 6; testes de Operar/Carteira e worker sem o laço do scalper ficam.

## Migration Plan

1. Design aprovado por Alan (`Pronto para Dev`).
2. Apply na branch `card-1075-remover-scalper`: UI, API, migração nova, flags, scripts/testes/protos, specs, apagar changes #1045/#1070.
3. PR → `develop`, `alembic upgrade head`, `./restart`, `/api/scalp/status` = 404, Monitor sem módulo, suíte + `openspec validate --all`.
4. PROD no lote (T16): a mesma migração apaga as 2 tabelas que existem lá; as 3 do diagnóstico só existem no DEV.
5. Rollback: reverter o commit da branch; as migrações antigas continuam a poder criar as tabelas num banco vazio; um banco já dropado precisaria de restore (P3). Sem restaurar o scalper como produto.

## Open Questions

Nenhuma bloqueante. O *como* (nome Alembic, lista de ficheiros, systemd) é P3 de Apply.

## P3 aceite (detalhe de Apply)

- Nome e corpo exactos da migração Alembic nova.
- Inventário de `backend/app/services/scalp_*`, `backend/app/routes/scalp.py`, models, scripts `scalp_*`, testes, protótipos e linhas systemd/overlay.
- Como o runtime-worker arranca sem o ramo `RUN_SCALP_LOOP`.
- Recriação dos snapshots Playwright do Monitor.

## Prototype

- Canónico: `frontend/public/prototypes/card-1075-remover-scalper/index.html` — clone da página viva `/monitor` + delta = módulo do scalper ausente. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` nas regiões clonadas. HTTP após o pai publicar: `https://dev.criptofarol.com.br/prototypes/card-1075-remover-scalper/`.
- Extras (não no index): `landing.html` (landing pública v4), `ajuda.html` (`/help`), `perfil.html` (Meu Perfil), `credenciais.html` (Credenciais da Binance). Cada um clone da página viva + copy sem scalper/scalp e sem anunciar que saiu.
- `cp`/clone = copied; ausência do módulo e frases sem scalp = generated.
- Apply lê este `design.md` e o HTML da pasta do proto como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B. Sem rework (zero P0/P1). P3 aceitos; o pai submete.

- P0: nenhum. O módulo do scalper não aparece; o index é clone de `/monitor` (landmarks intactos), não galeria nem ANTES/DEPOIS. Extras sem menção a scalper/scalp e sem anunciar a saída.
- P1: nenhum.
- P2: nenhum.
- P3 (aceito no Apply): thead `7d` vs vivo `Gráfico`; title da Ajuda ainda «card-718»; clip Operar incumbente; comments HTML; `DELTA:start=0`; tabela mobile em cards; busca truncada a 390; 404 `posthog-config.js` no extra da landing; overlay `detect.js` não injectado; nome da migração, inventário de ficheiros e snapshots Playwright.

Disposition: P0/P1 nenhum. P3 aceito no Apply. Sem rework.

Design Agent verdict: PASS

Snapshot: `.impeccable/critique/1075-card-1075-remover-scalper-A.md` e `.impeccable/critique/1075-card-1075-remover-scalper-B.md`

proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
