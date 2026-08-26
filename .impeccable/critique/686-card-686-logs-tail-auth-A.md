# Snapshot — Assessment A · card #686 `card-686-logs-tail-auth`

- Card: #686 P0 GET /api/logs/tail público
- Change: `card-686-logs-tail-auth`
- Critic: Assessment A (crítica isolada Impeccable, sem transcript do pai)
- Modelo: inherit
- UTC: 2026-08-25T19:25:00Z
- Status observado: Design
- UI impact: affected (Bearer no BackendLogViewer; 401/403 no banner existente; sem redesenho)
- Prototype URL: https://dev.criptofarol.com.br/prototypes/card-686-logs-tail-auth/
- Path: `frontend/public/prototypes/card-686-logs-tail-auth/index.html`
- Digest packet: `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`
- Digest disco: `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4` ✓
- Digest servido (curl DEV): `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4` ✓
- HTTP servido: 200
- Method: isolated Assessment A (A only; B separado no pai). Playwright indisponível (binário não instalado); julgamento via fonte HTML, comparação com `BackendLogViewer.tsx`, base `card-664-discovery-restore-reload`, live digest e rubrica Impeccable.
- Detector CLI (`detect.mjs`): `[]` (limpo)

---

## Brief

**Problema:** `GET /api/logs/tail` público devolve conteúdo sensível (incl. e-mail/link de reset em INFO) e `path` de filesystem; viewer faz `fetch` cru.

**Usuário:** admin autenticado no Combo que abre **Ver logs** durante otimização.

**Hipótese:** `Depends(get_current_admin)` + JSON sem `path` + forgot-password sem PII em INFO + `authFetch` no viewer fecha o vazamento sem redesenhar o modal.

**Outcome de design:** poll com Bearer; 401 = não logado; 403 = não admin; banner âmbar existente; stream mantém “Aguardando eventos…”; nunca expor path na UI/JSON.

**Direction:** clone shell autenticado (sidebar 224px, header 80/72, tokens escuros, Inter, nav real) + chrome atual do `BackendLogViewer`; delta = credencial + copy de erro observável.

**Scope UI:** modal **Logs do Backend** e contrato de fetch. Fora: redesenho, rotação de log, auth em massa.

**Modo Impeccable:** Operate.

---

## Impeccable Shape (recorte)

| Dimensão | Decisão |
|----------|---------|
| Audience | Admin no workspace Combo |
| Outcome | Ver tail autenticado ou erro 401/403 legível |
| Direction | Clone+delta sobre viewer existente |
| Estados | default (admin+Bearer), 401, 403 |
| Restrições | Sem path; sem toast paralelo; sem redesign |

---

## Critique

### Design Specificity Verdict

**Veredito:** **Específico ao Cripto Farol** — não é modal genérico de logs.

**Evidência:**
- Shell copiado da linha `card-664-discovery-restore-reload`: sidebar 224px, topbar 80px, mobilebar 72px, nav com Favoritos/Monitor/Descoberta/Combo/Carteira/Ajuda/Preferências/Usuários.
- Modal espelha classes/comportamento do `BackendLogViewer.tsx`: overlay `z-[200]`, painel `max-w-5xl`/`64rem`, `h-[85vh]`, título **Logs do Backend**, meta `{name} • atualiza a cada Ns`, status **Rolagem automática**, botão **Fechar**, banner âmbar, área mono `Aguardando eventos…`.
- Delta do card é explícito: simulação de tail com/sem `Authorization`, banners `HTTP 401` / `HTTP 403`, JSON simulado sem chave `path`, guard em JS que falha se `path` aparecer.

**Deterministic scan:** nenhum achado estrutural no HTML.

**Risco de genericidade:** baixo. O protótipo ancora no produto real; scaffolding (toolbar de fixture, `#auth-probe`) é claramente marcado como protótipo.

### Fidelidade à tela existente (gate bloqueante)

| Superfície | Julgamento |
|------------|------------|
| Shell autenticado | **Alta** — dimensões, nav, tokens e densidade batem com folha + base 664 |
| Modal `BackendLogViewer` | **Alta** — chrome, copy base, hierarquia e estados de erro alinhados ao componente React atual |
| Host Combo (`Ver logs`) | **Média** — stub `.combo-optimize` suficiente para abrir o modal; não replica página completa `ComboConfigurePage` nem o botão zinc claro do prod |

**Conclusão fidelidade:** a superfície **existente que muda** (modal viewer) está fiel. Host Combo simplificado é aceitável para delta-only; não constitui layout paralelo inventado.

### Produto e escopo

- Aderência total a `proposal.md`, `design.md`, `specs/log-viewer` e Apply contract.
- 401 vs 403 distinguíveis (sem token vs token presente + 403).
- Sem vazamento de path (`/srv/`, `.txt`) no DOM do protótipo; meta usa nome lógico `full_execution_log`, como produção.
- `#auth-probe` documenta Bearer para review — não entra no Apply.

### UX / hierarquia / carga cognitiva

**Checklist carga cognitiva (8 itens):** 1 falha leve — `.prototype-toolbar` adiciona decisão extra fora do fluxo real (aceito como controle de fixture).

| Item | Pass |
|------|------|
| Foco único no modal aberto | ✓ |
| Chunking | ✓ (head / erro / stream) |
| Agrupamento visual | ✓ |
| Hierarquia | ✓ título > meta > stream |
| Uma decisão por vez no modal | ✓ (só Fechar) |
| ≤4 opções visíveis no modal | ✓ |
| Memória de trabalho | ✓ erro co-localizado ao stream |
| Progressive disclosure | n/a |

**Carga:** baixa no modal; moderada só por causa dos controles de protótipo na página.

### Estados exercitados (fonte + asserts design.md)

| Estado | Bearer | Banner | Stream | Path |
|--------|--------|--------|--------|------|
| default | `Bearer proto-admin-token` | oculto | Aguardando eventos… | ausente |
| 401 | ausente | `HTTP 401 — faça login para ver logs` | Aguardando eventos… | ausente |
| 403 | presente | `HTTP 403 — apenas admin pode ver logs` | Aguardando eventos… | ausente |

Fixture também via `?fixture=401|403` no query string — útil para review rápido.

### Acessibilidade (recorte A)

- Modal: `role="dialog"`, `aria-modal="true"`, `aria-label="Logs do Backend"`.
- Escape e backdrop fecham — paridade parcial com prod.
- Focus trap completo e “Ir para o fim” **não** demonstrados no HTML estático; Apply herda implementação React com trap e scroll assistido.
- Contraste banner âmbar `#fbbf24` sobre fundo âmbar 10%: legível em desktop; não medido em mobile real nesta sessão A.

### Responsividade (fonte CSS)

- `@media (max-width:1023px)`: sidebar/topbar ocultos, mobilebar 72px — conforme folha.
- Modal `p-4`, `max-width:64rem`, `height:85vh` — paridade Tailwind do componente.
- Breakpoints 720px para empilhamento de toolbar de protótipo.

---

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | Fixture + banner + probe deixam auth/erro observáveis |
| 2 | Match System / Real World | 3 | Copy PT-BR clara; host Combo stub |
| 3 | User Control and Freedom | 3 | Fechar/Escape/backdrop; fixture não existe no prod |
| 4 | Consistency and Standards | 4 | Modal consistente com `BackendLogViewer` |
| 5 | Error Prevention | 3 | Guard JS contra `path` no JSON simulado |
| 6 | Recognition Rather Than Recall | 3 | Labels de fixture explícitos |
| 7 | Flexibility and Efficiency | n/a | Superfície Operate modal; fixture é tooling de design |
| 8 | Aesthetic and Minimalist Design | 3 | Toolbar + probe são ruído de protótipo |
| 9 | Error Recovery | 4 | 401/403 com próximo passo (“faça login” / “apenas admin”) |
| 10 | Help and Documentation | n/a | Modal operacional sem docs inline |
| **Total** | | **30/32** | **Good (~94%)** |

Heuristics 7 e 10 marcadas `n/a` (modal Operate, não dashboard de produtividade nem docs).

---

## Persona Red Flags

### Alex (Power User / admin)

- **Fluxo:** Combo → **Ver logs** → poll simulado com Bearer.
- **Red flags:** nenhuma bloqueante. Fixture acelera review de 401/403.
- **Gap menor:** não vê **Ir para o fim** quando scroll pausado (estado não modelado).

### Jordan (First-Timer)

- **Fluxo:** abre logs sem login (fixture 401).
- **Red flags:** nenhuma — banner diz explicitamente para fazer login; stream não finge conteúdo falso.

### Sam (Keyboard / SR)

- **Red flags (P2):** trap de Tab simplificado vs componente React; erro não anunciado via `aria-live` (prod também não usa — paridade, mas oportunidade futura).

---

## Priority Issues

### P0 — Blocking

(nenhum)

### P1 — Major

(nenhum)

### P2 — Minor

- **[P2] Host Combo stub vs `ComboConfigurePage` real** — `.combo-optimize` substitui a página densa de otimização; botão **Ver logs** não usa o tratamento zinc claro (`bg-zinc-50`) do TSX. **Por quê:** Alan valida delta no contexto mínimo, não no Combo completo. **Fix:** opcional — colar bloco do botão real se T7 exigir paridade do trigger. **Comando sugerido:** `$impeccable polish` (só se escopo expandir).

- **[P2] Estado “Rolagem pausada” / Ir para o fim ausente** — protótipo fixa “Rolagem automática”. **Por quê:** feature existente do viewer não regressa no Apply (código React intacto), mas protótipo não prova esse ramo. **Fix:** adicionar fixture opcional com scroll longo + botão cyan. **Comando:** `$impeccable harden`.

### P3 — Polish

- **[P3] Copy 401/403 vs asserts curtos do design.md** — protótipo usa “…para ver logs” extra; spec OpenSpec ainda satisfeita (`HTTP 401` + indicação de login). **Fix:** alinhar texto se quiser byte-match com Validation. **Comando:** `$impeccable clarify`.

- **[P3] Scaffolding visível** — `.prototype-toolbar` e `#auth-probe` não vão para produção; úteis para T7. **Fix:** nenhum no Apply.

- **[P3] Nomes de token CSS abreviados** — `--accent` vs `--accent-primary` na folha; valores corretos, nomes divergentes só no HTML estático.

---

## What's Working

1. **Clone+delta correto no modal** — o chrome do `BackendLogViewer` (dimensões, tipografia mono, banner âmbar, título/meta) está reproduzido com fidelidade alta; o reviewer reconhece o produto imediatamente.
2. **Contrato auth observável** — três estados distinguíveis, Bearer simulado, ausência de `path`, copy de erro acionável; cumpre spec `log-viewer` sem redesign.
3. **Shell autenticado canônico** — sidebar 224px, header 80/72, nav real e tokens escuros ancoram o protótipo no workspace DEV existente.

## Overall Impression

Entrega enxuta e disciplinada: o protótipo faz exatamente o que o card promete (credencial + erros visíveis) sem reinventar o modal. Ruído limitado a controles de fixture. Maior gap é contextual (Combo stub), não estrutural no viewer.

## Questions to Consider

- O host Combo precisa de paridade pixel do botão **Ver logs** para T7, ou basta o modal?
- Vale demonstrar scroll pausado no protótipo, ou confiar no componente React já em prod?
- `#auth-probe` deve sumir antes de Aprovação de Design, ou permanece como evidência de Bearer?

---

## Audit (recorte técnico A)

| Área | Resultado |
|------|-----------|
| A11y | Parcial — dialog semântico OK; live region ausente |
| Responsive | CSS alinhado; browser real não executado nesta sessão A |
| Perf | HTML estático leve (~35 KiB) |
| Segurança UX | Sem path/host leak no DOM; probe mostra token fictício (aceitável em DEV prototype) |
| Console | design.md cita 404 residual sem impacto — não revalidado aqui |

---

## Trace

1. `design.md` — escopo, estados, digest, validation asserts
2. `index.html` — implementação clone+delta
3. `BackendLogViewer.tsx` — referência de chrome produção
4. `card-664-discovery-restore-reload/index.html` — base shell
5. `cripto-farol-token-sheet.md` — dimensões nav/tokens
6. curl DEV — digest servido = disco = packet
7. `detect.mjs` — zero findings

---

## Findings (emissão curta para pai)

### P0

(nenhum)

### P1

(nenhum)

### P2

- Host Combo stub; botão **Ver logs** não espelha zinc claro do prod — **disposition: aberto**, aceito pelo escopo delta-only no modal
- Protótipo não modela “Rolagem pausada” / **Ir para o fim** — **disposition: aberto**, fora do delta auth; Apply mantém React existente

### P3

- Copy 401/403 ligeiramente mais longa que asserts do design.md — **disposition: fechado**, spec OK
- Scaffolding `.prototype-toolbar` / `#auth-probe` — **disposition: fechado**, não vai para Apply
- Tokens CSS com nomes abreviados vs folha — **disposition: fechado**, valores corretos

### Verdict

**PASS**

Zero P0/P1 aberto. Fidelidade do modal (superfície existente alterada) satisfatória. Gaps P2 são contexto/states não cobertos pelo delta, não bloqueiam Aprovação de Design.
