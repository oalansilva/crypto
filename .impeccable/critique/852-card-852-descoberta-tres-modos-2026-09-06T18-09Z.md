# Snapshot — card 852 · change card-852-descoberta-tres-modos

> Evidência longa do filho Design-autor. O `design.md` da change traz só as seções curtas; este arquivo é o snapshot completo (Brief/Critique/Audit/Trace, Nielsen, personas, metadata). Não enviar ao Gist.

## Metadata

- card: 852 — "Descoberta — simplificar tela em 3 modos (Montar / Acompanhar / Decidir)"
- change: `card-852-descoberta-tres-modos`
- worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-852-descoberta-tres-modos` · branch `card-852-descoberta-tres-modos` (base develop)
- Status observado: Design (não movido; sem `process_event`)
- autor: filho Design-autor isolado · modelo `muse-spark-1.3-contributor-free` (sem visão — sem revisão de pixels)
- data (UTC): 2026-09-06T18:09Z
- pipeline: context → shape → prototype → critique própria → audit → targeted fixes → polish (StrReplace) → browser gate real (CDP/Chromium, desktop+mobile) → reexecução pós-fix
- spawns: 0 (nenhum subagent; sem nested-spawn de A/B)

## Brief (integral, sintetizado do issue grelhado via `gh api`, sem reentrevista)

Problema: operador beta sofre para iniciar varredura e decidir o que promover; tela mostra 7 blocos com vocabulário de infra. História: como operador beta, montar/acompanhar/decidir em 3 modos simples sem ver chave/hash/token/fórmula, para enxergar melhor antes de decidir. Entra: 1 modo por vez (Montar / Acompanhando #X / Decidir); preflight humano `N combinações · ~T estimado · janela/período` + lista do que falta; leaderboard 1 ordenação + 3 colunas de risco + expansão + página 10–15 + evidência (janela, candles, fees); seleção inline + modal como edição avançada (2 ações); CTA iniciar estável `Iniciar varredura — N, ~T` + bloqueio nomeando diferença; promoção com resumo de risco lado a lado + Tier 3 + onde ver depois; manter foco/a11y, honestidade evidencial, copy destrutiva. Não entra: motor, ranking, elegibilidade, taxas, dedup, novas métricas/filtros, período, backend/workers/limites, migração, redesign visual. Vocabulário: varredura, rascunho, preflight, acompanhando, leaderboard, promover; evitar no caminho feliz: sweep, snapshot, draft, hash, token, dedup, lease, run, #PF-. Aceite: 7 itens (§5 do issue). Decisões operador 2026-09-06 rodada 1 (Alan, fechadas): ação dominante = Iniciar (Promover secundário); Short escondido do caminho feliz até ter dados. Página 10–15 = fato técnico p/ Design. Nota: evidência Impeccable dual-agent citada no issue (`.impeccable/critique/2026-09-06__frontend-src-pages-discoverypage-tsx.md`, 17/40, 5 issues P0–P2) **não existe nesta worktree** (dir `.impeccable/critique/` vazio); funcionalidade foi mantida por leitura direta de `DiscoveryPage.tsx` (2287 linhas).

## Shape (context)

- `node .agents/skills/impeccable/scripts/context.mjs --target /combo/discovery` executado uma vez: retornou product-schema + DESIGN.md (Binance) como sinal de forma.
- `DESIGN.md` = autoridade visual (não reescrita): canvas `#0b0e11`, primary `#FCD535`, texto `#EAECEF`/muted, cards `#1E2329`, radius 6–12px, CTA amarelo-preto, verde/vermelho só semântica de preço.
- Fidelidade bloqueante: `scripts/process-fsm/route-landmarks.yaml` → `/combo/discovery`: textos `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`; seletores `[]` (sem seletor estrutural — prova por texto + estrutura da página viva).
- Superfície viva mapeada (só leitura): breadcrumb Combo/Varreduras; h1 + subcopy; recovery banner; sweep progress card (pausar/cancelar/novo rascunho); draft grid (templates/symbols/timeframes/Long+Short-disabled/período/ranking); preflight aside (fórmula, hash, chave, token — a remover do caminho feliz); leaderboard 13 colunas, PAGE_SIZE=3, filtros, rank estável; modais promover/descartar; seletor de run histórica.

## Critique própria (protótipo v1)

- C1 (P1): shorthand `font: <peso> <tamanho> inherit` inválido em 5 regras (botoeiras caíam p/ 14px herdado). → fix aplicado.
- C2 (P2): tabs sem navegação por setas (roving tabindex parcial). → handler ArrowLeft/Right aplicado.
- C3 (P2): `:focus-visible` só nas tabs; botões `.btn/.exp/.cta` sem anel visível. → regra global aplicada.
- C4 (P3): 404 de `/favicon.ico` no console (protótipo sem ícone). → favicon inline data-URI aplicado; gate reexecutado.
- C5 (nota, não-defeito): assert `three-risk-cols` falhou por `text-transform: uppercase` no CSS (innerText maiúsculo) — corrigido no harness (comparação case-insensitive), não no protótipo.

## Audit (só com achado: harden/adapt/clarify)

- A1 (harden): `#lnk-prog` injetado via innerHTML com strings estáticas + binding imediato — sem vetor XSS; mantido.
- A2 (clarify): simulador de estado rotulado "só protótipo" p/ não confundir com produto; mantido.
- A3 (adapt): grid `.risk` 2 col em 390px — denso mas legível; aceito p/ protótipo, anotado p/ apply.
- Sem painel ANTES/DEPOIS como index, sem galeria de estados, sem HTML copiado (bytes copiados = 0).

## Trace (pipeline)

1. context 18:0xZ — script impeccable 1×.
2. shape — landmarks + DiscoveryPage integral + issue grelhado; design.md curto planejado.
3. prototype — `index.html` escrito à mão (clone estrutural + delta), 413 linhas.
4. critique/audit — acima (C1–C5, A1–A3).
5. targeted fixes + polish — 8 patches StrReplace (6 fonte/foco/setas + favicon; nenhum reemit de HTML).
6. browser gate — servidor de protótipos não via worktree nova (roots no boot 2026-09-05) → `systemctl restart criptofarol-dev-prototypes.service` (stateless) → 200 nas duas pontas; CDP Chromium 153: 25 asserts desktop+mobile.
7. Gate v1: 23/25 (favicon 404 + case do harness) → fixes → gate v2: **25/25, 0 console errors**.

## Nielsen (resumo, sem tabela integral)

Visibilidade de estado: modo único + chip + progresso com ARIA. Jargão: fora do caminho feliz (`<details>`). Controle: ver progresso/novo rascunho/limpar filtros. Consistência: Short escondido nos dois lugares; rank estável. Prevenção de erro: CTA desabilitado + impedimentos listados; bloqueio nomeia diferença. Reconhecimento: 3 linhas + resumo de risco lado a lado. Estética/minimalismo: 3 colunas de risco, resto em expansão.

## Personas

Operador beta: monta varredura 2–4×/semana, decide promoções; teme criar run duplicada e promover sem ver risco. Leitor de tela/teclado: exige foco, traps e rótulos sem regressão (aceite 7 preservado no spec).

## Veredito próprio

**PASS** — 25/25 asserts observáveis em browser real desktop+mobile, console limpo, servido == local (`9b298054…`, 32397 bytes). Limites: sem revisão de pixels (modelo sem visão; PNGs em `/tmp/card852-*.png`); página 12 como placeholder do 10–15 até confirmação técnica no apply; crítica dual-agent citada no issue ausente na árvore (usada leitura direta).
