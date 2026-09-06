## Context

Card [#818](https://github.com/oalansilva/crypto/issues/818). Status observado: **Design**. Bound `q_git=card-818-dsh-grill-spawn-cite`. Grelha fechada no body (Problema, História, Entra/não entra, Vocabulário, critérios, Riscos). Fronteira vazia. Este Design **não** reentrevista e **não** reabre #786 / #790.

Relacionado e **não** reaberto: #786 (grelha no root dsh; fail-closed de **papel** grill; matcher fora de `decide()`; FN `refine 701` sem needle), #790 (Design-autor já entregou após retry), #809 (tecto; pin `v1.1.6`), #822 (cwd Impeccable; grelha não pediu pin). Irmão no mesmo nucleus, **não** mergeado daqui: [#817](https://github.com/oalansilva/crypto/issues/817) (`card-817-dsh-reasoning-effort`, Status=Design) também espera tag patch `v1.1.7` e altera `scripts/process-fsm/dsh_plugin_lib.js` **e** `.dsh/plugin/process-fsm-guard.js` (pre-execute: grill → **`dsh_reasoning_effort_spawn`** → cordis → `runGuard`; mais `agent/request` / `agent/request-error`).

Factos live (este worktree; pin Cripto `v1.1.6`; produto origin tags até `v1.1.6`):

- `isGrillShapedSpawn` em `scripts/process-fsm/dsh_plugin_lib.js`: tools exactas `subagent` / `subagent_fork`; needle substring `grill-card` (case-insensitive `String.includes` após `toLowerCase()`, **não** regex) em `description`/`prompt` **e** `JSON.stringify` do objecto; parse de `arguments` string; parse fail → string crua; reason `dsh_grill_spawn`; `next()` não é chamado.
- Listener em `.dsh/plugin/process-fsm-guard.js` **antes** de `runGuard` / `decide()` / `isCordisRestricted` (live `v1.1.6`: grill → cordis → `runGuard`). #817, se aterrar primeiro, insere `dsh_reasoning_effort_spawn` entre grill e cordis e listeners `agent/request` / `agent/request-error`.
- Goldens `scripts/process-fsm/test_dsh_grill_spawn.py`: G1 description `grill-card 701` → deny; G2 prompt «Please run Grill-Card» → deny (papel); G4 Design-autor **sem** needle → allow; G5 `Task` / `spawn_subagent` / `task` → não é este deny; G6 JSON string description → deny; G10 unitário JS (nested stringify true; negativos `grill_card` / `grill card`).
- Overlay `.covenant-flow/overlay.yaml`: `pin: v1.1.6`; `clients.dsh.auto: false`. Change #786 em disco já arquivada (`openspec/changes/archive/2026-09-03-card-786-dsh-grill-root/`).
- Incidente: dsh `session-679a762b`, card #790, turno 2. Primeiro spawn Design-autor → `process-fsm-guard deny reason=dsh_grill_spawn` porque o prompt citava `grill-card fronteira vazia`, não porque pedia grelha. Retry sem a palavra passou.

Audience: operador do board no cliente dsh. Outcome: T3→T5 não atrasa por citação; filho grill continua impossível. Direction: apertar o helper JS (papel vs citação), não ensinar o modelo a omitir o ritual. Scope: plugin dsh + goldens + pin patch; zero UI de produto.

UI impact: none

live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Goals / Non-Goals

**Goals:**

- Distinguir **papel** de **citação** só em `isGrillShapedSpawn` (JS do plugin), sem ensinar `guard.py` `decide()`.
- Design-autor / Apply / reviewer isolados cujo prompt cita o ritual já fechado passam **este** deny (`next()` corre). Outro deny do Guard ainda pode aplicar.
- G1/G2/G6/G10 de **papel** permanecem deny. G5/G11/N3 intactos (tools Cursor/Grok/OpenCode e fonte de `guard.py` sem needle).
- Golden novo (G12): description de Design-autor + prompt com `grill-card fronteira vazia` → allow; G1 permanece deny.
- Pin: este card **inclui** o bump. Canal produto `oalansilva/covenant-flow`; tag = a deste card **depois** de `gh api` tags **e** rebase no tip/tag já existente (irmão #817 no mesmo nucleus). Pin-tests sobem para essa tag, não `v1.1.7` no vácuo.

**Non-Goals:**

- Permitir filho grill no dsh (root grelha; não spawna filho grill).
- Mudar Cursor/Grok: spawn de grill nesses clientes continua permitido.
- Reabrir Design do #790. Reabrir recorte do #786 (root, fail-closed de papel, matcher fora do Python). Reverter #817 (`dsh_reasoning_effort_spawn`, `agent/request`). Pin a partir de `v1.1.6` que clobber o sibling.
- Matcher no Guard Python. Deny global de todo spawn. Código de app (`backend/` / `frontend/src/`).
- Ensinar o modelo a omitir o ritual no briefing como «solução». Trocar o texto do comentário canónico T1.
- Falso negativo já aceite no #786 (description `refine 701` sem needle). Regex. Pin major. UI / HTML / `DESIGN.md` / Playwright desta coluna.

## Decisions

1. **Papel vs citação = dois haystacks + marcadores de citação pinados; description ganha.**  
   Algoritmo só em `isGrillShapedSpawn` (tools exactas inalteradas). Matching = `toLowerCase()` + `String.includes` — **não** regex, **não** `decide()`.  
   1. Recolher strings `description` e `prompt` (ver D2).  
   2. Se `description` contém `grill-card` → **deny** (papel). G1/G3/G6/G9. Citação no prompt **não** salva.  
   3. Senão, se nem description nem prompt contêm `grill-card` → **não** é este deny.  
   4. Senão (needle só no prompt / string crua de parse-fail): se o prompt contém **algum** marcador de citação da lista pinada → **não** é este deny (citação). Senão → **deny** (papel via prompt: G2, G10 parseFail, G10 nested `inner.prompt` sem marcador).  
   Lista pinada de marcadores (minúsculas; `includes`; **não** regex; Apply MUST NOT alargar):

   | Marcador | Porquê |
   | --- | --- |
   | `fronteira vazia` | facto fechado do incidente e critério 1 |
   | `do not re-interview` | briefing Design-autor |
   | `não reentrevistar` | idem PT |
   | `do not invoke grill-card` | citação negativa do ritual |
   | `não invocar grill-card` | idem PT |
   | `closed grill` | «closed grill facts» |
   | `grill-card dod` | Apply/review a citar o DoD |
   | `dod grelhado` | idem PT |
   | `grilled dod` | idem EN |

   Alternativa rejeitada: identity na description (`design-autor` / `apply` / `reviewer`) como allow em branco — o critério 1 exige só «description não é papel» + prompt com `grill-card fronteira vazia`; description `refine 701` + citação **passa**. Alternativa rejeitada: deny em «grelha a história» / `run grill-card` como needle extra — o briefing de Design **cita** essas frases como golden; voltaria o falso positivo. Alternativa rejeitada: ensinar o modelo a omitir a palavra. Alternativa rejeitada: matcher em `decide()`.

2. **Nested: andar só chaves `description` / `prompt`; MUST NOT `JSON.stringify` o objecto inteiro.**  
   Walk: se `args` é string, `JSON.parse`; parse fail → a string crua é haystack de **prompt** (G10 parseFail / G6). Se objecto: empilhar `args.description` e `args.prompt` se strings; **recursar só valores objecto** (incl. arrays). Cyclic → WeakSet / try-catch, não throw. **Proibido** concatenar `JSON.stringify(args)` — isso foi o alargamento #786 que trata citação profunda noutro campo como papel.  
   - `{ inner: { prompt: "x grill-card y" } }` → prompt aninhado, sem marcador → deny. G10 `nested` permanece `true`.  
   - `{ inner: { fact: "grill-card fronteira vazia" } }` (sem description/prompt com needle) → allow. Falso positivo de citação aninhada some.  
   - Papel metido só em `inner.task` (sem description/prompt) → falso negativo da mesma classe que `refine 701` sem needle (**não** deste card; não stringify para o tapar).  
   Alternativa rejeitada: stringify + allow-list no blob — reintroduz citação em campo irmão. Alternativa rejeitada: mudar G10 nested para false — partiria o fail-closed de papel aninhado em `prompt`.

3. **G12 (e irmãos Apply/review) via `apply` + `pre-execute`, não via `decide()`.**  
   Mesmo padrão G1–G9 (`import { apply } from` `.dsh/plugin/process-fsm-guard.js`). G10 continua unitário JS. G11/`guard.py` fonte **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`.

   | # | Caso | Esperado |
   | --- | --- | --- |
   | G1 | description `grill-card 701` | deny `dsh_grill_spawn`; `next` false (**permanece**) |
   | G2 | description `refine 701`, prompt `Please run Grill-Card on the issue` | deny (**permanece**; sem marcador) |
   | G6 | `arguments` JSON string `{"description":"grill-card 701"}` | deny (**permanece**) |
   | G10 nested | `inner.prompt` `x grill-card y` | `isGrillShapedSpawn` true (**permanece**) |
   | G10 neg | `grill_card` / `grill card` | false (**permanece**) |
   | G12 | description `design-autor 818`, prompt contém `grill-card fronteira vazia` | `next()` true; reason **não** é `dsh_grill_spawn` |
   | G12b | description `apply 818`, prompt cita DoD grelhado (`grill-card dod` ou `dod grelhado`) | idem allow |
   | G12c | description `diff-reviewer 818`, prompt com `closed grill` + `grill-card` | idem allow |
   | G12d | description `design-autor 818`, `inner.fact` contém `grill-card` sem `prompt`/`description` com needle | allow (não stringify) |
   | G4/G5/G11 | inalterados | allow / não este deny |

   G12 MUST usar a frase `grill-card fronteira vazia` (critério 1). Description G12 MUST NOT conter `grill-card`.

4. **«Listener inalterado» = ordem grill-antes-de-`runGuard` + reason, não bytes de `v1.1.6`.**  
   `isGrillShapedSpawn` MUST ser o **primeiro** deny de spawn no `tools/pre-execute`, **antes** de `runGuard`; deny `{ kind: "deny", reason: "process-fsm-guard deny reason=dsh_grill_spawn" }` sem `next()`. Isto **não** exige `.dsh/plugin/process-fsm-guard.js` byte-identical a `v1.1.6`. Se #817 já tiver aterrado `agent/request` / `agent/request-error` e o gate `dsh_reasoning_effort_spawn` entre grill e cordis, Apply #818 **mantém-nos**. O gate #817 MAY ficar depois do grill e antes de cordis. Apply MUST NOT reverter esses listeners. Apply MUST NOT mover o matcher grill para o plugin inline nem para Python. Cursor `Task` / Grok `spawn_subagent` / OpenCode `task` continuam fora (G5). Sem mudança de skill Cursor/Grok. Sem linha `AGENTS.md`. Sem texto T1 novo.

5. **Pin = tag deste card após rebase no tip/tag existente; não `v1.1.7` no vácuo.**  
   O helper vive no nucleus `scripts/process-fsm/` (e o plugin no mesmo pin) copiado por `implantar --pin`. Patch só no Cripto divergiria do produto (canal #786/#809). Origin/overlay live = `v1.1.6`; `v1.1.7` ainda livre na crítica, mas #817 disputa o mesmo número e os mesmos ficheiros. Apply MUST `gh api repos/oalansilva/covenant-flow/tags` **e** rebase o produto na tag/tip que já existir (incl. a de #817 se publicada). O fallback «próximo patch livre» cobre o **número**, não substitui rebase/merge: pin a partir de `v1.1.6` depois do sibling **clobbers** o sanitizer/gate #817. Pin-tests (`test_dsh_adapter.py`, needle em `test_grill_card.py`) sobem de `v1.1.6` para **esta** tag depois do rebase — MUST NOT hardcode `v1.1.7` no vácuo. `SCHEMA_MAJOR` 1; `clients.dsh.auto: false`. Alternativa rejeitada: residual «pin depois noutro card». Alternativa rejeitada: major. Alternativa rejeitada: só bump de número sem rebase.

6. **Skill / briefing: o ritual continua citado; a «solução» não é omitir a palavra.**  
   Canónico `grill-card`, comentário T1 e ramos Cursor/Grok **intocados**. Design-autor / Apply / review **devem** poder nomear o ritual fechado. O Guard dsh é que deixa de tratar essa citação como papel.

## Apply contract

Ordem (produto primeiro; zero UI Cripto):

1. `gh api repos/oalansilva/covenant-flow/tags` **e** rebase o checkout do produto na tag/tip que já existir (incl. #817 se tiver publicado o nucleus). MUST NOT partir de `v1.1.6` a ignorar o sibling.
2. TDD: acrescentar G12/G12b/G12c/G12d em `test_dsh_grill_spawn.py` **antes** de mudar o helper (live deve falhar G12). G1/G2/G6/G10 asserts de papel permanecem exactos.
3. `scripts/process-fsm/dsh_plugin_lib.js`: haystacks D1–D2 (sem `JSON.stringify` do objecto; lista de marcadores pinada). `guard.py` **não** se edita. Plugin: `isGrillShapedSpawn` continua **primeiro** entre os denys de spawn, **antes** de `runGuard`, reason `dsh_grill_spawn`, sem `next()` — **não** byte-identical a `v1.1.6`. MUST NOT reverter `dsh_reasoning_effort_spawn` nem `agent/request` / `agent/request-error` se #817 já os tiver posto (gate #817 MAY após grill, antes de cordis).
4. Correr `pytest scripts/process-fsm/test_dsh_grill_spawn.py` (e o pacote process-fsm sem GitHub): G1–G11 verdes; G12 allow; N3 fonte de `guard.py` sem needle.
5. Commit + tag patch no produto = **esta** tag após o rebase (se `v1.1.7` livre e o tip ainda é `v1.1.6`, MAY ser `v1.1.7`; se #817 já a usou, próximo patch livre — nunca major). Pin-tests sobem para essa tag, não hardcoded `v1.1.7`. `install.sh --pin` continua a copiar nucleus/adapters.
6. `implantar --pin` no worktree Cripto; overlay `pin:` = essa tag. MUST NOT `backend/**` nem `frontend/src/**`. MUST NOT reabrir #786/#790. MUST NOT clobber #817. MUST NOT alterar texto T1 nem Cursor/Grok grill spawn.

Rollback = pin Cripto `v1.1.6` **só** se o sibling #817 ainda não estiver pinado no consumidor; senão rollback = a tag do sibling, não um pin que apague `dsh_reasoning_effort_spawn`. Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [Corrida de pin `v1.1.7` com #817 no mesmo nucleus, sem merge] → Apply `gh api` tags **e** rebase no tip/tag existente; MUST NOT pin a partir de `v1.1.6` a clobber `dsh_reasoning_effort_spawn` / `agent/request`. Fallback de número ≠ rebase.
- [P2 aceite — marcadores incompletos vs `Do NOT spawn grill-card` / backticks] → briefing que cita o ritual com essa frase ou `` `grill-card` `` sem marcador pinado ainda pode deny. **Não** alargar a lista. G12 permanece a frase do incidente `grill-card fronteira vazia`.
- [P2 aceite — stuffed `refine 701` + Grill-Card + `fronteira vazia`] → bypass de papel via citação enxertada. Description `grill-card 701` ainda deny. Residual: não alargar marcadores.
- [Papel só noutro campo que não `description`/`prompt`] → FN da classe `refine 701`. Fora deste card. Stringify para o tapar reintroduz o incidente.
- [Apply mete o matcher em `decide()`] → G5/G11/N3 falham visível. Proibido.
- [Plugin omitido / `--patch` ausente] → spawn allow (#782). Residual aceite; não é deste card.

## Migration Plan

Aditivo sobre o tip pinado (live `v1.1.6`, ou a tag de #817 se já existir). Ordem = Apply contract (rebase **antes** do helper). Consumidor recebe o helper + goldens no pin **sem** apagar o gate #817. Rollback = pin da tag anterior que ainda contenha o sibling, não um reset cego a `v1.1.6` que clobber. Sem schema overlay. Sem canal novo.

## Open Questions

Nenhuma bloqueante. P1 (#817 pin race) fechado em D4/D5 + Apply contract. Residuais P2 aceites (não alargar marcadores): `Do NOT spawn grill-card` / backticks; stuffed `refine 701` + Grill-Card + `fronteira vazia`. FN papel noutro campo.

## UI impact

**none** — harness/plugin dsh + goldens + pin. Nenhuma rota, shell, componente ou copy de produto.

live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é o helper JS (papel deny / citação allow) + goldens pytest + pin. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

- P0: nenhum
- P1: nenhum (P1 r1 pin×#817 fechado: irmão nomeado; rebase no tip; «listener inalterado» = ordem grill-deny antes de `runGuard`, não bytes `v1.1.6`; MUST NOT reverter `dsh_reasoning_effort_spawn` / `agent/request`)
- P2 (aceites): `tasks.md` duplicado (cópia r1 após r2; Apply usa a 1.ª frente com rebase); stuffed citation `refine 701` + marcador; FN `refine 701` / campo irmão; marcadores incompletos vs `Do NOT spawn grill-card` / backticks; plugin omitido (#782)
- P3 (aceites): G12b `dod grelhado` sem needle; haystack ignora arrays; spec nested mistura G12d/G10; pin-tests live `v1.1.6` (pré-Apply)
- Prototype: N/A — `UI impact: none` (helper JS + goldens + pin; sem HTML)
- Snapshot: `.impeccable/critique/818-card-818-dsh-grill-spawn-cite-A.md` e `.impeccable/critique/818-card-818-dsh-grill-spawn-cite-B.md`
- Design Agent verdict: PASS
