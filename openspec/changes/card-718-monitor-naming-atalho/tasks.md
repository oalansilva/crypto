## 1. Busca sem hint falso

- [x] 1.1 Remover o `<span className="kbd">⌘K</span>` da busca em `frontend/src/components/monitor/MonitorStatusTab.tsx:1011`, sem adicionar listener nem mudar placeholder
- [x] 1.2 Verificar que nenhum `⌘K`/`Cmd+K`/`.search .kbd` resta visível na busca do `/monitor`

## 2. KPIs e seção com nome único de estado

- [x] 2.1 Remover as tags `<span className="tag">Compra</span>` e `<span className="tag">Venda</span>` dos KPIs em `MonitorStatusTab.tsx:1062-1076`
- [x] 2.2 Unificar o KPI de saída: passa a `Saída / cobertura` (não `Em saída`); KPI de posição permanece `Em posição`
- [x] 2.3 Verificar os 4 KPIs (`Em posição`, `Saída / cobertura`, `Total`, `Em carteira`) sem `.kpis .tag`
- [x] 2.4 Remover o badge `Estado {cfg.title}` em `MonitorStatusTab.tsx:1168` (titles Compra/Venda de SectionConfig) — remover o span, sem o substituir por `Estado hold/exit`

## 3. Status da linha e rótulo mobile (T6)

- [x] 3.1 Coluna Status de `table.signals` (`MonitorStatusTab.tsx` ~`:1294`, hoje `resolved.visual.badgeText`) passa a `Em posição` na seção hold e `Saída / cobertura` na seção exit
- [x] 3.2 Rótulo de estado visível no card mobile (`OpportunityCard.tsx` status-pill / `badgeText`, `data-testid` `monitor-card-signal-*`) usa os mesmos nomes canónicos
- [x] 3.3 Não alterar `markerLabel` nem copy de ordem Spot (BUY/SELL = Compra/Venda)

## 4. Ajuda — troca estrita (T6)

- [x] 4.1 `frontend/src/pages/HelpPage.tsx:42`: o parágrafo do Monitor deixa de ensinar Compra/Venda como estados; passa aos nomes canónicos (sem reescrever o guia; sem «entrada potencial»)
- [x] 4.2 `frontend/src/pages/MonitorPage.tsx` `ScreenHelpPanel` (`:9`): a mesma troca estrita na copy que ensina estados do Monitor

## 5. Verificação dos critérios de aceite

- [x] 5.1 KPI de posição == h3 `Em posição`, sem tag
- [x] 5.2 KPI de saída == h3 `Saída / cobertura`, sem tag
- [x] 5.3 Busca sem hint falso visível; sem foco ⌘K/Ctrl+K
- [x] 5.4 Coluna Status (desktop) e pill do card mobile com os mesmos nomes canónicos — não Compra/Venda
- [x] 5.5 Ajuda `/help` e ScreenHelpPanel sem ensinar Compra/Venda como estado do Monitor
- [x] 5.6 Regra HOLD/EXIT inalterada — só copy/atalho
