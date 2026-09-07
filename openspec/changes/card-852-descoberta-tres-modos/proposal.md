## Why

O operador beta abandona ou trava na Descoberta (`/combo/discovery`): a tela mostra ~7 blocos simultâneos (rascunho, preflight técnico, progresso, leaderboard com 13 colunas, filtros, modais) com vocabulário de infra (snapshot, hash, token, dedup, lease, #PF-). O caminho feliz — montar, acompanhar, decidir o que promover — fica ilegível.

## What Changes

- **3 modos, 1 visível por vez:** `Montar` (rascunho editável + preflight humano) / `Acompanhando #X` (rascunho colapsado, leaderboard travado no sweep em curso) / `Decidir` (ranking legível do sweep escolhido, sem varredura ativa).
- **Preflight humano 3 linhas:** `N combinações · ~T estimado · janela/período` + lista do que falta quando bloqueado (ex.: reduzir escopo, escolher 1 timeframe). Detalhe técnico (fórmula, snapshot, hash, token, chave) sai do caminho feliz para bloco expansível.
- **Leaderboard decidível:** 1 ordenação + 3 colunas de risco visíveis por padrão (Calmar, Max DD, Trades/cobertura); restante em expansão por linha; página 10–15; filtros não re-perguntam o rascunho; evidência estruturada (janela, candles, fees) preservada.
- **Período default = Todo o histórico** (ajuste Alan 2026-09-07): preset default do seletor passa a ser o histórico completo (opções menores continuam); preflight default e CTA `Iniciar varredura — N, ~T` refletem o histórico cheio com as datas da janela. Sem mudar motor.
- **Seleção inline:** busca + contador + marcar/desmarcar para casos comuns, sem modal; modal atual vira "edição avançada" com **2 ações de eixo inteiro** (Selecionar todos / Limpar seleção — o escopo filtrado já é coberto pela seleção inline), contador ao vivo no modal e contador inline refletindo após Aplicar.
- **CTA Iniciar dominante:** rótulo estável `Iniciar varredura — N, ~T`; bloqueio nomeia a diferença ("existe varredura igual em curso — ver progresso" vs "há outra em curso — conclua ou cancele"). Promover fica secundário no leaderboard (decisão operador 2026-09-06).
- **Short escondido** do caminho feliz (rascunho + filtros) até ter dados; consistência entre os dois (decisão operador 2026-09-06).
- **Promoção com resumo de risco lado a lado:** retorno, queda máxima, trades, cobertura, janela + destino Tier 3 + onde ver depois (reversibilidade).
- **Manter:** foco/acessibilidade atuais, honestidade evidencial (janela, cobertura, rank que não renumera), copy de escopo destrutivo.

## Capabilities

### New Capabilities

- `discovery-three-modes`: modos Montar / Acompanhar / Decidir com 1 visível por vez, preflight humano, leaderboard com 3 colunas de risco + expansão, seleção inline + edição avançada, CTA Iniciar estável com bloqueio nomeando diferença, promoção com resumo de risco lado a lado.

### Modified Capabilities

- `discovery-sweep` (leitura): nenhum requisito de motor alterado — varredura, ranking, elegibilidade (≥30 trades, ≥90%), taxas, deduplicação permanecem.

## Impact

- Frontend: `frontend/src/pages/DiscoveryPage.tsx` + `DiscoveryPage.css` + `SelectionWorkbench` (layout/copy dos 3 modos; sem mudar motor). Rota `/combo/discovery` já existente.
- Specs: delta em `openspec/changes/card-852-descoberta-tres-modos/specs/discovery-three-modes/spec.md`; spec canónica de sweep intacta.
- Fora: motor de varredura, ranking, elegibilidade, taxas, deduplicação, workers/fila/limites, migração, período histórico (exceto preset default = Todo o histórico, sem mudar motor), novas métricas/filtros, redesign visual (cores, marca, tipografia).
