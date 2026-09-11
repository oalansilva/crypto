## Why

Em PROD (2026-09-11, varredura `#862f31de`) o administrador da Descoberta viu ALPHA/USDT `RS-B109ED2C80` no topo das parciais com Calmar `1.195.206.471.012.770.100.000.000.000,00` e promoveu «a melhor agora». O walk-forward do mesmo resultado já era **NO-GO** (Sharpe 0,31). O número enorme nasceu de anualizar CAGR como se cada negócio fosse um dia (~31/365) e de formatar qualquer finito como dinheiro `pt-BR`; o veredito existia gravado e a lista não o pintava.

## What Changes

- O Calmar da Descoberta passa a usar o **tempo de calendário da janela** (primeira a última data), não a contagem de negócios como se cada um fosse um dia. Continua CAGR ÷ Max DD, com Max DD na mesma unidade (fração 0–1).
- Número absurdo ou não finito **não** aparece como dinheiro brasileiro de 27 dígitos: a célula é `N/A`. Essa linha **não** disputa o 1º lugar.
- Parciais (Acompanhar) e lista do Decidir mostram o veredito walk-forward quando existir (`NO-GO` / `GO`) na própria linha — sem abrir o gráfico e sem promover.
- Candidato `NO-GO` **permanece na lista com selo**; **nunca** fica acima de um `GO`. Só `GO` compete pelo 1º lugar contra outro `GO`. (Q1 aceite.)
- Copy da coluna deixa claro que o número é **Calmar**, não retorno e não taxa de acerto. `30 · 100%` continua negócios + cobertura; o cabeçalho/aria permanece «negócios / cobertura».
- ALPHA/USDT `RS-B109ED2C80` deixa de ser «melhor da parcial» por `1e27`; Sharpe ~0,31 e NO-GO ficam visíveis, abaixo de qualquer `GO` da mesma varredura.
- Correção vale para varreduras **novas**. Sem backfill da varredura `#862f31de`. A UI sanitiza display de valores já gravados (finito absurdo → `N/A`).

Fora (grelha): amostra insuficiente (#876); achatar métricas no favorito (#897); redesign dos 3 modos (#852); universo/split; backfill `#862f31de`; ensinar Calmar na landing/Ajuda; travar o clique Promover.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-leaderboard`: CAGR/Calmar com denominador de calendário da janela; teto numérico antes de persistir e antes de formatar `pt-BR`; célula absurda/`não finita` = `N/A` e não disputa 1º lugar; ranking elegível: todo `GO` acima de todo `NO-GO`; entre iguais, Calmar (já corrigido) → negócios → `result_id`; copy acessível da coluna Calmar e de `Trades/cobertura`.
- `discovery-three-modes`: selo `GO`/`NO-GO` visível nas parciais do Acompanhar e nas linhas do Decidir, sem abrir gráfico nem promover; Promover permanece clicável num `NO-GO` (Descoberta já é só admin; Combo já tem override).

## Impact

- Backend: cálculo de CAGR/Calmar no caminho da Descoberta (`combo_optimizer` / `calculate_cagr` / persistência em `discovery_tasks`); `rank_eligible` em `discovery_service` passa a ordenar por classe de veredito (`GO` antes de não-`GO`) e a tratar Calmar absurdo como `N/A`.
- API: payload do leaderboard/parciais expõe `oos_verdict.status` (`GO`/`NO-GO`) para a linha; métricas ranking nulas quando o valor não é finito ou ultrapassa o teto.
- Frontend: `DiscoveryPage.tsx` — célula Calmar (`fmtNum` com teto → `N/A`); selo na linha das parciais e do Decidir; cabeçalho/aria de Calmar e de negócios/cobertura; sem redesenhar os 3 modos.
- Specs canónicas: `openspec/specs/discovery-leaderboard`, `discovery-three-modes`.
- Sem mudança de universo, split 70/30, elegibilidade 30/90%, CTA Promover, favoritos (#897) ou landing/Ajuda.
