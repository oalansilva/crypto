---
card: 1160
change: card-1160-landing-auditoria
wave: 1160-d1
assessment: B (detector + clone gate + browser)
target: frontend/public/prototypes/card-1160-landing-auditoria/ (index.html, privacidade.html, termos.html)
public_url: https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/
live_url: https://criptofarol.com.br/
date: 2026-10-29
p0_count: 0
p1_count: 1
verdict: PASS com rework
---

# Assessment B — #1160 (onda 1160-d1)

Isolado do Assessment A (produto, UX, acessibilidade e fidelidade ficam com o A). Aqui: detector Impeccable, gate de clone e evidência de navegador.

## Detector Impeccable (`detect.mjs --json`)

| Alvo | Exit | Achados |
|---|---|---|
| `index.html` | 2 | 1 × `overused-font` (L34, Google Fonts: inter) |
| `privacidade.html` | 2 | 1 × `overused-font` (L16) |
| `termos.html` | 2 | 1 × `overused-font` (L16) |
| pasta do protótipo (inclui CSS) | 2 | 5: 3 × `overused-font` + 2 × `side-tab` (`delta.css:29` `.hero-risk`; `styles.css:637` `.risk-note`) |
| v4 viva (`cripto-farol-landing-v4/index.html`) | 2 | 1 × `overused-font` (L14) |

Separação delta × herdado:

- `overused-font` (Inter): **herdado** da v4 (a v4 dispara o mesmo). A linha do `<link>` fica em DELTA porque o delta tirou o IBM Plex Sans (3 → 2 famílias), mas a família Inter é da v4 e de `docs/brand-system.md`. P3 herdado; já registrado em Risks do design.md. Falso positivo para este card (Non-goal: sem troca de identidade).
- `side-tab` em `styles.css:637` (`.risk-note`): **herdado** (styles.css é a v4 byte a byte, sha `0014884b29cb`). P3 herdado.
- `side-tab` em `delta.css:29` (`.hero-risk`): **novo no delta**, repete o padrão da `.risk-note` da v4 de propósito (mesma família visual de aviso). Não está nos Risks do design.md, que só citam fontes e cores. P2 cosmético.

Overlay no navegador: não injetado (o critique deste card roda como dupla A/B sem live-server; a evidência de navegador é o Playwright abaixo). Sem `ignore.md`.

## Gate de clone (`scripts/process-fsm/design_clone_gate.py`)

O script não tem CLI (`--help` não imprime nada); rodado como módulo.

- Linhas 1–3 do design.md: `UI impact: affected` / `live_route: landing` / `surface: existing` — cada um em linha própria, parseáveis.
- `design_token_gap` = None; `requires_existing_clone` = True.
- Catálogo do HEAD, chave `landing`: selectors `.faq-section`, `.button-primary`; textos H1, "FAQ", "Quero meus 6 meses grátis".
- `classify(index.html, landing)` = **PASS** (HEAD e arquivo); `copied_utf8_sum` = **11.766 B**.
- `evaluate_clone_gate` = **True**; `clone_gate_ok` = **True**.
- `privacidade.html` / `termos.html`: BLOCKED (sem marcos da home; informativo, o catálogo não tem entrada para elas), `copied_utf8_sum` = 231 B cada.
- Conferência independente: 20 pares COPIED no `index.html` (17 HTML + 3 JS), 3 em cada página legal; todos substrings literais da v4; `styles.css` idêntico à v4. Bate com a Prototype Validation do autor.

## Navegador (Playwright 1.58.2, Chromium, URL pública, 1440×900 e 390×844 DPR 3 com toque)

40/42 asserts PASS. Por largura:

- Console: 0 `console.error`, 0 `pageerror`; 0 resposta ≥ 400; 0 request falho.
- Rolagem horizontal: 0 px no index, na Política e nos Termos, nas duas larguras.
- Imagens: todas carregam (`complete` e `naturalWidth > 0`). Hero `hero-1600.webp` nas duas larguras (390 × DPR 3 = 1170 → 1600w). 1440: `tabela-ativos.webp` e `grafico-estrategia.webp` inteiros. 390: `tabela-ativos-recorte.webp` (390 px de largura) e `grafico-estrategia-recorte.webp` (341 px).
- Aviso de risco do hero: 1440 dentro da primeira tela (bottom 712/900); 390 logo depois dos selos (bottom 903/844), como D6 descreve.
- CTA "Entrar no beta" na navegação visível sem rolar nas duas larguras (390: primeiro item, 110×36).
- Funil: `landing_cta_clicked` com hero, nav e footer; passo 1 vazio não avança; e-mail "erro…" → "Não conseguimos salvar agora…" e fica no passo 1; passo 1 → passo 2 com "Pronto, seu cadastro está salvo." e foco no WhatsApp; passo 2 → "Recebemos seu cadastro." / "próxima leva", foco no estado final, sem "e-mail"; "Pular esta etapa" → sucesso + `lead_step2_skipped`; nenhum evento com nome, e-mail ou WhatsApp.
- **FAIL (2/42, mesma causa nas duas larguras): Enter no campo de e-mail do passo 1** (ou "Ir" do teclado do celular) dispara o envio implícito do formulário. O botão do passo 1 é `type="button"` e o único `type="submit"` é o do passo 2, então o Enter roda o handler do passo 2: o formulário pula direto para "Recebemos seu cadastro.", sem mostrar o passo 2. Os eventos são `lead_form_submit_started:2` e `lead_form_submit_accepted:2`, sem `lead_step1_completed`. O payload vai com `step: 2` e sem o nome. Na v4 isso não acontecia porque nível e dificuldade eram `required` e a validação barrava o envio. O delta tornou os dois opcionais, então a falha é **nova**. Pelo D1 ("passo 2 sem lead do e-mail, cria"), em produção o lead nasceria sem nome, o Alan receberia o aviso "Lead completou o cadastro" no lugar de "Novo lead" e o funil perderia o passo 1.
- Páginas legais: o clique no rodapé abre `privacidade.html` e `termos.html` (H1 certo, rodapé, sem CNPJ, imagens ok, sem rolagem horizontal); canonical `https://criptofarol.com.br/privacidade` e `/termos`; cabeçalho com links de volta (`./`, `./#lista`).
- Meta do index: canonical apex; og:title, og:description e og:image; `twitter:card=summary_large_image`; JSON-LD Organization + FAQPage com parse ok, FAQPage = 6 perguntas = FAQ visível na mesma ordem; description com acentos; `assets/og-1200x630.jpg` = 1200×630, 83.006 B.
- Alvos de toque a 390: "Pular esta etapa" 150×44; botões do formulário 52 px de altura; CTA do rodapé 343×52; links do rodapé 44 px; "Entrar no beta" na nav 36 px de altura, a mesma altura dos outros itens da nav da v4.
- Texto a 200 % (root) no celular: transborda 99 px, igual na viva (a nav da v4 rola na horizontal). Herdado; não é achado.

### Peso e LCP (CDP `encodedDataLength`, cache desligado; LCP por PerformanceObserver)

| Cenário | Protótipo | Viva | Observação |
|---|---|---|---|
| 390, sem limite, transferido (3 rodadas) | **164,6 KB** (11 req) | **1.697,8 KB** (12 req) | −90 %; a viva leva o PNG de 1.419.857 B |
| 390, sem limite, LCP (mediana de 3) | **304 ms** (H1) | **280 ms** (H1) | no celular o LCP é o H1 nos dois; empate dentro do ruído |
| 390, limitado (150 ms RTT, 1,6 Mbps, CPU 4×), LCP | **748 ms** (H1) | **708 ms** (H1) | empate (1 rodada) |
| 390, limitado, `load` | **1.146 ms** | **8.468 ms** | ganho grande no load completo |
| 1440, sem limite, transferido | **193,5 KB** | **1.697,8 KB** | |
| 1440, sem limite, LCP (mediana de 3) | **328 ms** (hero-1600.webp) | **344 ms** (cripto-farol-hero.png) | |

Composição no celular: fontes 80,4 KB (Inter 48,8 + JetBrains Mono 31,6), imagens 68,5 KB, HTML 9,0 KB (gzip), CSS 6,6 KB. A viva leva 126 KB de fontes (3 famílias) e 1.558 KB de imagens. O LCP de ~1,26 s da auditoria original não se reproduz deste host (rede local ao servidor); a comparação justa é a da mesma sessão acima. Como o LCP do celular é texto, o ganho do WebP aparece no peso e no `load`, não no LCP; o gargalo do LCP no celular é a fonte do H1 (Inter 800 do Google Fonts).

## Achados priorizados

**P0** — nenhum.

**P1**
1. **Enter/"Ir" no passo 1 pula o passo 1 e manda passo 2 sem nome** (`index.html`, script DELTA: `form.addEventListener("submit")` + `data-save-step1` `type="button"`). Fluxo visível quebrado: o passo 2 opcional some, o lead pode nascer sem nome e `lead_step1_completed` não sai. Regressão nova do delta (na v4 os `required` barravam o envio). Correção: no handler de `submit`, se o passo ativo for o 1, chamar o mesmo caminho do botão do passo 1 (reportValidity → salvar → passo 2) e sair. Outra opção: o botão do passo 1 vira `type="submit"` e o handler despacha pelo passo ativo. Acrescentar ao Apply contract: "Enter no passo 1 = Entrar na lista do beta", e um teste no `tests/` da landing.

**P2**
1. **Erro do passo 2 não é demonstrável no protótipo** (`simulatedSave`: só um e-mail que começa com "erro" falha, e esse e-mail já falha no passo 1). O estado "Seu cadastro já está salvo, mas estas respostas não foram…" existe no código e no D4, mas o Alan não consegue vê-lo antes do T7. Correção: simular a falha do passo 2 por outro gatilho (ex.: dificuldade que começa com "erro") e citar o gatilho na seção Prototype do design.md.
2. **`side-tab` novo em `.hero-risk`** (`delta.css:29`, `border-left: 3px solid var(--gold)`). Achado do detector no delta, fora dos Risks do design.md. É coerente com a `.risk-note` da v4, então basta registrar como aceito (consistência com a v4) na lista de achados do detector em Risks, ou trocar por um marcador sem barra lateral. Sem impacto de escopo.

**P3 (detalhe de Apply / herdado)**
1. `overused-font` Inter nas 3 páginas: herdado da v4 e já aceito em Risks. Nada a fazer.
2. `side-tab` em `styles.css:637` (`.risk-note`): herdado da v4. Nada a fazer.
3. `og:image` e `twitter:image` apontam para `https://criptofarol.com.br/lp/og-1200x630.jpg`, que hoje devolve 200 `text/html` (fallback da SPA): o caminho só passa a existir com o `/lp/` do D10/D12. No Apply, conferir por HTTP que o `/lp/og-1200x630.jpg` sai como `image/jpeg` no `deploy.sh` (somar à lista de URLs que ele confere) e no validador de compartilhamento.
4. `favicon.ico` e `apple-touch-icon` ausentes no protótipo (o `<head>` tem só o SVG): D9 manda gerar no Apply. Já coberto pelos P3 aceitos.
5. `design_clone_gate.py` sem CLI (`--help` mudo): o motor é pin do covenant-flow, fora deste card.
6. No celular, a confirmação "Pronto, seu cadastro está salvo." fica no `role=status` abaixo dos botões do passo 2, e o título do passo 2 repete "Cadastro salvo". A mensagem é anunciada pelo leitor de tela e o foco vai para o WhatsApp, então funciona; repassado ao A, que cuida de UX.

## Disposition

Gate de clone verde (tokens L1–L3 ok, `clone_gate_ok` = True, 11.766 B copiados, COPIED literal da v4) e navegador limpo (0 erro, 0 ≥400, 0 overflow, imagens e recortes certos, meta/OG/JSON-LD presentes, peso −90 %). O único P1 é a regressão do Enter no passo 1, criada pelo delta ao tornar o passo 2 opcional. A correção é pequena e cabe no rework único, junto com o P2 do erro do passo 2 que hoje não aparece no protótipo.

**Verdict: PASS com rework**
