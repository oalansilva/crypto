## Why

Quarta história do épico #1116. Com o catálogo (#1117), o histórico Binance de ação e ETF (#1118) e o backtest individual de ação e ETF (#1119) em `develop`, o lote do Combo e da Otimização ainda deixa ação e ETF de fora quando há mais de 1 ativo, não avisa quanto histórico falta coletar, mostra só contagens agregadas (sem estado por ativo), não retoma depois de pausar, e Favoritos — o único lugar onde o resultado do lote fica consultável — só lista cripto.

## Problema

Alan não consegue reaproveitar o fluxo de combos e otimização em um universo misto sem restrições específicas de cripto.

## História

Como pesquisador, quero rodar e otimizar combos em ativos selecionados de diferentes classes para comparar oportunidades usando o mesmo fluxo.

## Entra

- [ ] **Lote misto:** a seleção em lote aceita cripto, ação e ETF juntos, pelo catálogo unificado. Cada ativo roda com a sua classe, fonte, sessão, ajuste e moeda, e o resultado guarda essas informações.
- [ ] **Mesmas regras do backtest individual:** cada ativo do lote é otimizado com as mesmas regras de execução, stop e precisão do backtest individual (#1119). Os bloqueios só-cripto caem apenas onde a capacidade já foi validada.
- [ ] **Tempo gráfico que não serve:** quando o tempo escolhido não está disponível para ação e ETF (1m, 5m, 30m), elas ficam fora com motivo antes de o lote começar, e as criptos rodam (decisão de Alan, 24/10/2026).
- [ ] **Lote grande:** qualquer tamanho de lote é aceito. Antes de confirmar, o lote mostra quantos ativos ainda precisam de coleta de histórico. A coleta mostra progresso por ativo e pode ser pausada ou cancelada (decisão de Alan, 24/10/2026).
- [ ] **Estado por ativo:** o lote mostra progresso, sucesso, insuficiência, rejeição e falha de cada ativo. Ativo com problema não aparece como resultado válido nem impede os demais.
- [ ] **Precisão diária visível:** ação ou ETF sem intradiário que cubra a janela gera resultado válido, com marca visível de precisão diária e do trecho sem intradiário; a precisão nunca cai em silêncio (decisão de Alan, 24/10/2026).
- [ ] **Mesma amostra:** todas as tentativas de otimização de um ativo usam a mesma amostra, sem baixar o histórico de novo a cada tentativa. Pausa, cancelamento e retomada preservam os resultados já concluídos e a identidade da execução.
- [ ] **Resultado vira favorito:** o melhor resultado de cada ação ou ETF do lote é gravado como favorito, igual à cripto hoje (nota "gerado em lote"); por isso o aceite depende do #1122 (decisão de Alan, 24/10/2026).
- [ ] **Comparação numa lista só:** os resultados aparecem numa única lista ordenável, com classe, moeda (USD ou USDT) e convenções em cada linha, e filtro por classe; USD e USDT nunca se confundem (decisão de Alan, 24/10/2026).
- [ ] **Verificação:** um lote com BTC/USDT, NVDA e um ETF gera favoritos consultáveis, com períodos efetivos, precisão e limitações visíveis. No mesmo lote com 5m, NVDA e o ETF ficam fora com motivo e BTC/USDT roda. A regressão de cripto mostra que o lote de cripto segue funcionando.

## Não entra

- Geração automática de estratégias novas.
- Ordens reais ou novo sistema de gestão de carteira.
- Descoberta de estratégias com ação e ETF: fica no #1121.
- Atualização automática e alertas de favoritos de ação e ETF: ficam no #1122.
- Benchmark escolhido e exportação completa com as novas convenções: ficam no #1123.

> Seções acima copiadas do body do issue [#1120](https://github.com/oalansilva/crypto/issues/1120) (grelhado; decisões de Alan de 24/10/2026 dentro de Entra). Não houve reentrevista.

## What Changes

- **Lote aceita cripto, ação e ETF juntos** no Combo (`/combo/configure`) e na Otimização (`/combo/optimize`). Seleção com mais de 1 ativo é sempre lote, mesmo que só 1 sobre para rodar. Cada ativo roda pelo mesmo caminho do backtest individual do #1119 (fonte, sessão, ajuste, moeda, gap no stop, precisão declarada, custos e anualização por classe). Ativo marcado pela Binance continua fora (#1117). A Descoberta continua recusando ação e ETF (#1121).
- **Fora com motivo antes de começar:** com 1m ou 5m (e 30m na Otimização), ação e ETF ficam fora do lote com o motivo, antes de confirmar; as criptos rodam. Na Otimização, em 15m, 1h ou 4h, ação e ETF cujo 5m não cobre a janela fixa (jan. 2024) também ficam fora, com "use 1d aqui ou o Combo". Na seleção mista, os tempos só de cripto aparecem marcados "(só cripto)".
- **Confirmar lote:** "Otimizar" (Combo) e "Run Optimization" (Otimização) com mais de 1 ativo abrem um painel no fluxo, sem modal, com quantos vão rodar por classe e moeda, **quantos precisam de coleta de histórico** (e de quê: o que a Binance tem para a janela e ainda não está guardado), quem fica fora e por quê, a configuração (tempo e período escolhidos) e a regra de favoritos. Qualquer tamanho de lote é aceito. Com um lote pausado, rodar pede para retomar ou encerrar o pausado antes de começar outro (decisão de Alan no Design, 24/10/2026).
- **Coleta dentro do lote, ativo por ativo**, com progresso por página; pausa e encerramento valem ao fim da etapa em curso (coleta ou otimização do ativo atual).
- **Estado por ativo:** na fila, coletando histórico, otimizando, sucesso, sucesso com precisão diária, insuficiente, rejeitado (walk-forward), falha, pulado (já nos favoritos), fora (antes de começar) e não rodou (lote encerrado), com motivo e filtro por estado; lote grande pagina de 50 em 50.
- **Pausar, Retomar e Encerrar** no mesmo lote (mesmo id): os concluídos e os favoritos já gravados ficam; Retomar continua do próximo passo. O lote em andamento ou pausado volta a aparecer quando a página é reaberta. O estado do lote passa a ser durável (hoje vive no Redis com prazo).
- **Mesma amostra por ativo:** o histórico é coletado uma vez e cada ativo otimiza numa amostra guardada no começo, lida por todas as tentativas.
- **Favoritos de ação e ETF gravados pelo lote**, como a cripto hoje (nota "gerado em lote"; sem nível de estrela até o #1122: estrelas, Telegram e Revalidar aparecem desabilitados com o motivo e o resumo do Monitor conta só cripto), com classe, fonte, sessão, ajuste, moeda, precisão, convenções, janela efetiva e amostra guardados no favorito.
- **Favoritos vira a lista única de comparação:** deixa de ser só cripto; filtro **Classe** (Todas, Cripto, Ações, ETFs) com contagem; cada linha mostra classe, moeda (USD ou USDT), precisão (marca âmbar de precisão diária com o trecho sem 15m), convenções, limitações e período efetivo; a ordenação existente vale para todas as classes; o fim do lote abre `/favorites?lote=<id>` com a faixa do lote.
- **Texto da recusa do #1119 sai do lote:** "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois" deixa de aparecer no Combo e na Otimização. Na Descoberta, que continua recusando (#1121), só o porquê troca para "ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois", no mesmo aviso e lugar do #1117.

## Capabilities

### New Capabilities

- `multiclass-batch`: lote misto no Combo e na Otimização — aceite por classe, fora com motivo antes de começar, confirmação com contagem de coleta, coleta por ativo, estados por ativo, pausa/retomada/encerramento duráveis, mesma amostra por ativo, gravação de favoritos de qualquer classe.
- `favorites-class-comparison`: Favoritos como lista única de cripto, ação e ETF, com classe, moeda, precisão, convenções e período efetivo por linha, filtro por classe e por lote, ordenação comum.

### Modified Capabilities

- `crypto-only-mvp`: o lote (Combo e Otimização) deixa de ser só cripto e Favoritos passa a listar ação e ETF; Descoberta continua só cripto até o #1121 e o Monitor até o #1122 (sobre o texto do #1119).
- `favorites-asset-type-filter`: Favoritos deixa de ser só cripto e ganha o filtro por classe em desktop e celular.

## Impact

- Backend: `services/batch_backtest_service.py` (plano por ativo, coleta, estados, retomada, gravação com identidade), `services/batch_backtest_store.py` (estado durável do lote e dos ativos), `tasks/batch_backtest_tasks.py`, `routes/combo_routes.py` (`/backtest/batch` aceita ação/ETF; novos `/backtest/batch/preview`, `/backtest/batch/{id}/resume`, lote ativo do usuário), `services/asset_analysis_guard.py` (escopo de lote), `services/equity_backtest.py` (reuso no lote), `services/market_history/` (progresso da coleta), `routes/favorites.py` (identidade da classe na listagem), `schemas/combo_params.py`; migração de tabelas do lote.
- Frontend: `pages/ComboConfigurePage.tsx`, `pages/ComboOptimizePage.tsx`, `components/BatchProgressPanel.tsx` (vira o painel por ativo), `hooks/useBatchJob.ts` (confirmação, retomada, recuperação do lote ativo), `lib/assetSelection.ts` (plano do lote por classe e tempo), `pages/FavoritesDashboard.tsx` (lista multiclasse, filtro Classe, faixa do lote).
- APIs: `POST /api/combos/backtest/batch` aceita ação/ETF; novos `POST /api/combos/backtest/batch/preview`, `POST /api/combos/backtest/batch/{id}/resume`, `GET /api/combos/backtest/batch/active`; `GET /api/combos/backtest/batch/{id}` ganha `items`; `GET /api/favorites/` ganha `asset`.
- Dependências: #1117, #1118, #1119 (em `develop`); **#1122 para o aceite** (identidade do favorito de ação/ETF, atualização e alertas). Contrato com o #1122 em `design.md`.
