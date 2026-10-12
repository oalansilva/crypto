## 1. Lista partilhada de período

- [x] 1.1 Na Descoberta (`DiscoveryPage.tsx`) substituir o seletor `all`/`2y`/`6m` pela lista do Entra, nesta ordem e com estes rótulos: 15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado, Todo o histórico. Chaves P3: `15d` `1m` `3m` `6m` `1y` `2y` `custom` `all`.
- [x] 1.2 No Combo (`ComboConfigurePage.tsx`) aplicar a mesma lista e os mesmos rótulos. Deixar de oferecer só Últimos 6 meses / Últimos 2 anos / Todo o período.
- [x] 1.3 Default da Descoberta ao abrir / rascunho novo: `15d`. Restore reidrata o `period_type` do snapshot e não aplica 15 dias por cima.
- [x] 1.4 Marca inicial do Combo permanece o incumbente `all`. Não mudar o `useState` inicial do Combo neste card.

## 2. Janelas «últimos X» e Personalizado

- [x] 2.1 Alargar `resolve_optimizer_date_range` (e o equivalente Combo `getPeriodDates`) para `15d`/`1m`/`3m`/`6m`/`1y`/`2y` a contar de hoje UTC, no espírito dos 6m/2y actuais. `all` continua `null,null` (histórico disponível dos símbolos).
- [x] 2.2 Personalizado: mostrar Data Inicial e Data Final; persistir as duas datas no rascunho, preflight e snapshot; Preflight e varredura usam esse intervalo.
- [x] 2.3 Bloquear início quando Personalizado está sem as duas datas, com Data Inicial depois da Data Final, ou com Data Final depois de hoje. Preflight nomeia o que falta com a copy da decisão 6 do `design.md`.
- [x] 2.4 Preflight e rascunho mostram o rótulo escolhido + janela de datas quando houver. A combinação avaliada é a janela escolhida, não uma das 3 opções antigas por omissão.

## 3. Janela curta e fecho

- [x] 3.1 15 dias ou 1 mês com 1d deixa iniciar; linhas sem amostra suficiente ficam com o selo «Amostra insuficiente» já existente. Sem limiar novo. Sem bloquear o Preflight por janela curta.
- [x] 3.2 Ranking principal, Short na Descoberta, Monitor e Favoritos intactos.
- [x] 3.3 Testes unitários/integração/e2e da lista, default 15d na Descoberta, Combo default `all` intocado, Personalizado inválido, e varredura na janela escolhida.
- [x] 3.4 Playwright contra o proto canónico `/prototypes/card-1078-opcoes-periodo/` (landmarks, 15 dias marcado, Personalizado, Preflight) e extra `combo.html` (lista igual, marca `Todo o histórico`).
