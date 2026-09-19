UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 969: selo GO/NO-GO da Descoberta, não o piso Combo

## Context

Card [#969](https://github.com/oalansilva/crypto/issues/969). Briefing = issue grelhado (`## Problema`, `## História`, `## Entra`, `## Não entra`). Decisões gravadas; este Design não as reabre.

O operador da Descoberta em `/combo/discovery` não consegue usar o selo GO/NO-GO para escolher candidatos swing: Descoberta e Combo partilham hoje `evaluate_walk_forward` / `DEFAULT_CRITERIA` (treino 100, Sharpe 0,8) + `OOS_CRITERIA` (holdout 20, retenção 50%) em `backend/app/metrics/criteria.py`. Esse piso de day trade marca quase tudo NO-GO, inclusive BTC/ETH 1d com Calmar alto e holdout positivo.

Elegibilidade da Descoberta já é independente (`MIN_ELIGIBLE_TRADES=30` + 90% cobertura). A grelha já põe todo GO acima de todo NO-GO (#896, Pronto) e pinta `seal-nogo` / `data-verdict`. Combo ao **salvar favorito** continua bloqueado por não-GO — fora deste card.

Testemunho PROD varredura `0d7990ca`, BTC `RS-E0E30719CC`, snapshot 492, só `multi_ma_crossover` 1d long: Combo actual = 0 GO; filtro desta história ≈ 28 GO.

Operador: administrador da Descoberta em `/combo/discovery` (modos Montar / Acompanhar / Decidir já vivos, #852).

Regiões clonadas (só estas): shell AppNav autenticado + heading + 3 modos + Montar (Preflight / Rascunho de varredura / «Descoberta de estratégias swing») + chrome Acompanhar + casca das grelhas Acompanhar/Decidir. Delta só: selos GO/NO-GO calibrados e motivos (treino vs holdout, valor observado e limiar). Estado visível do proto: **Decidir**.

## Goals / Non-Goals

**Goals:**

- Selo GO/NO-GO da Descoberta (Acompanhar e Decidir) deixa o perfil Combo 100 / 0,8 / 20.
- GO: elegível (≥ 30 trades de treino e 90% cobertura) + retrato de treino decente (Calmar ≥ 1, profit factor ≥ 1,5, max DD ≤ 35%) + Sharpe OOS > 0.
- NO-GO: Sharpe holdout ≤ 0, ou métrica ausente/não finita (fail-closed), ou elegível com retrato de treino a falhar os três — motivo aponta o treino, não só o holdout.
- Baixa amostra / Amostra insuficiente: só o aviso; sem GO nem NO-GO, mesmo se o holdout foi mau.
- A regra vale para todas as linhas (4h e 1d, long e short, qualquer template).
- Motivos legíveis na linha (treino vs holdout, valor e limiar). Promover no NO-GO elegível permanece.

**Non-Goals:**

- Alterar o gate Combo ao salvar favorito (100 / Sharpe 0,8 / 20 OOS / retenção 50%).
- Walk-forward rolante de vários ciclos.
- Recalcular varreduras já `completed` em PROD.
- Mudar ranking Calmar, Preflight, worker, templates, split 70/30 ou a política 30/90%.
- Travar Promover por NO-GO.
- Recortar o selo novo só a 1d long ou só a uma template.
- Redesign dos 3 modos (#852). #896 (ranking Calmar vs selo) não substitui esta calibração.

## Recorte

- **Audience:** operador da Descoberta em Decidir (e Acompanhar), a escolher quem promover.
- **Outcome:** BTC/USDT 1d long `RS-E0E30719CC` mostra GO; holdout mau mostra NO-GO com motivo de holdout; treino fraco mostra NO-GO com motivo de treino; baixa amostra não leva selo.
- **Direction:** clone+delta da rota viva `/combo/discovery`; Operate; refinement (não new-work). Tokens `DESIGN.md` Binance, sem reescrever.
- **Scope:** veredito persistido da Descoberta + selo/motivo na linha. Montar só landmarks.

## Decisions

### 1. Perfil de critérios da Descoberta, separado do Combo

A Descoberta SHALL gravar `oos_verdict` com um avaliador próprio (`evaluate_discovery_go_nogo` / perfil Discovery), não com `evaluate_walk_forward` + `DEFAULT_CRITERIA` / `OOS_CRITERIA`. Combo ao salvar favorito continua no gate actual (`walk-forward-oos-gate`).

O sítio barato: no persist da Descoberta (`discovery_tasks._persist_metrics_snapshot` / caminho que já copia `result["oos_verdict"]`), reavaliar IS+OOS com o perfil Discovery **antes** de gravar. `ComboOptimizer.run_optimization` e o Combo **não** mudam o default. Rejeitado: alterar `DEFAULT_CRITERIA` (quebraria o Combo). Rejeitado: flag `profile=` dentro do otimizador (toca o caminho Combo sem ganho de produto).

Fail-closed: Sharpe OOS ausente, nulo, `NaN` ou infinito → NO-GO com motivo de Holdout. Calmar / profit factor / max DD de treino ausentes ou não finitos num elegível → NO-GO com motivo de Treino.

Varreduras novas (e a que estiver a correr depois do deploy) passam pelo persist novo. Já `completed` não são recalculadas.

### 2. Barra do selo (produto, não Combo)

Num resultado **elegível** (≥ 30 trades de treino e 90% cobertura):

- **GO** se retrato de treino decente (Calmar ≥ 1, PF ≥ 1,5, max DD ≤ 35%) **e** Sharpe OOS finito **> 0**.
- **NO-GO** se Sharpe OOS ≤ 0, ou Sharpe OOS inválido (fail-closed), **ou** retrato de treino a falhar qualquer um dos três — mesmo com Sharpe OOS positivo.

Não entram no selo da Descoberta: piso 100 trades, Sharpe IS 0,8, 20 trades OOS, retenção 50%, CAGR vs B&H, expectancy, concentração (são Combo). BTC `RS-E0E30719CC` (43 trades, Sharpe ~0,50, Calmar ~10,6, holdout 24, Sharpe OOS ~0,35) é o aceite GO.

A mesma barra aplica-se a 4h, 1d, long, short e qualquer template.

### 3. Baixa amostra não recebe selo

`eligibility=low_sample` (`Baixa amostra`) e `insufficient_sample` (`Amostra insuficiente`) mostram só o aviso de amostra. A UI SHALL omitir GO/NO-GO mesmo se o holdout foi mau ou se um `oos_verdict` Combo-era existir no JSON. Rank continua `—`; Promover continua desligado nessas linhas (política 30/90% intacta).

Detalhe de Apply: persistir ou não o veredito interno nessas linhas; o contrato visível é a ausência do chip.

### 4. Motivo na linha; Promover continua

Acompanhar parciais e Decidir pintam o chip (`GO` azul informativo `#3b82f6` / `#93c5fd`; `NO-GO` danger `#f6465d` / `#ff8294`) e, em NO-GO, uma linha de motivo com segmento (`Treino` vs `Holdout`), valor observado e limiar. Sem tooltip-only. Sem exigir «+ detalhes» nem o diálogo Promover.

Exemplos de copy (produto, não HTML):

- Holdout — Sharpe OOS −0,18 ≤ 0 (limiar > 0)
- Treino — Calmar 0,42 < 1
- Holdout — Sharpe OOS ausente ou não finito

Promover num NO-GO **elegível** permanece (alerta, não trava). Ranking Calmar + classe GO acima de NO-GO (#896) fica.

## Apply contract

- Apply (pós `Pronto para Dev`) lê este `design.md` + `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html` como spec de UI; API é fonte de dados, não de layout.
- Fidelidade bloqueante: landmarks `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`; tokens `DESIGN.md` (não reescrever); pares `COPIED:start/end` no proto; T5 mede só `index.html`.
- Persist Descoberta: perfil Discovery (decisão 1–2); Combo `evaluate_walk_forward` intacto.
- UI: selo + motivo nas parciais e no Decidir; Baixa amostra / Amostra insuficiente sem GO/NO-GO; Promover enabled no NO-GO elegível; 4h e short na mesma regra.
- Sem backfill de `completed`. Sem redesenhar os 3 modos. Sem travar Promover. Sem mudar 30/90%, ranking Calmar, Preflight, worker, templates, split 70/30.
- Desvio do proto: path + elemento + motivo no PR; sem registro = bloqueio.

**P3 aceito (Apply):** nome exacto da função (`evaluate_discovery_go_nogo` vs perfil passado a um helper); se o persist reescreve `oos_verdict` ou grava um campo irmão; sanitizar selo na leitura de `low_sample` legado; testes unitários do perfil vs Combo; BTC `RS-E0E30719CC` como fixture de GO.

## Risks / Trade-offs

- [Sweeps `completed` em PROD continuam 0 GO] → aceite: sem backfill; só varreduras novas. Mitigação: copy do card já o diz; o proto mostra o selo novo, não o legado.
- [Operador lê NO-GO de treino como falha de holdout] → motivo na linha com segmento Treino + valor + limiar.
- [Baixa amostra com holdout mau pintava NO-GO] → UI omite o chip quando a elegibilidade é amostra.
- [Tocar no otimizador partilhado] → persist só no caminho Descoberta; Combo fora.

## Migration Plan

Sem Alembic. Deploy = worker/persist da Descoberta + frontend do selo. Rollback = voltar a gravar `evaluate_walk_forward` e a UI antiga. Sem job de dados. `completed` permanece Combo-era até uma varredura nova.

## Open Questions

Nenhuma de produto. Mecanismo (persist Discovery separado do Combo) fechado neste design.

## Prototype

- **URL:** https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/
- **Caminho:** `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html`
- **Digest (sha256):** `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` · 50488 bytes · servido == local (`cmp` clean)
- **Copiados vs gerados:** 10 pares `COPIED:start/end` · 27712 bytes copiados UTF-8 · resto gerado/delta
- **Base:** rota viva `/combo/discovery` (shell autenticado 224px + heading + 3 modos + Montar + Acompanhar + Decidir). Arranque a partir do proto irmão `card-954-discovery-acompanhar-stale` (chrome + grelha HEAD). Sem painel ANTES/DEPOIS. T5 mede só este `index.html`.
- **Clone vs delta:** COPIED = shell AppNav, heading, 3 modos, rascunho, Preflight, chrome Acompanhar, casca das duas grelhas, nota educacional. DELTA = selos GO/NO-GO do perfil Descoberta e motivos (BTC `RS-E0E30719CC` GO; AGLD NO-GO holdout; DOGE NO-GO treino; ADA Baixa amostra sem selo; SOL 4h e LINK short na mesma regra; Promover no NO-GO).
- **Fluxos:** default Decidir; Montar com landmarks Preflight/Rascunho; Acompanhar com parciais e os mesmos selos.
- **Viewports:** 1440×900 e 390×844.
- **Landmarks (catálogo HEAD, substring):** «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».

## Prototype Validation

- **URL:** https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/ — HTTP 200, 50488 bytes, sha256 `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe`, disco == HTTPS (`cmp` clean).
- **Comando:** Python Playwright + Chromium 1243 headed sob `xvfb-run -a` (`executable_path` do cache ms-playwright; não `curl`). Um ciclo por viewport: `page.goto` HTTPS + asserts + screenshot na mesma sessão.
- **Viewports:** 1440×900 e 390×844. Ambos PASS. 0 console error, 0 pageerror.
- **Asserts (mesmo critério nos dois viewports):** landmarks visíveis `Descoberta de estratégias swing` / `Preflight` / `Rascunho de varredura` (Preflight+Rascunho após tab Montar); Decidir default com BTC `RS-E0E30719CC` **GO**; AGLD **NO-GO** + motivo Holdout (Sharpe OOS −0,18 ≤ 0); DOGE **NO-GO** + motivo Treino (Calmar 0,42 < 1); ADA **Baixa amostra** sem chip GO/NO-GO; SOL 4h e LINK short na mesma regra; Promover enabled nos NO-GO elegíveis; 0 console/pageerror.
- **Re-gate (1×):** chip GO/NO-GO deixou de herdar `span{display:block}` (ficava barra full-width). Re-gate verde. PNGs: `.impeccable/critique/969-autor-desktop-1440x900.png`, `.impeccable/critique/969-autor-mobile-390x844.png`.
- Pares `COPIED:start`/`COPIED:end`: 10/10; soma UTF-8 das regiões copiadas 27712 > 0. T5 mede só este index.html.
- Sem emitir PASS oficial de T5 (pai após A/B).

## Impeccable

Operate; refinement (não new-work). Pipeline: context → shape → prototype → browser gate. Assessment A/B **não** spawnados neste filho — o pai spawna a dupla. `DESIGN.md` não reescrito. Surface brief: not-found (rota existente).

### Shape

- Job: operador da Descoberta a escolher candidatos pelo selo, não pelo piso Combo.
- Outcome: GO no BTC testemunho; NO-GO com motivo de holdout e de treino; baixa amostra sem selo.
- Direction: clone+delta; chip + motivo na linha do candidato.
- Untouched: Montar, 3 modos, ranking Calmar, Promover, Combo save-favorite, 30/90%.
- Assumptions (sem AskUser): persist no caminho Descoberta; fail-closed no Sharpe OOS; motivo visível sem expandir.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Sem P0/P1 novos de produto. Sem segundo rework. P3 aceitos no Apply.

**Design Agent verdict: PASS**

- **P0:** nenhum
- **P1:** nenhum
- **P3 (aceites Apply):** Montar condensado vs vivo; chip GO/NO-GO muted / barra full-width ~292×26 no mobile; mock sem linha Amostra insuficiente / fail-closed / PF-only; coluna Ação clipada a 1440 + scrollbar; default proto Decidir ≠ vivo Montar; `reasons` vivos ainda não pintados (delta); chrome `#0d7990ca` / `#PF-492`; mock `7 de 8`; nome exacto da função de persist (já no Apply contract)

**Prototype:** https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/ · digest `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` (50488 bytes, disco == HTTPS)

**Snapshot T7:** `.impeccable/critique/969-card-969-discovery-selo-go-nogo.md`

Dupla:
- A: `.impeccable/critique/969-card-969-discovery-selo-go-nogo-assessment-A.md`
- B: `.impeccable/critique/969-card-969-discovery-selo-go-nogo-assessment-B.md`

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
