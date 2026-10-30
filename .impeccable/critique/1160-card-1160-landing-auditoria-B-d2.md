---
card: 1160
change: card-1160-landing-auditoria
wave: 1160-d2
assessment: B (detector + clone gate + browser)
target: frontend/public/prototypes/card-1160-landing-auditoria/ (index.html, privacidade.html, termos.html, styles.css, delta.css)
public_url: https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/
live_url: https://criptofarol.com.br/
public_sha_index: 2128f1e48337 (= worktree)
date: 2026-10-29
p0_count: 0
p1_count: 1
verdict: PASS com rework
---

# Assessment B — #1160 (onda 1160-d2)

Isolado do Assessment A (produto, UX, acessibilidade e fidelidade ficam com o A). Aqui: detector Impeccable, gate de clone e evidência de navegador. Evidência no scratchpad da sessão: `c1160-b-d2/` (`detect-*.json`, `gate.json`, `browser-report.json`, `detect-browser-live-legal.json`, `shots/`, `tools/`).

## Detector Impeccable

### CLI (`detect.mjs --json`)

| Alvo | Exit | Achados |
|---|---|---|
| `index.html` | 0 | nenhum |
| `privacidade.html` | 0 | nenhum |
| `termos.html` | 0 | nenhum |
| pasta do protótipo (inclui CSS) | 2 | 3: `overused-font` `delta.css:6` (`@font-face` Inter); `side-tab` `delta.css:56` (`.hero-risk`); `side-tab` `styles.css:637` (`.risk-note`) |
| v4 viva (`cripto-farol-landing-v4/`) | 2 | `overused-font` `index.html:14` (Google Fonts Inter); `side-tab` `styles.css:637` |

Varredura por URL (`detect.mjs <url>`): indisponível, sem `puppeteer` no host. Substituída pelo detector de navegador injetado com Playwright (abaixo).

Separação:
- `overused-font`: mesma família Inter da v4. Na d1 o achado vinha do `<link>` do Google Fonts no HTML; desde o r1 a fonte é servida pela pasta e o achado mudou para o `@font-face` do `delta.css`. Herdado, já aceito em Risks. Não é da d2.
- `side-tab` `.hero-risk` (`delta.css:56`): é delta da d1 e foi aceito e mantido em Risks no r1 (mesma marca da `.risk-note`). Não é reaberto.
- `side-tab` `.risk-note` (`styles.css:637`): v4 byte a byte. P3 herdado.
- Nenhum achado novo da d2 no CLI. O `design-system-font-size` de `.signal-card strong`, citado pelo autor como achado do hook de escrita, não sai no CLI com a config do projeto; já está em Risks.

### Navegador (`detect-antipatterns-browser.js` injetado, 1440 e 390, protótipo × viva)

Todas as classes que aparecem no protótipo também aparecem na v4 viva, nas mesmas seções: `ai-color-palette` (ciano), `dark-glow` e `cramped-padding` no `.button-primary` (falso positivo: o botão usa `min-height` e flex), `radial-spotlight-glow` nas seções, `gradient-text`, `monotonous-spacing`, `marquee` (falso positivo: não há `<marquee>` nem classe de ticker, nas duas páginas), `hero-eyebrow-chip` e `all-caps-body` no rótulo, `line-length` ~106 no texto de abertura do produto e ~110 nas respostas do FAQ (largura da v4).

Só existem no delta, todos da d1 e não da d2: `line-length` na `.hero-risk` (~87 caracteres, `max-width: 640px`), na `.form-consent` (~86) e na `.footer-risk` (~122, `max-width: 880px`). O CTA do rodapé e os links do rodapé reaproveitam as classes da v4, então herdam `dark-glow` e a cor ciano. As páginas legais herdam os mesmos falsos positivos. Overlay visível ao usuário: não (o critique roda como dupla isolada sem live-server; injeção só no Playwright headless, capturas `B-d2-*-overlay-detector.png`).

## Gate de clone (`scripts/process-fsm/design_clone_gate.py` como módulo)

- L1–L3 do design.md: `UI impact: affected` / `live_route: landing` / `surface: existing`, um por linha, parseáveis. `design_token_gap` = None; `requires_existing_clone` = True.
- Catálogo do HEAD, chave `landing`: `.faq-section`, `.button-primary`; textos H1, "FAQ", "Quero meus 6 meses grátis" (hero e rodapé). O H1 continua igual (D13).
- `classify(index.html, landing)` = **PASS** (HEAD e arquivo); `copied_utf8_sum` = **9.100 B** (d1: 11.766 B, porque hero, rotina, benefícios, sinais, FAQ 6 e o aviso do cadastro viraram delta).
- `evaluate_clone_gate` = **True**; `clone_gate_ok` = **True**.
- `privacidade.html` / `termos.html`: BLOCKED (informativo, o catálogo não tem entrada para elas), `copied_utf8_sum` = 231 B cada.
- Conferência independente: 28 pares COPIED no `index.html` e 3 em cada página legal. **Todos são substrings literais da v4** (0 fora). 0 marcador dentro de tag. 28 pares DELTA. `styles.css` idêntico à v4 (sha `0014884b29cb`). URL pública com o mesmo sha do worktree (`2128f1e48337`). Bate com a Prototype Validation da d2.
- Observação do motor: `parse_live_route` devolve a justificativa `"surface: existing"`, porque o `\s+` da regex atravessa a quebra de linha. Não afeta `landing`; é do motor pinado (P3, card de motor).

## Navegador (Playwright 1.58.2, Chromium, URL pública; 1440×900 DPR 1 e 390×844 DPR 3 com toque)

**60/60 asserts PASS.**

- Console: 0 `console.error`, 0 `pageerror`; 0 resposta ≥ 400; 0 request falho; **só o host `dev.criptofarol.com.br`** (nenhum terceiro).
- Rolagem horizontal: 0 px no index, na Política e nos Termos, nas duas larguras.
- Imagens: todas carregam. 1440: `hero-1600.webp`, `monitor.webp` (418×556), `grafico-analise.webp` (978×656, lazy). 390: `hero-1600.webp`, `monitor.webp` (390×519, sem `loading`, topo em 975 px, abaixo da dobra), `grafico-analise-recorte.webp` (**341×394**, lazy).
- Primeira tela: 1440, aviso de risco termina em 712/900 (dentro); 390, termina em 946/844, logo depois dos selos e dos CTAs, como o spec pede ("at 390px after the CTAs"). Na d1 terminava em 903; o rótulo agora quebra em 2 linhas e o aviso em 3. CTA "Entrar na lista" na nav visível sem rolar, 44 px de altura a 390.
- Sinais: "Em posição" em 1 linha e "Saída / cobertura" em 2 linhas, 0 overflow (70,4 px a 1440, 39 px a 390).
- Formulário (nas duas larguras): passo 1 vazio não avança; Enter no passo 1 com e-mail vazio fica no passo 1; **Enter no passo 1 válido → passo 2**, com `lead_step1_completed`, sem `lead_form_submit_started:2`, foco no título do passo 2 e "Pronto, seu cadastro está salvo."; **erro do passo 2** (dificuldade "erro…") mostra "Seu cadastro já está salvo, mas estas respostas não foram…", fica no passo 2 e mantém "Pular esta etapa" (150×44) à mão; pular → "Recebemos seu cadastro.", foco no estado final, sem "e-mail"; Enter no WhatsApp do passo 2 envia o passo 2 e chega ao sucesso; erro do passo 1 ("erro@…") → "Não conseguimos salvar agora…" e fica no passo 1; `landing_cta_clicked` hero/nav/footer; nenhum evento com nome, e-mail ou WhatsApp. O erro sai no `role=status` (`role=alert` já é P3 aceito).
- Páginas legais: o clique no rodapé abre `privacidade.html` e `termos.html` (H1 certo, rodapé com aviso de "cripto, ações e ETFs", sem CNPJ, imagens ok, 0 overflow). Canonical `/privacidade` e `/termos`. Termos com ações e ETFs, Nova York, "à vista" e alerta sem ordem.
- Rodapé: Política, Termos e "Já tenho acesso" com 44 px; CTA 52 px (343 px de largura a 390); aviso com ações e ETFs; sem CNPJ.
- Meta: título, descrição e `og:description`/`twitter:description` com "ações e ETFs"; canonical apex; `twitter:card=summary_large_image`; JSON-LD Organization + FAQPage com parse ok; **FAQPage = FAQ visível, 6 de 6, pergunta e resposta, mesma ordem** (inclui "Funciona com ações e ETFs?"). Nada de "Teste qualquer estratégia", "outra exchange", "Sinal de Compra/Venda", "alvo", MATIC, CNPJ, "Restam", "Verifique seu e-mail". `og:title` e `og:image:alt` = H1 (só cripto); a imagem OG traz a frase de ações e ETFs.

### Tamanho efetivo do texto nos prints

Monitor: a imagem tem 804 px, 2× de 402 px CSS do app. A fonte de origem foi medida no clone do #1122 a 500 px (`main.monitor-board` com 401 px): rótulos 11 px, estados 12 px. Análise: a imagem está 1:1 com o gráfico do app; eixo e marcadores em 12 px; o menor texto do cabeçalho redesenhado tem 11 px.

| Print | Largura | Escala renderizada | Texto efetivo |
|---|---|---|---|
| Monitor | 1440 | 1,04× do app | 11,4 px (rótulos), 12,5 px (estados) |
| Monitor | 390 | 0,97× do app | **10,7 px** (rótulos), 11,6 px (estados): o próprio tamanho do app no celular |
| Análise (`grafico-analise.webp`) | 1440 | 1,153 | 13,8 px (eixo e marcadores) |
| Análise (recorte) | 390 | **0,692** (341 px de 493) | **8,3 px** (eixo, "COMPRA", "VENDA (−5,18%)", "Ação · Diário…"), **7,6 px** ("Último fechamento") |

O D8 diz que o recorte fica a "~0,79 da escala original a 390 px", mas a figura tem 341 px de largura, não 390.

### Peso e LCP (CDP `encodedDataLength`, cache desligado, 3 rodadas; LCP por PerformanceObserver)

| Cenário | Protótipo d2 | Viva (v4) | d1 (B) |
|---|---|---|---|
| 390, transferido | **184,6 KB** (10 req) | **1.658 KB** (12 req) | 164,6 KB |
| 390, LCP mediano | **128 ms** (H1) | 288 ms (H1) | 304 / 280 ms |
| 390, limitado (150 ms RTT, 1,6 Mbps, CPU 4×): LCP / load | **728 / 1.201 ms** (H1) | 708 / 8.463 ms (H1) | 748 / 1.146 ms |
| 1440, transferido | **197,1 KB** (10 req) | 1.658 KB | 193,5 KB |
| 1440, LCP mediano | **176 ms** (hero-1600.webp) | 364 ms (PNG) | 328 / 344 ms |
| 1440, limitado: LCP / load | **1.420 / 1.291 ms** | 8.520 / 8.454 ms | — |

Composição a 390: fontes 77,9 KB (Inter 48,3 + JetBrains Mono 31,5, locais), imagens 91,5 KB (hero 36,4, monitor 32,5, recorte 23,5), HTML 9,6 KB, CSS 5,6 KB. A página fica **89 % mais leve** que a viva. O ganho de 20 KB sobre a d1 vem do print do Monitor, que carrega logo de saída mesmo abaixo da dobra no celular (P3 já aceito: `fetchpriority`/`loading`). Os ganhos de LCP sobre a d1 vêm das fontes locais (r1). No limitado, o LCP do celular empata com a viva (H1 nos dois).

## Achados priorizados

**P0**: nenhum.

**P1**
1. **O recorte da análise no celular não é legível** (`assets/grafico-analise-recorte.webp` no `<picture>` do `#produto`; D8). A 390 a figura tem 341 px, então a imagem de 493 px sai a 0,692. O eixo e os marcadores "COMPRA" / "VENDA (−5,18%)", que são o que o benefício 01 e a rotina 02 prometem mostrar, ficam com **8,3 px**, e "Último fechamento" com 7,6 px. O Monitor fica com 10,7 px. Isso fere o requisito "Clean and legible product prints" ("At phone width every print SHALL render its text at a legible size"), que é o motivo do T6. Correção: refazer o recorte com ~340–360 px de largura natural (por exemplo jul.–out., ou eixo de preço mais estreito) para sair a ≥ 0,95 (≥ 11,4 px), ou redesenhar no recorte o eixo, os marcadores e o cabeçalho a 16–17 px (o `build_imgs_d2.py` já redesenha o eixo). Depois, corrigir o "~0,79" do D8 e somar ao browser gate um assert de texto efetivo ≥ 11 px (ou escala ≥ 0,9) no recorte a 390.

**P2**: nenhum.

**P3 (detalhe de Apply / herdado)**
1. Detector CLI: `overused-font` (`delta.css:6`) e `side-tab` (`styles.css:637`) herdados da v4; `side-tab` `.hero-risk` (`delta.css:56`) aceito em Risks no r1. Nada a fazer.
2. Detector de navegador: tudo herdado da v4, salvo `line-length` em `.hero-risk` (~87), `.form-consent` (~86) e `.footer-risk` (~122), todos da d1. No Apply, `max-width: 60–65ch` nesses três.
3. `og:title` e `og:image:alt` falam só de cripto (o `og:title` = H1 é decisão do D13). No Apply, o `og:image:alt` pode descrever a frase da imagem ("Cripto, ações e ETFs da Binance…"). A imagem OG foi desenhada em DejaVu, não em Inter: regerar com a fonte da marca junto da recaptura.
4. `https://criptofarol.com.br/lp/og-1200x630.jpg` ainda responde `200 text/html` (fallback da SPA). Já aceito: o `deploy.sh` confere `image/jpeg` depois do corte.
5. O print do Monitor corta a borda direita dos cartões (recorte a 402 px de um board de 401 px), visível nas duas larguras. Resolver na recaptura do DEV (task 2.10).
6. `monitor.webp` a 390 carrega logo de saída abaixo da dobra (+32,5 KB no primeiro carregamento). Já coberto pelo P3 `fetchpriority`/`loading`.
7. Varredura por URL do `detect.mjs` indisponível (sem `puppeteer` no host); `design_clone_gate.py` sem CLI e com `parse_live_route` que captura a linha seguinte como justificativa. Ambos são do motor ou do ambiente, fora do card.

## Disposition

O gate de clone está verde: tokens L1–L3 ok, `clone_gate_ok` = True, 9.100 B copiados, os 28 pares COPIED são literais da v4 e o `styles.css` é idêntico. O navegador está limpo: 60/60, 0 erro, 0 ≥ 400, 0 terceiro, 0 overflow, formulário inteiro e FAQPage = FAQ. A página fica 89 % mais leve que a viva, com LCP igual ou melhor. A d2 não trouxe achado novo do detector. O único P1 é o recorte do gráfico no celular, com texto de 8,3 px, contra o requisito de prints legíveis. A correção é só de imagem (recorte mais estreito ou rótulos redesenhados) e cabe no rework único.

**Verdict: PASS com rework**
