# Crítica de Design — Design-crítico (sem-tela) — card #1043

**Papel:** filho isolado **Design-crítico (sem-tela)** do Covenant Flow (cliente Cursor Agent, isolado, sem transcript do pai).
**Change:** `openspec/changes/card-1043-jev-medicao-explicita/`
**Card:** issue **#1043** em `oalansilva/crypto`, Project 1, `Status=Design`.
**Worktree/branch:** `/srv/apps/dev/criptofarol/crypto-worktrees/card-1043-jev-medicao-explicita` @ `card-1043-jev-medicao-explicita` (a partir de `develop` @ `38eec37b`).
**Sem-tela** (backend/harness): régua read-only de avaliação do scalp Jev. Prototype N/A, Impeccable N/A.
**Proxy modelo:** design-critic → deepseek-flash (deepseek-flash).

## Fontes lidas

- `.cursor/skills/design-critic/SKILL.md` (rúbrica, classificação P0/P1 vs P3, teto 1+1+1, bloco D4, tokens do gate do autor).
- `.cursor/skills/covenant-flow/SKILL.md` («Design — clone da página viva», «Design fecha em 1+1+1»).
- Pacote no worktree: `proposal.md`, `design.md`, `tasks.md`, `specs/scalp-jev-realized-measurement/spec.md`, `specs/scalp-jev-ohlcv-access/spec.md`, `.openspec.yaml`.
- Relatório do autor: `.impeccable/critique/1043-card-1043-jev-medicao-explicita.md`.
- Body do issue **#1043** só por REST (`gh api repos/oalansilva/crypto/issues/1043 --jq .body`); **não** usei `gh issue view`.
- Código real no worktree (leitura, sem alterar): `scripts/scalp_jev_eval.py`, `backend/app/database.py`, `backend/app/services/ohlcv_storage.py`, `backend/tests/unit/test_scalp_jev_eval_ruler.py`.

## Comparação por secção do briefing (issue #1043 vs `proposal.md`)

| Secção do issue | Resultado |
| --- | --- |
| `## Problema` | **IDENTICAL** |
| `## História` | **IDENTICAL** |
| `## Entra` (com `### Decisões fechadas (grelha 25/09)` + critérios) | **IDENTICAL** |
| `## Não entra` | **IDENTICAL** |
| `## Evidência (25/09, DEV)` | **IDENTICAL** |

A **História não foi reescrita nem reentrevistada**; o `proposal.md` é superset do issue (briefing verbatim + *como*).

## Rúbrica 1–8

| # | Item | Resultado | Evidência |
| --- | --- | --- | --- |
| 1 | Tokens do gate do autor (linha própria parseável; sem rota emprestada; Prototype/Impeccable N/A; D4 verbatim) | **PASS** | `UI impact: none` · `live_route: N/A régua read-only de avaliação no backend/harness do scalp Jev; não há tela de produto` · `surface: new`; só menções negativas às rotas de catálogo; bloco **D4** colado verbatim. |
| 2 | Fidelidade ao briefing grelhado | **PASS** | 5/5 secções **IDENTICAL**. |
| 3 | Escopo (nada do `Não entra`) | **PASS** | Limiar de confiança, política por regime, geometria alvo/stop e horizonte intactos; #1030/#1025 não reabertos; sem painel/Monitor; sem PROD. |
| 4 | Q1/Q2/Q3 preservadas com contrato observável | **PASS** | veredictos abaixo. |
| 5 | Falha ≠ insuficiência em todos os caminhos | **PASS** | veredicto abaixo. |
| 6 | Coerência interna (requisitos × cenários × tasks × decisões × riscos) | **PASS** | `tasks.md` com **27** caixas, todas `- [ ]` (0 marcadas); nenhuma task fora do contrato visível. |
| 7 | Riscos e alternativas | **PASS** | 8 decisões, cada uma com alternativa rejeitada real; 8 riscos com mitigação. |
| 8 | N/A (sem tela) | **PASS** | Sem protótipo/HTML/rota de catálogo; `design.md` **não** contém `## Design Critique`. |

**Veredito: PASS** — `rework: nao`, `p0_p1_count: 0`. Nenhum achado de produto/escopo.

## Q1/Q2/Q3 — veredicto

- **Q1 — preservada.** Corrida sem medir termina em erro accionável (exit `3`, distinto do `2` do `argparse`; decisão 3 / task 5.1) **e** o relatório é emitido antes do retorno (`print(report)`, `--json`, `--out`; `:1561-1568`; task 5.2), com `raise SystemExit(main())` (`:1574`) a propagar o código.
- **Q2 — preservada.** Acesso pelo **ambiente**, invocação inalterada (sem `--dsn`/`--db-url` nem env novo); `user`/`host`/`port`/`dbname` + origem declarados no sucesso **e** na falha, sem password (task 4.1); **causa real** (mensagem + classe, sanitizada) visível (decisão 5 / tasks 3.1-3.2).
- **Q3 — preservada.** Distinção explícita «medição parcial» vs «amostra insuficiente» com contagem de janelas sem preço, inclusive no **fecho por regime** (decisão 6 / task 2.3), sem mudar o predicado `n_priced < MIN_NON_OVERLAPPING_WINDOWS` do #1030.

## Falha ≠ insuficiência em todos os caminhos? — **Sim**

Veredicto escolhido primeiro pelo **estado da medição** (decisão 2); spec `No report path presents a non-measured realized side as insufficient sample`; fecho por regime rotula medição parcial (decisão 6); `--json` separa `measurement` de `insufficient` (decisão 7). Nenhum caminho do design colapsa as duas. O ponto residual A3 (bullets secundários de `reasons`) não afecta o rótulo do veredicto.

## Achados

| id | gravidade | classe | bloqueia_merge | achado | sugestão de fecho |
| --- | --- | --- | --- | --- | --- |
| A1 | P3 | mecanico | nao | Citações de linha ligeiramente deslocadas: `"insufficient": True` é `:1113` (design diz `:1112`); `ohlcv`/`ohlcv_candles` são `:1110-1111` (design diz `:1108-1110`); `def build_report` é `:1039` (diz `:1037+`); `def main` é `:1495` (corpo citado `:1546-1559`). | Acertar no Apply; sem efeito no contrato. |
| A2 | P3 | mecanico | nao | `OHLCV desativado (sem DATABASE_URL)` (`scalp_jev_eval.py:462`) parece **inalcançável**: `backend/app/database.py:72` (`DB_URL = resolve_db_url()`) levanta no import quando `DATABASE_URL` falta, pelo que o ramo cai antes em `OHLCV indisponível (import: RuntimeError)` (`:456`). | No Apply, tratar o import falhado como causa de `não medido` e manter `:462` como defesa; registar a observação. |
| A3 | P3 | contrato-visivel | nao | Em `não medido`, o rótulo fica correcto (`**Realizado não medido**`), mas a lista de `reasons` ainda pode incluir o bullet de amostra (`n_priced < mínimo`, `:1178-1181`) ao lado do motivo de medição; o design diz «declarada em separado» mas não fixa a ordem. | No Apply, emitir primeiro o motivo de medição e separar visualmente o motivo de amostra. |
| A4 | P3 | mecanico | nao | Log **presente mas vazio** ainda passa por `load_candles` (`:1558`, janela zero); `não aplicável` precisa de precedência sobre o resultado da leitura. | Task 1.2 já cobre a intenção; garantir no Apply a classificação `não aplicável` quando não há decisões. |

## P3 aceitos (detalhe de Apply — resolvidos no Apply, nunca reabertos como P0/P1)

- Nome/forma do resultado estruturado de `load_candles`; valor exacto do código de saída (`3` proposto); chave exacta `measurement.exit_code`.
- Regras exactas de sanitização (limite/padrões de DSN/password).
- Wording exacto dos rótulos (`**Realizado não medido**`, `**Medição parcial**`) e do texto da secção de medição.
- Se/como a identidade é confirmada por `SELECT` à sessão e comportamento com `repo._enabled=False`/import falhado.
- Separação «janela sem preço por cobertura» vs «por ausência de entrada» (`realized_for:562-563`).
- Como os testes injectam leitura falhada/parcial/sem cobertura sem DB real e provam o exit não-zero.
- **A1–A4** (acima): citações de linha, `:462` defensivo, ordem dos motivos, precedência de `não aplicável`.

## Factos verificados (path:linha)

- `scripts/scalp_jev_eval.py:1570` — `return 0`; `:1574` — `raise SystemExit(main())`; `def main` `:1495`. **Confirmado (Q1).**
- `scripts/scalp_jev_eval.py:442-520` — `load_candles -> tuple[CandleSeries, str]`; notas só com `type(exc).__name__` em `:456`, `:460`, `:470`, `:506`; `:462` `OHLCV desativado`; `:494-497`; `:508`; `:513-519` cobertura parcial. **Confirmado.**
- `scripts/scalp_jev_eval.py:1165-1166` — `if not series: reasons.append(f"realizado indisponível: {ohlcv_note}")`; `:1160` `reasons`; veredicto `:1385-1389` imprime `**Amostra insuficiente**` para qualquer `reason`. **Confirmado.**
- `scripts/scalp_jev_eval.py:1170-1181`, `:1233-1236` (`sample_sufficient`), `:88-89` (`MIN_NON_OVERLAPPING_WINDOWS=30`, `MIN_BUCKET_TRADES=20`); fecho por regime `:831-835`. **Confirmado (Q3).**
- `scripts/scalp_jev_eval.py:895-898` — `**{n_priced} com preço**`. **Confirmado.**
- `scripts/scalp_jev_eval.py:1561-1568` — `print(report)`, `--json`, `--out` antes de `:1570 return 0`. **Confirmado (Q1).**
- `scripts/scalp_jev_eval.py:50`; `:449-462` (`sys.path` + import `MarketOhlcvRepository`); `load_candles` só chamado em `:1558`; `scalp_jev_window_ab.py` usa `build_report` (`:197`, `:334`), não `load_candles`. **Confirmado.**
- `backend/app/database.py:54` `resolve_db_url()`; `:61` `settings.database_url` ou `DATABASE_URL`; `:64`, `:69` levantam; `:72` `DB_URL = resolve_db_url()` no import. **Confirmado.**
- `backend/app/services/ohlcv_storage.py:15` (`from app.database import DB_URL, engine`), `:283-289` (`_enabled = bool(DB_URL)`), `:413-420` (`read_recent_candles`). **Confirmado.**
- `backend/tests/unit/test_scalp_jev_eval_ruler.py` existe; `test_the_instrument_is_read_only` em `:269`. **Confirmado.**

## Proxies / evidência de gate

- `openspec validate card-1043-jev-medicao-explicita --strict` → literal: **`Change 'card-1043-jev-medicao-explicita' is valid`** (exit 0).
- `git status --porcelain` → `?? .impeccable/critique/1043-card-1043-jev-medicao-explicita.md` e `?? openspec/changes/card-1043-jev-medicao-explicita/` — nenhum `backend/**`/`frontend/**` tocado (branch `card-1043-jev-medicao-explicita` @ `38eec37b`).

**Não bate certo com o design (só citações, P3):** `"insufficient": True` é `:1113` (design `:1112`); `ohlcv`/`ohlcv_candles` são `:1110-1111` (design `:1108-1110`); `def build_report` é `:1039` (design `:1037+`); corpo de `main` citado como `:1546-1559`. Sentido factual preservado.

## Notas

Pacote read-only no que toca a produto; `proposal.md` é superset do issue (briefing verbatim + *como*). O ponto A2 (`:462` inalcançável) merece uma linha no Apply, mas não muda contrato. Teto sem-tela respeitado: 1 autor + 1 crítico, sem rework (0 P0/P1).
