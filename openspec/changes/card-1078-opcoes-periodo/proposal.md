## Why

Na Descoberta e no Combo o operador só consegue varrer três janelas (Todo o histórico, Últimos 2 anos, Últimos 6 meses). Sem janelas mais curtas nem intervalo à escolha, a varredura não cobre o período que ele quer avaliar.

## Problema
Na Descoberta e no Combo, o operador só consegue varrer Todo o histórico, Últimos 2 anos ou Últimos 6 meses — não há janelas mais curtas nem um intervalo de datas à escolha, então a varredura não cobre o período que ele quer avaliar.

## História
Como operador da Descoberta e do Combo, quero as mesmas opções de período (15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado com Data Inicial e Data Final, e Todo o histórico) para varrer estratégias na janela que me interessa.

## Entra
- Na Descoberta e no Combo, o campo de período deixa de ter só as 3 opções de hoje (Todo o histórico, Últimos 2 anos, Últimos 6 meses).
- As duas telas recebem a mesma lista: 15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado (Data Inicial e Data Final), Todo o histórico.
- Opções fixas (15 dias … 2 anos): janela «últimos X» a contar de hoje, no mesmo espírito dos 6 meses e 2 anos actuais. Datas exactas só em Personalizado.
- Ao abrir a Descoberta, o período marcado é 15 dias.
- O período marcado ao abrir o Combo ficou em aberto (a lista é a mesma; a marca inicial do Combo não foi decidida).
- Personalizado: o operador selecciona Data Inicial e Data Final; Preflight e varredura usam esse intervalo.
- Personalizado sem as duas datas, ou com Data Inicial depois da Data Final, não deixa iniciar; o Preflight diz o que falta.
- Em Personalizado, Data Final não pode ser depois de hoje; o Preflight bloqueia.
- Todo o histórico permanece na lista e continua a usar o histórico disponível dos símbolos escolhidos.
- Given um período escolhido no rascunho, When o operador corre o Preflight ou inicia a varredura, Then as combinações são avaliadas nessa janela (não numa das 3 opções antigas por omissão).
- Preflight e rascunho mostram o período escolhido (rótulo + janela de datas quando houver).
- Janela curta (15 dias ou 1 mês com 1d) deixa iniciar; linhas sem amostra suficiente ficam com o selo «Amostra insuficiente».

## Não entra
- Monitor.
- Lista/colunas de Favoritos.
- Ranking principal da Descoberta (Calmar vs CAGR vs Buy & Hold).
- Direção Short na Descoberta (continua só Long nesta etapa).

## What Changes

- O seletor de período na Descoberta (`/combo/discovery`) e no Combo (`/combo/configure`) passa a ter a mesma lista: 15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado (Data Inicial e Data Final), Todo o histórico. Deixa de ter só as 3 opções de hoje.
- Opções fixas resolvem janela «últimos X» a contar de hoje. Datas exactas só em Personalizado.
- **BREAKING** na Descoberta: ao abrir, o período marcado passa a ser 15 dias (hoje é Todo o histórico). Preflight, rascunho e varredura usam essa janela, não uma das 3 opções antigas por omissão.
- A marca inicial do Combo **não** muda neste card (ficou em aberto). O proto do Combo não trata nenhuma marca inicial nova como decisão.
- Personalizado inválido (faltam as duas datas, Data Inicial depois da Data Final, Data Final depois de hoje) bloqueia o início; o Preflight diz o que falta.
- Janela curta deixa iniciar; linhas sem amostra suficiente ficam com o selo «Amostra insuficiente» que já existe.
- Monitor, Favoritos, ranking principal e Short na Descoberta ficam fora.

## Capabilities

### New Capabilities

- `discovery-combo-period-window`: lista partilhada de período nas duas telas, janelas «últimos X», Personalizado com Data Inicial/Data Final, validação no Preflight, e avaliação na janela escolhida.

### Modified Capabilities

- `discovery-three-modes`: o preset default do seletor de período na Descoberta deixa de ser `Todo o histórico` e passa a ser `15 dias`; a lista deixa de ser só as 3 opções.
- `discovery-leaderboard`: janela curta (15 dias ou 1 mês com 1d) não bloqueia o início; linhas sem amostra suficiente continuam com o selo `Amostra insuficiente`.

## Impact

- Frontend: `DiscoveryPage.tsx` (seletor, default, datas Personalizado, Preflight/rascunho); `ComboConfigurePage.tsx` (mesma lista + datas; marca inicial incumbente intacta).
- Backend: preflight e snapshot da Descoberta (`period_type`, `start_date`, `end_date`); `resolve_optimizer_date_range` e o equivalente Combo (`getPeriodDates` / payload optimize/batch) passam a resolver 15d, 1m, 3m, 1y e custom. `all` continua a usar o histórico disponível dos símbolos.
- Sem Monitor, sem Favoritos, sem ranking, sem Short. Sem PROD neste card.
