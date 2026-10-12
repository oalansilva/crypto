UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1078](https://github.com/oalansilva/crypto/issues/1078). Briefing = issue grelhado. Sem reentrevista. Sem grelha neste filho.

Hoje o seletor de período na Descoberta (`/combo/discovery`) e no Combo (`/combo/configure`) só oferece `Todo o histórico`, `Últimos 2 anos` e `Últimos 6 meses` (`period_type`: `all` | `2y` | `6m`). A Descoberta abre em `all`. O Combo abre em `all` (rótulo vivo «Todo o período»). `resolve_optimizer_date_range` só converte `6m`/`2y`; `all` deixa `start_date`/`end_date` nulos e usa o histórico disponível dos símbolos.

**Audience:** operador a montar varredura na Descoberta ou a configurar um Combo.
**Outcome:** as duas telas partilham a lista de período do Entra; a Descoberta abre em 15 dias; Personalizado pede as duas datas e o Preflight bloqueia o inválido; janela curta não impede o início.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance. Sem mundo visual novo.
**Scope:** campo Período + Preflight/rascunho na Descoberta e no Combo. Sem Monitor, Favoritos, ranking, Short.

Regiões clonadas (só estas):

- `index.html` (canónico, `/combo/discovery`): shell AppNav; heading; 3 modos; cartão Rascunho (Templates, Símbolos, Timeframes swing, Direção, Ranking); painel Preflight; chrome Acompanhar; grelha Decidir. `COPIED:start`/`COPIED:end` nessas regiões.
- `combo.html` (extra, `/combo/configure`): shell AppNav com Combo activo; cartão Template Information; cartão Configuration (símbolos, timeframe, Direção, Deep Backtest, walk-forward). Delta só no campo Período + datas Personalizado + caixa de janela.

O index não é um painel ANTES/DEPOIS nem «6 estados».

## Goals / Non-Goals

**Goals:**

- Mesma lista nas duas telas: 15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado (Data Inicial e Data Final), Todo o histórico.
- Opções fixas = janela «últimos X» a contar de hoje. Datas exactas só em Personalizado.
- Ao abrir a Descoberta, 15 dias está marcado. Preflight e rascunho mostram o rótulo + janela de datas.
- Personalizado: as duas datas alimentam Preflight e varredura. Sem as duas, ou com Data Inicial depois da Data Final, ou com Data Final depois de hoje: não inicia; o Preflight nomeia o que falta.
- Todo o histórico continua a usar o histórico disponível dos símbolos.
- Janela curta (15 dias ou 1 mês com 1d) deixa iniciar; linhas sem amostra suficiente ficam com o selo «Amostra insuficiente».

**Non-Goals:**

- Monitor.
- Lista/colunas de Favoritos.
- Ranking principal da Descoberta (Calmar vs CAGR vs Buy & Hold).
- Direção Short na Descoberta (continua só Long nesta etapa).
- Decidir a marca inicial do Combo. Ficou em aberto. O proto do Combo não trata nenhuma marca inicial nova como decisão deste card.

## Decisions

1. **Página primária = `/combo/discovery`.** URL canónica do proto clona essa página viva e aplica só o delta do período. A outra superfície com copy visível é o Combo em `/combo/configure` (`combo.html`), não `/combo/select` (catálogo de templates, sem campo de período). Alternativa rejeitada — painel das duas no index: o clone canónico tem de ser a Descoberta.

2. **Lista e rótulos = Entra, iguais nas duas telas.** Opções, nesta ordem: `15 dias`, `1 mês`, `3 meses`, `6 meses`, `1 ano`, `2 anos`, `Personalizado`, `Todo o histórico`. O Combo deixa de dizer «Todo o período» / «Últimos 6 meses» / «Últimos 2 anos» como lista exclusiva; passa a esta lista. O espírito «últimos X» fica no comportamento, não num prefixo extra. Alternativa rejeitada — manter «Últimos N» só no Combo: o Entra pede a mesma lista.

3. **Default da Descoberta = 15 dias.** Substitui o preset `Todo o histórico` do #852. Restore de varredura gravada continua a reidratar o `period_type` do snapshot; não aplica 15 dias por cima. Alternativa rejeitada — default 15 dias também no Combo: o body deixou a marca inicial do Combo em aberto.

4. **Marca inicial do Combo = incumbente vivo, não decisão.** O Combo vivo abre em `all`. O proto `combo.html` mantém essa marca como clone do incumbente e **não** a apresenta como escolha deste card. Apply **não** muda o `useState` inicial do Combo. A Open Question fica em aberto.

5. **Chaves internas (P3 Apply, não produto):** `15d` | `1m` | `3m` | `6m` | `1y` | `2y` | `custom` | `all`. Fixas resolvem `start_date`/`end_date` com o mesmo relógio UTC de `resolve_optimizer_date_range` (`datetime.now(timezone.utc).date()`): 15 dias = `relativedelta(days=15)`; 1/3/6 meses = `relativedelta(months=N)`; 1/2 anos = `relativedelta(years=N)`. `all` continua `null, null`. `custom` persiste as datas escolhidas. O frontend envia `period_type` + datas; o worker não cai nas 3 opções antigas por omissão.

6. **Personalizado inline, sem modal.** Data Inicial e Data Final aparecem debaixo do select quando a opção é Personalizado; `type="date"`, min-height 44px, tokens Binance. Impedimentos de Preflight (copy de operador):
   - faltam as duas datas: «Seleccione Data Inicial e Data Final.»
   - só uma das duas: nomeia a que falta («Seleccione Data Inicial.» / «Seleccione Data Final.»)
   - Data Inicial depois da Data Final: «Data Inicial não pode ser depois da Data Final.»
   - Data Final depois de hoje (UTC): «Data Final não pode ser depois de hoje.»
   O CTA Iniciar fica desactivado enquanto houver impedimento. Alternativa rejeitada — modal de calendário: o Entra pede os dois campos no fluxo actual.

7. **Janela curta não é impedimento.** 15 dias ou 1 mês com 1d deixa iniciar. O listing-gate e o selo `Amostra insuficiente` já existentes tratam linhas sem amostra. Sem limiar novo. Sem bloquear o Preflight por «poucas velas».

8. **Preflight e rascunho mostram rótulo + janela.** Linha de 3: `N combinações · ~T estimado · {rótulo} [{data inicial}, {data final})` quando houver datas (fixas resolvidas ou Personalizado). Todo o histórico: rótulo sem inventar datas no cliente; se o preflight devolver janela dos símbolos, mostra-a. A linha «Período» do painel usa o mesmo rótulo.

## Risks / Trade-offs

- [Risco] Operador habituado a Todo o histórico na Descoberta achar a janela curta «vazia» → Mitigação: o Entra fecha 15 dias; selo «Amostra insuficiente» nas linhas curtas; início não é bloqueado.
- [Risco] Apply «completar» o default do Combo para 15 dias por simetria → Mitigação: decisão 4; Open Question; o proto não marca 15 dias no Combo.
- [Risco] Personalizado com Data Final = hoje vs half-open `[start, end)` a cortar o dia corrente → Mitigação: P3 Apply: o mesmo contrato de datas das opções 6m/2y actuais (`end = hoje UTC`); não redesenhar o intervalo.

## Migration Plan

- Sem Alembic. `period_type` já é texto; snapshots antigos `6m`/`2y`/`all` continuam válidos.
- Restore: snapshot com `6m`/`2y`/`all` marca a opção nova correspondente; snapshot sem chave nova não inventa Personalizado.
- Rollback: repor as 3 opções e o default `all` na Descoberta.
- PROD só por T16.

## Open Questions

- **Marca inicial do Combo.** A lista é a mesma; o período marcado ao abrir o Combo **não foi decidido**. Este card não escolhe 15 dias, Todo o histórico, nem outra opção como default novo do Combo. O proto `combo.html` mostra o incumbente vivo (`Todo o histórico`) só como clone, não como decisão.

## Apply contract

Apply lê este `design.md` e os HTML em `frontend/public/prototypes/card-1078-opcoes-periodo/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Lista idêntica nas duas telas, nesta ordem, com estes rótulos.
- Descoberta abre em 15 dias; Preflight/rascunho mostram rótulo + janela.
- Combo: lista nova; marca ao abrir = incumbente (`all`); Apply não muda esse default.
- Personalizado mostra Data Inicial e Data Final; inválido bloqueia e o Preflight nomeia o que falta (copy da decisão 6).
- Janela curta deixa iniciar; selo «Amostra insuficiente» nas linhas sem amostra.
- Ranking, Short, Monitor, Favoritos intactos.

**P3 aceito (Apply):** chaves `15d`/`1m`/`3m`/`6m`/`1y`/`2y`/`custom`/`all`; alargar `resolve_optimizer_date_range` e `getPeriodDates`; persistir datas no snapshot/preflight; `useState` da Descoberta `15d`; Combo `useState` inicial intocado; testes e fixtures que ainda afirmam só `6m`/`2y`/`all` ou default `all` na Descoberta; timezone UTC do «hoje».

## Recorte

- **Audience:** operador a escolher a janela da varredura.
- **Outcome:** lista partilhada; Descoberta em 15 dias; Personalizado validado; Combo sem default novo.
- **Direction:** clone `/combo/discovery` + extra `/combo/configure`; Operate; sem new-work.
- **Scope:** Período + Preflight. Ranking/Short/Monitor/Favoritos fora.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/` → `frontend/public/prototypes/card-1078-opcoes-periodo/index.html`. Clone da página viva `/combo/discovery` + delta só no período (lista, default 15 dias, Personalizado, Preflight). Landmarks: «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura». `COPIED:start`/`COPIED:end` nas regiões clonadas. T5 mede só este index.html.
- Extra: `https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/combo.html` — clone de `/combo/configure` + a mesma lista. Marca inicial = incumbente `Todo o histórico` (não decisão). Nunca URL canónica.
- Vista canónica: modo Montar; 15 dias marcado; 1d marcado; Preflight com rótulo 15 dias + janela; Personalizado revela as duas datas; inválido bloqueia. Decidir no mesmo ficheiro: uma linha com selo «Amostra insuficiente» (janela curta deixou iniciar). Sem painel ANTES/DEPOIS.

## Prototype Validation

- **URL canónica:** `frontend/public/prototypes/card-1078-opcoes-periodo/index.html`. Extra `combo.html` não entra no T5.
- **Digest (UTF-8 sha256):** `index.html` `455997ebc236a202f5baca1f55ec4ab3753914cbfbcf5b02c14dbcacf7ba2f9b` · 61431 B = 27836 copied + 33595 generated. Pares `COPIED:start`/`COPIED:end`: 15/15; soma UTF-8 copiada 27836 (> 0). T5 mede só este index.html. Landmarks `/combo/discovery` («Descoberta de estratégias swing», «Preflight», «Rascunho de varredura»).
- **browser_gate:** a dupla A/B abre a URL pública depois do pai publicar. O autor não spawna crítico.

## Impeccable

Operate, refinamento do incumbente `/combo/discovery` (primário) e `/combo/configure` (extra). Sem mundo visual novo. Delta só no campo de período, datas Personalizado e copy de Preflight. Tokens Binance clonados. A secção de crítica no `design.md` fica para o pai depois da dupla; este autor não a escreve.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B; sem rework (zero P0/P1 de produto).

- Autor: [design-autor 1078](073f1c96-54a4-4db1-9700-a58cf8bc88fd) isolado.
- Assessment A: [Assessment A 1078](2fe75b95-44f6-4521-8220-931bc102af6b) isolado.
- Assessment B: [Assessment B 1078](ae579e2b-dafe-4b6c-b961-288bd150be70) isolado.
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`.
- Proto canónico: https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/
- Proto extra: https://dev.criptofarol.com.br/prototypes/card-1078-opcoes-periodo/combo.html
- Snapshots: `.impeccable/critique/1078-card-1078-opcoes-periodo-A.md` e `…-B.md`. Gist OpenSpec não é a crítica.

- **P0** — nenhum.
- **P1** — nenhum.
- **P2** (residual, não bloqueia): no Combo, o hint azul afirma «todo o histórico» (Personalizado vazio) ou a janela futura enquanto o Preflight bloqueia o Personalizado inválido. CTA desactivado. Disposition: residual; sem rework.
- **P3** (aceitos, Apply): Montar/Combo condensados face ao vivo; Acompanhar estático; estimativa com Personalizado bloqueado; modal Promover e estados 403 ausentes; chaves internas e UTC; locale `mm/dd/yyyy` do Chromium; período abaixo da dobra; clip da coluna Ação.
- **Disposition:** marca inicial do Combo continua em aberto. O proto mostra o incumbente «Todo o histórico» e não o trata como decisão deste card. Descoberta abre em 15 dias, lista partilhada nas duas telas, Personalizado bloqueia inválido, janela curta deixa iniciar.

### Proxies

- `design.md` words: 1899
- HTML generated vs copied: 33595 vs 27836
- Spawns: 3
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

Design Agent verdict: PASS
