# Snapshot — card #686 `card-686-logs-tail-auth` (Assessment B / detector + browser)

- Card: #686
- Change: `card-686-logs-tail-auth`
- Critic: isolated Design Critic B (detector + Playwright; no transcript inherit)
- UTC: 2026-08-25T19:25:00Z
- UI impact: affected (BackendLogViewer auth delta; shell Combo clone)
- Prototype URL: https://dev.criptofarol.com.br/prototypes/card-686-logs-tail-auth/
- HTML path: `frontend/public/prototypes/card-686-logs-tail-auth/index.html`
- Digest claimed: `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`
- Digest observed (disk + served curl): `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4` — **match**
- Surfaces lidas (read-only): `index.html`; `frontend/src/components/BackendLogViewer.tsx`; trecho `ComboConfigurePage.tsx`; `openspec/changes/card-686-logs-tail-auth/design.md`

---

## Brief (recorte)

Admin autenticado no Combo abre **Ver logs**; poll passa a exigir Bearer admin; 401/403 no banner amber existente; JSON sem `path`; viewer chrome inalterado; shell autenticado Combo (sidebar 224px).

---

## Detector (`detect.mjs --json`)

Target: `frontend/public/prototypes/card-686-logs-tail-auth/index.html`

```json
[]
```

Exit code 0 — nenhum finding determinístico.

---

## Browser gate (Playwright Chromium headless)

Engine: `playwright@1.49.1` via npx em `/tmp` (sem writes no repo além do snapshot).

| Viewport | Size | Estados exercitados |
|----------|------|---------------------|
| desktop | 1440×900 | default, 401, 403 (+ Esc, Tab parcial) |
| mobile | 390×844 | default, 401, 403 (+ Esc) |

### Asserts observáveis

| Assert | desktop | mobile |
|--------|---------|--------|
| Shell Combo (`workspace-name=Combo`, h1=Otimizar) | ok | ok |
| Sidebar 224px visível | ok (224px flex) | ok (display none — mobilebar) |
| Botão **Ver logs** presente | ok | ok |
| Modal `aria-label="Logs do Backend"` | ok | ok |
| Título **Logs do Backend**, botão **Fechar** | ok | ok |
| Default: `Authorization: Bearer proto-admin-token` | ok | ok |
| Default: stream `Aguardando eventos…`, sem banner erro | ok | ok |
| 401: banner `HTTP 401 — faça login para ver logs` | ok | ok |
| 401: Authorization `(ausente)` | ok | ok |
| 403: banner `HTTP 403 — apenas admin pode ver logs` | ok | ok |
| 403: Bearer ainda presente | ok | ok |
| UI sem path `/srv/` | ok | ok |
| UI sem `full_execution_log.txt` | ok | ok |
| Esc fecha overlay | ok | ok |
| Console / page errors | ok ([]) | ok ([]) |

**Nota:** meta `full_execution_log • atualiza a cada 2s` espelha o viewer de produção (nome lógico allowlist, não path de filesystem).

### Console / page errors

Nenhum `console.error`, `pageerror` ou `requestfailed` material em desktop ou mobile.

### Teclado (amostra)

- Tab alcança `#open-logs`; Enter abre modal — ok.
- Tab dentro do modal: `#close-logs` → foco escapa para `<body>` / links da sidebar atrás do backdrop — **gap vs produção** (ver P2).
- Esc fecha modal — ok.
- Produção (`BackendLogViewer.tsx`) implementa focus trap, foco inicial no painel e `body overflow: hidden`; protótipo não.

### Contraste (amostra manual)

| Par | Ratio | WCAG AA 4.5:1 |
|-----|-------|---------------|
| `--text-muted` #707a8a on #0b0e11 | 4.46 | marginal fail |
| `#9ca3af` on `#111827` (modal meta) | 6.99 | pass |
| `#fbbf24` on `#181a20` (banner erro) | 10.42 | pass |

---

## Critique (detector + browser synthesis)

### Fidelidade ao produto

- **Shell autenticado:** sidebar fixa 224px desktop, nav Combo ativa, tokens `--bg-*` / accent, topbar/mobilebar — alinhado ao clone card-664 + escopo do design.
- **Viewer chrome:** estrutura modal (backdrop, header, meta mono, status rolagem, banner amber, stream monospace) bate com `BackendLogViewer.tsx`; delta auth (probe + copy 401/403) visível sem redesenho estrutural.
- **Conteúdo Combo:** seção simplificada (Otimizar + Ver logs) em vez da página completa com leaderboard/config — coerente com recorte “delta só credencial”; não é layout paralelo inventado.
- **Instrumentação protótipo:** toolbar fixture + `#auth-probe` são artefatos de validação; não devem ir para produção (Apply).

### Estados

Default / 401 / 403 comportam-se conforme contrato; fixture via select e query `?fixture=`; troca de fixture reabre viewer quando overlay aberto.

### Regressão layout

CSS herdado extenso (leaderboard, config-grid) permanece no arquivo mas não renderiza conteúdo extra — sem segunda UI paralela visível. Mobile esconde sidebar e usa mobilebar; modal ocupa viewport corretamente.

### A11y

- `:focus-visible` presente; botões min-height 44px; dialog `role="dialog"` + `aria-modal="true"`.
- Lacunas vs viewer real: sem focus trap, sem foco inicial no painel, sem lock de scroll do body (P2).
- Contraste `--text-muted` marginal 4.46:1 (P3).

---

## Audit (dimensões técnicas)

| Dimensão | Nota | Comentário |
|----------|------|------------|
| A11y | 2 | Teclado parcial; trap ausente |
| Performance | 4 | HTML estático leve |
| Theming | 3 | Tokens consistentes; probe/toolbar fora do produto |
| Responsive | 3 | Desktop + mobile validados |
| Implementation integrity | 4 | Detector limpo; delta auth simulado corretamente |

---

## Findings (emissão)

### P0

_(nenhum)_

### P1

_(nenhum)_

### P2

- **Modal sem focus trap / foco inicial** — Após abrir **Ver logs**, foco permanece no botão disparador; segundo Tab escapa do painel para links da sidebar atrás do backdrop. Produção trava Tab e foca `#log-panel`. disposition: `author-fix` (espelhar trap/foco/overflow do `BackendLogViewer` no protótipo).

### P3

- **Contraste `--text-muted` marginal** — #707a8a sobre #0b0e11 ≈ 4.46:1 (< 4.5:1 AA texto normal). disposition: `accept-or-polish`.
- **Instrumentação visível pós-abertura** — `#auth-probe` expõe Bearer no protótipo (útil para review; remover no Apply). disposition: `document-only`.
- **Botão Ver logs estilizado dark** — produção usa `bg-zinc-50` claro; protótipo usa `--bg-elevated` dark. Escopo do card é viewer, não Combo; delta visual menor. disposition: `accept`.

---

## Trace

1. `sha256sum` disco + `curl` URL servida → digest match claimed.
2. `node detect.mjs --json index.html` → `[]`.
3. Playwright desktop 1440×900: default/401/403 + asserts → all ok.
4. Playwright mobile 390×844: default/401/403 + asserts → all ok.
5. Keyboard probe → Esc ok; trap gap documentado.
6. Leitura `BackendLogViewer.tsx` → baseline focus trap / overflow.
7. Contraste amostral → text-muted marginal.

---

## Verdict

**PASS** — digest match; detector limpo; browser gate desktop/mobile verde nos asserts críticos do delta; zero P0/P1. P2 (focus trap) não bloqueia veredito B; recomendado polish autor antes de T7.

---

## Retorno ao pai (bullets)

- P0: _(nenhum)_
- P1: _(nenhum)_
- P2: modal sem focus trap/foco inicial vs `BackendLogViewer` produção — disposition `author-fix`
- P3: contraste text-muted marginal; auth-probe protótipo; estilo botão Ver logs — disposition `accept-or-polish` / `document-only` / `accept`
- **Verdict:** PASS
- **Snapshot:** `.impeccable/critique/686-card-686-logs-tail-auth-B.md`
- **Digest observado:** `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`
- **Viewports/asserts:** desktop 1440×900 — 14/14 ok; mobile 390×844 — 13/13 ok (+ sidebar hidden assert mobile-only); global sidebar 224px ok
