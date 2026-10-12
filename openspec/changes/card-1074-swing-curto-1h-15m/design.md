## Context

Card **#1074**, Status=Design. Briefing = issue grelhado (Problema, História, Entra, Não entra). Sem reentrevista. O título do GitHub ainda diz «com filtro do 1D»; o pacote segue o body: esse filtro **não entra**. 4h, 1h e 15m operam sozinhos.

Hoje a Descoberta (`/combo/discovery`) só aceita 4h e 1d (`DISCOVERY_SWING_TIMEFRAMES` e checkboxes em `DiscoveryPage.tsx`). O heading diz «Compare templates em 4h e 1d». O motor de combos cobra `TRADING_FEE` 0,075% por lado e **não** modela slippage; o worker da Descoberta grava `fees_slippage` 0,1% / 0,1%, rótulo que não bate com a conta. VWAP aparece no catálogo de indicadores (`vwap`) mas não há as duas formas pedidas (dia com reset 00h UTC; móvel de N candles). Day trade puro (1–15m, abertura de NY) já foi descartado na pesquisa; este card só entrega a ferramenta de swing curto.

UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + heading + 3 modos + Rascunho + Preflight + chrome Acompanhar + grelha parciais + header/grelha Decidir + nota rank-stable no **index.html**. `COPIED:start`/`COPIED:end` nessas regiões. Delta fora desses blocos (e só aí): copy do heading, eixo Timeframes swing (4h / 1h / 15m / 1d), chips dos 3 templates novos, rótulo de custo (taxa 0,075% + slippage do timeframe), filtro 1h/15m e linhas 1h/15m no placar. Sem extras. O index não é um painel de estados.

## Goals / Non-Goals

**Goals:**

- Preflight e tela de Descoberta aceitam 4h, 1d, 1h e 15m.
- 3 templates novos (Donchian+volume, squeeze de Bollinger, pullback média longa+RSI+ADX) no catálogo da Descoberta, via editor que já existe; um template já oferecido também completa backtest em 1h e 15m.
- Slippage fixo por lado na tabela de Entra, no mesmo valor em Combo, Descoberta, lote e revalidação; rótulo com taxa 0,075% e o slippage do timeframe.
- VWAP do dia (reset 00h UTC) e VWAP móvel de N candles (N otimizável, inclusive 1d) usáveis em regras de template.
- Selo e placar da Descoberta inalterados; promoção à mão.

**Non-Goals:**

- Filtro de tendência do gráfico diário; hora do dia; stop por ATR; funding; motor além de slippage e VWAP.
- Campo na tela para mudar slippage; recalcular já os favoritos; limiar próprio; GO/NO-GO do Combo como veto; promoção automática.
- Tela nova; `lab_` soltos; script de varredura; rodar a varredura neste card; short; ao vivo; paper; PROD.
- Alargar o produto a 1m, 5m ou 30m na Descoberta ou na tabela de slippage.

## Decisions

1. **A superfície é `/combo/discovery`.** Delta de copy no heading, no eixo de timeframes, nos templates do rascunho e no rótulo de custo do placar. Sem rota nova. Alternativa rejeitada — tela nova ou painel ANTES/DEPOIS: o body proíbe tela nova e o clone canónico tem de ser a Descoberta viva.

2. **Contrato de timeframes da Descoberta = a tabela de Entra.** `DISCOVERY_SWING_TIMEFRAMES = ("15m", "1h", "4h", "1d")`. UI: quatro checkboxes no mesmo fieldset «Timeframes swing», grelha 2×2, rótulos «15 minutos», «1 hora», «4 horas», «1 dia». Default permanece `1d` (não pré-marca 1h/15m). Impedimento: «Escolha 1 timeframe (4h, 1h, 15m ou 1d).» Heading: «Compare templates em 4h, 1h, 15m e 1d.» Filtro do leaderboard inclui 1h e 15m. 4h e 1d continuam. Sem checkbox de 1m, 5m ou 30m. Sem filtro 1D ao lado. Alternativa rejeitada — emprestar o seletor completo do Combo: alargaria o produto.

3. **Intervalos que o Combo já deixa rodar e que a tabela deste card não lista (1m, 5m, 30m) — *como* técnico, sem alargar o produto.** O Combo (`ComboConfigurePage`, `ComboOptimizePage`, `TIMEFRAME_OPTIONS`) já oferece 1 minuto, 5 minutos e 30 minutos. Esses intervalos **não** entram em `DISCOVERY_SWING_TIMEFRAMES`, **não** ganham linha na tabela de slippage, **não** ganham copy na Descoberta e **não** herdam por aproximação o 0,03% de 1h nem o 0,05% de 15m. Um backtest Combo nesses intervalos continua a correr como hoje (taxa 0,075%; sem a tabela nova). O motor não passa a recusá-los; este card também não lhes atribui valor novo. Isto não é escolha de operador.

4. **Slippage: uma tabela, quatro caminhos, sem campo.** Helper único, chave = timeframe do run:

   | Timeframe | Slippage por lado |
   | --- | --- |
   | 1d, 4h | 0,02% (0,0002) |
   | 1h | 0,03% (0,0003) |
   | 15m | 0,05% (0,0005) |

   Soma-se à taxa já usada (`TRADING_FEE` 0,075% por lado). Aplicação no fill: compra `preço × (1 + slip)`, venda `preço × (1 − slip)`, nas duas pernas, igual ao `slippage` que o backtester antigo já conhecia mas o Combo não ligava. Combo, Descoberta, lote e revalidação de favoritos chamam o mesmo helper. Descoberta persiste `fees_slippage` com a taxa 0,075% e o slip do timeframe; o rótulo visível é `taxa 0,075%` + `slippage 0,02%` / `0,03%` / `0,05%` conforme a linha. Sem input. Números de 1d/4h já salvos mudam na próxima atualização normal — não neste card. Alternativa rejeitada — slippage só na Descoberta: o body pede os quatro caminhos iguais.

5. **Três templates pelo editor que já existe.** Nomes de operador: «Canal Donchian + volume»; «Squeeze de Bollinger»; «Pullback média longa + RSI + ADX». Saem do fluxo Combo de templates (indicadores já no catálogo: `donchian`, `bbands`/`kc`, médias, `rsi`, `adx`, volume). Sem ficheiros `lab_`. Não fixam timeframe. Aparecem no catálogo da Descoberta. Critério de fecho: cada um completa backtest sem erro em 4h, 1h e 15m (ex. BTC/USDT); um template que a Descoberta já oferece (ex. `Bollinger_Breakout` ou cruzamento de médias) completa 1h e 15m sem erro. Alternativa rejeitada — scripts soltos ou motor novo: o body proíbe.

6. **VWAP em duas formas no editor, não na tela da Descoberta.** (a) VWAP do dia: preço típico × volume acumulado desde 00:00 UTC, zera a cada meia-noite UTC; critério de produto em 15m, 1h e 4h. (b) VWAP móvel: soma (típico × volume) / soma volume nos últimos N candles; N otimizável como os outros parâmetros; também em 1d. Um template pode usar as duas numa regra de entrada ou saída. Sem hora do dia. Sem UI extra em `/combo/discovery` além do template aparecer na lista. Alternativa rejeitada — VWAP só como o `vwap` pandas-ta de sessão sem reset UTC explícito: o body pede o zero às 00h UTC.

7. **Veredito e promoção ficam.** `evaluate_discovery_go_nogo` (Calmar ≥ 1, PF ≥ 1,5, DD ≤ 35% no treino; Sharpe OOS > 0). Elegibilidade 30 trades e cobertura ≥ 90%. Promover à mão, tier 3, pela própria tela. Sem limiar deste card. Sem veto Combo. Sem promoção automática. Short continua fora do caminho feliz da Descoberta (já escondido). Alternativa rejeitada — GO/NO-GO Combo ou filtro 1D: o body lista os dois em Não entra.

8. **Histórico ~900 dias em 1h/15m é facto de dados, não picker novo.** O seletor de período (6m, 2y, all) permanece. «Todo o histórico» em 1h/15m usa as velas que existem (cerca de 900 dias). Cobertura e `Amostra insuficiente` já tratam falta de velas. Sem calendário novo.

## Risks / Trade-offs

- [Números de 1d/4h já salvos descem na próxima atualização] → Aceite no body. Este card não dispara recálculo; a revalidação normal aplica a tabela.
- [1h/15m com ~900 dias falham cobertura em «todo o histórico» vs calendário 2017+] → Elegibilidade já existente; não inventar velas nem alargar ingestão neste card.
- [Combo em 1m/5m/30m sem linha na tabela] → Intencional: sem valor novo. Risco de o Apply «completar» a tabela por simetria → P3 de Apply se alguém o fizer; o contrato é a tabela de Entra.
- [VWAP do dia em 1d degenera a um ponto por barra] → Fora do critério de produto (15m/1h/4h); a móvel cobre 1d.

## Migration Plan

- Sem Alembic de produto. `fees_slippage` já é JSON.
- Deploy: a lista da Descoberta e o helper de slippage passam a valer nos novos runs e na próxima atualização de favoritos.
- Rollback: reverter a change; rascunhos com 1h/15m falham preflight como hoje; favoritos já recalculados ficam com os números da última corrida.
- PROD só por T16. Este change não publica PROD.

## Open Questions

Nenhuma. As decisões de operador estão no body. O *como* dos intervalos fora da tabela (decisão 3) não reabre Entra.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1074-swing-curto-1h-15m/` → `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`. Clone da página viva `/combo/discovery` (base proto #969 = shell + Montar + Acompanhar + Decidir) + delta só no heading, timeframes, templates das lacunas e rótulo de custo. Landmarks: «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura». `COPIED:start`/`COPIED:end` nas regiões clonadas.
- Vista canónica (`data-state="montar"`): modo **Montar**; heading com 4h, 1h, 15m e 1d; quatro checkboxes (1d marcado; 4h, 1h e 15m disponíveis, sem 1m/5m/30m); chips dos 3 templates novos + um já existente; Preflight sem campo de slippage; nota de custo só de leitura «taxa 0,075% · slippage do timeframe». Decidir no mesmo ficheiro (não é URL irmã): evidência `taxa 0,075% · slippage 0,03%` numa linha 1h e `slippage 0,05%` numa linha 15m; selo GO/NO-GO da Descoberta; Promover à mão. Sem filtro 1D. Sem painel ANTES/DEPOIS.

## Prototype Validation

- **URL canónica:** `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`. Sem HTML irmão. T5 mede só este index.
- **Digest (UTF-8 sha256):** `index.html` `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` · 53208 B = 26304 copied + 26904 generated. Pares `COPIED:start`/`COPIED:end`: 14/14; soma UTF-8 copiada 26304 (> 0). T5 mede só este index.html. Landmarks `/combo/discovery` («Descoberta de estratégias swing», «Preflight», «Rascunho de varredura»).
- **browser_gate:** a dupla A/B abre a URL pública depois do pai publicar. O autor não spawna crítico.

## Impeccable

Operate, refinamento do incumbente `/combo/discovery`. Sem mundo visual novo. Delta só de copy e chips no eixo de timeframes, templates e rótulo de custo. Tokens Binance clonados. A secção de crítica no `design.md` fica para o pai depois da dupla; este autor não a escreve.

## Design Critique

Com-tela. Autor + dupla A/B. Zero P0/P1. Sem rework.

- P0: nenhum
- P1: nenhum
- P2: no Decidir, o cabeçalho cola slippage 0,03% num sweep misto (1d seria 0,02%; 15m mostra 0,05%). Não bloqueia. Apply persiste o custo por linha.
- P2: linhas 1d/4h omitem «taxa 0,075% · slippage 0,02%» (1h/15m estão correctos; a nota do Montar já lista os três). Não bloqueia.
- P3: Montar condensado, timeframes em botão, Short no rascunho congelado, Promover recortado no desktop, chip GO no mobile, HTTPS 404 até a publicação do proto, mock estático. Aceito no Apply.

Disposition: submeter. P3 aceito no Apply. P2 não bloqueia.

Design Agent verdict: PASS

Snapshot: `.impeccable/critique/1074-card-1074-swing-curto-1h-15m-assessment-A.md` e `.impeccable/critique/1074-card-1074-swing-curto-1h-15m-assessment-B.md`

Spawns: 3

proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
