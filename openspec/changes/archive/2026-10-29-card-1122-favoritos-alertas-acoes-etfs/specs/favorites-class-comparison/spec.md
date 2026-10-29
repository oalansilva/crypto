## REMOVED Requirements

### Requirement: Monitor, Telegram e Revalidar fora para ação e ETF até o #1122
**Reason**: O #1122 liga o Monitor, os alertas, as estrelas e o Revalidar de ação e ETF.
**Migration**: Ver "Estrelas e Revalidar valem para ação e ETF; a estrela é a porta do Monitor", abaixo.

## ADDED Requirements

### Requirement: Estrelas e Revalidar valem para ação e ETF; a estrela é a porta do Monitor
Nas linhas e nos cartões de ação e ETF, as estrelas e "Revalidar" SHALL funcionar como na cripto. O resumo por estrelas ("Acompanhar N", "Interesse alto N", "Top picks N") e o filtro por estrelas MUST contar todas as classes. A nota "Monitor, Telegram e Revalidar: ainda não para ações e ETFs…" e o texto "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs" MUST sair; no lugar deles, a linha MUST mostrar o status de atualização (`favorite-backtest-refresh`). A configuração da fonte antiga MUST aparecer como "Stooq · fonte antiga · diário", e não como "Binance Ações".

Favoritos MUST NOT ter controle de alerta (`monitor-telegram-favorite-toggle`). Em todas as classes:
- abaixo do subtítulo, a ajuda "Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor). Sem estrela, fica só aqui; lote e Descoberta salvam sem estrela.";
- na célula das estrelas da linha e do cartão, a legenda "No Monitor" (com estrela) ou "Fora do Monitor" (sem estrela);
- ao dar a primeira estrela, o status da página MUST dizer "<ativo> <tempo> entrou no Monitor com o alerta ligado." e a legenda ao lado da estrela MUST dizer "No Monitor · alerta ligado"; ao tirar a última, o status MUST dizer "<ativo> <tempo> saiu do Monitor e não manda mais alerta.";
- no resumo por estrelas, "Acompanhar" (1 estrela) MUST dizer "No Monitor, com alerta ligado", e não "Monitorar quando fizer sentido";
- no cartão do celular, cada estrela MUST ter alvo de pelo menos 44 px.

#### Scenario: Estrela em NVDA
- **WHEN** Alan marca 2 estrelas na linha de NVDA
- **THEN** o nível MUST ser gravado e NVDA MUST entrar no Monitor e no resumo "Interesse alto"

#### Scenario: Primeira estrela em QQQ do lote
- **WHEN** Alan dá 1 estrela ao favorito de QQQ 1d gravado pelo lote, sem estrela
- **THEN** a legenda MUST mudar de "Fora do Monitor" para "No Monitor · alerta ligado"
- **AND** o status MUST dizer "QQQ 1d entrou no Monitor com o alerta ligado."

#### Scenario: Linha da fonte antiga
- **WHEN** Favoritos lista um favorito de NVDA da fonte antiga
- **THEN** a linha MUST mostrar "Stooq · fonte antiga · diário" e nenhum controle de alerta
