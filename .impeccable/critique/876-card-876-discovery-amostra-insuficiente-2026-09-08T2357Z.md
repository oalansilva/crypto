# Snapshot — card 876 · change card-876-discovery-amostra-insuficiente

> Evidência longa do filho Design-autor. O `design.md` traz só recorte; este arquivo é o snapshot completo. Não enviar ao Gist. O autor não emite `Design Agent verdict` final nem `## Design Critique`.

## Metadata

- card: 876 — "Descoberta: varredura não deve gastar minutos em par sem histórico suficiente"
- change: `card-876-discovery-amostra-insuficiente`
- worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-876-discovery-amostra-insuficiente` · branch `card-876-discovery-amostra-insuficiente` (tracking origin/develop)
- Status observado: Design (T3 pelo pai; este filho não chama `process_event`)
- autor: filho Design-autor isolado · mesmo modelo do pai · sem visão de pixels
- data (UTC): 2026-09-08T23:57Z
- pipeline: context → shape → prototype → critique própria → audit → polish (StrReplace) → browser gate
- spawns: 0 (sem nested A/B)

## Brief (integral — issue grelhado via `gh api repos/oalansilva/crypto/issues/876`, sem reentrevista)

**Problema:** administrador dispara varredura grande em PROD e espera horas enquanto pares sem histórico suficiente ainda correm o grid (~16 mil parâmetros, 1–2 min); o progresso conta isso como sucesso e o ranking parcial polui.

**História:** como administrador da Descoberta, quero que combinação sem histórico mínimo termine em segundos, entre no progresso como amostra insuficiente e apareça no Decidir sem rank e sem promover.

**Entra:** mesmo em «todo o histórico», listagem curta demais para alguma vez 30 negócios → segundos, sem grid; progresso `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente`; sucesso = rodou e deixou candidato (inclui `Baixa amostra` pós-grid); ignoradas = não rodou (cancelar); amostra insuficiente = listagem curta, sem otimização; Decidir mostra a linha, sem rank, sem promover, selo `Amostra insuficiente` (não misturar com `Baixa amostra`), métricas N/A, fora do top-5; varredura só com listagem curta conclui (0 sucesso + N amostra insuficiente), não falha de worker; «1 por sweep» nesta VPS não muda; par com histórico cheio segue o caminho feliz.

**Não entra:** concorrência/Celery; redesign 3 modos/top-5 (#852); run `#c243f729`; universo 694; Calmar inflado com histórico cheio; poupar tempo em par com anos de candles e poucos negócios.

**Vocabulário:** histórico mínimo; amostra insuficiente (quarto saco + selo); baixa amostra (pós-grid); sucesso; ignorada; varredura; parciais top-5. Avoid: «aumentar o sweep»; sucesso = elegível; cobertura = «temos 2 anos»; ignorada = listagem curta; baixa amostra = amostra insuficiente.

**Aceite:** 8 givens do body. Fronteira de operador vazia.

**Como (Design):** medir listagem antes do grid; traduzir «não dá para 30» em barras do timeframe com split 70/30; persistir quarto contador + linha Decidir; reconcile não trata só-amostra-insuficiente como falha operacional; chip vs texto = Apply.

## Shape

- `node .agents/skills/impeccable/scripts/context.mjs --target /combo/discovery` uma vez. PRODUCT.md + DESIGN.md Binance (não reescrita). Surface brief: not-found. Modo: Operate.
- Audience: administrador da Descoberta, varredura grande, VPS saturada.
- Outcome: ver pares sem histórico sem esperar minutos de grid, sem poluir top-5.
- Direction: clone+delta da rota viva; mesmo chrome e selo amber; palavras distintas.
- Scope: Acompanhar (fórmula) + Decidir (linha). Montar intacto. Sem painel ANTES/DEPOIS.
- Assumptions (sem AskUser): teto teórico 1 negócio por barra de treino; medição em claim-time.

## Decisions (mecanismo)

1. Gate em `run_combination` após `sweep.state==running`, antes de `run_optimization`/`generate_stages`. Mesmo `fetch_ohlcv` do otimizador.
2. Corte se listagem vazia/`<2` ou `len(split_train_holdout(df, 0.7)[0]) < 30`.
3. Estado `insufficient_sample`; contador `insufficient_sample`; `processed = succeeded+failed+skipped+insufficient_sample`; só-esse-desfecho → `completed`.
4. UI: fórmula com quarto termo; linha Decidir selo `Amostra insuficiente`, rank —, N/A, sem CTA Promover.

## Critique própria (autor, não A/B)

- C1 (P2): logo relativa `../../brand` no servidor de `/prototypes` 404 no console desktop. → StrReplace para `/brand/cripto-farol-logo-v6-transparent.svg` + favicon data-URI. Re-gate 17/17.
- C2 (P3): chip vs texto do selo — mesmo `.sample-badge` amber da baixa amostra, palavras distintas. Apply.
- Detector Impeccable: `[]`.

## Audit

- A1 (harden): proto estático, sem innerHTML de input; tabs só setam classes.
- A2 (adapt): tabela Decidir vira cards em ≤720px (`data-label`); linha insuficiente permanece legível.
- A3 (clarify): `Baixa amostra` vizinha intacta para não misturar selos.

## Browser gate (autor)

- URL: https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/
- sha256 `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` · 33203 bytes · servido == local
- Chromium headless, viewports 1440×900 e 390×844
- 17/17 PASS × 2; 0 console error; 0 pageerror; 0 ≥400
- PNGs: `/tmp/card876-gate/{desktop,mobile}-{montar,acomp,decidir}.png`
- Veredito do autor (não final da coluna): PASS. Pai dispara A/B.

## Trace

1. Skills: openspec-new-change, openspec-ff-change, design-critic (etapas autor), covenant-flow, impeccable (context+shape+craft-floor).
2. Briefing: REST issue #876 (DoD completo).
3. `openspec new change` + ff artifacts + `openspec validate` strict OK.
4. Proto clone+delta; bounce `criptofarol-dev-prototypes.service` para incluir o worktree novo nos roots.
5. Gate falhou 1/17 (404 console) → polish → re-gate 17/17.
6. Sem `process_event`, sem commit/push, sem `## Design Critique`, sem spawn A/B, sem editar `backend/` nem `frontend/src/`.
