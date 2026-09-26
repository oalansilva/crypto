# Relatório do autor — card-1043-jev-medicao-explicita (Design, sem-tela)

**Papel:** filho isolado **Design-autor** do card **#1043** (Covenant Flow, cliente Cursor, **sem-tela**). Sem transcript do pai; prompt autocontido. Não spawnei filhos, não chamei `process_event`, não arrastei Status/board, não fiz commit/push, não publiquei Gist, não comentei a issue, não escrevi a secção `## Design Critique`, não chamei `move_agent_to_root`. Todo o trabalho dentro do worktree `card-1043-jev-medicao-explicita` (`/srv/apps/dev/criptofarol/crypto-worktrees/card-1043-jev-medicao-explicita`), a partir de `develop` @ `38eec37b`.

## O que li

- `.cursor/skills/openspec-new-change/SKILL.md`, `.cursor/skills/openspec-ff-change/SKILL.md`, `.cursor/skills/design-critic/SKILL.md` (bloco **D4** e tokens do gate do autor), `.cursor/skills/covenant-flow/SKILL.md` («Design — clone da página viva», «Design fecha em 1+1+1», «Card primeiro, OpenSpec mais completo»), `AGENTS.md`, `openspec/config.yaml`.
- Body do issue **#1043** só por REST (`gh api repos/oalansilva/crypto/issues/1043 --jq .body`); sem `gh issue view`. O issue grelhado é o briefing — não reentrevistei, não inventei história.
- Change modelo `card-1030-jev-limiar-retorno-liquido` (proposal/design/tasks/spec, formato e tokens) e o código citado no prompt, confirmado linha a linha no worktree.

## Factos conferidos (path:linha, no worktree)

- `scripts/scalp_jev_eval.py:1570` — `main()` termina com `return 0`; `:1574` — `raise SystemExit(main())`. Nenhum caminho de erro não-zero. **Confirmado (Q1).**
- `scripts/scalp_jev_eval.py:1165-1166` — `if not series: reasons.append(f"realizado indisponível: {ohlcv_note}")`; a lista `reasons` (`:1160`, `:1167-1181`) alimenta o veredicto em `:1386-1389`, que imprime `**Amostra insuficiente**` para qualquer `reason`. **Confirmado** (o prompt citava `:1166` para a linha; a condição `if` está em `:1165`, o `append` em `:1166`).
- `scripts/scalp_jev_eval.py:1233-1236` — `sample_sufficient = len(windows) >= 30 and stats_all["n_priced"] >= 30`; `:88-89` — `MIN_NON_OVERLAPPING_WINDOWS = 30`, `MIN_BUCKET_TRADES = 20`; `:1170-1181` — `reasons` por `len(windows)` e `n_priced`. **Confirmado.**
- `scripts/scalp_jev_eval.py:831-835` — fecho por regime usa `elif stats["n_priced"] < MIN_NON_OVERLAPPING_WINDOWS` (o prompt citava `~:831-836`). **Confirmado (Q3).**
- `scripts/scalp_jev_eval.py:895-898` — a linha de amostra mostra `**{stats['n_priced']} com preço**`; o «57 de 74» já é visível. **Confirmado.**
- `scripts/scalp_jev_eval.py:442-520` — `load_candles` devolve `tuple[CandleSeries, str]`; notas com só `type(exc).__name__` em `:456` (`import`), `:460` (`repo`), `:470` e `:506` (`falhou na leitura`); `:462` (`OHLCV desativado (sem DATABASE_URL)`); `:494-497` (`sem candles que cubram a janela`); `:508` (`OHLCV sem candles`); `:513-519` (nota de **cobertura parcial**). O prompt citava `:449-470` e `:498`/`:506`; a realidade é a acima (sem mudança de sentido). **Confirmado (Q2 — causa real).**
- `scripts/scalp_jev_eval.py:50` — docstring: OHLCV lido com `DATABASE_URL` do ambiente; `:449-462` — `load_candles` faz `sys.path` e importa `MarketOhlcvRepository`. **Confirmado.**
- `scripts/scalp_jev_eval.py:1561-1568` — `print(report)`, JSON opcional e `out_path.write_text(...)`; `:1570` `return 0`. A escrita precede o retorno (base da decisão 3). **Confirmado.**
- `scripts/scalp_jev_eval.py:1112`, `:1254` — `summary["insufficient"]` nasce `True` e vira `bool(reasons)`; `:1108-1110` — `summary["ohlcv"]`/`ohlcv_candles`. Os dois eixos (medição/amostra) estão misturados no JSON. **Confirmado.**
- `backend/app/database.py:54` — `resolve_db_url()`; `:61` — `settings.database_url` ou `DATABASE_URL`; `:64`, `:69` — levanta se inválido/ausente; **`:72`** — `DB_URL = resolve_db_url()` corre no import. O prompt citava `:54-71`; a linha do `DB_URL` é **`:72`** (correção registada). **Confirmado.**
- `backend/app/services/ohlcv_storage.py:15` — `from app.database import DB_URL, engine`; `:283-289` — `MarketOhlcvRepository`, `self._enabled = bool(DB_URL)`; `:413-420` — `read_recent_candles` com `with engine.begin() as conn`. A régua não tem parâmetro de acesso. **Confirmado.**
- `backend/tests/unit/test_scalp_jev_eval_ruler.py` — testes da régua e do gate read-only (`test_the_instrument_is_read_only` referido no `tasks.md`); usam `ruler.build_report`/`ruler.CandleSeries`. **Confirmado.**

## O que produzi

- `openspec/changes/card-1043-jev-medicao-explicita/` criado no worktree (planning home `repo` = worktree, confirmado por `openspec status --json`): `proposal.md`, `design.md`, `tasks.md`, `specs/scalp-jev-realized-measurement/spec.md`, `specs/scalp-jev-ohlcv-access/spec.md`, `.openspec.yaml`.
- `proposal.md` copia **verbatim** do issue `## Problema`, `## História`, `## Entra` (com `### Decisões fechadas (grelha 25/09)` e os critérios observáveis) e `## Não entra`; acrescenta `## Evidência (25/09, DEV)` verbatim (contexto) e `## Why`/`## What Changes`/`## Capabilities`/`## Impact` ao serviço do standard OpenSpec.
- `design.md` com `## Context` (factos path:linha acima), tokens do gate, bloco D4 colado verbatim, `## Vocabulário`, `## Goals / Non-Goals`, `## Decisions` (8, cada uma com alternativa rejeitada real), `## Risks / Trade-offs`, `## Apply contract` (visível + P3) e `## Open Questions`. **Sem** `## Design Critique`.
- `tasks.md`: todas as caixas `- [ ]` (nenhuma marcada), com a nota do gate Design → Aprovação de Design → Pronto para Dev.
- `openspec validate card-1043-jev-medicao-explicita --strict` → **`Change 'card-1043-jev-medicao-explicita' is valid`** (exit 0); `openspec status` → `4/4 artifacts complete`.

## Tokens do gate do autor (linha própria parseável)

```
UI impact: none
live_route: N/A régua read-only de avaliação no backend/harness do scalp Jev; não há tela de produto
surface: new
```

`Prototype N/A` e `Impeccable N/A` com justificativa não-vazia no `design.md` (instrumento read-only de backend/harness; sem superfície visual, sem copy visível). Nenhuma rota de catálogo emprestada.

## Decisões de Design (não de operador) fixadas no `design.md`

1. Estado da medição como **resultado estruturado** (`medido` | `medição parcial` | `não medido` | `não aplicável`), não inferido de texto (decisão 1).
2. Dois eixos independentes — **medição vs amostra** — e rótulo do veredicto escolhido primeiro pelo estado da medição (decisão 2).
3. **Q1**: `não medido` com decisões ⇒ `main()` devolve **`3`** e o processo sai não-zero, com relatório emitido antes; `medição parcial`/`medido`/`não aplicável` ⇒ `0` (decisão 3). Fronteira `não aplicável` (log ausente/vazio) documentada.
4. **Q2**: acesso pelo **ambiente**, invocação inalterada; relatório declara `user`/`host`/`port`/`dbname` e origem, no sucesso e na falha, sem password; confirmação de sessão por `SELECT` read-only best-effort (decisão 4).
5. Causa real visível (mensagem do erro + classe), sanitizada (decisão 5).
6. **Q3**: «medição parcial» com contagem de janelas sem cobertura e motivo, inclusive no fecho por regime, distinta de insuficiência de amostra; regra `n_priced < 30` do #1030 intacta (decisão 6).
7. `summary["measurement"]` próprio; `insufficient` mantém o significado de amostra (decisão 7).
8. Read-only preservado; sem nova aresta de escrita nem env/argumento de acesso (decisão 8).

**Não-entra preservado:** limiar de confiança, política por regime, geometria alvo/stop e horizonte inalterados; #1030/#1025 não reabertos; sem painel/Monitor; PROD fora (T16).

## O que deixei em aberto (P3 / fronteiras)

- Nome/forma exacta do resultado estruturado de `load_candles`; valor exacto do código de saída (`3` proposto); regras de sanitização (limite/padrões); wording exacto dos rótulos; se/como a identidade é confirmada por `SELECT`; como separar «janela sem preço por cobertura» de «sem entrada»; como os testes injectam leitura falhada/parcial sem DB real.
- **Fronteira `não aplicável`** (log ausente/vazio fora do contrato de erro) é a única fronteira de produto que pode ser lida como P0 se o crítico entender que o issue exige erro também aí; a evidência do card é sobre OHLCV com 74 janelas, não sobre log vazio.
- Nenhuma pergunta ao operador: Q1/Q2/Q3 vieram fechadas na grelha de 25/09.

## Proxies

```
proxy modelo: design-autor → deepseek-flash (deepseek-flash)
```
