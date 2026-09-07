# Snapshot ajustes-Alan — card 852 descoberta-três-modos — 2026-09-07T01-56Z

Filho Design-autor isolado, rodada ajustes-Alan (sem transcript). Card 852 `change card-852-descoberta-tres-modos`, Status=Design.
Decisões operador Iniciar-domina + Short-escondido mantidas. Nada de T5/process_event/branch/Status.

## Pedidos de Alan (2 — ambos implementados)

1. **Período histórico padrão = Todo histórico.** Preset default do seletor passa a ser o histórico completo; opções menores continuam. Preflight default (`N combinações · ~T · janela`) e rótulo do CTA `Iniciar varredura — N, ~T` passam a refletir o histórico cheio; preflight mostra as datas da janela.
2. **Edição avançada com Selecionar todos + Limpar seleção.** Botões explícitos e visíveis no modal: `Selecionar todos` (marca todos do eixo — inclui os filtrados) e `Limpar seleção` (desmarca tudo), além das 2 ações existentes. Contador do inline reflete após Aplicar.

## O que mudou (arquivos/patches)

- `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` (StrReplace, 9 edições):
  - `<select id="sel-period">`: default `all` (`Todo o histórico` primeiro, `selected`); `2y`/`6m` continuam.
  - JS: `PERIODS = {all: [01 jan 2017, 01 jan 2026)×6, 2y: [01 jan 2024, 01 jan 2026)×2, 6m: [01 jul 2025, 01 jan 2026)×1}` + `period()`; `estimate(n)` = `n × factor`.
  - `sync()`: preflight 3 linhas com label + datas da janela; `pf-tech` dinâmico; rascunho congelado via `<span id="draft-frozen">` dinâmico (botão `novo rascunho` preservado).
  - Estáticos coerentes com o default: CTA `Iniciar varredura — 24, ~2h 24min`, `pf-tech` com janela cheia.
  - Modal edição avançada: + `Selecionar todos` (`#m-adv-select-all`, marca o eixo inteiro ignorando filtro), + `Limpar seleção` (`#m-adv-clear-all`, desmarca tudo); `Limpar` refinado para desmarcar os filtrados (com filtro vazio = tudo, igual ao comportamento anterior); contador ao vivo `#m-adv-count` (`N de M selecionados`, atualiza em clique e checkbox); sub do modal atualizado.
  - Preservados: 7 pares `COPIED:start/end`, linhas `live_route:`/`surface:` (design.md), landmarks, dialogs íntegros, Short escondido, Iniciar-domina.
- `openspec/changes/card-852-descoberta-tres-modos/specs/discovery-three-modes/spec.md`: novo Requirement `Full-history default period` + cenário; Requirement de seleção reescrito para 4 ações + contadores + cenário bulk.
- `openspec/changes/card-852-descoberta-tres-modos/design.md`: `## Prototype` Digest/Fluxos atualizados; Recorte com exceção do preset (sem mudar motor); `## Prototype Validation` com nota da rodada; `## Design Critique` do pai NÃO tocada.
- `openspec/changes/card-852-descoberta-tres-modos/tasks.md`: 2.1 (default + datas) e 4.1 (4 ações + contadores) atualizados.
- `openspec/changes/card-852-descoberta-tres-modos/proposal.md`: bullet do default + 4 ações; Impact/Fora com exceção do preset.

## Novo digest/bytes

- Local: `f5c81ef71539fdac2ad40ef27cea3e586513d9ee2cf37344c1390a3bde21c648` · 34662 bytes (anterior `9bffc2df…` · 33294).
- Servido (`curl http://127.0.0.1:5176/prototypes/card-852-descoberta-tres-modos/` 200, sem restart — server lê o worktree): mesmo sha256/bytes. **servido == local.**

## Sanity browser real (Playwright + Chromium, `/tmp/card852-sanity.py`)

| Viewport | Resultado |
|---|---|
| 1440×900 | 25/25 PASS, 0 console errors, 0 pageerrors |
| 390×844 | 25/25 PASS, 0 console errors, 0 pageerrors |

Ação→resultado (ambos viewports): default `#sel-period=all`; preflight `24 combinações · ~2h 24min estimado · todo o histórico [01 jan 2017, 01 jan 2026)`; CTA `Iniciar varredura — 24, ~2h 24min`; abrir edição avançada → botões novos visíveis; `Selecionar todos` → `8 de 8 selecionados` → Aplicar → inline `8 selecionados`; `Limpar seleção` → `0 de 8 selecionados` → Aplicar → inline `0 selecionados`; regressão: landmarks 3/3, 1-modo (`panel-montar`), Promover abre com `.risk`+`.dest` dentro de `#m-promote` e fecha com Escape, avançada com `.body` dentro de `#m-adv` fecha com Escape e foco retorna a `#adv-sym`.

## Check gate

- `clone_gate_ok(change, proto, repo) == True` local pós-edição (7 pares COPIED intactos, textos do catálogo presentes, `live_route: /combo/discovery` + `surface: existing` intactos).

## Veredito

**PASS** — os 2 ajustes estão no protótipo + OpenSpec, digest atualizado com servido==local, gate True, sanity 50/50 sem erros.
