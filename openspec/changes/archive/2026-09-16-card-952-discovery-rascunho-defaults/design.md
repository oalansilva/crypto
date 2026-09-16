UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 952: rascunho novo sem Templates nem Símbolos, Time Frames em 1 dia

## Context

Card [#952](https://github.com/oalansilva/crypto/issues/952). Briefing = issue grelhado. Sem reentrevista.

Hoje `/combo/discovery` em modo Montar, ao carregar o catálogo num rascunho que não é restore, pré-escolhe os primeiros templates e os primeiros símbolos; Time Frames inicia em 4 horas + 1 dia. O botão «Novo rascunho» libera o configurador mas **não** limpa a seleção. Restaurar uma varredura já gravada reaproveita os eixos gravados; o fallback actual de Time Frame vazio cai em 4 horas + 1 dia.

**Audience:** operador que abre a Descoberta para montar a varredura do zero.
**Outcome:** rascunho novo sem pré-escolha; único default = 1 dia; início continua bloqueado até haver 1 template e 1 símbolo.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** modo Montar, rascunho novo e restore. Sem Combo, catálogo, preflight/limite/promoção, redesenho.

Regiões clonadas (só estas): shell AppNav; modo Montar; cartões Templates / Símbolos / Time Frames; painel Preflight «Falta fazer».

## Goals / Non-Goals

**Goals:**

- Rascunho novo (primeira abertura ou «Novo rascunho»): Templates 0, sem chips; Símbolos 0, sem chips; Time Frames só **1 dia** marcado, **4 horas** desmarcado.
- «Falta fazer» visível no rascunho novo (falta template e símbolo); início não dispara varredura vazia.
- Operador ainda marca templates, símbolos e 4 horas depois, como hoje.
- Reabrir varredura já gravada traz o que estava marcado; não aplica estes defaults por cima.

**Non-Goals:**

- Tela Combo.
- Mudar o catálogo de templates ou a lista de símbolos.
- Mudar regras de preflight, limite de combinações ou promoção.
- Redesenhar o layout das três opções.
- Direção, período e métrica de ranking: ficam como hoje.

## Decisions

### 1. Defaults novos só no rascunho novo

Primeira abertura e «Novo rascunho» partilham o mesmo estado: seleção vazia + Time Frames `1d`. Não é um preset de catálogo; é ausência de pré-escolha.

Rejeitado: manter os primeiros do catálogo e só desmarcar 4 horas. Rejeitado: vazio também em Time Frames (o único default pedido é 1 dia).

### 2. «Novo rascunho» passa a limpar

Hoje o botão só `setDraftFrozen(false)` e volta a Montar. Neste card aplica os defaults novos: zera Templates/Símbolos/`committedSelection` e Time Frames só 1 dia. Direção, período e ranking não são resetados por este card.

Rejeitado: novo botão noutro sítio do Montar como produto (o proto expõe o controlo no header do rascunho só para o gate; Apply mantém o sítio vivo — Acompanhar / rascunho colapsado).

### 3. Restore não recebe overlay

`hydrateFromSweep` continua a copiar `axes.templates`, `axes.symbols` e `axes.timeframes` gravados. Não corre os defaults de rascunho novo por cima. Se `timeframes` vier vazio, **não** cair em `['4h', '1d']` — deixa o eixo vazio e o aviso já existente («Selecione ao menos um timeframe.») fala.

Rejeitado: fallback 4h+1d «por segurança». Rejeitado: forçar 1 dia em cima de um restore mudo.

### 4. Mecanismo (como, não Q)

O catálogo hoje aplica `flat.slice(0, 3)` e `list.slice(0, 4)` quando `skipCatalogDefaultsRef` é falso; Time Frames nasce `['4h','1d']`; restore põe o skip a true e reaproveita eixos, com fallback `['4h','1d']` se o eixo vier vazio. Apply: não pré-escolher quando o rascunho é novo; estado inicial `['1d']`; `newDraft` limpa; restore sem TF não inventa 4h+1d. Aceite observável = grelha do issue.

## Risks / Trade-offs

- [Risco] Operador habituado à pré-escolha achar a tela «quebrada» porque «Falta fazer» aparece logo → Mitigação: consequência explícita na grelha; o aviso já existe e nomeia o que falta.
- [Risco] «Novo rascunho» apagar uma selecção que o operador ainda queria reutilizar → Mitigação: o pedido fecha este comportamento; a varredura anterior continua no histórico.
- [Risco] Restore antigo sem Time Frame ficar sem eixo marcado → Mitigação: melhor que inventar 4h+1d; o aviso de timeframe vazio já existe; início continua bloqueado.

## Migration Plan

Sem schema. Rollback = repor pré-escolha dos primeiros itens, default `['4h','1d']` e `newDraft` sem limpar. Catálogo e preflight intactos.

## Open Questions

Nenhuma. Defaults, restore e fora fechados na grelha. O *como* (não overlay no restore; sem fallback 4h+1d) está nas decisões acima.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Rascunho novo: 0 templates, 0 símbolos, só **1 dia** marcado, **4 horas** desmarcado.
- «Falta fazer» visível; início bloqueado; não dispara varredura vazia.
- Operador ainda marca templates, símbolos e 4 horas depois.
- Restore traz o gravado; não aplica estes defaults por cima.
- Direção, período e ranking iguais ao vivo. Layout das três opções não redesenhado.

**P3 aceito (Apply):** deixar de pré-escolher no `useEffect` do catálogo (não `slice(0, 3)` / `slice(0, 4)` em rascunho novo); `useState` inicial de Time Frames `['1d']`; `newDraft` zera seleção + `committedSelection` e aplica `['1d']` (sítio vivo do botão permanece Acompanhar / rascunho colapsado); `hydrateFromSweep` sem fallback `['4h','1d']`; testes que ainda afirmam 3 templates / 4 símbolos / 4h+1d no rascunho novo.

## Recorte

- **Audience:** operador a montar uma varredura do zero na Descoberta.
- **Outcome:** rascunho novo vazio, só 1 dia marcado; restore intacto.
- **Direction:** clone da rota viva `/combo/discovery` + delta de defaults; Operate; sem new-work.
- **Scope:** Montar (Templates, Símbolos, Time Frames, Preflight). Acompanhar/Decidir só chrome de modos, sem delta.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/
- Path: `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html`
- Digest: `eab36595d3bc5548` (sha256 completo `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5`).
- Base: clone de `/combo/discovery` (shell AppNav HEAD + modo Montar vivo com os três cartões e Preflight). Arranque visual a partir do chrome do proto irmão `card-948-discovery-deleted-favorite`; cartões Montar alinhados a `DiscoveryPage.tsx`. Sem painel ANTES/DEPOIS. T5 mede só este `index.html`.
- Landmarks (catálogo HEAD, substring): «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Clone vs delta: COPIED = shell AppNav, modo Montar (heading + tabs), cartões Templates / Símbolos / Time Frames, painel Preflight «Falta fazer». DELTA = 0 templates, 0 símbolos, só 1 dia marcado, 4 horas desmarcado, aviso visível, início bloqueado. Restore = irmão `restore.html` (3 templates, 4 símbolos, 4h+1d gravados — nunca URL canónica).
- Estado default: rascunho novo em Montar.

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/
- Path: `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html`
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://, não curl).
- Disco == HTTPS: sha256 `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` (32337 bytes). `clone_gate_ok` local True. Rota viva sem sessão → `/login` (não conta como a rota).
- Ações: default Montar (rascunho novo) → marcar 4 horas → marcar 1 template e 1 símbolo → «Novo rascunho» (volta aos defaults).
- Asserts (35/35 PASS nos dois viewports): landmarks «Descoberta de estratégias swing» / Preflight / Rascunho de varredura; 0 templates / 0 símbolos / sem chips; só **1 dia** marcado; **4 horas** desmarcado e marcável; «Falta fazer» visível; início desactivado; cartões Templates / Símbolos / Timeframes swing reconhecíveis; Direção Long, período Todo o histórico, ranking Calmar; após marcar 1+1 o aviso some e o início habilita; «Novo rascunho» restaura os defaults; 0 console/pageerror. Irmão `restore.html`: 3 templates, 4 símbolos, 4h+1d, aviso escondido (5/5).
- Pares `COPIED:start`/`COPIED:end`: 6/6, soma UTF-8 9899 (> 0). T5 mede só este index.html.
- Detector `detect.mjs`: advisory `em-dash-overuse` (copy viva `Iniciar varredura —`); sem P0/P1.
- Resultado do gate do autor: asserts verdes. Sem emitir PASS de T5 (pai após A/B).

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B; sem rework (zero P0/P1 de produto).

- Autor: [design-autor 952](e2ed5954-c23d-4880-849e-d4d6b0986206) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 952](cb0a8d1a-ae6e-4c8d-ab5f-e85387a5dd8c) isolado; `model: cursor-grok-4.6-high`.
- Assessment B: [Assessment B 952](dc6341b0-4d06-4b09-b5b1-17beeb08f0e9) isolado; `model: cursor-grok-4.6-high`.
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/

P3 aceite (detalhe de Apply, não reabrir como P0/P1): sítio vivo de «Novo rascunho» (Acompanhar / rascunho colapsado, não o header do gate); `slice`/`useState(['1d'])`/`newDraft`/`hydrate` sem fallback 4h+1d; tabs Acompanhar/Decidir disabled no mock; Preflight abaixo da dobra em 390; segmentos 4h/1d com input 0×0; em-dash da copy viva.

### Proxies

- `design.md` words: 1476
- HTML generated vs copied: 22438 vs 9899
- Spawns: 3
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
