# Snapshot ajustes2 — card 852 descoberta-três-modos — 2026-09-07T02-11Z

Filho Design-autor isolado, rodada ajuste-Alan-2 (sem transcript). Card 852 `change card-852-descoberta-tres-modos`, Status=Design.
Cwd imposto: crypto-worktrees/card-852-descoberta-tres-modos (só essa árvore). Sem T5/process_event/branch/Status. Nada de nested-spawn/Gist.
Decisões operador Iniciar-domina + Short-escondido mantidas (não reabertas). `## Design Critique` do design.md NÃO tocada.

## Pedido de Alan (decisão fechada)

A edição avançada estava **duplicada** com 4 ações (Selecionar filtrados / Selecionar todos / Limpar / Limpar seleção). Reduzir para exatamente **2 ações de eixo inteiro**: `Selecionar todos` e `Limpar seleção` — remover `Selecionar filtrados` e `Limpar` (o escopo filtrado já é coberto pela seleção inline; a edição avançada opera o eixo todo).

## O que mudou (arquivos/patches)

- `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` (StrReplace, 3 edições; sem reemitir o arquivo):
  - `.rowbtns` do modal `#m-adv`: removidos `#m-adv-select` (Selecionar filtrados) e `#m-adv-clear` (Limpar); ficam `#m-adv-select-all` (Selecionar todos) e `#m-adv-clear-all` (Limpar seleção), mantendo `#m-adv-ok` (Aplicar).
  - JS: removidos os listeners `$("m-adv-select")…` e `$("m-adv-clear")…`; ficam os de `#m-adv-select-all` (marca o eixo todo) e `#m-adv-clear-all` (limpa tudo).
  - Subtítulo do modal: `Templates — selecionar todos ou limpar seleção.` / `Símbolos — selecionar todos ou limpar seleção.` (era `…filtrados, todos, limpar ou limpar seleção.`).
  - Contador `#m-adv-count` inalterado (`X de N selecionados`, atualiza em clique e checkbox); inline reflete após Aplicar.
  - Preservados: 7 pares `COPIED:start/end`, `live_route:/combo/discovery`, `surface:existing`, dialogs íntegros (header + corpo DENTRO do `role=dialog`), default Período = Todo histórico, Iniciar-domina, Short-escondido.
- `openspec/changes/card-852-descoberta-tres-modos/specs/discovery-three-modes/spec.md`: Requirement `Inline selection, modal as advanced edit` reescrito — o modal = "edição avançada" com exatamente 2 ações de eixo inteiro (`Selecionar todos`/`Limpar seleção`); `SHALL NOT` ter ação de escopo filtrado; contador do modal ao vivo + inline após Aplicar. Cenário `Advanced edit whole-axis actions` (era `…bulk actions`) reformulado para as 2 ações e ausência de ação filtrada.
- `openspec/changes/card-852-descoberta-tres-modos/proposal.md`: bullet Seleção inline reduzido de 4 ações para **2 ações de eixo inteiro** (Selecionar todos / Limpar seleção), com a nota de que o escopo filtrado já é coberto pela inline.
- `openspec/changes/card-852-descoberta-tres-modos/tasks.md`: 4.1 reduzido para exatamente 2 ações de eixo inteiro (Selecionar todos / Limpar seleção), escopo filtrado resolvido inline (sem ação própria na edição avançada), contador do modal `X de N` + inline após Aplicar.
- `openspec/changes/card-852-descoberta-tres-modos/design.md`: linha `## Prototype` **Digest** atualizada para o novo sha256/bytes; `Fluxos/estados` (modal edição avançada) reescrito para 2 ações; `## Prototype Validation` com nova nota `Ajuste-Alan-2 2026-09-07`. `## Design Critique` NÃO tocada.

Nota: `.design-digest` do change não foi tocado (é gravado somente por `process_event` T5; fora do escopo desta rodada).

## Novo digest/bytes

- Local: `8e9c02221ea6c2db885c17e08541c01f3b6c99f206023c226962c74bb0748aee` · 34075 bytes (anterior `f5c81ef7…` · 34662).
- Servido (`curl http://127.0.0.1:5176/prototypes/card-852-descoberta-tres-modos/` 200, sem restart — server lê o worktree): mesmo sha256/bytes; `diff` local↔servido vazio. **servido == local.**

## Sanity browser real (Playwright + Chromium, `/tmp/card852-sanity-ajustes2.py`)

| Viewport | Resultado |
|---|---|
| 1440×900 | 31/31 PASS, 0 console errors, 0 pageerrors |
| 390×844 | 31/31 PASS, 0 console errors, 0 pageerrors |

PNGs reais: `/tmp/card852-ajustes2/desktop-adv.png`, `desktop-promote.png`, `mobile-adv.png`, `mobile-promote.png`.

Ação→resultado (ambos viewports; confirmação adicional desktop 1440×900 com foco no modal):
- Abrir edição avançada (`#adv-tpl`): modal `#m-adv` abre; `.rowbtns` = exatamente {`Selecionar todos`, `Limpar seleção`, `Aplicar`}; `#m-adv-select`/`#m-adv-clear` inexistentes (count 0); subtítulo `Templates — selecionar todos ou limpar seleção.`; contador inicial `3 de 8 selecionados` (default 3 templates).
- `Selecionar todos` (`#m-adv-select-all`) → `8 de 8 selecionados` → Aplicar (`#m-adv-ok`) → inline `#c-tpl` = `8 selecionados`.
- `Limpar seleção` (`#m-adv-clear-all`) → `0 de 8 selecionados` → Aplicar → inline `#c-tpl` = `0 selecionados`.
- Regressão: default `#sel-period=all` (Todo histórico); preflight `24 combinações · ~2h 24min estimado · todo o histórico [01 jan 2017, 01 jan 2026)`; CTA `Iniciar varredura — 24, ~2h 24min`; landmarks 3/3 (h1 `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`); 1 modo visível; filtro inline `#q-tpl` filtra a lista; dialog Promover íntegro (header + `.risk` + `.dest`/Tier 3 + `.body` DENTRO de `#m-promote`) fecha com Escape; dialog avançada íntegro (header + `.body` DENTRO de `#m-adv`) fecha com Escape e foco retorna a `#adv-sym`; 0 console errors; 0 pageerrors.

## Check gate

- `clone_gate_ok(change, proto, repo) == True` local pós-edição (design_clone_gate): `live_route: /combo/discovery` + `surface: existing` (linhas standalone) intactos; protótipo com 7 pares `COPIED:start/end` (sum 1801 bytes) só no espelhado do vivo; landmarks do catálogo (`route-landmarks.yaml`) batem. **gate True.**

## Veredito

**PASS** — edição avançada reduzida a exatamente 2 ações de eixo inteiro (Selecionar todos / Limpar seleção) no protótipo + OpenSpec (spec/proposal/tasks/design), digest atualizado com servido==local (sha256 `8e9c0222…`, 34075 bytes), gate True, sanity 62/62 sem erros e regressões passando.
