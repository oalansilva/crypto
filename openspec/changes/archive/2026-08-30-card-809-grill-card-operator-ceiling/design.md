## Context

Card [#809](https://github.com/oalansilva/crypto/issues/809). Q1=A, Q2=A, Q3=A congeladas (não reabrir). Relacionado e **não** reaberto: #667 (porta + ledger no issue — Pronto), #755 (todas as options — Pronto), #786 (grelha dsh no root — Done). Não reescrever bodies já grelhados (#795, #799, #801).

Factos live (worktree + produto `oalansilva/covenant-flow` tag **`v1.1.5`**):

- Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.5`. Adapter `.cursor/skills/grill-card/SKILL.md` **sem** tecto de linguagem. Vendor `.cursor/skills/grilling/SKILL.md` intacto (Matt `❓`/`➡️`).
- Comentário canónico pinado (spec viva + needle `DOD_NEEDLES`) = `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` (**Q3=A**).
- Bloco `## Grill-card` de `covenant-flow`: disparo = body sem as 6 seções; pai relaying `todas as options` / `não colapsa`; `Cliente dsh:` dsh não spawna filho grill. **Não** nomeia o tecto.
- Peles `.grok` / `.dsh` / `.opencode` `grill-card`: stubs thin MUST Read do canónico (≤8 linhas não-vazias no body).
- Evidência 2026-08-30 (Qs de desenho no cartão do host): #795 Q2 função vs interpolar yaml; #799 Q3 soma de marcadores de cópia; #801 Q3 não medir um predicado interno.
- `scripts/process-fsm/test_grill_card.py`: needles de porta, host options, vendor Matt, stubs Grok, pin-test `v1.1.5` quando `install.sh` existe. Sem golden de tecto.
- `SCHEMA_MAJOR` 1; canal v1 = copiar e commitar (`implantar --pin`).

**UI impact: none.** Tecto no adapter de processo + uma frase no runbook + goldens. Nenhuma rota, shell, componente ou copy de ecrã do CriptoFarol.

## Goals / Non-Goals

**Goals:**

- Tecto de linguagem no **adapter** `grill-card` (não no vendor): Qs e options em português de operador em **todo** card em Em Refinamento (**Q1=A**).
- Identificador do git (função, path, flag yaml, evento de fluxo, hash) → facto no body ou *como* em Riscos para Design, nunca option no host.
- Other vazio, silêncio e «não percebi» / «isto é técnico» reclassificam; **nunca** aceite da recomendada (**Q2=A**).
- Fronteira vazia deste adapter = 6 seções DoD **e** nenhuma decisão de operador em aberto. Comentário = linha pinada (**Q3=A**). Árvore Matt completa continua no Design.
- Uma frase exacta no bloco Grill-card de `covenant-flow` (além do relay de options).
- Golden em `test_grill_card.py` (produto + pin): dumps reprovados vs aprovados; equivalente de produto além dos três de harness.
- Pin patch `v1.1.6` (esperado; Apply confirma origin) → `implantar --pin` no Cripto.

**Non-Goals:**

- Editar o vendor `grilling`. Promover `/opsx:explore` a porta; schema `grill-driven`; `grill-with-docs` / `to-spec` / `CONTEXT.md` / ADR. Marketplace no lugar de `grill-card`.
- Reabrir #667 / #755 / #786. Reescrever #795 / #799 / #801. Mexer em colunas / T1 / `process-fsm.yaml` / `enabled_tools`.
- Contar «não percebi» / Other / silêncio como aceite da recomendada. Mudar o **texto** do comentário canónico.
- Inchar peles `.grok` / `.dsh` / `.opencode`. Código de app (`backend/` / `frontend/src/`). UI / HTML. Pin major.

## Decisions

1. **Q1=A — o mesmo tecto em todo Em Refinamento.**  
   Adapter (não vendor). Histórias de produto (ex. Monitor) e cards de harness. Alternativa rejeitada: tecto só em harness.

2. **Q2=A — Other / silêncio / «não percebi» nunca aceitam a recomendada.**  
   Facto no body ou *como* no Design. A recomendada **não** fica decidida. Outras Qs da mesma rodada continuam à espera. Other do host (#755) é linha automática, não option listada: Other vazio, silêncio (sem resposta) e «não percebi» / «isto é técnico» (via Other ou texto livre) **reclassificam**. Alternativa rejeitada: Other = A / rubber-stamp. Golden MUST NOT tratar «não percebi» como *texto da option recomendada*.

3. **Q3=A — texto canónico exacto; só muda o *quando*.**  
   Linha pinada inalterada. Idempotente (já exacto → não duplica; texto canónico errado → edita/minimiza). Alternativa rejeitada: novo texto de handoff.

4. **Golden = lista de identificadores *e* exemplos fixos (ambos).**  
   Residual da grelha. Só lista = falso negativo nos três dumps de evidência se o scanner for estreito. Só exemplos = o tecto não pega Q nova com path. Apply MUST ter os dois no mesmo `test_grill_card.py`.

   **Lista (scanner `ceiling_violation(text) -> bool`)** — corre sobre o prompt **e** cada option de cada Q fechada do dump. P1 r2: o matcher MUST ser estreito o bastante para **passar** Qs de operador que usam português corrente; esconder as palavras no `pass_operator.md` **não** basta.

   | Classe | Match (estreito) | MUST NOT match |
   | --- | --- | --- |
   | path git | `/` + extensão `\.(py\|ts\|tsx\|js\|mjs\|yaml\|yml)$` | — |
   | token de código | backtick com `_` ou `()` ou `.` (não reticências) | — |
   | SHA | `\b[0-9a-f]{40}\b` **ou** 7–39 hex com **pelo menos um dígito e pelo menos uma letra a–f** | palavra PT só-letras (`acabada`); data compacta só-dígitos (`20260830`); `\b[0-9a-f]{7,40}\b` largo |
   | evento / flag | token `process_event` ou `iniciar_design` (word-boundary ou backtick) | verbo PT `priorizar` / `Não priorizar ainda` (T1 só Alan) |

   Dump **passa** só se o scanner é falso em todas as Qs fechadas.

   Pytest MUST incluir estes asserts de unidade (um scanner largo falha-os):

   ```
   assert not ceiling_violation("Não priorizar ainda")
   assert not ceiling_violation("A história está acabada")
   assert not ceiling_violation("evidência 20260830")
   assert ceiling_violation("process_event priorizar")
   assert ceiling_violation("94f8ed41")
   ```

   **Exemplos fixos** em `scripts/process-fsm/fixtures/grill_ceiling/` (reconstruções; **não** `gh issue edit` daqueles cards):

   | Ficheiro | Papel |
   | --- | --- |
   | `fail_795_q2.md` | harness: função vs interpolar yaml |
   | `fail_799_q3.md` | harness: soma de marcadores de cópia |
   | `fail_801_q3.md` | harness: não medir um predicado interno |
   | `fail_monitor_path.md` | produto: Q só inteligível com path/componente do Monitor |
   | `pass_operator.md` | Qs de operador (quem sofre / o que passa-falha / o que não entra) **incluindo** `Não priorizar ainda`, `acabada` e `20260830` |
   | `fail_stamp_other_empty.md` | Other submetido vazio → adapter gravou a recomendada |
   | `fail_stamp_silence.md` | silêncio (sem resposta) → adapter gravou a recomendada |
   | `fail_stamp_nao_percebi.md` | Other/texto livre «não percebi» ou «isto é técnico» → adapter gravou a recomendada |

   Equivalente de produto além dos três de harness = `fail_monitor_path.md` (ex.: option A path `frontend/src/pages/Monitor.tsx` vs B componente `WatchlistRow`). `pass_operator.md` MAY usar o mesmo tema Monitor **sem** path/função/flag; MUST conter as três frases de falso-positivo acima. Fixture **errada** (proibida): «não percebi» como *label da option recomendada* — o Other do host #755 é automático e não entra em `options[]`.

5. **Frase exacta no bloco Grill-card (uma linha, além do relay).**  
   Apply MUST inserir esta frase no `## Grill-card` de `.cursor/skills/covenant-flow/SKILL.md`, depois do parágrafo de relay de options e **antes** de `Cliente dsh:`:

   `Tecto: Qs e options em português de operador em todo card em Em Refinamento; identificador do git é facto no body ou *como* no Design, não option no host; Other vazio, silêncio e «não percebi» / «isto é técnico» reclassificam e nunca aceitam a recomendada.`

   A linha de disparo (body sem as 6 seções) e a de relay **permanecem**. Golden: a secção contém a frase exacta **e** `todas as options` / `não colapsa`.

6. **Tag patch `v1.1.6`, canal usual.**  
   Origin live = `v1.1.5`. Sem schema overlay. Apply MUST `gh api repos/oalansilva/covenant-flow/tags` antes de taggar; se `v1.1.6` estiver ocupada, bump patch seguinte (nunca major). `SCHEMA_MAJOR` 1. Pin-tests que cravam `v1.1.5` sobem para a tag deste card. Ordem: commit no produto → tag → `implantar --pin` no Cripto.

7. **Peles thin; canónico leva o tecto.**  
   `.grok` / `.dsh` / `.opencode` `grill-card` continuam MUST Read do canónico. Apply MUST NOT copiar o tecto para os stubs (body ≤8 linhas não-vazias). Vendor `grilling` intocado. `grok_stubs.py` / `dsh_stubs.py` / `AGENTS.md` / `process-fsm.yaml` intocados salvo o pin que já copia peles.

8. **Disparo «oferecer grill» inalterado.**  
   Continua: Em Refinamento **e** body sem as 6 seções. O tecto **não** obriga a re-grelhar um DoD já escrito. T1 só Alan. Needles de «Quando disparar» no canónico permanecem.

9. **Onde o tecto vive no canónico (Apply, não agora).**  
   Nova secção no adapter `.cursor/skills/grill-card/SKILL.md` (não no vendor): regra Q1, teste de identificador, facto vs *como*, paragem = 6 seções + zero decisão de operador, reclassificar Q2, *quando* do comentário Q3. `## Como` passo 4/5 alinha o *quando*; o texto do comentário não muda. Contrato N≥2 / D5 / ramos Cursor-Grok vs dsh **intactos**.

## Apply contract

Ordem (produto primeiro; zero UI Cripto):

1. Canónico `grill-card`: secção de tecto + *quando* da fronteira (D9). Comentário = linha pinada. Vendor `grilling` intocado.
2. Uma frase D5 no bloco Grill-card de `covenant-flow`. Disparo e relay intactos. Stubs Grok/dsh/OpenCode **não** incham.
3. Goldens D4 em `test_grill_card.py` + `fixtures/grill_ceiling/`. Scanner apertado (asserts `Não priorizar ainda` / `acabada` / `20260830` passam). Needles Q2 (Other/silêncio/«não percebi») / Q3. Pin-tests → tag deste card. N1 (#755) verdes.
4. Commit + tag patch no produto (esperado **`v1.1.6`**; Apply confirma origin).
5. `implantar --pin` no worktree Cripto; overlay `pin:` = essa tag. MUST NOT `backend/**` nem `frontend/src/**`. MUST NOT reabrir #667/#755/#786 nem reescrever #795/#799/#801.

Rollback = pin Cripto `v1.1.5`. Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [Scanner estreito deixa passar Q de desenho sem path] → golden **ambos**: os quatro fail dumps são rede mesmo se o scanner falhar um padrão novo. Residual A (P2): a lista não cobre *todo* identificador possível.
- [Scanner largo falha Qs de operador] → P1 r2 fechado: matcher SHA misto + eventos só `process_event`/`iniciar_design`; `pass_operator.md` MUST conter `Não priorizar ainda`, `acabada`, `20260830`; asserts de unidade pinados em D4.
- [Reclassificar é texto, não Guard] → aceite (P2 A): ritual #755 não muda; golden Q2 = três dumps de *stamp* (Other vazio / silêncio / «não percebi» via Other), nunca «não percebi» como label da option. Residual: modelo ignora o adapter — visível no próximo grill, não em pytest de skill.
- [Vendor Matt vs paragem do adapter] → aceite (P3 A): a árvore vendorada continua no Design; o adapter pára nas 6 seções + zero Q de operador.
- [Tag `v1.1.6` ocupada entre Design e Apply] → Apply confirma origin e bump patch seguinte; nunca major.
- [DoD já escrito com Qs de desenho no histórico] → D8: tecto não re-grelha. Residual aceite: cards antigos ficam; o tecto vale daqui para a frente.
- [Pele Grok/dsh/OpenCode sem o tecto] → MUST Read; inchar stubs é regressão do needle ≤8.

## Migration Plan

Aditivo sobre `v1.1.5`. Ordem = Apply contract. Consumidor recebe o adapter + a frase + goldens no pin. Rollback = pin `v1.1.5`. Sem schema overlay. Sem canal novo.

## Open Questions

Nenhuma bloqueante. Q1–Q3 congeladas. P1 B (scanner falso-positivo; Other/silêncio) fechados em D2/D4/D5. Residuais A P2/P3 aceite: scanner não cobre todo identificador; tecto é skill não Guard; árvore vendor vs paragem do adapter.

## UI impact

**none** — adapter `grill-card` + uma frase no runbook `covenant-flow` + goldens pytest. Nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`. Não há tela CriptoFarol a prototipar; o aceite é texto de adapter/runbook + dumps golden. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum (r1 B: scanner falso-positivo e Other/silêncio — fechados em r2: matcher SHA misto, eventos só `process_event`/`iniciar_design`, `pass_operator` com «Não priorizar ainda» / `acabada` / `20260830`; Other/silêncio/«não percebi» nunca aceitam a recomendada)
- **P2:** scanner não cobre todo identificador; reclassificar é skill não Guard; fronteira vendor vs stop do adapter — accepted-residual
- **P3:** FN `WatchlistRow` / `` `priorizar` ``; pytest ≤8 só no stub dsh; tag `v1.1.6` Apply confirma origin
- Prototype: N/A — `UI impact: none` (adapter + frase + goldens; zero tela)
- Snapshot: `.impeccable/critique/809-card-809-grill-card-operator-ceiling-A.md` (B: `...-B.md`) — crítica de processo, não visual
- `Design Agent verdict: PASS`
