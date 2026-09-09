# Assessment A — card 876 · change card-876-discovery-amostra-insuficiente

> Avaliador A isolado (produto / UX / a11y / fidelidade). Mesmo modelo do chat. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, backend, `frontend/src` ou OpenSpec. Única escrita: este arquivo.

## Metadata

- card: 876 — "Descoberta: varredura não deve gastar minutos em par sem histórico suficiente"
- change: `card-876-discovery-amostra-insuficiente`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-876-discovery-amostra-insuficiente`
- data (UTC): 2026-09-09T0005Z
- UI impact (rubrica): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` · 33203 bytes
- Servido HTTPS == local: IDENTICAL (`cmp` limpo)
- Folha de tokens: path `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` **ausente neste worktree**; chrome lido via `DESIGN.md` (não reescrito) + `frontend/src/index.css` + folha-irmã card-720. Folha = chrome; **não** substitui landmarks.
- Issue: REST `gh api repos/oalansilva/crypto/issues/876` (não `gh issue view`). Grelha fechada; não reaberta.

## Limitação de sessão (obrigatória)

Playwright Chromium 1243 (`executable_path` cache ms-playwright arm64), viewport 1440×900:

| URL pedida | URL final | Landmarks `/combo/discovery` |
|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0/3 |
| `https://criptofarol.com.br/combo/discovery` | `https://criptofarol.com.br/login` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTP, (2) HTML local, (3) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

## Tokens parseáveis (rubrica)

`design.md` linhas próprias:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa não vazia no corpo (clone+delta da rota existente; Acompanhar fórmula + Decidir linha). **PASS** deste item da rubrica.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` texts (selectors `[]`):

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto `index.html` + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 L1317 + subcopy 4h/1d L1318–1320 | h1 visível no default; exact count 1, `first_visible=true` |
| `Preflight` | h2 L1919 · `aria-label="Preflight da varredura"` L1916 | h2 + `aria-label="Preflight da varredura"`; hidden no default Acompanhar (igual ao vivo com live sweep); **visível após tab Montar** |
| `Rascunho de varredura` | h2 L1759 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-876-discovery-amostra-insuficiente/` → `index.html` é a página (shell + heading + 3 modos + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `get_by_text('ANTES')` deu 1 por substring case-insensitive em «o servidor confere **antes** de iniciar» — falso positivo, não galeria.
- Não é grelha de N estados no lugar de lista+detalhe. Decidir é tabela de candidatos (4 linhas mock, incluindo a delta).
- Tabs trocam markup (`.modepanel.active` + `aria-selected`); não é `aria-pressed` cosmético.

Chrome presente (sidebar 224px, Inter, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Descoberta ativa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Digest: local `a128a598…` == HTTPS 200 33203 bytes == digest do `design.md` / prompt do autor.

PNGs do autor `/tmp/card876-gate`: desktop 1440×900 (acomp/montar) e 1440×1058 (decidir full-page); mobile 390×844 (acomp/montar) e 404×2287 (decidir full-page). Distintos entre modos (não byte-idênticos).

## Produto (escopo — não reabrir grelha)

Delta pedido: progresso com `W amostra insuficiente`; Decidir linha sem rank; selo `Amostra insuficiente` ≠ `Baixa amostra`; métricas N/A; sem Promover; clone da página viva.

| Aceite visível | Evidência proto (Playwright + pixels) | Disposition |
|---|---|---|
| Fórmula `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente` | `18 processadas = 12 sucesso + 1 falha + 1 ignoradas + 4 amostra insuficiente` (`data-testid=counter-invariant`); 12+1+1+4=18 | OK |
| Top-5 Acompanhar **não** inclui amostra insuficiente | `partials_has_insufficient=false`; ranks 1–5 com Calmar numérico | OK |
| «1 por sweep» inalterado | «Limites: 8 global · 1 por sweep · fila justa» visível | OK |
| Decidir: linha existe, rank `—`, selo `Amostra insuficiente` (não `Baixa amostra`) | `data-testid=row-insufficient`; `.rank` = `—`; seal exact; `row_has_baixa=0` | OK |
| Calmar / Max DD / Trades = N/A | 3× `N/A` exact na linha (desktop e mobile 390) | OK |
| **Sem** controlo Promover (não basta desabilitar) | `promote_in_row=0`; só `Excluir`; página ainda tem 2× Promover nas elegíveis | OK |
| Vizinho `Baixa amostra` intacto (pós-grid) | selo + botão desabilitado «Baixa amostra»; Calmar 3,20; 18 trades — vocabulário não misturado | OK |
| Não entra: redesign 3 modos / 1 por sweep / Calmar de par com histórico cheio | 3 tabs Montar/Acompanhar/Decidir preservados; limite 1 por sweep no chrome; BTC/ETH com Calmar cheio | OK |

Não-goals de motor (claim-time, split 70/30, persistência `insufficient_sample`, reconcile completed) são contrato de Apply, não tela — P3 se citados.

## UX

Hierarquia h1 → tablist 3 modos → 1 painel. Default Operate = Acompanhar em curso (cena do incidente PROD). Quarto termo na **mesma** linha de progresso: um glance, sem painel extra. Decidir: a linha BLZ lê-se no mesmo padrão da baixa amostra (rank travado, selo amber, ações à direita) com duas diferenças óbvias (N/A vs números; ausência de Promover vs botão morto «Baixa amostra»). Isso reduz mistura de vocabulário.

Carga cognitiva: fórmula de 4 sacos = +1 cláusula na linha já viva; ainda <4 decisões visíveis no glance do Acompanhar (Pausar / Cancelar / Novo rascunho). Na linha insuficiente, 1 ação (Excluir). Tablist = 3.

Prevenção: impossível promover a linha cortada (CTA ausente). Recuperação: Excluir presente (inspectável, como hoje); mock sem modal de confirmação do vivo.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; alvos ≥44px; `prefers-reduced-motion`.
- Tablist/tab/tabpanel + `aria-controls` + roving tabindex + setas (ArrowRight a partir do **selecionado**, não do focado — paridade com o vivo #852).
- `role=progressbar` com valuemin/max/now; região de tabela `tabindex=0`.
- Selo é texto visível na célula candidato (lê-se no SR); linha tem `data-testid`.
- Gaps vs vivo (P3): `Excluir` sem `aria-label` com `result_id`; sem `sr-only` a explicar ausência de Promover (o selo na mesma linha cobre o significado); Montar sem CTA Iniciar (fora do delta).

Contraste: pares Binance do `DESIGN.md` / selo amber idêntico a `.sample-badge` do vivo (`rgba(245,158,11,.35)` / `#fbbf24`). Sem par novo inventado.

## Responsividade

Desktop 1440: fórmula e linha Decidir legíveis; ações à direita. Mobile 390: tablist 3 colunas; tabela vira cards `data-label`; linha insuficiente permanece com `—`, selo, 3× N/A, só Excluir full-width. Header mobile 72px (folha). Sem overflow bloqueante observado no PNG.

## Estados

Mock cobre: Acompanhar em curso com W>0; Montar rascunho (landmarks); Decidir misto (elegível / baixa amostra / amostra insuficiente). Não mocka: loading/erro de leaderboard, vazio, sweep só-W concluído (`EM CURSO` vs `CONCLUÍDA`), sessão expirada. O aceite «varredura só com listagem curta conclui» é sobretudo reconcile/chip já vivo — P3 de cobertura de mock, não buraco de contrato visível do delta.

## Design specificity

A composição é da Descoberta (modos #852, fórmula de progresso, leaderboard Calmar, selo amber de amostra). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate**.

## Heurísticas Nielsen (0–4, Operate; snapshot only)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + 18/24 + 4 sacos |
| 2 | Match between system and real world | 4 | Vocabulário da grelha (amostra insuficiente ≠ baixa amostra) |
| 3 | User control and freedom | 3 | Pausar/Cancelar/Excluir; cancel confirm do vivo omitido no mock |
| 4 | Consistency and standards | 4 | Mesmo padrão de leitura da baixa amostra; palavras distintas |
| 5 | Error prevention | 4 | Promover ausente na linha cortada |
| 6 | Recognition rather than recall | 4 | Selo na linha; N/A nas colunas já nomeadas |
| 7 | Flexibility and efficiency | 3 | Filtros/paginação do Decidir vivo omitidos |
| 8 | Aesthetic and minimalist design | 3 | Montar esquelético vs vivo; Promover outline vs fill amarelo |
| 9 | Help users recognize/recover errors | 3 | Sem modal Excluir; sem estado erro |
| 10 | Help and documentation | 3 | Nota educacional do leaderboard; sem glossário extra do 4.º saco (a fórmula já nomeia) |

## Cognitive load

- Checklist: hierarquia 1 h1; 1 modo visível; fórmula numa linha; delta localizado. **Pass**.
- Pontos de decisão visíveis >4: não no glance do Acompanhar (3 CTAs + tabs). Decidir por linha elegível = 2 (Promover/Excluir); insuficiente = 1. **Pass**.

## Emotional journey

Vale (espera de minutos em BLZ) → pico (W aparece em segundos na fórmula, top-5 limpo) → fim (Decidir mostra o par, sem Calmar falso, sem promover). Reassegurança: vizinho `Baixa amostra` continua a existir para quem já rodou o grid.

## Personas (2–3)

1. **Admin da varredura grande (PROD, VPS 4 cores):** precisa ver que pares mortos não estão em «sucesso». A fórmula de 4 termos e o top-5 sem W resolvem o glance do Acompanhar.
2. **Admin no Decidir:** precisa distinguir listagem curta (sem otimização) de evidência fraca pós-grid. Selo + N/A + ausência de Promover vs botão «Baixa amostra» com números.
3. **Admin teclado / SR:** tabs e selo textual funcionam; nome acessível do Excluir é mais fraco que o vivo (P3).

## Strengths

- Clone estrutural da rota (heading + 3 modos + progresso + leaderboard), não galeria.
- Delta mínimo e legível no sítio certo (fórmula + uma linha).
- Vocabulário da grelha respeitado; não-goals visíveis respeitados (1 por sweep; modos não redesenhados).

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar comprimido vs vivo: sem Iniciar varredura, workbench «Edição avançada», checkboxes 4h/1d, período/ranking, impedimentos/`<details>` técnicos. Landmarks Preflight + Rascunho presentes. Não é redesign dos 3 modos; Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** Decidir omitiu filtros, paginação, `+ detalhes`, modais Promover/Excluir e `aria-label` do Excluir com `result_id`.
- **P3-3** Promover das linhas elegíveis é outline transparente; vivo é fill `--accent-primary` / texto `#181a20` (`DESIGN.md` CTA amarelo).
- **P3-4** Contagem mock «16 de 16 candidatos» com 4 `<tr>`; estado terminal só-W (`CONCLUÍDA`, 0 sucesso + N amostra insuficiente) não mockado.
- **P3-5** CSS vars do proto (`--accent`, `--border`) vs folha (`--accent-primary`, `--border-default`); valores hex batem Binance.
- **P3-6** Chip vs texto do selo: mesmo `.sample-badge` amber (aceite da grelha = Apply).
- **P3-7** Setas do tablist avançam pelo tab **selecionado**, não o focado (paridade #852).

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Sem galeria/ANTES-DEPOIS como index. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.
