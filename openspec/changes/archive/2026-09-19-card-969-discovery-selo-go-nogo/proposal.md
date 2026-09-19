## Problema

O operador da Descoberta em produção não consegue usar o selo GO/NO-GO para escolher candidatos swing: a regra copiada do Combo (100 trades de treino, Sharpe 0,8, 20 no holdout) marca quase tudo NO-GO, inclusive BTC/ETH 1d com Calmar alto e holdout positivo.

## História

Como operador da Descoberta, quero um selo GO/NO-GO calibrado para swing 1d de cripto, para a grelha Decidir mostrar quem sobreviveu ao holdout em vez de reprovar o conjunto inteiro por piso de day trade.

## Entra

- O selo GO/NO-GO da Descoberta (Acompanhar e Decidir) deixa de usar o perfil Combo de 100 trades de treino / Sharpe 0,8 / 20 trades de holdout.
- A regra vale para **todas** as linhas da varredura (4h e 1d, long e short, qualquer template), não só 1d long.
- Na Descoberta, **GO** quando o resultado já é elegível (≥ 30 trades de treino e 90% de cobertura), o retrato de treino é decente (Calmar ≥ 1, profit factor ≥ 1,5, max DD ≤ 35%) e o holdout não implodiu (**Sharpe OOS > 0**).
- **NO-GO** quando o holdout tem Sharpe ≤ 0, ou a métrica de holdout está ausente/não finita (fail-closed), **ou** a linha já é elegível mas o retrato de treino falha Calmar 1, profit factor 1,5 ou max DD 35% — mesmo com Sharpe de holdout positivo; o motivo aponta o retrato de treino (não só o holdout).
- Linha **Baixa amostra** / **Amostra insuficiente** mostra só o aviso de amostra: **sem GO nem NO-GO**, mesmo se o holdout foi mau.
- Elegibilidade, ranking por Calmar, cobertura e Promover continuam como hoje: NO-GO é alerta e **não** trava Promover.
- Varreduras novas (e a que estiver a correr depois do deploy) mostram o selo novo; varreduras já `completed` não são recalculadas neste card.
- Os motivos do selo continuam legíveis (treino vs holdout), com valor observado e limiar.

Critérios:

- **Dado** um BTC/USDT 1d long elegível com 43 trades de treino, Sharpe ~0,50, Calmar ~10,6, holdout 24 trades e Sharpe OOS ~0,35 (testemunho `RS-E0E30719CC` na varredura PROD `0d7990ca`)
- **Quando** o selo é avaliado com a regra nova
- **Então** a linha mostra **GO** (hoje é NO-GO só por 43 < 100 e Sharpe 0,50 < 0,80)

- **Dado** um elegível cujo holdout tem Sharpe negativo (ex. AGLD/AUCTION na mesma corrida)
- **Quando** o selo é avaliado
- **Então** a linha mostra **NO-GO**

- **Dado** um elegível com Sharpe de holdout positivo cujo retrato de treino falha Calmar 1, profit factor 1,5 ou max DD 35%
- **Quando** o selo é avaliado
- **Então** a linha mostra **NO-GO** e o motivo aponta o retrato de treino (não só o holdout)

- **Dado** um resultado com menos de 30 trades de treino
- **Quando** a grelha lista
- **Então** permanece **Baixa amostra** / sem rank; o selo não inventa GO nem mostra NO-GO, mesmo se o holdout foi mau

- **Dado** uma linha 4h ou short (qualquer template) que passa a mesma barra
- **Quando** o selo é avaliado
- **Então** recebe GO ou NO-GO pela mesma regra das linhas 1d long

Testemunho da corrida PROD (snapshot 492 resultados, só `multi_ma_crossover` 1d long): Combo actual = 0 GO; regra 30+Sharpe 0,5+retenção 50% = 2 GO (BTC e ETH); filtro desta história (elegível + Calmar/PF/DD + Sharpe OOS > 0) ≈ 28 GO.

Relacionado: #896 (ranking Calmar vs selo; já Pronto) não substitui esta calibração.

## Não entra

- Alterar o gate Combo ao **salvar favorito** (100 trades / Sharpe 0,8 / 20 OOS / retenção 50%)
- Walk-forward rolante de vários ciclos
- Recalcular varreduras já `completed` em PROD
- Mudar ranking Calmar, Preflight, worker, templates, split 70/30 ou a política de 30 trades / 90% de cobertura
- Travar Promover por NO-GO
- Recortar o selo novo só a 1d long ou só a uma template

## Why

O selo da Descoberta em produção copia o piso Combo de day trade (100 trades de treino, Sharpe 0,8, 20 no holdout) e marca quase tudo NO-GO — inclusive BTC/ETH 1d com Calmar alto e holdout positivo. O operador não consegue usar o selo para escolher quem sobreviveu ao holdout.

## What Changes

- A Descoberta passa a avaliar o selo GO/NO-GO com um perfil próprio, separado do Combo.
- GO: elegível (≥ 30 trades de treino e 90% cobertura) + retrato de treino decente (Calmar ≥ 1, profit factor ≥ 1,5, max DD ≤ 35%) + Sharpe OOS > 0.
- NO-GO: Sharpe holdout ≤ 0, ou métrica ausente/não finita (fail-closed), ou elegível com retrato de treino a falhar os três — mesmo com Sharpe OOS positivo; o motivo aponta o treino, não só o holdout.
- Baixa amostra / Amostra insuficiente: só o aviso; sem GO nem NO-GO, mesmo se o holdout foi mau.
- A regra vale para todas as linhas (4h e 1d, long e short, qualquer template).
- NO-GO continua alerta: Promover não trava. Ranking Calmar, cobertura, Preflight, worker, templates, split 70/30 e política 30/90% ficam.
- Varreduras novas (e a que estiver a correr depois do deploy) mostram o selo novo; `completed` não são recalculadas.
- Motivos continuam legíveis na linha (treino vs holdout), com valor observado e limiar.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-leaderboard`: o veredito persistido da Descoberta deixa o perfil Combo (100 / 0,8 / 20 / retenção 50%) e passa a usar o perfil desta história; Baixa amostra não recebe selo; fail-closed no holdout; varreduras novas.
- `discovery-three-modes`: Acompanhar e Decidir pintam o selo calibrado e o motivo (treino vs holdout, valor e limiar); Promover no NO-GO elegível permanece; a regra não recorta 1d long nem uma template.

## Impact

- Backend: caminho da Descoberta no otimizador/worker passa a gravar `oos_verdict` com o perfil Discovery; Combo ao salvar favorito continua em `evaluate_walk_forward` / `DEFAULT_CRITERIA` + `OOS_CRITERIA` (`walk-forward-oos-gate` **não** muda).
- Frontend: `DiscoveryPage.tsx` — selo e motivo nas parciais e no Decidir; sem travar Promover; sem redesenhar os 3 modos.
- Specs canónicas: `openspec/specs/discovery-leaderboard`, `openspec/specs/discovery-three-modes`.
- Protótipo: `frontend/public/prototypes/card-969-discovery-selo-go-nogo/`.
- Fora: gate Combo ao salvar favorito; walk-forward rolante; recalcular `completed` em PROD; ranking/Preflight/worker/templates/split 70/30/política 30/90%; travar Promover; recortar o selo a 1d long ou a uma template.
- Relacionado #896 (ranking Calmar vs selo; já Pronto) não substitui esta calibração.
