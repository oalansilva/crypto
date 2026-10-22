# Assessment A — card 1117 · change card-1117-catalogo-ativos

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem commit/push/Gist/comentário no issue. Única escrita: este arquivo.

`proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5, effort high)` · cliente Claude Code (adapter cooperativo, não oficial; sem modo Auto) · superfície claude-desktop

## Metadata

- card: 1117 — Encontrar e selecionar cripto, ações e ETFs da Binance (épico #1116)
- change: `card-1117-catalogo-ativos`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1117-catalogo-ativos`
- branch / q_git: `card-1117-catalogo-ativos` @ `1a06caec` (pacote untracked)
- tuple: `bound_card=1117` · Status esperado=Design (MUST NOT arrastar)
- data (UTC): 2026-10-20T03:16Z
- model_selection_capture: `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/75a8c3fd-67b3-47af-8fab-98f9288bc88e/scratchpad/cf-assess-a-1117.json` (role `assessment-a`, band `juizo`, `claude-opus-5-5`, effort high, attempt `a4c74c02-2e20-4f65-9059-ed48615271f0`, capture_sha256 `0734218dc7bff68540e794c59b368125bc93f8315af04c9a315acf41fa8c502b`)
- runtime_evidence_birth: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1117-catalogo-ativos/.cursor/tmp/claude-evidence/a4c74c02-2e20-4f65-9059-ed48615271f0.birth.json`
- Fronteira: `gh api repos/oalansilva/crypto/issues/1117 --jq .body` (Problema / História / Entra / Não entra + 5 decisões de Alan de 20/10/2026). Sem reentrevista.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: `python3 -m http.server 8817` (cwd `frontend/public`, bind 127.0.0.1, morto no fim) + Playwright Python + Chromium `/usr/bin/chromium-browser --no-sandbox` headless, 1440×900 e 390×844, locale pt-BR. Screenshots em `/tmp/1117-A-shots/` (não versionados). Zero `pageerror` nas três telas e nos dois viewports.
- Mode: Impeccable **critique** (Operate, clone+delta). `DESIGN.md` autoridade visual, não sobrescrito.

## Digests (disco == servido)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| `openspec/changes/card-1117-catalogo-ativos/design.md` | `2a9c311ddbd376da611c9ddb8444053b713423942dd0f5b87dca8601a4556e9d` | 20095 | — |
| disco `index.html` (canônico) | `adc5399aa05592724e71d91b3c19301252ac3c5862e52a8532a9c1b382fc784d` | 94274 | — |
| disco `combo.html` | `273d89b502e6e4b374a15c811493e8bb7683b3bb8da1e27afd4477a1e9b4b450` | 52418 | — |
| disco `optimize.html` | `cd932a7e5cfa7b2b4c7696de71e8c7de4ff9a01ed916e5336a22650f5ea395e5` | 47137 | — |
| `http://127.0.0.1:8817/prototypes/card-1117-catalogo-ativos/` (index) | idêntico | 94274 | 200 |
| `…/combo.html` | idêntico | 52418 | 200 |
| `…/optimize.html` | idêntico | 47137 | 200 |
| HTTPS `dev.criptofarol.com.br/prototypes/card-1117-catalogo-ativos/` | — | — | 404 (pai ainda não publicou) |

Disco == servido == prompt == `design.md` §Prototype Validation: IDENTICAL. Pares `COPIED:start/end` 20/20 (index), 8/8 (combo), 4/4 (optimize); blocos `DELTA` 4 / 3 / 3.

## Tokens parseáveis (rubrica D4)

`design.md` L1–L3, linhas próprias:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

`scripts/process-fsm/design_clone_gate.py` importado: `design_token_gap → None`; `parse_ui_impact → affected`; `parse_live_route → /combo/discovery`; `parse_surface → existing`; `requires_existing_clone → True`; `classify(index.html, "/combo/discovery") → PASS`. Regiões clonadas listadas por arquivo em §Context. URL canônica = clone de `/combo/discovery` + delta, **não** painel ANTES/DEPOIS nem grade de N estados; `combo.html` e `optimize.html` são extras de clone (cada tela com copy visível ganha URL própria, como manda o covenant-flow). **PASS** deste item.

Observação de parser (não do autor): `LIVE_ROUTE_RE` captura a linha seguinte (`surface: existing`) como "justificativa" porque `\s+` atravessa a quebra de linha. Inofensivo aqui.

## Fidelidade (clone da página viva)

Catálogo `route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura` → 1/1/1 visíveis no default Montar (1440 e 390).

Fonte viva (só leitura): `DiscoveryPage.tsx` tem os eixos Templates e Símbolos lado a lado (`md:grid-cols-2`), cada um com "Edição avançada" (workbench) + busca inline de 30 itens; "Carregando catálogo…" sem fim quando vazio. `ComboConfigurePage.tsx`: Market Data, Escopo Todos/Seleciona, lista dupla, Top 10. `ComboOptimizePage.tsx`: `glass-strong` + roxo, campo `<input type="text">` Symbol com padrão `BTC/USDT` / `?symbol=`.

- Shell AppNav (sidebar 224px, Descoberta / Combo `aria-current=page`), heading, 3 modos, Rascunho, Timeframes, Direção, Período/Ranking (#1078), Preflight, Acompanhar e Decidir: clonados e fiéis aos tokens Binance (`--bg-*`, `--accent #fcd535`, 44px).
- Delta restrito ao seletor de ativos, ao bloco "Fora desta varredura", ao CTA, ao aviso ao rodar e ao toggle Demonstração. Nada mais muda na Descoberta.
- Desvio: o eixo Templates foi condensado (só resumo + chip, sem "Edição avançada" nem busca inline) e o Ativos passou a ocupar a largura toda. O `design.md` diz "Templates não mudam" → P2 abaixo.
- Combo e Otimização reusam o shell Binance escuro; o vivo ainda tem chrome glass/zinc/roxo. Mesmo tratamento do #1078 → P3.

## Produto (Entra / Não entra do body)

| Entra | Proto (Playwright 1440 + 390) | OpenSpec | Disposition |
|---|---|---|---|
| Catálogo de todas as ações/ETFs + spot USDT, com pesquisa, paginação, filtro por classe/nome/símbolo | filtros `Todas 8.685 · Cripto 725 · Ações 4.832 · ETFs 3.128` (`aria-pressed`); `nvidia` → NVDA/NVDX/NVDQ; ETFs paginam `1–6 de 3.128` → `7–12` | `binance-asset-catalog`, `asset-selection`, decisões 11/13 | OK |
| Seleção individual e em lote, mesma pesquisa em Combo, Descoberta e Otimização; Otimização sem texto livre | mesmo componente nas 3 telas; optimize `input[type=text]` = 0, rádio único | decisão 2/7; Non-Goal "lote em /combo/optimize → #1120" | OK com P2 de juízo (lote na Otimização) |
| "Todos" = filtro atual, com contagem antes de confirmar | `Todos do filtro (3.112)` → alertdialog "Incluir 3.112 ETFs negociáveis… 16 ativos marcados ficam de fora…"; Cancelar não muda; Incluir soma (`3.114 selecionados`) | decisão 4, `discovery-catalog-selection` MODIFIED | OK |
| Ação/ETF escolhível; aviso claro ao rodar | Descoberta: "Fora desta varredura: 1 ativo (1 combinação) — NVDA (Ação) — análise ainda não disponível…"; só ações → CTA disabled + motivo; Combo só NVDA → alerta "Nada foi executado nem salvo"; misto → "Lote iniciado com 9 pares cripto. Fora do lote: NVDA (Ação), SPY (ETF)"; Optimize QQQ/NVDA → alerta | decisão 6, 14 | OK (P2 na copy prévia do Combo) |
| Distinguir listado, negociação, histórico; conta fora | 3 fatos por linha: classe · `Negociável/Suspenso/Fora de mercado/Sem negociação/Sem regras/Removido` · `Histórico local desde/até / sob demanda / não coletado`; nada sobre conta | decisão 3 | OK (P3: "listado" vive no slot de negociação via Removido) |
| Removido/suspenso marcado com motivo, individual, nunca em lote/"todos" | `waves` → Suspenso + "Negociação pausada pela Binance (status BREAK). Só entra por escolha individual."; `Todos (0)` disabled; `agld` → Removido + data; Top 10 só negociáveis | decisão 5 | OK com P2 (juízo + chip oculto) |
| Cripto só USDT | só pares `/USDT` | `binance-asset-catalog` | OK |
| Verificação BTC/USDT, NVDA, SPY/QQQ; contagem = Binance − excluídos; limite de ingestão não trunca | todos achados na 1ª página; 4.832 + 3.128 = 7.960 = união 7.970 − 10 excluídos (decisão 11) | spec + tasks 4.4 | OK |
| Reconciliar estático × regras; excluir RIGHT/derivativos; falha visível sem lista vazia/fixa | Demonstração: âmbar "Ações e ETFs desatualizados… lista válida de 19 out. 2026, 18:00"; vermelho "Cripto indisponível… Tentar de novo", filtro Cripto "indisponível"; seleção preservada | decisões 8/11/12/15 | OK |

**Não entra** — sem vazamento: nenhum botão de coleta de histórico; nada de ordem ou conta; nenhum par não-USDT; ações/ETFs nunca executam (Descoberta, Combo e Otimização só rodam a parte cripto ou bloqueiam).

### Decisões 5 e 6 contra o body

- **Decisão 5** ("nunca entra sozinho num lote" = só entra por marcação item a item; pode compor seleção de vários). A leitura literal de "sozinho" (= automaticamente) sustenta isso. O resumo de Alan, porém, diz "removido/suspenso marcado, individual, **fora do lote**", que também admite "nunca roda em lote". Concretamente, no `combo.html` WAVES/USDT (Suspenso) escolhido à mão entra em silêncio no "Lote iniciado com 9 pares cripto", com o chip escondido em "+3 ativos". Não é furo, porque o body admite a leitura, mas é juízo que o `design.md` declara fechado ("Nenhuma de produto") → P2.
- **Decisão 6** (Descoberta e lote misto rodam só a parte cripto, com aviso): bate com "ao rodar, o usuário recebe aviso com motivo claro… nunca erro genérico" e com o Não entra (ações e ETFs não rodam). Reusa o padrão `exclusions` do Preflight vivo. OK.

## UX

- Hierarquia: Rascunho → Templates → **Ativos** (contagem por classe + frescor → busca → classes → lista → pager → Todos/Limpar → confirmação → Selecionados) → Timeframes → Período. Preflight à direita ecoa "Pronto para iniciar · ações e ETFs fora" + bloco âmbar. A ordem segue o modelo mental (achar → filtrar → escolher → revisar).
- Carga cognitiva: média. Três fatos por linha em chips de cores distintas (classe com cor; negociação neutra/âmbar; histórico apagado) leem bem. Seis linhas por página. A confirmação inline evita modal. O seletor empurra Timeframes/Período para baixo da dobra (aceitável). Em `optimize.html`, na coluna estreita, cada linha quebra os fatos em duas linhas e o seletor passa de ~1000px antes de Timeframe/Run → P3.
- Estados de recuperação: vazio `zzzz` → "Nenhum ativo para "zzzz" em todas as classes. Confira o símbolo ou troque a classe. A seleção atual foi mantida."; Limpar → "Escolha ao menos 1 ativo." + CTA disabled; `?symbol=XYZ/USDT` → aviso "não está no catálogo da Binance", nada marcado; `?symbol=btc/usdt` resolve sem diferenciar caixa.
- Pico: "Fora desta varredura: 3.113 ativos (3.113 combinações)… e mais 3.110 ações e ETFs, pelo mesmo motivo. Eles continuam na seleção do rascunho; nada é perdido." deixa claro o que roda e o que não roda.

## Acessibilidade

- Teclado: busca → 4 filtros (`aria-pressed`) → checkboxes por linha (rótulo `BTC/USDT — Cripto`, `…, Suspenso`); Space marca; `:focus-visible` 2px `#3b82f6` em todos. Confirmação `role=alertdialog` recebe foco em "Incluir" e devolve foco a "Todos" no OK/Cancelar. **Esc não fecha** → P2.
- Live regions: contagem `aria-live=polite`, range do pager `aria-live`, alertas `role=alert/status`, aviso ao rodar `aria-live=assertive`.
- Alvos: botões/filtros 44px; linha inteira (`label`, 52px) é alvo do checkbox de 18px; remover chip 28px (≥24px, AA 2.5.8).
- Contraste (WCAG AA 4.5:1, texto 12px): `--text-muted #707a8a` sobre `.ap` `#181a20` = **4.01:1** (linha de frescor do catálogo, que carrega a data da lista) e sobre `#0b0e11` = **4.46:1** (fato "Histórico…"). O resto do delta passa: `--text-tertiary` 6.1–6.8, âmbar `#fbbf24` 11.6, `--danger-text` 7.35, azul `#93c5fd` 9.6 → P2.
- Toggle Demonstração `position:fixed` cobre conteúdo do clone: em 390×844 tapa o filtro "Cripto" (`elementFromPoint` → details.demo); em 1440×900 tapa Ranking/Elegibilidade do Preflight → P2 (só protótipo).

## Responsividade

1440: `scrollWidth == clientWidth`; linha em 3 colunas (check · id · fatos). 390: `scrollWidth 390`; fatos descem para baixo do nome; pager empilha; Preflight abaixo do Rascunho (incumbente). Combo e Optimize sem overflow nos dois viewports.

## Estados (dentro do clone)

| Estado | index | combo | optimize |
|---|---|---|---|
| Pesquisa + filtro por classe | ✓ | ✓ | ✓ |
| Contagem do "Todos" + confirmação | ✓ | ✓ | n/a (escolha única) |
| Suspenso / removido / fora de mercado / sem negociação / sem regras | ✓ | ✓ | ✓ (`?symbol=WAVES/USDT` → Suspenso) |
| Aviso ao rodar ação/ETF | ✓ Preflight | ✓ alerta / lote misto | ✓ alerta |
| Falha Binance com lista anterior | ✓ | ✓ | ✓ |
| Falha sem lista + Tentar de novo | ✓ | ✓ | ✓ |
| Vazio de pesquisa | ✓ | ✓ | ✓ |
| Símbolo fora do catálogo na URL | n/a | n/a | ✓ |

## Heurísticas Nielsen (0–4) — só neste snapshot

| # | Heurística | Score | Nota |
|---|-----------|-------|------|
| 1 | Visibility of system status | 3 | frescor, contagens, Preflight; marcado some no "+N" |
| 2 | Match with real world | 4 | Cripto/Ação/ETF, "Negociável", "Histórico não coletado" |
| 3 | User control and freedom | 3 | Cancelar, chip ×, Limpar; sem Esc na confirmação |
| 4 | Consistency and standards | 3 | mesmo componente nas 3 telas; Templates condensado diverge do vivo |
| 5 | Error prevention | 4 | Todos exclui marcados; CTA bloqueia só ações; `?symbol=` validado |
| 6 | Recognition rather than recall | 4 | busca por nome; fatos na linha |
| 7 | Flexibility and efficiency | 3 | Todos do filtro, Top 10; sem atalho de teclado próprio |
| 8 | Aesthetic and minimalist | 3 | denso mas legível; optimize longo na coluna estreita |
| 9 | Recognize, diagnose, recover | 4 | motivos nomeados, "nada é perdido", Tentar de novo |
| 10 | Help and documentation | 3 | notas fixas sob Selecionados |
| **Total** | | **34/40** | Good |

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2 · juízo] Decisão 5, ativo marcado no lote do Combo** (`combo.html`). WAVES/USDT (Suspenso), escolhido à mão, roda em silêncio no "Lote iniciado com 9 pares cripto", e o chip marcado fica escondido em "+3 ativos". A leitura do autor é defensável pelo body ("nunca entra *sozinho*"), mas o resumo de Alan ("individual, fora do lote") admite a outra leitura. Corrigir: o pai põe essa leitura explicitamente no pedido de Aprovação de Design, em vez de "Open Questions: nenhuma". **Parte mecânica:** chips de ativos marcados sempre visíveis (antes do "+N") e o aviso ao Otimizar nomeia os marcados incluídos no lote.
- **[P2 · juízo] Lote na Otimização** (`optimize.html` / Non-Goals). O Entra diz "Seleção individual e em lote… na configuração de combo, na descoberta e na otimização"; o Design faz `/combo/optimize` em escolha única e manda o lote para o Combo, atribuindo-o ao #1120. O body do #1120 fala em lote de otimização em geral e não cita `/combo/optimize`. A leitura combina com a decisão de Alan "otimização entra com a mesma pesquisa", mas é estreitamento de Entra → Alan confirma na Aprovação. **Parte mecânica:** no `design.md`, justificar pela decisão de Alan e pelo lote já existente no Combo, não por #1120.
- **[P2 · mecânico] Copy do Combo antes do clique com só ação/ETF** (`combo.html`). Com só NVDA, o texto continua "1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos." A decisão 6 promete que "a cópia do botão já avisa antes do clique", e isso só vale no lote misto. Corrigir: com só ações e ETFs, a copy diz que nada será executado e por quê.
- **[P2 · mecânico] Eixo Templates condensado no clone** (`index.html`). O vivo tem "Edição avançada" + busca inline nos dois eixos, lado a lado; o proto deixa só o resumo de Templates. Como o `design.md` diz "Templates não mudam" e o Apply lê o HTML como layout, o risco é remover a edição de Templates. Corrigir: clonar o bloco Templates do vivo (com o botão e a busca) ou anotar no `design.md` que a condensação é só do proto.
- **[P2 · mecânico] Contraste do delta abaixo de AA**: `.ap-fresh` (data do catálogo) 4.01:1 e `.fact.hist` 4.46:1 com `--text-muted`, a 12px. Corrigir: usar `--text-tertiary` (6.1–6.8:1) nesses dois textos de contrato.
- **[P2 · mecânico] Esc não fecha a confirmação `alertdialog`** (3 telas). Corrigir: Esc = Cancelar, devolvendo o foco a "Todos do filtro".
- **[P2 · mecânico] Toggle Demonstração cobre o clone**: em 390×844 tapa o filtro "Cripto"; em 1440×900 tapa Ranking/Elegibilidade do Preflight. Corrigir: posicioná-lo fora do conteúdo (por exemplo, no rodapé da página, sem `fixed`) ou recolhido num canto que não cubra nada.

### P3 — detalhe de Apply / mock (não reabrir como P0/P1)

- **[P3] Mock de paginação**: amostra de 31 itens; ETFs página 2 mostra 3 linhas com "7–12 de 3.128"; Top 10 adiciona 8 (AVAX/MATIC fora da amostra). Disposition: **aceito-P3-Apply**.
- **[P3] "Incluir 3"** quando 1 dos 3 já estava selecionado (soma real +2). Copy pode dizer "3 (2 novos)". Disposition: **aceito-P3-Apply**.
- **[P3] Cripto indisponível**: alerta duplicado (banner + lista) e pager "0 resultados" sob o alerta; Preflight/Combo não comentam cripto já selecionado quando a classe está indisponível. Disposition: **aceito-P3-Apply**.
- **[P3] "Listado" no slot de negociação**: o body pede distinguir listado, negociação e histórico; o proto mostra classe · negociação (com Removido) · histórico. A distinção existe (Removido + data de saída), mas a spec diz "expose separately". Disposition: **aceito-P3-Apply**, que mantém o campo separado na API.
- **[P3] Densidade do seletor em `optimize.html`** na coluna estreita (~1000px). Disposition: **aceito-P3-Apply** (variante compacta para escolha única).
- **[P3] Chrome glass/zinc/roxo do vivo** em `/combo/configure` e `/combo/optimize` × shell Binance no proto (igual ao #1078). Disposition: **aceito-P3-Apply**.
- **[P3] HTTPS público 404**: publicação do pai. Disposition: **aceito-P3-Apply** (pai publica).
- **[P3] Decisões 9–15** (tabelas, identidade, reconciliação, job, API, 422, ingestão), tamanho de página, regra UP/DOWN. Já aceitas no `design.md`. Disposition: **aceito-P3-Apply**.

## Disposition (resumo)

| Finding | Gravidade | Classe | Bloqueia? | Disposition |
|---|---|---|---|---|
| (nenhum P0/P1) | — | — | não | n/a |
| Decisão 5 marcado no lote Combo | P2 | juízo (+ mecânico: chip/aviso) | não | levar a Alan na Aprovação |
| Lote na Otimização / atribuição #1120 | P2 | juízo (+ mecânico: texto) | não | levar a Alan na Aprovação |
| Copy Combo só ação/ETF | P2 | mecânico | não | autor corrige |
| Templates condensado | P2 | mecânico | não | autor corrige |
| Contraste `.ap-fresh` / `.fact.hist` | P2 | mecânico (a11y) | não | autor corrige |
| Esc no alertdialog | P2 | mecânico (a11y) | não | autor corrige |
| Toggle Demonstração cobre conteúdo | P2 | mecânico | não | autor corrige |
| Mock, copy "novos", crypto-down, listado, densidade, chrome, HTTPS, decisões 9–15 | P3 | detalhe de Apply | não | aceito-P3-Apply |

## Tokens do autor

**ok** — `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`; regiões clonadas marcadas por arquivo; canônico = clone `/combo/discovery`; extras `combo.html` / `optimize.html` nunca canônicos; sem ANTES/DEPOIS nem N estados.

## Resumo

```
P0: 0
P1: 0
P2: 7 (2 juízo, 5 mecânicos)
P3: 8
verdict: PASS
```

## Verdict

**PASS**

Nenhum P0/P1 de produto, escopo ou contrato visível. Todos os itens de Entra estão no protótipo e no OpenSpec; nada de Não entra vazou. Os P2 mecânicos cabem no único rework do teto 1+1+1, se o pai abrir. Os dois P2 de juízo vão a Alan no pedido de Aprovação de Design, sem segunda rodada.

## Artefactos desta sessão

- `.impeccable/critique/1117-card-1117-catalogo-ativos-A.md` (este arquivo; única escrita no repo)
- Screenshots de trabalho em `/tmp/1117-A-shots/` (não versionados)
