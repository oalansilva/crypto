# Assessment A — card 852 · change card-852-descoberta-tres-modos

> Avaliador A isolado: mesmo modelo do chat (`muse-spark-1.3-contributor-free`), sessão
> distinta, sem transcript de ninguém, sem compartilhar resultados com B. Sem nested-spawn
> (0 subagents). Nada foi movido (Status, branch, worktree, `process_event` não tocados).
> **Sem visão neste modelo** — `read_image` rejeitado pelo runtime ("model does not declare
> image input"). Nenhuma revisão de pixels alegada: avaliação por markup integral do
> protótipo (421 linhas lidas), fonte viva `DiscoveryPage.tsx` (2287 linhas — greps +
> trechos-chave lidos, sem edição), landmarks do catálogo, briefing via `gh api` e
> forense de bytes/dimensões dos PNGs (IHDR + sha256, sem abrir pixels).

## Metadata

- card: 852 — "Descoberta — simplificar tela em 3 modos (Montar / Acompanhar / Decidir)"
- change: `card-852-descoberta-tres-modos` · branch `card-852-descoberta-tres-modos` (base develop)
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-852-descoberta-tres-modos`
- data (UTC): 2026-09-06T18-16Z
- UI impact: **affected** (layout/copy da Discovery; confirma `design.md`)
- Entradas lidas: `design.md` (51 linhas) · `proposal.md` · `tasks.md` ·
  `specs/discovery-three-modes/spec.md` (8 requirements) · `index.html` do protótipo
  (integral) · `DiscoveryPage.tsx` (só leitura) · `DESIGN.md` (autoridade, não reescrita) ·
  `scripts/process-fsm/route-landmarks.yaml` · issue 852 via `gh api` (PROIBIDO `gh issue
  view` respeitado) · snapshot do autor `.impeccable/critique/852-...-18-09Z.md` (referência)
- Escrita única permitida: este arquivo em `.impeccable/critique/**`. Todo o resto intacto.

## Fidelidade (clone da rota viva?)

Landmarks do catálogo para `/combo/discovery` (texts, selectors `[]`):

| Landmark | Rota viva (`DiscoveryPage.tsx`) | Protótipo (`index.html`) |
|---|---|---|
| `Descoberta de estratégias swing` | h1 linha 1155 ✓ (subcopy idêntica, 1156–1158) | h1 linha 110 + mesma subcopy linha 111 ✓ |
| `Preflight` | `aria-label="Preflight da varredura"` (1607) + h2 `Preflight do servidor` (1610) ✓ | `aria-label="Preflight da varredura"` (165) + h2 `Preflight` (166) ✓ |
| `Rascunho de varredura` | h2 (1443) em section `aria-label="Novo rascunho de varredura"` (1439) ✓ | article `aria-label="Rascunho de varredura"` (129) + h2 (131) ✓ |

Estrutura clonada (irmão, não cópia de HTML — bytes copiados 0, verificado por leitura):
breadcrumb Combo/Varreduras · h1+subcopy · progress card (pausar/cancelar/novo rascunho,
`role=progressbar` com aria-valuemin/max/now) · draft grid (templates/símbolos/timeframes/
período/ranking; Short desabilitado nos dois) · preflight aside · leaderboard
(sort/filter/evidência janela+candles+fees/rank estável + nota educacional) · modal
Promover (Tier 3) · seletor de run histórica (vivo) / simulador rotulado "só protótipo".
Rubrica anti-fraude: **sem** painel ANTES/DEPOIS como index ✓, **sem** galeria de estados
no lugar de lista+detalhe ✓ (há tabela real com 24 linhas + expansão), **não** é só
chrome (não há sidebar; tokens/design copiados com landmarks presentes) ✓, tabs do
protótipo **trocam markup** (`.modepanel.active` + `aria-selected` + roving tabindex +
`renderLb()` no Decidir; simulador troca painel e estado) — não é toggle cosmético ✓.
Sessão: **sem sessão de browser** (rota viva é autenticada; `/login` não contaria).
Avaliação via fonte + landmarks + forense — nenhum landmark ausente ⇒ **nenhum P0**.

Servido == local (verificado nesta sessão, duas pontas por bytes):
`https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/` → HTTP 200,
32397 bytes, sha256 `9b298054e8874fc80ebbde1d16b5cec3c896816f168bd8802c9b4034aae4ef13`
== arquivo local == digest do `design.md`. ✓

Forense dos screenshots do autor (`/tmp/card852-*.png`, IHDR + sha256, sem pixels):
6 arquivos (não 7); **todos 390 de largura** — `desktop-*` = 390×844, `mobile-*` =
780×1688 (2x DPR de 390×844). **Nenhum screenshot 1440 existe.** E
`desktop-promote.png` é **byte-idêntico** a `desktop-decidir.png` (sha256
`2db2f2cb…` nos dois) — o modal Promover não tem captura distinta. Ver A1/A2.

## Produto (aderência — 8 requirements + decisões operador)

1. **1 modo visível** ✓ (CSS `.modepanel{display:none}/.active{display:block}`).
2. **Iniciar colapsa + trava** ✓ (mock: `btn-start` → sim acomp, rascunho colapsado textual, `lb-acomp` travado; vivo já tem `draftFrozen`).
3. **Preflight 3 linhas + impedimentos, técnico em `<details>`** ✓.
4. **Leaderboard 1 ordenação + 3 risco + expansão + 12/pág** ✓ (6 `th` exatos; 24 linhas → "Página 1 de 2").
5. **Seleção inline + avançada 2 ações** ✓ (busca+contador inline; modal selecionar-filtrados/limpar+aplicar).
6. **CTA estável + bloqueio nomeando diferença** ✓ — e aqui o delta é real: o vivo
   (`LIVE_BLOCK_COPY`, linha 216-217) tem mensagem única sem diferença e sem link; o
   protótipo tem mesmo-escopo vs outro-escopo + "ver progresso" ✓.
7. **Promoção risco lado a lado + Tier 3 + Favoritos** ✓ (4 campos + destino + confirmação
   citando Favoritos → Tier 3; reversibilidade textual).
8. **Short escondido consistente** ✓ (rascunho + filtros sem short; decisão operador 2026-09-06).
Decisões operador fechadas respeitadas: Iniciar domina (CTA full-width vs Promover
secundário por linha), Short escondido. Problema/usuário/hipótese/valor explícitos no
`design.md`; hipótese falsificável sem tocar motor/ranking/elegibilidade ✓.
Gaps de fusão no apply: modal do protótipo **omite** Descartar por linha, estados
dedup (`duplicate`/`already_promoted`), bloco 409 e nota de revalidação sob lock do vivo
→ ver P1-F1. Problema de vocabulário residual: ver P2-F2.

## UX

Hierarquia h1 → tabs → 1 painel; CTA dominante único por modo; carga cai de ~7 blocos e
13 colunas para 1 modo e 6 colunas ✓. Fluxo completo clicável no mock (montar → acomp
→ decidir → promover; "novo rascunho" e "ver progresso" voltam) ✓. Prevenção: CTA
desabilitado + impedimentos acionáveis; bloqueio distingue os dois casos ✓.
Recuperação: modais fecham por ✕/Voltar/Esc/overlay, foco retorna ao gatilho ✓.
Gaps: estado vazio de filtro sem mensagem (P2-F3); parciais do Acompanhar estáticas
top-5 sem contagem (P2-F4); cancel do mock pula a confirmação do vivo (P3-F7).

## Acessibilidade (markup)

Tabs com tablist/tab/tabpanel + `aria-controls` + setas + roving tabindex +
`:focus-visible` global ✓; progressbar ARIA completa ✓; modais `dialog`+`aria-modal`+
traps de Tab + Esc + `lastFocus` ✓; `aria-live` no preflight e paginação,
`role=alert` no bloqueio, `role=status` na confirmação ✓; botões ícone com
`aria-label="Fechar"` ✓; expansões com `aria-expanded` ✓; buscas com label associado ✓;
tabelas em `role=region` com `tabindex=0` + `caption` de rank estável ✓; alvos ≥44px ✓.
Pares de contraste são os tokens do vivo/DESIGN.md (nenhum par novo além de alertas
âmbar no mesmo padrão do vivo) ⇒ sem regressão introduzida no mock; regressão real só
se o apply quebrar — tasks 1.2 e req 8 cobrem. Vocabulário residual (P2-F2) afeta
clareza para leitor de tela no caminho feliz.

## Responsividade (markup, sem pixels)

`grid2` 1fr+330 ≥1024px, 1 coluna abaixo; filtros 4 cols ≥768px, 2 cols abaixo; tabela
com scroll horizontal acessível por teclado; `.risk` 2 cols no 390px (denso porém
legível — concordo com A3 do autor); modais `max-height:90vh` com scroll interno;
listas inline com `max-height` + scroll ✓. Composição desktop 1440 **não verificável por
pixels** (ver A1) — por markup, sem risco estrutural (max-width 1480, breakpoints
consistentes com o vivo).

## Estados (vivo → protótipo → apply)

| Estado | Vivo | Protótipo | Apply deve… |
|---|---|---|---|
| loading (preflight/LB/recovery) | ✓ | ausente (mock estático) | preservar código vivo |
| vazio (0 candidatos no filtro) | ✓ "Nenhum candidato…" | **tbody vazio sem mensagem** (P2-F3) | adicionar mensagem |
| erro (preflight/start/LB/retry) | ✓ | ausente | preservar |
| sucesso (promoção/toast) | ✓ toast | ✓ mensagem + confirmação | fundir (toast do vivo) |
| permissão negada 403 | ✓ painel | ausente | manter fora do switch (P1-F1) |
| dado obsoleto (stale+revalidar) | ✓ | estático "Snapshot válido" | preservar bloco stale |
| rework (cancel confirm, 409) | ✓ | pulado no mock | preservar (P1-F1) |
| sessão expirada | ✓ painel | ausente | manter fora do switch |

## Achados com disposition

- **P0 — nenhum.** Todos os landmarks presentes; sem ANTES/DEPOIS, sem galeria, sem
  chrome-só, sem toggle-cosmético. (disposition: n/a)
- **P1-F1 — Fusão apply pode regredir Descartar/dedup-409/stale-403.** O protótipo
  (correto como mock de delta) omite: botão Descartar por linha + copy destrutiva,
  estados `duplicate`/`already_promoted`, bloco 409, nota de revalidação sob lock, painel
  403, bloco stale, sessão expirada. Se o apply seguir o mock literalmente, há regressão
  de honestidade evidencial. (disposition: **aclarar no apply antes de codar** — tasks
  1.1/5.1 + req 8 passam a listar explicitamente "preservar Descartar, dedup/409,
  stale, 403, sessão expirada fora do switch de modos"; desvio sem registro = bloqueio
  pelo próprio contrato do `design.md`.)
- **P1-A1 — Evidência desktop 1440 inexistente.** `design.md` §Prototype Validation
  alega "desktop 1440×900 (5 screenshots)"; os 4 arquivos `desktop-*` têm IHDR 390×844
  e só há 6 arquivos (não 7). Composição desktop segue não-revisada por pixels.
  (disposition: **recapturar pré-Aprovação de Design** — 1440×900 reais dos 3 modos +
  mobile; ou registrar escopo aprovado só-markup com revisão humana de pixels no apply.)
- **P1-A2 — Modal Promover sem captura distinta.** `desktop-promote.png` ≡
  `desktop-decidir.png` (mesmo sha256). (disposition: **recapturar com modal aberto**
  junto com A1.)
- **P2-F2 — Jargão residual no caminho feliz.** `Snapshot válido` (eyebrow do Preflight,
  Montar) e chip `RUNNING` (Acompanhar) violam o vocabulário do próprio card (`_Avoid:
  snapshot, run…`); o gate do autor não incluía `snapshot`/`run` na regex. O `<details>`
  técnico está correto. (disposition: **trocar no apply** — ex.: "Pronto para iniciar" /
  "Conferido pelo servidor" e chip "EM EXECUÇÃO"; manter `snapshot` só no `<details>`.)
- **P2-F3 — Filtro zerado sem mensagem.** `renderLb()` com 0 linhas gera `tbody` vazio
  (só "0 de 24 candidatos" no contador); o vivo tem `empty-state` amigável.
  (disposition: **adicionar no apply** — mensagem + "Limpar filtros".)
- **P2-F4 — Parciais do Acompanhar indefinidas.** `lb-acomp` mostra top-5 estático sem
  contagem/paginação; o comportamento de parciais travadas no sweep em curso precisa de
  definição (o vivo deriva o leaderboard do `viewSweep`, separado do ativo).
  (disposition: **definir no apply**, task 1.1.)
- **P3-F5 — 12/pág é placeholder.** Dentro de 10–15, com confirmação técnica pendente
  (custo do 3 atual) — já registrado no `design.md`; só reforço. (disposition: confirmar
  no apply, task 3.1.)
- **P3-F6 — Micro-copy.** `href="#"` em `#lnk-prog` (só mock); "CAGR vs B&H" vs "CAGR vs
  Buy & Hold" do vivo; cancel do mock sem confirmação. (disposition: alinhar no apply;
  manter confirmação e copy destrutiva do vivo.)
- **P3-F7 — Copy `leases` preservada no vivo** (cancel confirm, linha 1371) — jargão,
  mas fora do escopo do card e protegida pela cláusula "manter copy destrutiva".
  (disposition: **aceitar**, informativo.)

## Nielsen (resumo tabular)

| Heurística | Avaliação |
|---|---|
| Visibilidade de estado | 1 modo + chip + progresso ARIA; simulador rotulado "só protótipo" ✓ |
| Jargão / mundo real | Quase limpo; ressalva P2-F2 (`Snapshot válido`, `RUNNING`) |
| Controle e liberdade | ver progresso / novo rascunho / limpar filtros / Esc / overlay ✓ |
| Consistência | Short escondido nos dois lugares; rank estável com caption ✓ |
| Prevenção de erro | CTA desabilitado + impedimentos; bloqueio nomeia diferença ✓ |
| Reconhecimento | 3 linhas + resumo de risco lado a lado + onde-ver-depois ✓ |
| Estética/minimalismo | 3 colunas de risco, resto em expansão; 12/pág ✓ |
| Ajuda/recuperação | Falta vazio-amigável (P2-F3); erros do vivo fora do mock (P1-F1 cobre apply) |
| Acessibilidade/estados | Sem regressão no mock; estados do vivo preservados via P1-F1 |

## Veredito parcial do Design Agent: **PASS (condicional)**

O protótipo demonstra os 8 requirements + as 2 decisões do operador em markup
observável, clona os 3 landmarks, respeita tokens/DESIGN.md e bate byte-a-byte com o
servido. Nenhum P0. Condições (não-corretivas do mock, corretivas do processo/apply):
recapturar evidências desktop + modal (P1-A1/A2) antes ou como condição da Aprovação de
Design; fundir estados do vivo no apply sem regressão (P1-F1); copy sem jargão + vazio
amigável + parciais definidas (P2). Sem revisão de pixels (modelo sem visão) — aprovação
humana deve incluir passada visual nos viewports recapturados.

## Pendências (fora do meu escopo de escrita)

1. Recaptura 1440×900 (3 modos) + modal Promover distinto + passada visual humana.
2. Aprovação de Design (Alan) — Status não movido por este assessor.
3. Apply somente após `Status=Pronto para Dev` (T8), com P1-F1/P2 como checklist.
