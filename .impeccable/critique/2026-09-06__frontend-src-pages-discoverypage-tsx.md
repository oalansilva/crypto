Method: dual-agent (A: cda71a48-fc40-4a5a-a7c2-5dd6044e4c80 · B: 8aee45ba-f965-40c9-840a-d31f4b53f967)
Target: frontend/src/pages/DiscoveryPage.tsx
Slug: frontend-src-pages-discoverypage-tsx
Date: 2026-09-06

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | 3 fontes concorrentes (recovery + progresso + preflight); draftFrozen sem saída clara |
| 2 | Match System / Real World | 1 | Fala em sweep/preflight/snapshot/hash; usuário pensa "testar 3 estratégias em BTC no 4h" |
| 3 | User Control and Freedom | 2 | Undo existe, mas congelamento pós-start só deixa "Novo rascunho"; cancel em 2 cliques com copy de lease |
| 4 | Consistency and Standards | 2 | Primário amarelo consistente, mas 3 sistemas de filtro diferentes; PAGE_SIZE 3 vs 6 |
| 5 | Error Prevention | 2 | Preflight bloqueia, mas `blockedOtherSelection` invisível até virar live-block genérica |
| 6 | Recognition Rather Than Recall | 1 | Exige lembrar activeSweep vs viewSweep, draftMetric vs metric, hash #PF-XXXX entre 3 lugares |
| 7 | Flexibility and Efficiency | 2 | Há bulk-actions e tabs com setas, mas sem caminho feliz em 1 clique / repetir varredura |
| 8 | Aesthetic and Minimalist Design | 1 | 7 blocos simultâneos; preflight sozinho tem 10+ elementos; tabela 13 colunas |
| 9 | Error Recovery | 3 | Melhor parte: preflight/start/session/lb/conflict 409 com ação; peca no toast genérico de pause/cancel |
| 10 | Help and Documentation | 1 | Sem guidance decisório: o que é Calmar bom? quando promover? por que Calmar vs delta B&H? |
| **Total** | | **17/40** | **Crítico — abaixo da faixa típica 20-32; pede simplificação estrutural, não polish** |

## Design Specificity Verdict

Intercambiável (falha). Composição de admin genérico dark, vocabulário de backend (sweep, preflight, snapshot, draft, dedup, leases, token). Troque template/símbolo por job/recurso e serve a qualquer batch-runner. Única especificidade real está no leaderboard (CAGR/B&H/Max DD/Calmar) — e mesmo aí sem tradução visual para decisão swing. Tom sóbrio ok, mas sóbrio ≠ críptico.

Deterministic scan: `detect.mjs --json frontend/src/pages/DiscoveryPage.tsx` → exit 0, `[]`, 0 findings. Ou seja: sem violações mecânicas, o problema é IA/carga cognitiva, não lint.

Evidência objetiva (B): 13 colunas; 4 filtros leaderboard + 2 configs + workbench; ~14 CTAs globais + 2 por linha; 7 seções/banners simultâneos; PAGE_SIZE=3; jargões renderizados (snapshot, #PF-, Chave do rascunho UUID, sweep_id, run, leases, token, elegibilidade ≥30/≥90%, candles expected/observed, fees/slippage, dedup, result_id, Tier 3, 403/409).

Browser/overlay: sem injeção (sem browser nesta run). Fallback = leitura estática integral (2287 linhas + CSS + Workbench 534 linhas).

## Overall Impression

Funcionalidade ok, interface operando como cockpit de infra em vez de apoio à decisão. O maior ganho não é visual, é reduzir de 7 blocos concorrentes para 1 modo visível por vez: Montar → Acompanhar → Decidir.

## What's Working (manter)

1. Disciplina de foco/a11y acima da média: foco vai ao progresso após start e ao fim, focus-trap nos modais, retorno de foco, aria-describedby, data-label mobile.
2. Honestidade evidencial: janela UTC, observed/expected candles + source/version, fees/slippage, badge Baixa amostra com critério, rank global que não renumera, disclaimer histórico.
3. Escopo destrutivo bem delimitado em copy: discard e cancel explicam o que fica e o que sai. Raro e valioso.

## Priority Issues (simplificação)

P0 — Modelo mental duplo (activeSweep vs viewSweep) + rascunho congelado. Fix: um modo por vez (Acompanhando #X vs Montando próxima); rascunho colapsado durante execução; "Duplicar como base" em vez de "Novo rascunho" críptico; remover hydrate silencioso.

P0 — Preflight expõe internals e bloqueia sem checklist. Fix: 3 linhas humanas (Escopo N · Tempo ~T · Janela) + lista de impedimentos acionáveis; esconder UUID/hash/token/fórmula em detalhe expansível.

P1 — Leaderboard ilegível (13 col × 3 linhas). Fix: 1 ranking + 3 colunas de risco por padrão (ex. Calmar, Max DD, Trades/cobertura), resto em expansão; página 10–15; fundir filtros com facetas do sweep; evidence estruturada.

P1 — Seleção fragmentada (2 cards + modal 4 bulk-actions + 2 modos). Fix: seleção inline com busca/contador para casos comuns; Workbench vira "edição avançada"; unificar em 2 ações; eliminar all+exceções da UI.

P2 — CTA Iniciar instável + bloqueio live invisível. Fix: rótulo estável ("Iniciar varredura — N, ~T") + estado explícito nomeando a diferença (símbolos? período?) com link "ver progresso".

## Persona Red Flags

First-timer: trava em "Catálogo inteiro · N exceções", Workbench com aplicar/descartar, "Aguardando escopo", 13 siglas sem glossário.
Cauteloso: não promove porque modal mostra IDs mas não risco lado a lado (DD/trades/cobertura/janela), nem reversibilidade/onde ver depois; 409 "equivalente" sem porquê.
Power: não repete variando 1 eixo — frozen impede clonar-e-ajustar, histórico sem diff, symbolOptions instável.

## Minor Observations

- H1 duplicado; Short desabilitado no rascunho mas presente nos filtros; 4 IDs concorrentes (UUID, #PF-, result_id, favorite_id); "Limites: 8 global · 1 por sweep" sem posição/ETA; PAGE_SIZE divergente; período 6m/2y/all sem datas antes do start; `−` U+2212 vs `-`; mobile empilha 2 CTAs full-width por linha; toast sem ação.

## Questions to Consider

1. Se o beta só pode fazer UMA coisa aqui, iniciar ou promover — por que competem em pé de igualdade?
2. Que decisão um UUID/hash já ajudou um investidor a tomar?
3. Por que escolher símbolo/timeframe 2× e período 0× após o start?
4. Que medo o PAGE_SIZE=3 protege — do usuário ou do servidor?
5. Como a tela prova "nenhum candidato é salvo sem revisão" no clique Promover?

## Run Notes

- slug: frontend-src-pages-discoverypage-tsx OK; ignore list: ausente (sem .impeccable/critique/ignore.md)
- independência: A e B isolados, prompts self-contained, sem troca entre si
- CLI: exit 0, 0 findings, target 2287 linhas
- browser: não usado (sem automação nesta run); overlay: sem injeção; live-server: n/a
- temp cleanup: n/a; snapshot: este arquivo; trend: n/a nesta run
