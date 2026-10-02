# Tasks — card-1075-remover-scalper

Apply só com Status=Pronto para Dev (T8). Não marcar estas tasks durante o Design.

> UI impact: affected. Protótipo: `frontend/public/prototypes/card-1075-remover-scalper/`. Alinhar `/monitor` ao `index.html` (módulo do scalper ausente; board intacta).

## 1. Monitor

- [x] 1.1 Remover `ScalpModule` de `/monitor` (`MonitorStatusTab` e ficheiro do módulo). Nenhum elemento scalper visível em desktop e mobile.
- [x] 1.2 Manter Em posição, Saída/cobertura, KPIs, filtros, `table.signals` e Operar como hoje.
- [x] 1.3 Não acrescentar banner, toast, Telegram nem texto de descontinuação.

## 2. Copy visível

- [x] 2.1 `/help` fora do `OnboardingGuide`: tirar menções a scalper/scalp; manter Operar com confirmação e carteira opcional. `OnboardingGuide` intacto.
- [x] 2.2 Meu Perfil: tirar a cláusula de que a chave Spot alimenta o scalp BTCUSDT.
- [x] 2.3 Credenciais da Binance (`BinanceCredentialsForm` variant profile e help da API Key): zero menção a scalper/scalp; leitura + Spot para Operar ficam.
- [x] 2.4 Landing v4 + `docs/landing-page.md`: zero menção a scalper/scalp; Operar com confirmação, nunca saque, não opera sozinho. Sem anunciar que saiu.

## 3. Backend

- [x] 3.1 Remover o router `/api/scalp/*`. Critério: `GET /api/scalp/status` → 404.
- [x] 3.2 Remover o laço do scalper na API e no runtime-worker. Worker continua fila da Descoberta e atualização de favoritos.
- [x] 3.3 Remover serviços `scalp_*`, envio `cfscalp_` e classes de banco do scalper. Backend sobe sem erro.
- [x] 3.4 O Farol deixa de perguntar ao Jev. Não cancelar conta TypeSafe nem apagar chaves guardadas.

## 4. Banco

- [x] 4.1 Migração Alembic **nova** que dá DROP nas 5 tabelas: `scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions`, `scalp_calibration_state`.
- [x] 4.2 Não apagar nem reescrever `20260921_0001`, `20260921_0002`, `20260927_0001`.

## 5. Flags e operação

- [x] 5.1 Remover `RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*`/`TYPESAFE_*` do código, units systemd do repositório e docs de operação (incl. overlay).
- [ ] 5.2 Depois do `./restart` no DEV: sobe sem essas flags e sem log de diagnóstico do scalper.

## 6. Scripts, testes, protótipos, specs

- [x] 6.1 Remover scripts `scalp_*`.
- [x] 6.2 Remover testes unitários e e2e do scalper (`card-1001`/`1006`/`1008`/`1045`/`1070` e irmãos).
- [x] 6.3 Remover protótipos dos cards de scalper em `frontend/public/prototypes/`.
- [x] 6.4 Regravar snapshots visuais do Monitor sem o módulo.
- [x] 6.5 Retirar capabilities `scalp-*` de `openspec/specs/` via os deltas desta change; `monitor`, `user-onboarding` e `landing-conversion-copy` deixam de citar o scalper.
- [x] 6.6 Apagar de `openspec/changes/` as changes ativas `card-1045-jev-diagnostico-recalibracao` e `card-1070-scalp-jev-lucro-liquido`. Não mexer nos archives #1001–#1043.

## 7. Não quebrar o partilhado

- [x] 7.1 Chave Spot em Meu Perfil, Operar (`binance_spot_orders`), candles e runtime-worker (sem o laço do scalper) continuam.
- [x] 7.2 Não tratar ordens/saldo na Binance. Não mudar #1074. Não arrastar Status de #1045/#1070.

## 8. Verify

- [x] 8.1 `openspec validate --all` (ou validate desta change `--strict`) verde.
- [x] 8.2 Suíte focada (backend sem scalp + frontend Monitor/Help/Profile/landing) verde.
- [ ] 8.3 Após integração em `develop`: `./restart`; `/api/scalp/status` = 404; `/monitor` sem módulo; Ajuda/Perfil/Credenciais/landing sem a palavra scalp.
