# Tasks — card-969-discovery-selo-go-nogo

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Perfil Discovery separado do Combo

- [x] 1.1 — Avaliador `evaluate_discovery_go_nogo` (ou equivalente) no caminho de persist da Descoberta: GO se elegível + Calmar ≥ 1 + PF ≥ 1,5 + max DD ≤ 35% + Sharpe OOS finito > 0; NO-GO se Sharpe OOS ≤ 0, métrica OOS ausente/não finita (fail-closed), ou retrato de treino a falhar os três. Motivos nomeiam Treino vs Holdout, valor e limiar.
- [x] 1.2 — Combo `evaluate_walk_forward` / `DEFAULT_CRITERIA` / `OOS_CRITERIA` / retenção 50% e o gate ao salvar favorito permanecem. Sem flag no otimizador que mude o Combo. Fixture BTC `RS-E0E30719CC` (43 trades, Sharpe ~0,50, Calmar ~10,6, holdout 24, Sharpe OOS ~0,35) → GO.

## 2. Amostra e âmbito

- [x] 2.1 — `low_sample` / `insufficient_sample`: UI omite GO e NO-GO mesmo se o holdout foi mau. Rank `—` e Promover desligado nessas linhas (30/90% intacta).
- [x] 2.2 — A mesma barra aplica-se a 4h e 1d, long e short, qualquer template. Varreduras novas (e a que estiver a correr depois do deploy) gravam o selo novo; `completed` não são recalculadas.

## 3. UI da linha

- [x] 3.1 — Acompanhar parciais e Decidir: chip GO (azul informativo) / NO-GO (danger) + motivo visível sem gráfico, sem «+ detalhes» e sem diálogo Promover. Promover enabled no NO-GO elegível. Ranking Calmar + GO acima de NO-GO intactos.
- [x] 3.2 — Fidelidade ao proto `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html`; landmarks `Descoberta de estratégias swing` / Preflight / Rascunho de varredura; modos #852 sem regressão.

## 4. Verificação

- [x] 4.1 — Testes: BTC GO vs Combo 100/0,8; holdout Sharpe ≤ 0 → NO-GO holdout; treino fraco + OOS positivo → NO-GO treino; baixa amostra sem selo; 4h/short mesma regra; Combo save-favorite inalterado. Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 4.2 — `openspec verify` desta change.
