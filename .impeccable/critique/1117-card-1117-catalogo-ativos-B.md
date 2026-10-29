# Assessment B (detector + browser real) — card 1117 · change card-1117-catalogo-ativos

> Assessor B isolado, sem transcript do pai nem de A. Sem nested-spawn. Cliente Claude Code (adapter cooperativo, não oficial; sem modo Auto), superfície claude-desktop.
> Único ficheiro escrito neste filho: este snapshot (shots de trabalho em `/tmp/1117-B-shots/`, não versionados).
> Modelo declarado (captura `cf-assess-b-1117.json`): rótulo **Opus 5.5**, slug **`claude-opus-5-5`**, effort `high`, faixa `juizo`, papel `assessment-b`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 1117
model: Opus 5.5 (claude-opus-5-5)
digest_match: disk==expected==HTTP local IDENTICAL (index, combo, optimize); HTTPS DEV 404 (não usado como prova)
detector: [] index exit 0; [] combo exit 0; [] optimize exit 0
P0: nenhum
P1: nenhum
P2: Combo só ação/ETF — cópia do Otimizar promete «otimiza, salva em favoritos»; falha cripto + pesquisa «btc» — vazio culpa o símbolo
P3: marcado escondido em «+N ativos» na seleção grande; × dos chips 28px; toggle Demonstração cobre conteúdo no 390; «Tentar de novo» quebra no 390; paginação/Top 10 mock; HTTPS 404; overlay detect.js não injectado
verdict: PASS
```

- UTC: 2026-10-20T03:15Z
- Tuple (read-only): `bound_card=1117` · `q_git=card-1117-catalogo-ativos` · Status=Design (bind do prompt). Sem `process_event`, sem mover Status, sem commit/push/Gist/comentário.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1117 --jq .body` (Problema / História / Entra / Não entra). Sem reentrevista.
- Protótipo canónico: `frontend/public/prototypes/card-1117-catalogo-ativos/index.html` (clone `/combo/discovery`). Extras: `combo.html` (`/combo/configure`), `optimize.html` (`/combo/optimize`).
- HTTP local: `python3 -m http.server 53145 --bind 127.0.0.1` (cwd `frontend/public`), em segundo plano; **processo morto no fim** (porta livre confirmada).
- HTTPS DEV `https://dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/` (+ `combo.html`, `optimize.html`) → **404** (605/615/618 B). Ainda não publicado; não usado como prova.
- Browser: Playwright Python + `chromium_headless_shell-1243` (`chrome-headless-shell-linux-arm64`), headless, `--no-sandbox`, `colorScheme: dark`, `locale: pt-BR`. Viewports **1440×900** e **390×844**.

## 1. Digest servido == local

| Ficheiro | sha256 (disco = esperado = HTTP local = documento do Playwright) | bytes | HTTP local |
|---|---|---|---|
| `index.html` (e `/`) | `adc5399aa05592724e71d91b3c19301252ac3c5862e52a8532a9c1b382fc784d` | 94274 | 200 |
| `combo.html` | `273d89b502e6e4b374a15c811493e8bb7683b3bb8da1e27afd4477a1e9b4b450` | 52418 | 200 |
| `optimize.html` | `cd932a7e5cfa7b2b4c7696de71e8c7de4ff9a01ed916e5336a22650f5ea395e5` | 47137 | 200 |
| `design.md` (disco) | `2a9c311ddbd376da611c9ddb8444053b713423942dd0f5b87dca8601a4556e9d` | 20095 | — |

Digest calculado sobre `response.body()` do Playwright nos dois viewports: **IDENTICAL** nas três telas.

## 2. Detector Impeccable

- `node .agents/skills/impeccable/scripts/detect.mjs --json <html>` (cwd worktree): `index.html` → `[]` exit 0; `combo.html` → `[]` exit 0; `optimize.html` → `[]` exit 0.
- Ignore list `.impeccable/critique/ignore.md`: ausente.
- Overlay live `detect.js`: não injectado (CLI + Playwright).
- Nota: `.cursor/skills/impeccable/SKILL.md` não existe neste repo; o uso veio de `.agents/skills/impeccable/`.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py`)

| Check | Resultado |
|---|---|
| `design_token_gap(design.md)` | `None` |
| `parse_ui_impact` / `parse_live_route` / `parse_surface` | `affected` / `/combo/discovery` / `existing` |
| `evaluate_clone_gate(design.md, proto_dir, repo)` (catálogo `load_head_catalog`) | **True** |
| `landmarks_match(/combo/discovery, index.html)` | **True** (`Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`) |
| `copied_utf8_sum(index.html)` | **31381** (> 0); COPIED 20/20; DELTA 4/4 |
| `classify(index.html, '/combo/discovery')` | PASS |
| `canonical_proto_html(proto_dir) == index.html` | True |
| Extras: `combo.html` COPIED 8/8 · 7100 B; `optimize.html` COPIED 4/4 · 4695 B | rotas `/combo/configure` e `/combo/optimize` fora do catálogo de landmarks (esperado para extras; o gate usa só o index) |

Números batem com `## Prototype Validation` do `design.md`.

## 4. Browser real — matriz

230 asserts (115 por viewport): **224 PASS, 6 FAIL**. Os 6 FAIL estão classificados em §6 (2 → P2-1; 4 → P3-1). Mais uma sonda de seguimento (4 corridas: index/combo × 2 viewports) para a seleção pequena com marcado, paginação, pesquisa com falha de cripto e alvos de toque.

Console `error` + `pageerror` = **0** em todas as cargas (3 telas × 2 viewports + `optimize.html?symbol=XYZ/USDT|NVDA|WAVES/USDT`). Respostas ≥400 no prefixo local = 0. `scrollWidth == clientWidth` (1440/1440 e 390/390) na carga e depois das interações, nas três telas.

### Ações exercidas (as mesmas nos dois viewports)

- Carga canónica; landmarks; ausência de botões Antes/Depois e de «Edição avançada»; eixo «Ativos».
- Pesquisa `nvidia`, `btc`, `nvda`, `spy`, `qqq`, `waves`, `zzzz`; filtros `Cripto`, `Ações`, `ETFs`, `Todas`.
- `Todos do filtro` com `nvidia` → contagem; ETFs → abrir confirmação → Cancelar → abrir → Incluir; `waves` → botão em 0; Cripto → Todos → Incluir; depois WAVES individual.
- Index: Limpar → só NVDA → misto BTC+NVDA; Demonstração → falha de ações/ETFs → falha de cripto → filtro Cripto → Tentar de novo.
- Combo: Limpar + remover chip BTC → só NVDA → Otimizar; Top 10 + SPY → Otimizar; Demonstração (cripto sem lista, ações/ETFs desatualizados).
- Optimize: tipo de input; QQQ → Run Optimization; WAVES individual; Demonstração cripto sem lista; `?symbol=XYZ/USDT` (+ Run), `?symbol=NVDA`, `?symbol=WAVES/USDT`.

### Asserts × critérios do Entra

| # | Assert | index 1440 | index 390 | combo 1440 | combo 390 | optimize 1440 | optimize 390 |
|---|---|---|---|---|---|---|---|
| 1 | Digest servido == esperado | PASS | PASS | PASS | PASS | PASS | PASS |
| 2 | 0 console error / pageerror / ≥400 | PASS | PASS | PASS | PASS | PASS | PASS |
| 3 | Sem scroll horizontal (carga e pós-interação) | PASS | PASS | PASS | PASS | PASS | PASS |
| 4 | Cada linha mostra 3 fatos: classe · negociação · histórico | PASS | PASS | PASS | PASS | PASS | PASS |
| 5 | Pesquisar «nvidia» encontra NVDA (1º; NVDX, NVDQ depois) | PASS | PASS | PASS | PASS | PASS | PASS |
| 6 | Filtro Cripto/Ações/ETFs: `aria-pressed=true` e só a classe | PASS | PASS | PASS | PASS | PASS | PASS |
| 7 | Encontra BTC/USDT, NVDA, SPY, QQQ | PASS | PASS | PASS | PASS | PASS | PASS |
| 8 | WAVES/USDT marcado `Suspenso` + motivo «status BREAK… Só entra por escolha individual.» | PASS | PASS | PASS | PASS | PASS | PASS |
| 9 | `Todos do filtro (3)` com «nvidia»; ETFs `(3.112)` | PASS | PASS | PASS | PASS | n/a (escolha única) | n/a |
| 10 | Confirmação `role=alertdialog` visível antes de aplicar: «Incluir 3.112 ETFs… 16 ativos marcados ficam de fora…» | PASS | PASS | PASS | PASS | n/a | n/a |
| 11 | Seleção não muda antes de confirmar; Cancelar não muda | PASS | PASS | PASS | PASS | n/a | n/a |
| 12 | Incluir soma ETFs e IBIC (Fora de mercado) fica de fora | PASS | PASS | PASS | PASS | n/a | n/a |
| 13 | «waves» → `Todos do filtro (0)` desabilitado | PASS | PASS | PASS | PASS | n/a | n/a |
| 14 | Cripto Todos: «511 negociáveis… 214 marcados de fora»; WAVES/XMR/AGLD não entram | PASS | PASS | PASS | PASS | n/a | n/a |
| 15 | Marcado escolhido individualmente: chip `WAVES/USDT · Cripto · Suspenso` tracejado (seleção pequena, sonda) | PASS | PASS | PASS | PASS | PASS (`?symbol=WAVES/USDT` e clique) | PASS |
| 15b | Idem depois de «Todos» cripto (512 selecionados): chip visível | FAIL → P3-1 | FAIL → P3-1 | FAIL → P3-1 | FAIL → P3-1 | n/a | n/a |
| 16 | Index inicial BTC+NVDA: «Fora desta varredura: 1 ativo (1 combinação)» + motivo; Iniciar habilitado | PASS | PASS | — | — | — | — |
| 17 | Index só NVDA: Preflight bloqueia «Nenhuma combinação válida: a análise ainda não está disponível para ações e ETFs…» | PASS | PASS | — | — | — | — |
| 18 | Index misto: «Pronto para iniciar · ações e ETFs fora» | PASS | PASS | — | — | — | — |
| 19 | Index Limpar → «Escolha ao menos 1 ativo.» + CTA disabled | PASS | PASS | — | — | — | — |
| 20 | Combo só NVDA → Otimizar: alerta «Análise ainda não disponível para ações e ETFs… Nada foi executado nem salvo.» | — | — | PASS | PASS | — | — |
| 20b | Combo só NVDA: cópia sob o botão avisa antes do clique | — | — | FAIL → P2-1 | FAIL → P2-1 | — | — |
| 21 | Combo misto (Top 10 + SPY): cópia «2 ações e ETFs ficam fora»; Otimizar → «Lote iniciado com 8 pares cripto · Fora do lote: NVDA (Ação), SPY (ETF)» | — | — | PASS | PASS | — | — |
| 22 | Combo default BTC/USDT, `Limpar (1 ativo)`, Top 10; Top 10 não adiciona marcados; sem rádio Todos/Seleciona | — | — | PASS | PASS | — | — |
| 23 | Optimize sem texto livre: 0 `input[type=text]`/`textarea`; linhas = `radio`; sem «Todos» | — | — | — | — | PASS | PASS |
| 24 | Optimize QQQ → Run: alerta «…Nada foi executado.» | — | — | — | — | PASS | PASS |
| 25 | `?symbol=XYZ/USDT`: nada marcado + «XYZ/USDT não está no catálogo da Binance»; Run → «Escolha um ativo» | — | — | — | — | PASS | PASS |
| 26 | `?symbol=NVDA` → `NVDA · Ação`; `?symbol=WAVES/USDT` → chip Suspenso | — | — | — | — | PASS | PASS |
| 27 | Falha ações/ETFs: aviso âmbar com «lista válida de 19 out. 2026, 18:00»; lista mantida | PASS | PASS | PASS | PASS | — | — |
| 28 | Falha cripto sem lista: alerta + «Tentar de novo»; filtro Cripto mostra alerta (0 linhas, não vazio mudo, não lista fixa); chip «indisponível»; seleção preservada | PASS | PASS | PASS | PASS | PASS (alerta) | PASS |
| 29 | «Tentar de novo» restaura catálogo | PASS | PASS | — | — | — | — |
| 30 | «zzzz» → vazio com orientação | PASS | PASS | — | — | — | — |
| 31 | Paginação `1–6` → `7–12 de 8.685` → `1–6`; Anterior desabilita na pág. 1 (sonda) | PASS | PASS | PASS | PASS | — | — |

## 5. Confronta Entra (só o visível no proto; backend = Apply)

| Entra | Proto (browser) | Disposition |
|---|---|---|
| Catálogo com todas as ações/ETFs + pares spot USDT; pesquisa, paginação, filtros por classe, nome e símbolo | contagens 8.685 / 725 / 4.832 / 3.128; pesquisa por nome («nvidia») e símbolo; pager; filtros com `aria-pressed` | PASS (contagem real vs Binance = Apply) |
| Mesma pesquisa nas três telas; otimização sem texto livre | mesmo `AssetPicker`; Optimize só rádio; `?symbol=` validado | PASS |
| «Todos» = filtro atual, com contagem antes de confirmar | `Todos do filtro (N)` + `alertdialog` com N e marcados de fora; Cancelar não muda | PASS |
| Ação/ETF escolhível; aviso com motivo claro ao rodar | alerta em Combo e Optimize; Preflight «Fora desta varredura» / bloqueio na Descoberta | PASS (cópia pré-clique do Combo = P2-1) |
| Distinguir listado · negociação · histórico | 3 fatos por linha | PASS |
| Removido/suspenso marcado com estado e motivo; individual sim, lote/Todos nunca | WAVES/XMR/AGLD/IBIC/AVB/FEED/TMHC marcados; fora de Todos e Top 10; individual entra com chip marcado | PASS |
| Cripto só USDT | só pares `/USDT` | PASS |
| Falha da Binance informada, sem catálogo vazio nem lista fixa | aviso âmbar (lista anterior) / alerta vermelho + Tentar de novo | PASS (vazio da pesquisa durante a falha = P2-2) |
| Exclusão RIGHT/derivativos, reconciliação, limite de ingestão | não é tela | P3 Apply (design.md decisões 11–15) |

## 6. Findings

### P0 — nenhum

### P1 — nenhum

Todos os critérios críticos do Entra passaram nos dois viewports e nas três telas. Nenhum fluxo quebra.

### P2 — não bloqueiam; corrigir no rework único ou no Apply

- **P2-1 · `combo.html` (1440 e 390) · cópia do Otimizar com só ação/ETF.** Com só NVDA selecionado, o texto sob o botão diz «1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.» A tela promete uma execução que não acontece, e isso contradiz a decisão 6 do `design.md` («A cópia do botão já avisa antes do clique»). A nota sob «Selecionados» e o alerta ao clicar cumprem o Entra, por isso fica em P2 e não P1. **Corrigir:** quando a seleção tem 1 ativo e ele é ação ou ETF, a cópia passa a dizer, por exemplo, «NVDA é ação: a otimização ainda não roda para ações e ETFs». *Mecânico* (assert 20b falhou); a severidade é *juízo*.
- **P2-2 · index/combo/optimize (picker compartilhado) · vazio da pesquisa durante a falha de cripto.** Com «Falha de cripto sem lista» e filtro Todas, pesquisar «btc» mostra «Nenhum ativo para "btc" em todas as classes. Confira o símbolo ou troque a classe.» O banner vermelho continua acima e o filtro Cripto mostra «indisponível», mas a mensagem do vazio culpa o símbolo, quando a causa real é a falha da Binance. **Corrigir:** com cripto indisponível, o vazio diz que os pares cripto estão indisponíveis agora (e oferece Tentar de novo), em vez de «Confira o símbolo». *Juízo* (observado na sonda e no screenshot; nenhum assert do Entra falhou).

### P3 — aceites (Apply / mock; não reabrir como P0/P1)

- **P3-1 · index/combo · marcado escondido na seleção grande.** Os chips mostram 8 e o resto vira «+N ativos». Se WAVES (Suspenso) é escolhido depois de «Todos» cripto, ele fica dentro de «+504 ativos», e a contagem «512 selecionados · 512 cripto» não diz quantos marcados existem. Com seleção pequena o chip aparece tracejado e com «Suspenso» (PASS), e a linha da pesquisa continua marcada. Apply: mostrar os marcados primeiro nos chips ou somar «· N marcado» na contagem. *Mecânico* (4 FAIL do assert 15b).
- **P3-2 · as três telas · botão × dos chips com 28×28px** (8 por tela), contra os «alvos de 44px» declarados no `design.md`. O mínimo AA de 24px é cumprido. Apply: área de toque de 44px. *Mecânico.*
- **P3-3 · 390 · toggle «Demonstração · catálogo» fixo** no canto inferior direito cobre parte do alerta do Combo, da nota de classe e do painel Ready to Optimize. Existe só no protótipo. *Juízo.*
- **P3-4 · 390 · banner «Cripto indisponível»:** o botão «Tentar de novo» fica inline e quebra a frase («foi / mantida.»). Polish. *Juízo.*
- **P3-5 · mock de paginação e amostra:** sem pesquisa, «7–12 de 8.685» repete a amostra de 32 linhas; página de 6 itens. O `design.md` já marca isto como P3. *Mecânico.*
- **P3-6 · Combo Top 10:** inclui AVAX/MATIC fora da amostra, por isso «8 pares». É mock e está documentado. *Mecânico.*
- **P3-7 · HTTPS DEV 404** nas três URLs até o pai publicar. Disco = HTTP local = esperado. *Mecânico.*
- **P3-8 · overlay `detect.js` não injectado;** evidência = CLI `[]` + Playwright. `.cursor/skills/impeccable/SKILL.md` ausente; foi usada a cópia de `.agents/skills/impeccable/`. *Mecânico.*
- **P3-9 · decisões 9–15 do `design.md`** (catálogo persistido, identidade, reconciliação, job, API, 422, ingestão sem fallback): não são tela. São detalhe de Apply.

Observações (não são findings): `combo.html`/`optimize.html` dão `classify` = BLOCKED só porque as rotas extra não estão em `route-landmarks.yaml`; o gate canónico usa o index e passa. WAVES escolhido individualmente conta na varredura como cripto (2 combinações). Isso bate com «pode ser escolhido individualmente»; o `design.md` não pede outro comportamento.

## 7. Nielsen (só evidência visível)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | contagem por classe com `aria-live`; frescor do catálogo; Preflight «ações e ETFs fora» | — |
| 2 | Match com o mundo | Cripto/Ação/ETF; Negociável/Suspenso/Fora de mercado; motivos em PT | — |
| 3 | Controlo | Cancelar na confirmação; × nos chips; Limpar | P3-2 (alvo) |
| 4 | Consistência | mesmo picker nas 3 telas; Optimize em escolha única | — |
| 5 | Prevenção de erro | confirmação antes do lote; marcados nunca por lote; Preflight bloqueia só ações/ETFs | P2-1 (cópia pré-clique) |
| 6 | Reconhecimento | 3 fatos por linha; motivo inline | P3-1 (marcado em «+N») |
| 7 | Flexibilidade | pesquisa por nome e símbolo; Todos do filtro; Top 10 | — |
| 8 | Estética | tokens incumbentes; detector `[]` | P3-3/P3-4 |
| 9 | Recuperação | Tentar de novo; seleção preservada | P2-2 (vazio culpa o símbolo) |
| 10 | Ajuda | nota fixa sob Selecionados | — |

## 8. Veredito

**PASS.** Zero P0/P1. Detector `[]` nas três telas. Gate estático verde (`design_token_gap=None`, `evaluate_clone_gate=True`, landmarks `/combo/discovery` presentes, `copied_utf8_sum=31381`). Digest disco = HTTP local = Playwright = esperado nas três telas. 224/230 asserts PASS em 1440×900 e 390×844, sem erro de console e sem scroll horizontal. Os 6 FAIL são P2-1 (2) e P3-1 (4), nenhum num critério do Entra. HTTPS DEV ainda 404 (registado).

Disposition: as duas P2 são de cópia e cabem no rework único do teto ou no Apply. As P3 ficam aceites no Apply.

## 9. Referências

- Disco: `frontend/public/prototypes/card-1117-catalogo-ativos/{index,combo,optimize}.html` · `openspec/changes/card-1117-catalogo-ativos/design.md`
- HTTP local (evidência, já parado): `http://127.0.0.1:53145/prototypes/card-1117-catalogo-ativos/`
- HTTPS (ainda 404): https://dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/
- Viewports: 1440×900 · 390×844 · `colorScheme: dark` · `locale: pt-BR`
- Shots + `results.json`: `/tmp/1117-B-shots/` (não versionados)
- Captura de modelo: `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/75a8c3fd-67b3-47af-8fab-98f9288bc88e/scratchpad/cf-assess-b-1117.json`
- Birth: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1117-catalogo-ativos/.cursor/tmp/claude-evidence/37182717-df72-4f8f-96ec-fc4050dfc1f0.birth.json`

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)
