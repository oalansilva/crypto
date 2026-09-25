# Crítica de Design — Design-crítico (sem-tela) — card #1030

**Papel:** filho isolado **Design-crítico (sem-tela)** do Covenant Flow (cliente Cursor Agent, isolado, sem transcript do pai).
**Change:** `openspec/changes/card-1030-jev-limiar-retorno-liquido/`
**Card:** issue **#1030** em `oalansilva/crypto`, Project 1, `Status=Design`.
**Worktree/branch:** `/srv/apps/dev/criptofarol/crypto-worktrees/card-1030-jev-limiar-retorno-liquido` @ `card-1030-jev-limiar-retorno-liquido` (a partir de `develop` @ `6a10529e`).
**Sem-tela** (backend/harness): régua de avaliação e limiar de confiança do scalp Jev. Prototype N/A, Impeccable N/A.
**Proxy modelo:** design-critic → deepseek-flash (deepseek-flash).

## Fontes lidas

- `.cursor/skills/design-critic/SKILL.md` (rúbrica, classificação P0/P1 vs P3, teto 1+1+1, tokens do gate).
- `openspec/changes/card-1030-jev-limiar-retorno-liquido/{proposal.md,design.md,tasks.md,specs/**}` (2 specs).
- Relatório do autor: `.impeccable/critique/1030-card-1030-jev-limiar-retorno-liquido.md`.
- Body do issue **#1030** só por REST (`gh api repos/oalansilva/crypto/issues/1030 --jq .body`); **não** usei `gh issue view`. Body do **#1029** por REST, só para testar a fronteira.
- Código no worktree (leitura, sem alterar): `backend/app/services/scalp_engine.py`, `scalp_service.py`, `scalp_window.py`, `scripts/scalp_jev_eval.py`.

## Comparação por secção do briefing (issue #1030 vs `proposal.md`)

Comparação programática (extracção de secções `^## ` e igualdade exacta, incluindo blocos `- `):

| Secção do issue | Resultado |
| --- | --- |
| `## Problema` | **IDENTICAL** |
| `## História` | **IDENTICAL** |
| `## Entra` (com critérios observáveis) | **IDENTICAL** |
| `## Não entra` | **IDENTICAL** |
| `## Evidência (homologação do #1025, 23/09)` | **IDENTICAL** |

A **História não foi reescrita nem reentrevistada**; o `proposal.md` só acrescenta as secções OpenSpec (`Why`, `What Changes`, `Capabilities`, `Impact`).

## Rúbrica 1–7

| # | Item | Resultado | Evidência |
| --- | --- | --- | --- |
| 1 | Fidelidade ao briefing grelhado | **PASS** | 5/5 secções IDENTICAL (tabela acima); `proposal.md:1-48` verbatim. |
| 2 | Escopo (nada do `Não entra`; #1029 declarado, não resolvido) | **PASS** | Proibições em `design.md:63-64,138`, `tasks.md:6,48`; specs sem tocar a pergunta do modelo/faixa (`specs/scalp-confidence-threshold-per-regime/spec.md:76-80`). Fronteira #1029 **declarada**: `design.md:95-100` (decisão 7, «Fronteira declarada»), `design.md:117-118` (risco), `design.md:154-156` (open question 3), `tasks.md:57` (7.3). |
| 3 | Contrato visível (3 decisões fechadas + reversível) | **PASS** | (a) um por regime (calmo/ativo) com regime sem amostra **fechado**: `design.md:78,93-95`, `tasks.md:44`; (b) amostra insuficiente → valor em uso **mantido** e bot **não opera**, insuficiência **declarada**: `design.md:60,93`, `specs/scalp-confidence-threshold-per-regime/spec.md:40-53`; (c) confiança que **não separa** → limiar **desligado**, decisão por previsão × custo × regime: `design.md:96-98`, `specs/scalp-jev-net-return-ruler/spec.md:51-62`; limiar **explícito e reversível por configuração**: `design.md:107-109`, `specs/.../spec.md:59-73`. |
| 4 | Coerência interna (requisitos × cenários × tasks × decisões × riscos; caixas; nada fora do contrato) | **PASS** | 9 decisões mapeiam nas 13 requirements dos 2 specs (régua: acurácia+amostra=d1; cobertura/retorno esperado=d2; um por regime+fecho=d3/d5; separação=d6; insuficiência=d5; taxa real=d8; homogeneidade=d7; read-only=d8; decisão: política por regime=d4; fronteira única=d3/d9; fechado preserva valor=d5; config reversível=d9; log-only=d4/apply). `tasks.md`: **28** caixas `- [ ]`, **0** `- [x]`. Nenhuma task fora do contrato (secções 1–7 cobrem rúbrica, decisão, config, testes, gate). |
| 5 | Tokens do gate em linha própria parseável + D4 verbatim | **PASS** | `design.md:19-21`: `UI impact: none` · `live_route: N/A régua read-only e limiar de confiança no backend/harness do scalp Jev; não há tela de produto` · `surface: new`. Sem rota de catálogo emprestada (só a lista proibida em `design.md:23`). Prototype **N/A** e Impeccable **N/A** com justificativa não-vazia (`design.md:23`). Bloco **D4** `diff` skill↔design = `D4_IDENTICAL` (`design.md:25`). |
| 6 | Riscos e alternativas | **PASS** | Cada decisão 1–9 tem ≥1 alternativa rejeitada real (`design.md:70-101`); 10 riscos com mitigação (`design.md:111-120`). |
| 7 | N/A (sem tela) | **PASS** | Sem protótipo/HTML/rota de catálogo: `design.md:3,23,64`, `proposal.md:80`; tokens `UI impact: none` / `live_route: N/A`. |

**Veredito: PASS** — nenhum achado P0/P1 (produto/escopo/contrato visível). Zero achados em produto/escopo/contrato.

## Rúbrica do clone gate

- **`UI impact: none`** — linha própria parseável (`design.md:19`). OK.
- **`live_route`** — `N/A` com justificativa não-vazia e sem empréstimo de rota de catálogo (`design.md:20,23`). OK.
- **`surface`** — `new`, justificado como nova *capability de decisão* e não superfície de tela (`design.md:21,23`). OK.
- **Prototype N/A / Impeccable N/A** — ambos presentes com razão curta não-vazia (`design.md:23`). OK.
- **Sem-tela não usa rota emprestada** — `live_route: N/A`; a menção a `/monitor`, `/favorites`, `/combo/...`, `landing` é a lista de proibição, não um valor de rota. OK.

## Achados

```
FINDING
gravidade: P3
classe: implementacao
conserto_obvio: sim
conserto_proposto: Ajustar no Apply a âncora de código do gate `low_confidence` para `backend/app/services/scalp_engine.py:381` (a condição `if confidence_min is not None and jev.confidence < confidence_min:`); hoje o design cita `:382` (linha do `return CycleIntent`).
bloqueia_merge: nao
file: openspec/changes/card-1030-jev-limiar-retorno-liquido/design.md:12
summary: Âncora de linha do gate `low_confidence` off-by-one (`:382` vs condição real em `:381`) — detalhe de Apply, sem efeito no contrato visível (decisões/valores/tokens inalterados).
```

**Nota sobre P3:** não há nenhum achado P0/P1. O único P3 é detalhe de implementação (âncora de linha), aceite em `design.md` e resolvido no Apply — **nunca** reaberto como P0/P1.

## Evidência da validação e higiene

`openspec validate card-1030-jev-limiar-retorno-liquido --strict` (worktree), output literal:

```
Change 'card-1030-jev-limiar-retorno-liquido' is valid
```

(exit code 0)

`git status --porcelain` (worktree), output literal:

```
?? .impeccable/critique/1030-card-1030-jev-limiar-retorno-liquido.md
?? openspec/changes/card-1030-jev-limiar-retorno-liquido/
```

- **Nenhum ficheiro de `backend/**` ou `frontend/**` foi tocado** — as únicas entradas são os dois artefactos untracked (relatório do autor + change). `scripts/**` igualmente intacto.
- `design.md` **não** contém `## Design Critique` (grep sem resultado): essa secção é do pai.

## Nota

**Não edito a secção `## Design Critique` do `design.md`** (é do pai). Este relatório é a única escrita deste filho; não alterei `proposal.md`/`design.md`/`tasks.md`/`specs/**`, não corri `process_event`, não toquei board/GitHub/Gist, não commitei/pushei e não toquei em código de produto.

`proxy modelo: design-critic → deepseek-flash (deepseek-flash)`
