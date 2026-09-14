# Assessment A — card 935 · change card-935-favorites-combo-return

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo + PNGs `935-A-*` + JSON de gate.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 935 — Favoritos e Combo mostram retornos diferentes na mesma estratégia
- change: `card-935-favorites-combo-return`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-935-favorites-combo-return`
- data (UTC): 2026-09-14T01:32Z
- Status observado (bind do prompt): Design · com-tela
- UI impact (rubrica): **affected** · `live_route: /favorites` · `surface: existing` — linhas próprias 17–19 de `design.md` (parseáveis)
- Issue: REST `gh api repos/oalansilva/crypto/issues/935` (não `gh issue view`). Fronteira de operador vazia; canónico e recorte vs #897 / 32 vs 33 já fechados. Não reabertos.
- Digest proto (autor, verificado nesta sessão):
  - canónico `index.html` sha256 `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` · 42089 B
  - extra `analise.html` sha256 `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c` · 26812 B
- Servido HTTPS == local: IDENTICAL (`sha256` e bytes iguais nos dois HTML; HTTP 200)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Chromium headed (`xvfb-run -a` + Playwright `chromium.launch({headless:False})`, `executable_path=/usr/bin/chromium-browser`, `--no-sandbox`). MCP `cursor-ide-browser` não manteve tab (`navigate` / `viewId` falharam). Inspeção visual desta sessão = Playwright + pixels.

## Limitação de sessão (obrigatória)

Playwright Chromium headed, viewport 1280×800:

| URL pedida | URL final | Landmarks `/favorites` |
|---|---|---|
| `https://dev.criptofarol.com.br/favorites` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0/4 |
| `https://dev.criptofarol.com.br/combo/results` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | n/a (rota extra) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `FavoritesDashboard.tsx` + `ComboResultsPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 17–19:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/favorites`; extra `/combo/results` em `analise.html`; regiões clonadas marcadas (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»). **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `index.html` | `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` | 42089 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/` | idêntico | 42089 | 200 |
| disco `analise.html` | `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c` | 26812 | — |
| HTTPS `…/analise.html` | idêntico | 26812 | 200 |
| `design.md` Prototype | prefixos `2f2bb0a5…` / `1bc09427…` iguais | iguais | — |

## Fidelidade (clone da página viva)

Catálogo `/favorites` (`route-landmarks.yaml`): selectors `table.fav-strategies` · texts `Estratégias favoritas`, `Symbol`, `Estratégia`, `Ações`.

| Landmark | Vivo `FavoritesDashboard.tsx` (sem sessão) | Proto `index.html` + Playwright + PNG |
|---|---|---|
| `table.fav-strategies` | L1467 | count=1, `isVisible=true` no desktop 1280; hidden no mobile 390 (cards), igual ao vivo `@media max-width:1023px` |
| `Estratégias favoritas` | h1 L1262 | h1 visível desktop e mobile |
| `Symbol` | thead L1473 + filtro L1323 | visível no thead desktop; filtro «Symbol» também |
| `Estratégia` | thead L1474 | visível no thead desktop |
| `Ações` | thead L1488 | visível no thead desktop |

Anti-padrões P0:

- URL canónica `…/prototypes/card-935-favorites-combo-return/` → `index.html` é a página de Favoritos (shell AppNav + heading + tier cards + filtros + `table.fav-strategies` + 2 linhas). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `getByText('ANTES/DEPOIS')` visível = 0 (o comentário de fonte «No ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar de lista+detalhe. Default = Operate na listagem.
- Extra `analise.html` **não** é o index; copy visível de `/combo/results` noutro URL.
- `COPIED:start`/`COPIED:end` presentes (4 pares no index, 5 no extra). `copied_utf8_sum` medido aqui (inner, sem comentários): index 7457 / analise 4735 vs `design.md` 7661 / 4981 — diferença de contagem T5, não contrato de tela.

Chrome presente (sidebar 224px, Inter/BinanceNova, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Favoritos ativa) = **folha**, não prova. Prova = landmarks 4/4 no proto canónico, alinhados ao TSX.

Extra `/combo/results` (catálogo: `.combo-page` + texts `Lista de operações`, `Análise da estratégia`): clone estrutural visível = `combo-page`, «Voltar aos favoritos», `aria-label="Análise da estratégia"`, `data-testid="combo-result-summary"`, chips SOL/USDT · 1d · Long, `dl` Retorno total / Taxa de acerto / Drawdown máximo / Operações, gráfico, chrome `StrategyTradesTable` (Operação/Tipo/Data/Sinal/Preço/Lucro/Prejuízo), disclaimer educacional. Delta = «Retorno total» = composto grande. Lista 33 negócios permanece (fora).

PNGs do autor (lidos + refeitos nesta sessão):

- `.impeccable/critique/card-935-index-desktop-1280x800.png` (autor) e `935-A-index-desktop-1280x800.png`
- `.impeccable/critique/card-935-index-mobile-390x844.png` e `935-A-index-mobile-390x844.png`
- `.impeccable/critique/card-935-analise-desktop-1280x800.png` e `935-A-analise-desktop-1280x800.png`
- `.impeccable/critique/card-935-analise-mobile-390x844.png` e `935-A-analise-mobile-390x844.png`

Pixels desktop index: h1 «Estratégias favoritas» + tabela + SOL RETURN **+98.591,56%** + ETH **+35,00%**. Sem galeria. Nome da estratégia trunca a 1280 («Médias Móveis: Tendência …») — incumbente `table-layout:fixed`. Mobile index: cards; nome inteiro; mesmos números. Análise desktop/mobile: resumo **+98.591,56%** · 68,75% · 14,15% · 32; lista «33 negócios».

## Produto (escopo — não reabrir grelha)

Delta pedido (issue #935): RETURN da grade e «Retorno total» do resumo da **mesma** linha já preenchida = composto canónico **grande**; incidente SOL **+98.591,56%**, não 985,85%; Sharpe/acerto/DD/n intocados; compostos <100% não regridem; «Voltar aos favoritos» preserva o grande. Fora: #897 vazio, 32 vs 33, holdout, Monitor, redesign, milhar vs `toFixed`.

| Aceite visível | Evidência (Playwright + pixels + HTML) | Disposition |
|---|---|---|
| Grade SOL: RETURN **+98.591,56%** (contém 98.591 / 98591), **não** 985,85 | desktop `[data-testid=favorite-sol-incident] [data-metric=return]` exact; mobile card idêntico | OK |
| Grade SOL: Sharpe 0,45 · 32 · win 68,75% · Max DD 14,15% | quatro `data-metric` exact desktop e mobile | OK |
| Resumo da mesma linha: «Retorno total» **+98.591,56%**, não 985,85% | `combo-result-summary [data-metric=return]` desktop e mobile | OK |
| Acerto / Max DD / n do resumo iguais à grade | 68,75% · 14,15% · 32 no `dl`; Sharpe continua só na grade (vivo `ComboResultsPage` tem 4 métricas, sem Sharpe no resumo) | OK |
| ETH grade **+35,00%** (não 0,35% nem 3.500%) | `[data-testid=favorite-small-compound]` + card mobile | OK |
| «Voltar aos favoritos» deixa RETURN grande | click → `index.html`; SOL ainda `+98.591,56%`; ETH ainda `+35,00%` | OK |
| Fora: #897 vazio | duas linhas preenchidas (combo-saved); sem CTA de preencher vazio | OK |
| Fora: 32 vs 33 | resumo/grade 32; h2 «Lista de operações · velas atuais · 33 negócios»; 33 `<tr>` / 33 cards. Não «corrigido» | OK |
| Fora: holdout / Monitor / redesign / milhar vs toFixed | sem Treino vs Holdout; Monitor só nav clone; thead igual ao vivo; copy `98.591` com milhar (igualdade = composto grande, não o glifo) | OK |
| Contrato 169,51 / 16951 → +16.951% | documentado no `design.md` / spec; proto demonstra a **mesma** regra no incidente 98.591 (não há terceira linha #193) | OK como regra; cobertura de mock = P3 |

Não-goals de motor (`formatMetricPercentage` vivo ainda faz `|v|>1 ⇒ já é %` em `ComboResultsPage.tsx` L381–384; helper único vs dois formatadores; `total_return` vs `total_return_pct`) são contrato de Apply — P3 se citados, nunca P0/P1.

## UX

Hierarquia: shell autenticado → h1 Estratégias favoritas → resumo por estrelas → filtros → tabela (desktop) / cards (mobile). Delta localizado na célula Return já nomeada e no `dd` «Retorno total». ETH +35% é o vizinho de não-regressão.

Análise: chips de identidade → nome da estratégia → 4 métricas do resumo (retorno agora grande) → gráfico «velas atuais» → lista 33. O glance do incidente lê-se em segundos: o ~100× desapareceu.

Carga cognitiva: uma decisão (é o mesmo composto?). Quatro métricas no resumo (≤4). Filtros da grade são clone, não opções novas. **Low.**

Prevenção: o operador deixa de promover/descartar por 985,85%. Recuperação: Voltar devolve à grade com o grande.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`.
- «Retorno total» é texto visível no `dt`/`dd`, não tooltip. Contrato do card é número visível — cumprido.
- Chart da grade: `aria-label="Ver análise completa"` (link SOL). Resumo: `aria-label="Análise da estratégia"` + `dl` «Resumo de desempenho e risco». Gráfico ilustrativo com `role="img"`.
- Alvos: nav/filtros/mobile CTAs ≥40–44px. Estrelas 28px e ícones de linha 32px = padrão vivo, não deste card.
- Contraste: pares Binance do clone (`#fcd535` em `#0b0e11`, verde `#0ecb81` / vermelho `#f6465d` para return/DD). Sem par novo inventado.
- Cor do RETURN positivo não é a única via: o glifo `+` e o `%` estão no texto.

Gaps vs vivo (P3): `Delete` só `title`; alvos 32px dos ícones; truncagem desktop do nome.

## Responsividade

Desktop 1280: tabela visível; colunas Symbol / Estratégia / TF / Sharpe / Trades / Win% / Return / Max DD / Ações no PNG. Mobile 390: tabela `display:none`; cards com Sharpe / Trades / Win% / Return / Max DD; header 72px; Analisar/Revalidar/Delete em alvos largos. Análise mobile: resumo 2×2 wrapa; 33 trade-cards; desk-trades hidden.

## Estados

Mock cobre: default Operate da grade (SOL incidente filled + ETH <100% filled); análise do incidente com resumo canónico + lista 33. Não mocka: loading, vazio, erro, linha Descoberta sem métrica (#897 fora), sessão expirada, segunda `analise.html` da linha ETH. O aceite visível do incidente está coberto. Restante = P3 de cobertura de mock.

Abrir gráfico → voltar: HTML estático não reescreve células; demonstra o *contrato visível*, não a persistência. Persistência = P3 de Apply.

## Design specificity

A composição é da grade autenticada de Favoritos e do resumo `/combo/results`. Não iria a um SaaS genérico inalterado: AppNav Cripto Farol, `table.fav-strategies`, chips SOL/USDT, «Voltar aos favoritos», tokens Binance. Modo Impeccable: **Operate**. Delta = só o número canónico grande.

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | RETURN e Retorno total visíveis no estado padrão |
| 2 | Match between system and real world | 4 | Composto canónico grande nas duas pontas; vocabulário da grelha |
| 3 | User control and freedom | 4 | «Voltar aos favoritos» preserva o grande |
| 4 | Consistency and standards | 3 | Lista 33 vs resumo 32 (fora); truncagem do nome; breakpoints 1400 vs vivo |
| 5 | Error prevention | 4 | Elimina o ~100× que levava a decisão errada no Monitor |
| 6 | Recognition rather than recall | 4 | Mesmo número; não exige calcular 985,85 × 100 |
| 7 | Flexibility and efficiency | 3 | Filtros/export clone; sem atalho novo (fora) |
| 8 | Aesthetic and minimalist design | 3 | Clone Binance/Favoritos; truncagem incumbente |
| 9 | Help users recognize/recover errors | 3 | Mock sem estados erro/vazio |
| 10 | Help and documentation | 3 | Sem copy nova de ajuda; briefing no issue |
| **Total** | | **35/40** | **Good (Operate clone saudável)** |

## Cognitive load

Checklist: single focus (retorno da linha) · chunking do resumo (4 métricas) · grouping (dl + tabela) · hierarquia clara · uma decisão de cada vez · ≤4 no glance do resumo · sem memory bridge (mesmo número nas duas telas) · progressive disclosure (lista abaixo). **0–1 falhas = low.**

Pontos de decisão visíveis na linha = Analisar / Revalidar / Delete (iguais ao vivo). Sem wall of options nova.

## Emotional journey

Vale (PROD: grade +98.591,56% vs resumo 985,85% — o operador não decide o Monitor) → pico (as duas pontas lêem o composto grande) → fim (Voltar devolve o mesmo número). Reassegurança: ETH +35% não explode nem encolhe.

## Personas (2–3)

1. **Admin que compara Favoritos com a análise da mesma linha (Riley / incidente):** o glance das duas telas agora bate. Red flag vivo (985,85%) corrigido no proto.
2. **Alex (power user da grade):** Analisar → Voltar em um clique; filtros clone intactos. Sem wizard novo.
3. **Sam (teclado / SR):** `dt` «Retorno total» anunciável; link do gráfico com `aria-label`; ícones 32px e Delete só `title` = vivo (P3).

## Strengths

- Clone estrutural da rota canónica (`table.fav-strategies` + 4 texts), não galeria nem ANTES/DEPOIS.
- Extra `/combo/results` com copy visível do resumo noutro URL.
- Delta mínimo e no sítio certo: o composto grande nas duas pontas do incidente.
- ETH +35% como vizinho de não-regressão na mesma grade.
- Prototype Validation com desktop+mobile; disco == HTTPS.

## Prototype Validation (rubrica)

`design.md` § Prototype Validation presente: comando xvfb+Playwright headed, URLs canónico+extra, viewports 1280×800 e 390×844, asserts de landmarks e contrato, console 0, 35/35, digests. PNGs do autor no disco. Esta sessão reexecutou o gate (desktop contrato + Analisar; voltar; mobile 20/20 PASS; 0 console errors). **PASS** deste item.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum — classificação D4: só P0/P1 de contrato visível vs P3 de Apply)_

## P3 — detalhe de Apply (aceito; não reabrir como P0/P1)

- **Helper `formatMetricPercentage` vs `formatSignedPct`:** o vivo ainda encolhe composto >100% (`ComboResultsPage.tsx` L381–384). Apply alinha o formatador do resumo; um helper vs dois é mecanismo. Já no Apply contract.
- **ETH +35% só na grade:** `Analisar` da linha ETH é `button`, não `href=analise.html`. O spec pede resumo ~+35% ao abrir a análise; o proto demonstra a não-regressão na grade. Apply aplica o mesmo formatador a qualquer linha já preenchida. Não exigir segunda página de proto.
- **Contrato 169,51 / 16951 → +16.951%:** documentado; proto não tem terceira linha #193. A regra é a mesma do incidente 98.591. Teste de Apply, não redesign.
- **32 vs 33 na lista:** fora (#897). Deixar.
- **Truncagem desktop** de «Médias Móveis: Tendência Confirmada»: `table-layout:fixed` incumbente. Mobile mostra o nome inteiro. Não alargar colunas.
- **Alvos 28/32px**, `Delete` só `title`, `border-left` 3px nos cards mobile (detector `side-tab`): clone vivo / #897. Não é redesign deste card.
- **Copy de milhar vs `toFixed`:** igualdade = composto grande (contém 98591 / 98.591), não o glifo. Fora.
- **Breakpoints 1400 vs vivo 1540/1280:** proto mantém Win%/Max DD visíveis a 1280. Apply preenche células do vivo; não inventar layout.
- **Mock:** sem loading/vazio/erro. Extra omite painéis vivos não-contrato (regras, transparência, OOS/holdout). Correto.
- **`copied_utf8_sum`:** medição A inner 7457/4735 vs `design.md` 7661/4981. Contagem, não tela.
- **Copy «Backtest aguardando atualização»:** chrome vivo de refresh pending ao lado de métricas filled. Fora; Apply não deixa o refresh reencolher o retorno.

## Playwright (esta sessão)

- Desktop 1280×800: landmarks 4/4; SOL RETURN e Retorno total `+98.591,56%`; NÃO 985,85; Sharpe 0,45 · 32 · 68,75% · 14,15%; ETH +35,00%; Analisar → analise.html; Voltar → index com o grande. 0 console.
- Mobile 390×844: tabela hidden; cards com os mesmos números; análise resumo grande + 33 cards. 20/20 PASS.
- Live `/favorites` e `/combo/results` → `/login` (descartado).
- PNGs: `935-A-index-desktop-1280x800.png`, `935-A-index-mobile-390x844.png`, `935-A-analise-desktop-1280x800.png`, `935-A-analise-mobile-390x844.png`.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não promover detalhe de formatador / milhar / 32 vs 33 / #897 a P0/P1. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Clone canónico = `/favorites` + delta, não galeria. Extra `/combo/results` com copy visível do resumo. Contrato do incidente visível nas duas pontas (desktop e mobile). Disco == HTTPS. `/login` descartado. P3 aceitos.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 935
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: formatador Apply; ETH análise não prototipada; 16.951 sem 3ª linha; 32 vs 33 fora; truncagem; alvos 32px/side-tab; milhar vs toFixed; breakpoints; mock; copied_utf8_sum
verdict: PASS
```
