# Design — card 852: Descoberta em 3 modos (Montar / Acompanhar / Decidir)

live_route: /combo/discovery
surface: existing

UI impact: **affected** — muda layout e copy da Discovery (`/combo/discovery` passa a exibir 1 de 3 modos por vez em vez dos ~7 blocos simultâneos).

## Problema

O operador beta trava na Descoberta: ~7 blocos simultâneos com vocabulário de infra (snapshot, hash, token, dedup, #PF-) escondem o caminho feliz montar → acompanhar → decidir.

## Usuário afetado

Operador beta da Descoberta (grupo fechado, manual), que monta varreduras e decide o que promover a favorito tier 3.

## Hipótese

1 modo visível por vez + preflight em 3 linhas + leaderboard com 3 colunas de risco reduzem abandono no início e trava na tabela, sem mudar motor, ranking ou elegibilidade.

## Resultado esperado

Os 7 critérios de aceite do issue (§5) passam em browser real: Montar só com preflight humano; iniciar colapsa e trava em `Acompanhando #X`; bloqueio nomeia a diferença; leaderboard 1 ordenação + 3 colunas + 10–15/pág; seleção inline; promoção com resumo de risco; sem regressão de foco/a11y.

## Recorte

- **Audience:** operador beta (não público, não admin de motor).
- **Outcome:** decidir o que promover com risco visível, sem abandonar.
- **Direction:** simplificar interface; ação dominante = **Iniciar**, Promover secundário; **Short escondido** do caminho feliz (decisões operador 2026-09-06, rodada 1 — não reabertas).
- **Scope:** só `DiscoveryPage` (layout/copy/estados). Fora: motor, ranking, elegibilidade, taxas, dedup, workers, período (exceto preset default do seletor = Todo o histórico, sem mudar motor — ajuste Alan 2026-09-07), novas métricas, redesign visual.

## Apply contract

- O apply (pós `Pronto para Dev`) carrega este `design.md` + o protótipo abaixo como **spec de UI** antes de editar `frontend/src`; contrato de API é fonte de dados, não de layout.
- Fidelidade bloqueante: landmarks do catálogo (`Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`) + tokens/estados de `DESIGN.md` (sem reescrevê-la).
- Desvios do protótipo: registrar path, elemento e motivo no handoff/PR; sem registro = bloqueio.
- Dialog íntegro: os modais Promover e edição avançada têm header + corpo DENTRO do `role=dialog` (fix 2026-09-06: `</div>` → `</header>` nas linhas ~246/270 do protótipo; o apply NÃO copia o typo).
- Fora do switch de modos (preservar sem regressão no apply): Descartar por linha + copy destrutiva, estados dedup (`duplicate`/`already_promoted`), bloco 409, nota de revalidação sob lock, painel 403, bloco stale, sessão expirada.
- Parciais do Acompanhar: top-5 travadas do sweep em curso, sem paginação nem re-perguntar o rascunho.
- Página 10–15: fato técnico (performance/custo do 3 atual) a confirmar no apply; protótipo usa 12.
- Proibido no apply: reintroduzir UUID/hash/token/fórmula no caminho feliz; renumerar rank sob filtro; re-perguntar rascunho nos filtros do leaderboard.

## Prototype

- **URL:** https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/
- **Caminho versionado:** `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` (branch `card-852-descoberta-tres-modos`)
- **Digest (sha256):** `8e9c02221ea6c2db885c17e08541c01f3b6c99f206023c226962c74bb0748aee` · 34075 bytes · servido == local (ajustes-Alan 2026-09-07: default Todo histórico; ajuste-Alan-2 2026-09-07: edição avançada reduzida de 4 para 2 ações de eixo inteiro; anterior `f5c81ef7…` 34662 bytes)
- **Viewports:** desktop 1440×900, mobile 390×844
- **Base usada:** rota viva `/combo/discovery` nesta worktree — landmarks do catálogo (`route-landmarks.yaml`) + estrutura de `frontend/src/pages/DiscoveryPage.tsx` (2287 linhas, só leitura); nenhum HTML fonte copiado.
- **Fluxos/estados:** Montar (rascunho editável + preflight 3 linhas com default `Todo o histórico` + datas da janela + CTA estável do histórico cheio) · Acompanhando #A8421 (rascunho colapsado + progresso + leaderboard travado, parciais top-5) · Decidir (leaderboard #A8390, 24 candidatos; filtro zerado com mensagem + "Limpar filtros") · bloco "mesmo escopo vs outro escopo" + ver progresso · modal Promover (dialog íntegro: header + resumo de risco lado a lado + Tier 3 + onde ver depois) · modal edição avançada (2 ações de eixo inteiro: Selecionar todos / Limpar seleção + contador ao vivo `X de N`; filtro + marcar/desmarcar permanecem inline; inline reflete após Aplicar) · simulador de estado rotulado "só protótipo". Vocabulário PT: "Pronto para iniciar" (preflight), chip "EM CURSO" (`snapshot` só no `<details>` técnico).
- **Delta aplicado (só card 852):** 1 modo visível por vez; preflight humano + impedimentos, técnico em `<details>`; leaderboard 1 ordenação + Calmar/Max DD/Trades-cobertura + expansão + 12 por página; seleção inline + modal avançado; CTA `Iniciar varredura — N, ~T` dominante; Short fora do caminho feliz; promoção secundária com resumo de risco.

## Prototype Validation (fix 2026-09-06T18-30Z — re-gate pós-correção dos modais)

- **URL:** https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/ (gate executado contra `http://127.0.0.1` local, mesmos bytes — sha256 igual nas duas pontas: `0a2bc572…`, 32946 bytes)
- **Viewports:** desktop 1440×900 (4 PNGs reais em `/tmp/card852-desktop-*.png`) + mobile 390×844 (4 PNGs reais em `/tmp/card852-mobile-*.png`); `desktop-promote.png` ≠ `desktop-decidir.png` (captura distinta com modal aberto).
- **Asserts EM ESCOPO DE DIALOG (o que o gate anterior perdeu):** `.risk`/`.dest`+Tier 3/ações/confirmar DENTRO de `#m-promote`; `.body` DENTRO de `#m-adv`; geometria desktop (dialog 520px, corpo 518px dentro, padding 20px, corpo abaixo do header) e mobile (dialog 350px, corpo 348px dentro, padding 20px); Escape fecha + foco retorna + trap Tab; confirmação cita Favoritos.
- **Resultado resumido:** 48/48 PASS (24 por viewport), 0 erros de console, 0 pageerrors, 0 recursos ≥400, servido == local. Sem revisão de pixels (modelo sem visão; PNGs para revisão humana). Veredito próprio: **PASS**.
- **Gate clone (design_clone_gate, rodada gate 2026-09-06):** `design.md` declara `live_route: /combo/discovery` + `surface: existing` (linhas standalone); protótipo com 7 pares `COPIED:start/end` só no espelhado do vivo (cabeçalho, h2+chip do rascunho, timeframes, período, header/meta do leaderboard, nota rank-stable); `clone_gate_ok == True` local; copiados 1801 bytes vs gerados ~31199 bytes; servido == local (sha256 `9bffc2df…`, 33294 bytes, sem restart — server lê o worktree); sanity 1440×900: landmarks 3/3 + dialog Promover abre/fecha (Escape), 0 erros de console.
- **Ajustes-Alan 2026-09-07 (default Todo histórico + 4 ações edição avançada):** `clone_gate_ok == True` local pós-edição (7 pares COPIED intactos, landmarks 3/3); servido == local sem restart (sha256 `f5c81ef7…`, 34662 bytes, `curl http://127.0.0.1:5176/prototypes/card-852-descoberta-tres-modos/` 200); sanity browser real 2 viewports (1440×900 + 390×844, Playwright+Chromium): 25/25 PASS por viewport — default `#sel-period=all`, preflight `24 combinações · ~2h 24min estimado · todo o histórico [01 jan 2017, 01 jan 2026)`, CTA `Iniciar varredura — 24, ~2h 24min`, `Selecionar todos`→`8 de 8`→inline `8 selecionados`, `Limpar seleção`→`0 de 8`→inline `0 selecionados`, regressão (landmarks 3/3, 1-modo, dialogs íntegros com Escape+foco, 0 console errors, 0 pageerrors). Veredito próprio: **PASS**.
- **Ajuste-Alan-2 2026-09-07 (edição avançada 4→2 ações de eixo inteiro):** removidos `#m-adv-select` (Selecionar filtrados) e `#m-adv-clear` (Limpar) e seus 2 listeners (StrReplace, sem reemitir); ficam `#m-adv-select-all` (Selecionar todos) + `#m-adv-clear-all` (Limpar seleção); subtítulo `…— selecionar todos ou limpar seleção.`; contador `#m-adv-count` `X de N` continua. `clone_gate_ok == True` local pós-edição (7 pares COPIED intactos — sum 1801 bytes; landmarks 3/3); servido == local sem restart (sha256 `8e9c0222…`, 34075 bytes, `curl http://127.0.0.1:5176/prototypes/card-852-descoberta-tres-modos/` 200, `diff` vazio); sanity browser real 2 viewports (1440×900 + 390×844, Playwright+Chromium): 31/31 PASS por viewport — edição avançada mostra só `Selecionar todos` + `Limpar seleção` (sem `Selecionar filtrados`/`Limpar`; `.rowbtns` = exatamente {Selecionar todos, Limpar seleção, Aplicar}); `Selecionar todos`→`8 de 8 selecionados`→Aplicar→inline `8 selecionados`; `Limpar seleção`→`0 de 8 selecionados`→Aplicar→inline `0 selecionados`; regressão (default `#sel-period=all` Todo histórico, preflight `24 combinações · ~2h 24min estimado · todo o histórico [01 jan 2017, 01 jan 2026)`, CTA `Iniciar varredura — 24, ~2h 24min`, dialogs Promover/avançada íntegros com header+corpo DENTRO do `role=dialog` + Escape+foco, filtro inline ok, 0 console errors, 0 pageerrors). Veredito próprio: **PASS**.

## Design Critique (pai — síntese A/B + re-gate)

- P0 — nenhum (A, B, re-gate). Landmarks 3/3 no proto e na fonte viva; sem ANTES/DEPOIS; sem galeria; não só-chrome. Disposition: aceitar.
- P1-B — modais com `</div>` no lugar de `</header>` (BLOCKED de B): corrigido no fix, 2 linhas via StrReplace; re-gate 62/62 com asserts em escopo de dialog + geometria. Disposition: resolvido.
- P1-A1/A2 — evidência desktop 1440 + modal distinto: recapturados (4× 1440×900 reais, promote ≠ decidir). Disposition: resolvido tecnicamente; passada visual humana segue pendente (P3-R1).
- P1-F1 — fusão apply sem regressão (Descartar/dedup-409/stale/403/sessão): vinculada em tasks 1.1/5.1 + req 8 + Apply contract. Disposition: aceitar com vínculo.
- P2 — PT ("Pronto para iniciar", "EM CURSO"), vazio com "Limpar filtros", parciais top-5 definidas: incorporados no fix. Disposition: resolvidos.
- P3 — página 12 como placeholder de 10–15 (confirmar no apply, task 3.1); micro-copy; `leases` preservado fora de escopo; rota viva sem sessão (só fonte; apply confirma em DEV); mobile bytes não-determinísticos. Disposition: aceitar como pendências do apply.
- Riscos não bloqueantes: passada visual humana dos PNGs antes da Aprovação de Design (Alan); sem revisão de pixels pelos modelos.
- Refs: protótipo https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/ (sha256 `0a2bc572…`, 32946 bytes, servido == local); snapshots `.impeccable/critique/852-card-852-descoberta-tres-modos-2026-09-06T18-09Z.md` (autor), `…-assessment-A-2026-09-06T18-16Z.md`, `…-assessment-B-2026-09-06T18-19Z.md`, `…-fix-2026-09-06T18-35Z.md`, `…-regate-2026-09-06T18-36Z.md`.
- Design Agent verdict: **PASS**.
