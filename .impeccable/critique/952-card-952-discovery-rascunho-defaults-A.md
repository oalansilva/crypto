# Assessment A — card 952 · change card-952-discovery-rascunho-defaults

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat (Grok 4.6). Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `952-A-*` (+ JSON de gate). Sem HTML fonte colado.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 952 — "Descoberta: rascunho novo sem Templates nem Símbolos, Time Frames em 1 dia"
- change: `card-952-discovery-rascunho-defaults`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-952-discovery-rascunho-defaults`
- branch: `card-952-discovery-rascunho-defaults`
- tuple: `bound_card=952` · `q_git=card-952-discovery-rascunho-defaults`
- data (UTC): 2026-09-16T18:22Z
- Status observado: **Design** (GraphQL pontual `repository.issue(number:952).projectItems` → Project 1 / oalansilva, `fieldValueByName(Status)=Design`. GraphQL remaining=4161. MUST NOT `gh project item-list`.)
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` · 32337 bytes
- Servido HTTPS == local: IDENTICAL (`sha256` e bytes iguais; HTTP 200)
- Issue: REST `gh api repos/oalansilva/crypto/issues/952` (não `gh issue view`). Grill: Q1 = defaults só no rascunho novo; reabrir varredura gravada traz o marcado · Q2 = Direção, período e ranking ficam como hoje — fechadas; **não reabertas**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1243 (`chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror no proto, restore e live.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; regiões clonadas marcadas («só estas»: shell AppNav; modo Montar; cartões Templates / Símbolos / Time Frames; painel Preflight «Falta fazer»). **Não** empresta `/combo/select` nem `/favorites` (`Available Templates` visível = 0; sem `href` para `/favorites`; nav Favoritos = chrome AppNav). **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html` | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/` | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 | 200 |
| `design.md` Prototype / prompt do pai | prefixo `eab36595d3bc5548` · completo igual | 32337 | — |

Disco == HTTPS: IDENTICAL. Restore irmão `restore.html` **não** é URL canónica (não medido como T5).

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 da página | h1 visível no default Montar (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` | h2 visível no default Montar (painel activo — rascunho novo) |
| `Rascunho de varredura` | h2 em tabpanel Montar | h2 visível no default Montar |

Anti-padrões P0:

- URL canónica `…/prototypes/card-952-discovery-rascunho-defaults/` → index é a página (shell 224px + heading + 3 modos + Montar com os três eixos + Preflight). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. Texto visível `ANTES/DEPOIS` = 0 (o comentário de fonte «sem painel ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar da página viva. Default = um rascunho Montar. Restore = irmão `restore.html`, fora da URL canónica.
- Tabs: `role=tablist` + `aria-selected` (não `aria-pressed`). Montar `aria-selected=true`. Acompanhar/Decidir presentes e disabled (sem sweep no rascunho novo — chrome de modos, sem delta). 1 tabpanel visível.
- 6 pares `COPIED:start/end` (copied > 0). Delta óbvio = 0 templates, 0 símbolos, só 1 dia marcado, 4 horas desmarcado, «Falta fazer» visível, início bloqueado.

Chrome presente (sidebar 224px, Inter, nav Descoberta activa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Rótulos vivos das três opções: `Templates` / `Símbolos` / `Timeframes swing` (não «Time Frames» de briefing). Layout `md:grid-cols-2` igual ao vivo: cartões Templates|Símbolos; fieldset Timeframes|Direção; Período|Ranking. **Não redesenhado.**

## Produto (aceite visível — não reabrir Q1 / Q2)

Delta pedido: rascunho novo sem pré-escolha; único default = 1 dia; «Falta fazer» + início bloqueado; operador ainda marca depois; «Novo rascunho» volta aos defaults; restore traz o gravado. Direção / período / ranking iguais ao vivo.

Contrato visível julgado no proto HTTPS (Playwright + pixels), não no HTML fonte.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Rascunho novo: 0 templates, 0 símbolos, sem chips | Desktop/mobile default: `tpl_checked=0` `sym_checked=0` `chips_*=0`. Copy «0 de 8 selecionados». Checkboxes visíveis desmarcadas. PNG `952-A-desktop-1440x900-montar-default.png` / `952-A-mobile-390x844-montar-default.png`. | OK |
| Só **1 dia** marcado; **4 horas** desmarcado | `tf-1d` checked, bg `rgba(252,213,53,0.1)` amarelo; `tf-4h` unchecked, bg `rgb(24,26,32)` muted. Altura 44px. | OK |
| «Falta fazer» visível; início bloqueado | Painel amarelo: «Escolha ao menos 1 template.» + «Escolha ao menos 1 símbolo.» CTA `disabled`, texto `Iniciar varredura — —, —`, min-height 44. Estado Preflight «Bloqueado — veja o que falta». | OK |
| Não dispara varredura vazia | Clique nativo no CTA disabled → `TimeoutError`; URL inalterada; `still_disabled=true`; 0 dialog / 0 nav. | OK |
| Operador ainda marca templates, símbolos e 4 horas | Marcar 4h → checked, início continua bloqueado (faltam eixos). Marcar 1 template + 1 símbolo → chips, «2 combinações válidas», aviso some, CTA amarelo enabled `Iniciar varredura — 2, —`. PNG `952-A-desktop-1440x900-marcar-1tpl-1sym.png`. Mobile 1+1 igual. | OK |
| «Novo rascunho» volta aos defaults | Após 1+1+4h: `tpl/sym=0`, chips 0, só 1 dia, 4h off, «Falta fazer» de novo, CTA disabled. Direção Long + período Todo o histórico + ranking Calmar **não** resetados (Q2). PNG `952-A-desktop-1440x900-novo-rascunho.png`. | OK |
| Restore (irmão, não canónico) traz o gravado | `restore.html`: 3 templates + 4 símbolos marcados, 4h+1d ambos on, aviso hidden, CTA enabled «24 combinações». **Não** aplica defaults novos por cima. PNG `952-A-desktop-1440x900-restore-irmao.png`. | OK |
| Direção, período, ranking iguais ao vivo | Long marcado; `Todo o histórico`; `Calmar (recomendado)`. Copy de ajuda Short = vivo. Q2 **não reaberta**. | OK |
| Layout das três opções não redesenhado | Mesma grelha 2 colunas do TSX; Timeframes é fieldset swing (não terceiro cartão inventado). | OK |

Q1/Q2 **não reabertas**. Mecanismo (`slice` do catálogo, `useState(['1d'])`, `newDraft` limpa, `hydrateFromSweep` sem fallback `['4h','1d']`) = P3 Apply já aceite em `design.md`.

## UX

Hierarquia: h1 → tablist 3 modos → Rascunho + Preflight. Default Operate = Montar (rascunho novo). Glance: eixos vazios + 1 dia amarelo + aviso nomeado + CTA morto. Sem terceiro estado inventado.

Carga: decisão no rascunho novo = marcar o que entra (já era o trabalho); o delta **remove** pré-escolha, não acrescenta controlo. Tablist = 3. «Falta fazer» é o mesmo bloco vivo (card 852), agora no caminho feliz do rascunho vazio — risco já aceite na grelha (operador habituado à pré-escolha).

## Acessibilidade

- `lang=pt-BR`; alvos Time Frames / CTA / Novo rascunho `min-height` 44px (desktop e mobile).
- Tablist/tab/tabpanel + `aria-selected` (não `aria-pressed`). 1 tabpanel visível.
- «Falta fazer» é texto (template + símbolo), não só cor. 1 dia vs 4 horas distinguem-se por texto + `checked` + paleta amarela vs muted.
- Início `disabled` (não só paleta). Após 1+1, enabled.
- Contraste: pares Binance (amarelo CTA/selecção vs muted desmarcado vs aviso `#fbbf24`).
- Nav do shell e sítio de «Novo rascunho» no header do rascunho = proto de gate; Apply mantém o sítio vivo (já P3 aceite).

## Responsividade

- Desktop 1440×900: contrato visível sem clip dos eixos / Preflight. Sidebar 224px. PNGs `952-A-desktop-1440x900-{montar-default,marcar-4h,marcar-1tpl-1sym,novo-rascunho,restore-irmao}.png`.
- Mobile 390×844: cartões empilhados; 1 dia/4 horas 44×139.5; «Falta fazer» e CTA 44px visíveis. Sidebar some (clone do vivo). PNGs `952-A-mobile-390x844-{montar-default,marcar-1tpl-1sym,novo-rascunho}.png`.
- Sem overflow que esconda o contrato. 0 console / 0 pageerror.

## Estados

Mock cobre: rascunho novo vazio; marcar 4h ainda bloqueado; 1+1 destrava; «Novo rascunho» restaura; restore gravado 3+4+4h+1d. Não mocka: restore com Time Frame vazio (aviso «Selecione ao menos um timeframe.» — decisão 3, Apply); workbench real; POST de varredura. Cobertura de mock = P3, não buraco do contrato visível no index.

## Design specificity

Composição da Descoberta (Montar + Preflight humano + Timeframes swing 4h/1d + Long-only). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip RASCUNHO + «Bloqueado — veja o que falta» + 0/8 |
| 2 | Match between system and real world | 4 | Vazio = falta escolher; 1 dia = default pedido |
| 3 | User Control and Freedom | 4 | Marca/desmarca eixos; Novo rascunho limpa; restore intacto |
| 4 | Consistency and Standards | 4 | Copy e layout vivos; Q2 intacta |
| 5 | Error Prevention | 4 | CTA disabled; clique vazio não navega |
| 6 | Recognition rather than recall | 4 | Aviso nomeia template e símbolo; 1 dia vs 4 horas no sítio |
| 7 | Flexibility and efficiency | 3 | Workbench / catálogo completo = vivo, condensado no proto |
| 8 | Aesthetic and Minimalist Design | 4 | Delta mínimo; sem galeria de estados |
| 9 | Help users recognize/recover errors | 4 | Falta fazer some quando 1+1; Novo rascunho recupera o vazio |
| 10 | Help and Documentation | 3 | Hint Long/Short; Ajuda fora |
| **Total** | | **38/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta = ausência de pré-escolha + 1 default. **Pass**. Decisão no glance Montar ≤4 (marcar template / símbolo / 4h opcional / iniciar quando verde). Sem painel ANTES/DEPOIS a traduzir.

## Emotional journey

Vale (pré-escolha a desmarcar) → pico (rascunho vazio honesto + 1 dia + aviso do que falta) → fim (marca 1+1, CTA liga; Novo rascunho volta; restore não mexe). Reassegurança: Direção/período/ranking não saltam.

## Personas (arquivo; não no chat)

1. **Alex (rascunho novo):** abre Montar, 0/0, só 1 dia, não consegue iniciar.
2. **Alex (escolhe eixos):** marca 4h + 1 template + BTC; aviso some; inicia enabled.
3. **Sam (teclado / SR):** landmarks 3/3; CTA disabled anunciável; Time Frames 44px; Novo rascunho restaura.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: só a ausência de pré-escolha + default 1 dia.
- Q1 (novo vs restore) visível em duas URLs, canónica só o index.
- Q2 visível: Long / Todo o histórico / Calmar sobrevivem ao Novo rascunho.

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: contrato visível PASS. Landmarks 3/3 no default Montar. 0 console / 0 pageerror.
- Live `/combo/discovery` → `/login` (descartado). PNG `952-A-live-combo-discovery.png`.
- Detector: não corrido aqui (Assessment A; B é o detector).
- PNGs: `952-A-desktop-1440x900-{montar-default,marcar-4h,marcar-1tpl-1sym,novo-rascunho,restore-irmao}.png`, `952-A-mobile-390x844-{montar-default,marcar-1tpl-1sym,novo-rascunho}.png`, `952-A-live-combo-discovery.png`. Gate: `952-A-gate.json`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Sítio de «Novo rascunho» no header do rascunho (gate). Apply mantém o sítio vivo — Acompanhar / rascunho colapsado. Já aceite em `design.md`.
- **P3-2** Tabs Acompanhar/Decidir disabled sem `#sweep`. Recorte: chrome de modos, sem delta. Apply lê o vivo quando há histórico.
- **P3-3** Catálogo mock 4 templates / 4 símbolos; busca local; «Edição avançada» sem workbench real. Non-goal: não mudar o catálogo.
- **P3-4** Restore irmão: 4 símbolos marcados, 3 chips visíveis (clone do extra do vivo). Não é overlay de defaults.
- **P3-5** Mecanismo: deixar de `slice(0, 3)` / `slice(0, 4)` no rascunho novo; `useState` inicial `['1d']`; `newDraft` zera + `['1d']`; `hydrateFromSweep` sem fallback `['4h','1d']`; testes que ainda afirmam 3/4/4h+1d. Já no contrato Apply.
- **P3-6** Nav/CSS vars do proto vs folha = clone de shell. Copy `Iniciar varredura —` (em dash) = vivo; advisory do detector, não P0.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1 / Q2. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (6 pares). Delta = rascunho novo vazio + só 1 dia. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`. Restore irmão não canónico. Q1/Q2 fechadas.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 952
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Novo rascunho no header (Apply sítio vivo); tabs Acompanhar/Decidir disabled; catálogo mock; chips restore extra; slice/useState/hydrate Apply; shell/em-dash vivo
verdict: PASS
```
