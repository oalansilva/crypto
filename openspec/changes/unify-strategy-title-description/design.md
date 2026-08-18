# Design: Identidade pública editável no Combo

## Status do gate

- Card: `#549`
- Change: `unify-strategy-title-description`
- Status observado: `Design` (retorno de `Pronto para Dev` — design anterior obsoleto)
- **UI impact: affected** — lápis/edição inline no resultado Combo (admin) + hierarquia título + descrição em Descoberta, Favoritos e Monitor
- Aprovação humana: pendente. Este artefato não autoriza implementação.
- Decisões Alan 2026-08-18: catálogo **global**; edição no **resultado do Combo**

## Problema

Duas fricções no mesmo reconhecimento da estratégia:

1. **Leitura fragmentada.** Combo já mostra nome público + descrição. Descoberta usa `template_id` cru; Favoritos empilha linha intermediária; OpportunityCard rotula `estratégia` / `descrição`.
2. **Copy travada no código.** Mapas em `strategy_descriptions.py`; `combo_templates.description` ignorado quando há mapa; sem `display_name` persistido; `ComboEditPage` bloqueia prebuilts `is_readonly`. Alan não consegue ajustar o texto público e ver o mesmo texto em Descoberta, Favoritos e Monitor.

## Usuário e contexto

- **Editor:** admin no resultado Combo, após validar backtest. Quer corrigir título e tese em linguagem de trader sem clonar template.
- **Leitor:** admin e usuário comum nas outras telas. Só leem; não veem lápis.
- Desktop-first; mobile Combo com input + textarea + Salvar/Cancelar sem clip.

## Hipótese

Se o Combo resultado for a superfície de edição **e** as outras telas consumirem o mesmo resolvedor (banco > mapa > fallback), uma alteração de Alan no Combo passa a ser a identidade da estratégia em todo o produto.

## Resultado esperado

- Admin vê lápis no bloco `combo-result-summary` (título + descrição).
- Salvar persiste no catálogo global; próximo fetch em Descoberta/Favoritos/Monitor mostra o texto novo.
- Descoberta: `display_name` + `description`; modal promover igual; `template_id` só em meta.
- Favoritos: um título + descrição; apelido só como meta se diferente.
- Monitor: lista e detalhe sem prefixos `estratégia` / `descrição`.
- Fallback sem mapa: nome cru + descrição segura; título nunca `Estratégia Cripto Farol`.
- Redaction preservada; chave técnica só em meta para admin.

## Não objetivos

- Reescrever mapas Python um a um.
- Apelido por usuário.
- Editar indicadores/schema/JSON pelo lápis.
- Redesenhar `ComboEditPage`, Home ou ChartModal.
- Ranking, promoção, dedup, walk-forward (#472).

## Base visual e fidelidade

Protótipo clona shell autenticado (sidebar 224 px, header 80 px, tokens canvas `#0b0e11`, card `#181a20`/`#1e2329`, CTA `#fcd535`).

**Combo:** clonar bloco `data-testid="combo-result-summary"` de `ComboResultsPage.tsx` — badges símbolo/TF/direção, `h1` 2xl/3xl, descrição `text-sm leading-6 max-w-3xl`, grid de métricas. Delta = lápis 44 px + edição inline.

**Descoberta / Favoritos / Monitor:** delta de hierarquia do protótipo existente; texto sincronizado após save no Combo.

## Decisões de produto e contrato

### 1. Hierarquia única (leitura)

Título público + descrição pública. Metadados abaixo, nunca no título.

### 2. Fonte canônica com override

Prioridade: (1) `combo_templates.display_name` / `description` não vazios; (2) mapas Python; (3) fallback seguro. Chave técnica não muda.

### 3. Superfície de edição

Só resultado Combo. Um lápis → modo edição com input + textarea → Salvar/Cancelar. Admin only (`isAdmin`); API 403 para não-admin.

### 4. Readonly vs identidade

`is_readonly` bloqueia PUT técnico; endpoint `PUT .../identity` aceita prebuilt.

### 5. Validação

Título obrigatório (teto ~120); descrição obrigatória (teto 500); sem promessa de retorno.

### 6. Copy longa

`overflow-wrap: anywhere`; título dominante.

## Interação Combo (delta)

**Leitura (admin):** `h1` + botão lápis (`aria-label="Editar nome e descrição da estratégia"`, 44×44) + descrição.

**Edição:** input substitui `h1`; textarea substitui parágrafo; Salvar (`#fcd535`) / Cancelar; Escape cancela.

**Estados:** leitura, edição, saving, validação vazia, erro API, sucesso, não-admin sem lápis, mobile 390.

**data-testid:** `combo-edit-identity`, `combo-identity-title-input`, `combo-identity-description-input`, `combo-identity-save`, `combo-identity-cancel`.

## Impeccable Brief

- **Problema:** identidade ilegível entre telas + copy não editável.
- **Usuário:** admin corrige tese no Combo; traders leem nas outras telas.
- **Resultado:** um texto, quatro superfícies; edição onde a identidade já é padrão visual.
- **Direção:** Operate / refinamento mínimo — shell intacto; lápis + inline; outras telas só hierarquia.
- **Escopo:** Combo resultado; Descoberta leaderboard + modal; Favoritos desktop/mobile; Monitor lista + detalhe.
- **Estados:** leitura, edição, save ok, 403/oculto, copy longa, fallback, apelido favorito, Monitor expandido.
- **Interação:** lápis → campos → Salvar; tabs do protótipo mostram paridade pós-save.
- **Restrições:** DESIGN.md read-only; redaction preservada.

## Prototype

- **URL navegável:** `https://dev.criptofarol.com.br/prototypes/unify-strategy-title-description/`
- **Path versionado:** `frontend/public/prototypes/unify-strategy-title-description/index.html`
- **Base:** shell Combo/Descoberta/Favoritos/Monitor atuais.
- **Delta v2:** aba **Combo** default; lápis; save atualiza texto nas outras abas.
- **Cenários:** mapeado; fallback; apelido; edição Combo; validação vazia.

## Prototype Validation

- **URL:** https://dev.criptofarol.com.br/prototypes/unify-strategy-title-description/
- **Viewports:** desktop 1280×900, mobile 390×844
- **Comando:** Playwright headless (Chromium) contra URL DEV servida
- **Ações/asserts:**
  - Combo: `combo-edit-identity` → editar → `combo-identity-save` → `combo-result-title` atualizado
  - Paridade: após save, `discovery-strategy-title`, `favorites-strategy-title`, `monitor-row-strategy-title` iguais ao Combo
  - Não-admin: toggle admin desmarcado → lápis oculto
  - Estados extras no protótipo: saving (700ms), erro API (descrição contém `erro-api`), validação vazia, cenários mapped/fallback/alias
  - Monitor: detalhe expandido sem prefixos `estratégia`/`descrição`
- **Resultado:** verde, zero erros de página (2026-08-18)

## Impeccable Critique

**Assessment A/B (Task isolada, inherit, read-only):** direção de produto sólida; fidelidade ao bloco `combo-result-summary` boa; paridade pós-save demonstrada. Achados P1 corrigidos no protótipo v2: microcopy escopo global, toggle não-admin, ARIA básica no formulário, apelido em Favoritos no cenário alias, Escape no modal, estados saving/erro simulados. P2 aceito: detalhe Monitor simplificado vs OpportunityCard completo (implementação segue spec).

## Impeccable Audit

A11y: lápis 44px, `aria-label`, `aria-invalid`/`aria-describedby`, `role="status"` no save-note, Escape fecha modal, tabs com teclado. Responsivo: 1080/720, combo grid 1 col mobile, ações empilhadas. **Aceito** com P2 documentado (labels visíveis opcionais na implementação).

## Impeccable Trace

- Target: `frontend/public/prototypes/unify-strategy-title-description/index.html`
- Change: `unify-strategy-title-description` · card #549
- Browser gate: Playwright Chromium @ DEV URL, desktop + mobile, paridade + não-admin verdes
- Crítica isolada: Task inherit, read-only (2026-08-18)

## Design Critique

Design anterior (só leitura) **obsoleto**. Escopo v2: edição Combo + catálogo global + hierarquia nas três telas de leitura. Achados P0/P1 do critic endereçados no protótipo; browser gate verde.

**Design Agent verdict: PASS**
