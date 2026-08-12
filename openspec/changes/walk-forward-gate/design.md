# Design: Walk-forward gate (out-of-sample) para promoção a favorito

## Context

O otimizador combo (`ComboOptimizer.run_optimization`, `backend/app/services/combo_optimizer.py`) otimiza parâmetros sobre o período inteiro informado (default 2017→hoje) e valida no mesmo período — não existe split treino/holdout em lugar nenhum do código (busca por `holdout`/`out_of_sample`/`walk-forward` retorna zero ocorrências). O vencedor é escolhido por score (`0.7*sharpe + 0.3*return`) sobre esse período único. A promoção a favorito (manual `POST /api/favorites/` e automática no batch) não aplica nenhum gate de elegibilidade: `evaluate_go_nogo` (`backend/app/metrics/criteria.py`) só roda no fluxo legado `BacktestService._calculate_enhanced_metrics` e é apenas informativo.

O problema: candidato overfitado no período único vira favorito e alimenta sinais no Monitor sem evidência fora da amostra. Spec histórica `06-strategy-lab-langgraph` já usou walk-forward 70/30 — reutilizamos o aprendizado de produto (split temporal), não a stack removida.

Stakeholders: Alan (decisor), usuários do Monitor (consomem sinais), DEV/QA (implementação), PO (critérios).

## Goals / Non-Goals

**Goals**
- Split temporal treino/holdout na otimização single e batch (default 70/30, configurável).
- Otimização somente no treino; métricas e veredito no holdout.
- Gate GO/NO-GO (`criteria.py`) sobre o holdout bloqueando promoção a favorito sem GO (override admin explícito).
- Comparativo IS/OOS no resultado e revalidação de favoritos existentes na janela recente (sem auto-alteração).

**Non-Goals**
- Não refazer o Strategy Lab nem reintroduzir LangGraph.
- Não implementar walk-forward com janelas rolantes múltiplas na primeira versão (apenas split 70/30 configurável por fração ou datas).
- Não alterar a escolha do "vencedor" dentro do treino (mantém score atual), apenas validar no holdout.
- Não alterar o Monitor nem o fluxo de sinais nesta change.
- Sem migration de banco destrutiva (dados novos ficam no JSON `metrics`).

## Decisions

### D1 — Modelo de split: frações temporais (70/30) sobre candles contíguos, não janelas rolantes
O otimizador já carrega candles por intervalo; o split divide o array de candles ordenado por tempo em treino (70% mais antigo) e holdout (30% mais recente), com suporte a frações customizadas (ex.: 60/40) ou datas explícitas de corte.
- Alternativas: janelas rolantes múltiplas (complexidade alta, dados curtos por janela; adiado), split aleatório (vaza temporalidade — rejeitado), holdout por amostragem estratificada (sem sentido para série temporal).
- Razão: simples, auditável, alinhado à spec histórica 70/30 e ao esforço do card.

### D2 — `ComboOptimizer` ganha parâmetro de split e produz `best_metrics_train` + `best_metrics_holdout`
O run de otimização roda as etapas (grid/adaptativo) apenas com candles de treino; após escolher `best_params`, o final backtest roda no treino e, em seguida, um segundo backtest com os mesmos `best_params` no holdout. As métricas OOS usam `_metrics_from_trades` + heavy metrics (CAGR, benchmark, regime) quando aplicável.
- Alternativa: rodar o holdout apenas no endpoint de promoção — rejeitado porque o comparativo IS/OOS precisa estar no resultado desde a otimização.
- Impacto: `run_optimization` (assinatura de entrada) e `_execute_opt_stages`/final backtest; retrocompatível (sem split → comportamento atual, período inteiro, sem gate).

### D3 — Gate `evaluate_go_nogo` no holdout com bloqueio na API de favoritos
Novo módulo (ou função no `combo_optimizer`/`favorites`): `evaluate_holdout_eligibility(metrics_holdout)` → veredito + motivos (reutiliza `DEFAULT_CRITERIA`/`evaluate_go_nogo` com `min_trades` do holdout).
- `POST /api/favorites/`: rejeita (422/403) payload sem veredito GO no holdout, exceto com `override_oos=True` + role admin. O payload pode trazer `oos_metrics` + `oos_verdict`; se ausente para estratégias vindas do otimizador novo, o backend recalcula no backtest (custo) — **decisão**: exigir `oos_metrics` no payload salvo, evitando recálculo implícito e latência; sem o campo, rejeita com motivo (não retroage para payloads antigos, que continuam criando favoritos sem gate — falha segura para o novo fluxo, compatível com dados legados).
- Batch (`batch_backtest_service.run_batch_backtest`): candidato NO-GO não é salvo; motivo vai para o job result.
- Auto-refresh de favoritos existentes: preserva comportamento atual (não recusa atualização), mas anexa revalidação da janela recente.
- Alternativa: bloquear no frontend apenas — insuficiente (API é a fonte de verdade); bloquear no otimizador — não impede chamadas diretas à API.

### D4 — Revalidação de favoritos: novo endpoint `POST /api/favorites/{id}/revalidate`
Roda backtest do favorito na janela mais recente (ex.: últimos 90d ou período de `period_type`), calcula métricas e veredito, e retorna relatório de degradação (IS salvo vs janela recente). Não altera o favorito (flag `auto_update=false` na primeira versão).
- Alternativa: revalidar no auto-refresh e atualizar silenciosamente — muda o comportamento observado do favorito sem decisão explícita (fora de escopo).

### D4b — Backfill em massa de revalidação (solicitação de Alan, card 470)
Alan solicitou que a regra walk-forward **rode e atualize todas as estratégias já salvas** nos favoritos e monitor — não apenas restrinja novas promoções. Implementação:
- Novo endpoint `POST /api/favorites/revalidate-all` (admin; ex.: job em background com progresso) que itera todas as estratégias salvas (favoritos e favoritos do curated catalog usados pelo Monitor), roda o backtest na janela recente com o mesmo split/gate walk-forward e **atualiza os dados persistidos** do favorito: `metrics.revalidation` (comparativo IS vs janela recente, veredito GO/NO-GO, motivos) e marcação de degradação (`metrics.revalidation_verdict`, `metrics.revalidation_at`).
- **Não altera parâmetros** da estratégia nem a remove do Monitor — a regra só revalida e registra o estado; degradação é informativa (badge/estado), a decisão de remoção continua humana.
- Execução em lote com limite de itens por run (reuso de `FavoriteBacktestRefreshService`/limites de CPU), idempotente e com relatório de resumo (revalidados, falhas, NO-GO).
- Fallback: se o worker `favorite_backtest_refresh_loop` já tiver dados recentes do favorito, reusa o backtest mais recente para o comparativo (evita recomputo em massa caro) — primeira versão: recomputo por favorito na janela recente, com cache de OHLCV existente.
- Alternativa: revalidar apenas na próxima iteração do auto-refresh — lento demais para atender "todas já salvas" no momento da mudança; o endpoint explícito atende ao pedido.

### D5 — UI: comparativo IS/OOS + motivo de bloqueio
- `ParameterOptimizationResults`/`ComboResultsPage`: se `oos_metrics` presente, exibe seção "Treino vs Holdout" com métricas lado a lado e veredito GO/NO-GO (reutiliza `GoNoGoIndicator`).
- `SaveFavoriteModal`: quando NO-GO, botão desabilitado com motivo; admin vê checkbox "Salvar mesmo assim (override)".
- `FavoritesDashboard`: badge "Revalidação" quando houver relatório recente com NO-GO na janela recente (alimentado pelo backfill em massa/endpoint individual); badge/estado "Degradado" quando o backfill registra NO-GO na janela recente.
- Monitor: estratégias revalidadas refletem o veredito/degradadação no estado observado (badge de revalidação), sem alterar a seção HOLD/EXIT.
- Fidelidade: clona o shell/tokens atuais (`DESIGN.md`, `index.css`, componentes existentes); redesenha apenas o delta (coluna extra no comparativo, badge no dashboard).

## Risks / Trade-offs

- [Aumento de latência do backtest final (2 runs: treino + holdout)] → Mitigação: holdout roda apenas após `best_params` (1 run extra por otimização), não por combinação do grid.
- [Holdout curto demais produz `min_trades` não atendido → candidatos válidos rejeitados] → Mitigação: motivo explícito no veredito; frações configuráveis para períodos curtos.
- [Payloads antigos sem `oos_metrics` não podem ser salvos por fluxos que passem a exigir o campo] → Mitigação: exigência vale para o fluxo novo do otimizador; criação legada sem o campo mantém comportamento atual (compatibilidade), e o gate documenta o comportamento.
- [Falso sentimento de segurança se holdout for curto (ex.: 30d com regime atípico)] → Mitigação: expor métricas lado a lado e mínimo de trades no holdout; revalidação manual disponível.
- [Backfill em massa custoso (N símbolos × backtest na janela recente)] → Mitigação: limite de itens por run, reuso de cache OHLCV existente, job em background com progresso; execução única no momento da mudança e depois via endpoint manual.
- [Backfill atualiza dados de favoritos e pode gerar ruído visual (badges)] → Mitigação: atualização só de `metrics.revalidation*` (sem tocar parâmetros/auto_refresh_status), badges informativos e decisão de remoção permanece humana.
- [Custo adicional no batch (N símbolos × 1 run holdout)] → Mitigação: apenas 1 backtest extra por símbolo; sem mudança na paralelização atual.

## Migration Plan

1. Implementar split no otimizador com flag retrocompatível (sem split = comportamento atual).
2. Expor `oos_metrics`/`oos_verdict` no payload de resultado; UI exibe comparativo quando presente.
3. Aplicar gate no `create_favorite` (rejeição + override admin) e no batch.
4. Endpoint de revalidação + UI.
5. Migrations: nenhuma obrigatória (JSON em `metrics`); opcional coluna `oos_verdict` no `FavoriteStrategy` — decisão: manter no JSON para evitar migration nesta change.
6. Rollback: flag/feature toggle de split desliga o gate sem afetar criação legada.

## Open Questions

- Fração default definitiva (70/30) precisa de validação com Alan? (spec histórica usava 70/30 — manter).
- Override NO-GO deve exigir log de auditoria além de role admin? (sugerido: sim, reusar `admin-action-audit-log` se presente).
- Janela default da revalidação (90d? período_type?) — proposta: mesma janela do favorito ou 90d se não houver dado suficiente.
- Bypass por payload legado: exigir marcador de origem (`source: optimizer_v2`) no payload para aplicar o gate seletivamente — decisão pendente de aprovação de Alan (detalhe em D3/Assessment A).

## Prototype

- **URL HTTP navegável:** https://dev.criptofarol.com.br/prototypes/walk-forward-gate/
- **Caminho versionado:** `frontend/public/prototypes/walk-forward-gate/index.html`
- **Versão/digest:** v3 pós-polish (Assessment A corrigido); servido pelo vite DEV (sem rebuild necessário)
- **Base do sistema atual:** shell autenticado do Cripto Farol (sidebar 224px, header workspace, tokens `--canvas #0b0e11`, `--surface #1e2329`, `--primary #fcd535`, trading `#0ecb81`/`#f6465d`, tipografia BinanceNova/Inter), clonado do protótipo do card #463 (mesmo shell/tokens)
- **Escopo desktop e mobile:** tabela comparativa (>=900px) e cards empilhados com veredito por métrica (<=900px); tabs móveis Results/Favoritos
- **Fluxos e estados representados:** candidato GO; candidato NO-GO (bloqueio + motivos); override admin (checkbox pré-marcado, auditoria); holdout sem trades suficientes (badge warn); revalidação de favorito com degradação (janela 90d, sem auto-alteração); configuração de split (70/30 → 60/40)
- **Delta destacado:** coluna Holdout + vereditos por critério; banner GO/NO-GO; hint de bloqueio; modal com bloco de inelegibilidade; badge de revalidação no dashboard

## Impeccable Brief

- **Problema:** otimizador promove candidato a favorito sem evidência fora da amostra; usuário (Alan/trader) precisa ver o desempenho do holdout e entender por que um candidato foi bloqueado.
- **Usuário:** admin/trader do beta fechado que roda otimização e gerencia favoritos.
- **Resultado esperado:** decisão clara de elegibilidade (GO/NO-GO) com evidência comparativa IS/OOS, bloqueio compreensível na promoção e revalidação não destrutiva de favoritos existentes.
- **Direção:** Operate mode — superfície de decisão em app dark Binance-style; clareza de estado > expressão; o delta se comunica por cor de veredito (green/red tokens) e posição da coluna holdout.
- **Escopo:** resultados de otimização, modal salvar favorito, dashboard de favoritos (badge revalidação). Fora: Monitor, sinais, backend.
- **Estados:** GO, NO-GO, override admin, holdout insuficiente, revalidação com degradação, payload legado sem OOS.
- **Interação:** troca de cenários (protótipo), abrir/fechar modal (Escape/backdrop), override via checkbox, revalidar por favorito.
- **Restrições:** tokens do DESIGN.md (sem amarelo para dado secundário — tags holdout em cinza), fidelidade ao shell atual, a11y (foco, Escape, contraste AA em texto pequeno).

## Impeccable Critique

### Assessment A (produto/UX/a11y/responsividade/estados) — critic read-only independente

**Veredito: PASS (após correções).** Achados da rodada 1 (7 P1, ~14 P2) e disposição:

| Achado (P1) | Disposição |
| --- | --- |
| Override salva com mensagem "veredito GO" com banner NO-GO (mentia sobre o estado) | Corrigido: cenário override mantém fluxo NO-GO, checkbox pré-marcado, feedback correto |
| Ícone ✓ no banner NO-GO (sinal contraditório) | Corrigido: glifo troca dinamicamente para ✕ |
| Botão salvar habilitado em NO-GO divergia de D5 | Corrigido: hint de bloqueio inline abaixo do botão |
| Modal sem foco inicial, focus trap, Escape, restauração | Corrigido: foco no input, Escape fecha, foco restaurado ao gatilho |
| Estado "holdout sem trades suficientes" ausente | Corrigido: cenário com badge warn, métricas em "—", motivo explícito |
| Bypass via payload legado (threat model) | Decisão de design: exigir `source: optimizer_v2` para gate seletivo — **pendente de Alan** (Open Question) |
| Contraste do vermelho (#d64555 → falha AA) | Corrigido: token `trading-down #f6465d` do DESIGN.md |

P2 corrigidos: benchmark B&H no comparativo (CAGR auditável), janela "últimos 90 dias" no banner, botão Revalidar por favorito, `scope="col"`, touch target "Ver relatório" ≥36px, tags "holdout" em cinza (sem amarelo de marca para dado), formato pt-BR consistente no nome default, CSS morto removido.
P2 aceitos: modal monolítico no banner de revalidação (mock do protótipo; superfície real definida na implementação), tabs móveis sem role=tab (aceito para protótipo).

### Assessment B (detector + navegador) — vision (qwen3.7-plus) + Playwright

**Veredito: PASS.** Três rodadas de julgamento visual por pixels (subagent `vision`):
- Rodada 1: 2 P0 (veredito NO-GO e tabela de favoritos invisíveis no mobile) + 2 P1/P2 → corrigidos com cards empilhados mobile
- Rodada 2: P0 resolvidos; 2 P2 (input truncado, botão relatório quebrando) → polish
- Rodada 3: **PASS limpo** — 6/6 critérios em 8 screenshots, sem overflow/contraste/sobreposição; 8 mudanças da rodada 2→3 confirmadas

## Impeccable Audit

- **Acessibilidade:** contraste vermelho corrigido para token `#f6465d`; foco inicial + Escape + restauração no modal; `scope="col"` nas tabelas; labels de campo usam `muted-strong`; touch targets ≥36px no delta. Resíduo P2 aceito: labels `muted` herdados fora do delta.
- **Performance:** protótipo estático HTML+CSS+JS inline, sem assets externos, sem network calls — zero custo.
- **Responsividade:** tabela (≥900px) vs cards empilhados (≤900px) com vereditos por métrica; tabs móveis; sem overflow detectado em 390px e 1440px.
- **Theming:** tokens do DESIGN.md aplicados (canvas/surface/primary/trading); exceção registrada: nenhuma — amarelo de marca removido de tags de dado.
- **Integridade:** 81 asserts Playwright verdes (desktop 1440x900 + mobile 390x844), sem erros de console/pageerror; detector Impeccable: 1 anti-pattern P2 `flat-type-hierarchy` (11–20px em tabela financeira densa — classificado como aceito: hierarquia real é dada por cor/fonte mono/negrito, densidade intencional de tabela de dados).

## Impeccable Trace

- **Versões:** Impeccable skill local (scripts `context.mjs`, `detect.mjs`); Playwright via `frontend/node_modules`; vision = `opencode-go/qwen3.7-plus` (única exceção de roteamento visual do projeto).
- **Comandos:**
  - `node .agents/skills/impeccable/scripts/context.mjs --target frontend/src/pages/ComboResultsPage.tsx` (produziu PRODUCT.md)
  - `node .agents/skills/impeccable/scripts/detect.mjs --target frontend/public/prototypes/walk-forward-gate/index.html` → 1 anti-pattern P2
  - `node tests/e2e/walkforward-prototype-check.spec.mjs` → **81 checks, 0 falhas** (desktop 1440x900 + mobile 390x844, URL https://dev.criptofarol.com.br/prototypes/walk-forward-gate/)
  - Vision: 3 rodadas sobre `/tmp/opencode/wf-gate-shots/*.png` (go/nogo/override/modal/favorites, desktop+mobile)
- **Digest/target:** `frontend/public/prototypes/walk-forward-gate/index.html` (servido via vite DEV; evidência invalidada a cada rebuild/restart)
- **Modelo:** Assessment A = reviewer subagent na sessão principal (mesmo LLM/modelo `deepseek-v4-flash` da sessão — herança de modelo observada via spawn da sessão; ver regra de roteamento). Assessment B = `vision` (qwen3.7-plus, exceção explícita de roteamento visual do projeto para julgamento de pixels). Igualdade de modelo A/B com a sessão principal é a configuração de subagents do projeto (`.opencode/agent/`); evidência de spawn registrada em `.impeccable/vision-router.jsonl`.
- **Findings do detector:** `flat-type-hierarchy` (1) — classificado como aceito com justificativa (densidade de tabela de dados financeira).
- **Vínculo com Prototype Validation:** mesma versão v3 validada nos 81 asserts e nas 3 rodadas vision; browser gate executado sobre a URL DEV servida.

## Prototype Validation

- **URL servida:** https://dev.criptofarol.com.br/prototypes/walk-forward-gate/ (vite DEV local 5173 idêntico; verificado por md5 idêntico entre arquivo e resposta)
- **Viewports:** desktop 1440x900 e mobile 390x844
- **Comando:** `node tests/e2e/walkforward-prototype-check.spec.mjs` → **81 checks, 0 falhas**
- **Asserts cobertos:** badge GO/NO-GO/warn, banner (texto/ícone/cor), split 70/30→60/40, coluna OOS (desktop) e tags holdout (mobile), vereditos por métrica (GO/NO-GO/dash), botão salvar GO habilitado, modal (abre/fecha, bloco inelegível, checkbox override pré-marcado, confirm desabilitado sem override, feedback override, Escape, foco restaurado), banner revalidação (janela 90 dias, badge NO-GO, relatório, botão revalidar), tabs móveis, ausência de console/page errors
- **Resultado:** PASS em desktop e mobile, 0 falhas, 0 erros de console/página
- **Versão validada:** v3 (pós-polish) — qualquer alteração posterior no HTML/CSS/JS ou rebuild/restart invalida esta evidência

## Design Critique

- **Produto:** gate GO/NO-GO no holdout + comparativo IS/OOS + override admin + revalidação sem auto-alteração resolve o problema real (overfit → favorito) com decisão defensável; override com trilha de auditoria é a saída correta de exceção.
- **UX:** hierarquia clara (banner de veredito → coluna holdout → vereditos por critério); bloqueio comunicado em 3 camadas (badge, banner, hint/modal); revalidação não destrutiva; carga cognitiva adequada.
- **Acessibilidade:** ver Assessment A/B — foco, Escape, contraste AA no delta, `scope` e touch targets corrigidos; resíduos herdados do sistema classificados.
- **Responsividade:** desktop/mobile cobertos com quebras adequadas; vereditos e badges visíveis em ambos.
- **Estados:** GO, NO-GO, override, holdout insuficiente, revalidação com degradação e payload legado (sem comparativo) cobertos; "trades insuficientes" e "override" eram os pontos mais fracos da rodada 1 e estão corrigidos.
- **Fidelidade:** shell/tokens/tipografia clonados do sistema atual (base: protótipo #463 + DESIGN.md); delta óbvio (coluna holdout + vereditos + badges); nenhum layout paralelo inventado.
- **Riscos/pendências não bloqueantes:** bypass por payload legado (Open Question para Alan — exigir `source` marker no payload); modal monolítico de revalidação (superfície real na implementação); janela default de revalidação (90d proposto).

**Prototype Validation:** 81 asserts Playwright verdes em desktop/mobile sobre a URL DEV, 3 rodadas vision PASS, sem erros de console/página.

**Design Agent verdict: PASS** — `UI impact: affected`, protótipo v3 validado em navegador real (desktop+mobile), achados P1/P2 corrigidos ou classificados, zero P0/P1 aberto no escopo do delta. Aprovação humana (`Aprovação de Design -> Pronto para Dev`) pertence a Alan.
