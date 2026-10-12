# Proposal: card-1075-remover-scalper

Card: #1075. Briefing = body grelhado da issue (copiado abaixo). Sem reentrevista.

## Problema

O scalper BTC/USDT nunca operou com lucro líquido. Ele ocupa espaço no Monitor, roda um laço em background no DEV, guarda estado em tabelas e soma muito código que precisa ser mantido. O Alan decidiu parar o scalper e tirar tudo, inclusive o que já está em produção.

Hoje está assim:

- **Em produção:** o módulo Scalp BTCUSDT aparece no Monitor de todo utilizador autenticado. Há tabelas `scalp_user_states` e `scalp_fills` (cards #1001 a #1043). Ninguém ligou o interruptor (0 estados, 0 fills). O worker de produção não corre o laço dedicado; a API ainda pode correr o laço se alguém ligar. As 3 tabelas do diagnóstico/recalibração não existem em produção.
- **No DEV (`develop`):** 1 interruptor ligado, calibração a correr, 2 diagnósticos, 1 versão de confiança, 0 fills. O laço pergunta ao Jev; não saiu ordem. Já está na develop o código do #1045 e do #1070 (PRs #1067, #1068, #1069, #1072 e #1073): diagnóstico diário, recalibração, prova de lucro líquido, fronteira de regime e as tabelas `scalp_jev_diagnoses`, `scalp_confidence_versions` e `scalp_calibration_state`.
- O Jev (TypeSafe) só é usado por este scalper. Operar, Carteira, candles e o runtime-worker (fila da Descoberta e favoritos) são outra coisa.

O Alan já cancelou #1045 e #1070 no board. Cancelar o card não apaga o código: o do #1045 e do #1070 continua na develop (PRs já mergeadas) até ESTE card o remover. O próximo lote ainda pode levar esse código se este card não o tirar.

## História

Como Alan, quero o scalper removido do sistema inteiro (tela, laço, ordens, tabelas, scripts, configuração e documentação), para o Monitor e o código ficarem só com o que eu uso. Quero também que nenhuma parte do #1045 ou do #1070 chegue à produção.

## Entra

1. **Tela.** O módulo do scalper some do Monitor. O Monitor continua igual no resto: Em posição, Saída/cobertura, KPIs e filtros.
   - Critério: em `/monitor`, desktop e mobile, não aparece nenhum elemento do scalper; o resto da tela funciona como hoje.
   - Os textos que citam o scalper em Ajuda, Perfil, Credenciais da Binance e na landing deixam de falar dele.
   - Critério: nenhuma dessas telas menciona scalper/scalp.
   - Some sem aviso: não entra banner, Telegram nem texto de descontinuação.
   - Critério: Monitor, Ajuda, Perfil, Credenciais e landing não anunciam que o scalper saiu.
2. **Backend.** Saem a API `/api/scalp/*`, o laço do scalper (na API e no runtime-worker), os serviços do scalper, o envio de ordens `cfscalp_` e as classes de banco do scalper.
   - Critério: `/api/scalp/status` responde 404.
   - Critério: o backend e o runtime-worker sobem sem erro, e os outros trabalhos do worker (fila da Descoberta e atualização de favoritos) continuam rodando.
3. **Banco.** Uma migração nova apaga as 5 tabelas do scalper e os dados delas: `scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions` e `scalp_calibration_state`. As migrações antigas ficam no histórico; a remoção é por migração nova, para não quebrar bancos que já as aplicaram (DEV e PROD).
   - Critério: depois de aplicar as migrações, as 5 tabelas não existem no DEV; em PROD, depois do lote, também não.
4. **Configuração e operação.** Saem as flags do scalper (`RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*`/`TYPESAFE_*`) do código, das unidades de serviço do repositório e da documentação de operação. O runtime-worker continua existindo, porque é usado por outros trabalhos.
   - Critério: depois do `./restart`, o DEV sobe sem nenhuma flag do scalper e sem o log de diagnóstico do scalper.
   - O Farol deixa de usar o Jev. A conta e as chaves guardadas podem ficar sem uso.
   - Critério: depois do `./restart` no DEV (e, no lote, em produção), o Farol não pergunta ao Jev.
5. **Scripts, testes e specs.**
   - Saem os scripts `scalp_*`, os testes unitários e e2e do scalper e os protótipos dos cards de scalper.
   - Os snapshots visuais do Monitor são regravados sem o módulo.
   - As capabilities OpenSpec `scalp-*` são retiradas e as specs compartilhadas (`monitor`, `user-onboarding`, `landing-conversion-copy`) deixam de citar o scalper.
   - As changes ativas do #1045 e do #1070 saem de `openspec/changes/`.
   - Critério: a suíte de testes e o `openspec validate --all` passam sem nada do scalper.
6. **Não quebrar o que é compartilhado.** A chave Spot da Binance em Meu Perfil, o envio de ordens de Operar (`binance_spot_orders`), o armazenamento de candles e o runtime-worker continuam funcionando.
   - Critério: Operar e Carteira funcionam como antes.

## Não entra

- Tratar ordens abertas ou saldo na Binance deixados pelo scalper. O Alan disse para não se preocupar com isso.
- Remover o runtime-worker, a chave Spot da Binance, o envio de ordens de Operar ou o armazenamento de candles.
- Apagar ou reescrever as migrações antigas, ou as changes OpenSpec já arquivadas dos cards #1001 a #1043 (ficam como histórico).
- Mudar o card #1074 ou qualquer outra estratégia.
- Cancelar os cards #1045 e #1070 no board: o Alan já cancelou; este card não mexe na coluna.
- Banner, Telegram ou texto de descontinuação do scalp BTCUSDT.
- Cancelar a conta do Jev ou apagar chaves guardadas.

## Why

O scalper BTC/USDT nunca operou com lucro líquido, ocupa o Monitor, corre um laço e tabelas que ninguém usa em produção, e o código do #1045/#1070 ainda está na develop — se este card não o tirar, o próximo lote ainda pode levá-lo. Alan quer o sistema só com o que usa.

## What Changes

- **BREAKING (UI):** o módulo Scalp BTCUSDT some de `/monitor`. Em posição, Saída/cobertura, KPIs, filtros e Operar ficam.
- **BREAKING (copy):** Ajuda, Perfil, Credenciais da Binance e landing v4 deixam de mencionar scalper/scalp. Sem banner, Telegram ou texto de descontinuação.
- **BREAKING (API):** saem `/api/scalp/*` (critério: `/api/scalp/status` → 404), o laço na API e no runtime-worker, serviços, ordens `cfscalp_` e classes de banco do scalper.
- **BREAKING (banco):** migração nova apaga as 5 tabelas (`scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions`, `scalp_calibration_state`). Migrações antigas ficam no histórico.
- Saem flags `RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*`/`TYPESAFE_*` do código, units e docs de operação. O Farol deixa de perguntar ao Jev. Runtime-worker, chave Spot, Operar e candles ficam.
- Saem scripts `scalp_*`, testes e protótipos dos cards de scalper. Snapshots do Monitor regravados sem o módulo.
- Capabilities `scalp-*` retiradas; `monitor`, `user-onboarding` e `landing-conversion-copy` deixam de citar o scalper. Changes ativas `card-1045-jev-diagnostico-recalibracao` e `card-1070-scalp-jev-lucro-liquido` saem de `openspec/changes/`.

## Capabilities

### New Capabilities

- `scalper-removed`: o Farol deixa de ter o scalper (tela, API, laço, ordens `cfscalp_`, tabelas, flags, Jev, scripts e testes). Operar, Carteira, chave Spot, candles e runtime-worker (fila da Descoberta e favoritos) continuam.

### Modified Capabilities

- `monitor`: o workbench `/monitor` deixa de hospedar o módulo Scalp BTCUSDT; board (Em posição, Saída/cobertura, KPIs, filtros, `table.signals`, Operar) permanece.
- `user-onboarding`: Ajuda (`/help`) fora do `OnboardingGuide` deixa de admitir o scalp opcional no Monitor; Operar com confirmação e carteira opcional ficam; Perfil e Credenciais da Binance deixam de citar o scalper.
- `landing-conversion-copy`: a landing v4 deixa de admitir o scalp opcional; Operar com confirmação, nunca saque, e «não opera sozinho» sem cláusula de scalp.
- `scalp-direcional-jev`, `scalp-monitor-panel`, `scalp-monitor-horizonte`, `scalp-ws-fresh-state`, `scalp-jev-horizonte`, `scalp-jev-diagnostic-log`, `scalp-jev-consult-cadence`, `scalp-jev-call-timeout`, `scalp-jev-entry-verdicts`, `scalp-jev-model-version`, `scalp-jev-toxicity-band`, `scalp-book-toxic-observability`, `scalp-confidence-gate`, `scalp-confidence-threshold-per-regime`, `scalp-regime-gate`, `scalp-aggressive-exit`, `scalp-jev-eval-ruler`, `scalp-jev-net-return-ruler`, `scalp-jev-ohlcv-access`, `scalp-jev-realized-measurement`, `scalp-jev-cost-band`, `scalp-jev-scale-record`, `scalp-jev-window-ab`, `scalp-maker-fee-hurdle`: todas as requirements vigentes são retiradas (o produto já não tem este scalper).

## Impact

- Frontend: `ScalpModule` sai de `/monitor`; copy em `HelpPage`, `ProfilePage`, `BinanceCredentialsForm` e landing v4; snapshots `visual-critical` do Monitor; testes e2e `card-1001`/`1006`/`1008`/`1045`/`1070`; protótipos `frontend/public/prototypes/card-1*scalp*` e irmãos.
- Backend: rotas `/api/scalp/*`, serviços `scalp_*`, loop, stream BTCUSDT do scalper, modelos/tabelas, flags e units systemd.
- Banco: migração Alembic nova `DROP TABLE` das 5 tabelas; as antigas (`20260921_0001`, `20260921_0002`, `20260927_0001`) ficam.
- OpenSpec: changes ativas #1045 e #1070 saem de `openspec/changes/`; archives #1001–#1043 ficam; `openspec validate --all` verde sem capabilities `scalp-*`.
- Fora: Binance (ordens/saldo do scalper), conta Jev, chaves guardadas, card #1074, coluna Cancelado do board.
