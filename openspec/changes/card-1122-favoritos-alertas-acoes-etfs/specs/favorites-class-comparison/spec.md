## REMOVED Requirements

### Requirement: Monitor, Telegram e Revalidar fora para ação e ETF até o #1122
**Reason**: O #1122 liga o Monitor, os alertas, as estrelas e o Revalidar de ação e ETF.
**Migration**: Ver "Estrelas, Alertar e Revalidar valem para ação e ETF", abaixo.

## ADDED Requirements

### Requirement: Estrelas, Alertar e Revalidar valem para ação e ETF
Nas linhas e nos cartões de ação e ETF, as estrelas, o controle "Alertar" (do dono) e "Revalidar" SHALL funcionar como na cripto. O resumo por estrelas ("Acompanhar N", "Interesse alto N", "Top picks N") e o filtro por estrelas MUST contar todas as classes. A nota "Monitor, Telegram e Revalidar: ainda não para ações e ETFs…" e o texto "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs" MUST sair. No lugar deles, a linha MUST mostrar o status de atualização (`favorite-backtest-refresh`). A configuração da fonte antiga MUST aparecer como "Stooq · fonte antiga · diário", e não como "Binance Ações".

#### Scenario: Estrela em NVDA
- **WHEN** Alan marca 2 estrelas na linha de NVDA
- **THEN** o nível MUST ser gravado e NVDA MUST entrar no Monitor e no resumo "Interesse alto"

#### Scenario: Alertar em SPY
- **WHEN** o dono ativa "Alertar" na linha de SPY
- **THEN** `notify_telegram` MUST virar verdadeiro e o controle MUST anunciar "Alertar no Telegram: ligado"

#### Scenario: Linha da fonte antiga
- **WHEN** Favoritos lista um favorito de NVDA da fonte antiga
- **THEN** a linha MUST mostrar "Stooq · fonte antiga · diário" e o mesmo controle "Alertar"
