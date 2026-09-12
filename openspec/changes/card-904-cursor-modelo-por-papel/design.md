## Context

Card [#904](https://github.com/oalansilva/crypto/issues/904) (Operação, P2). Briefing = issue grelhado (DoD completo; aceite de operador não reabre). Status=Design. Cliente desta sessão: Cursor Agent. Sem-tela.

Facto vigente: Task/subagent usa `inherit` salvo pedido explícito no chat. A lista fechada isolada isola **transcript**, não o modelo. Busca/exploração avulsa e fecho de lote **não** estão nessa lista. Specs `cursor-code-review`, `developer-tooling`, `covenant-flow`, `cursor-harness`, `llm-flow-emission` (e `impeccable-design-gate` para A/B) exigem herdar. Agent files em `.cursor/agents/` declaram `model: inherit`; spawn genérico cola o corpo e **não** lê o cabeçalho. Overlay `clients.*.auto: false`. Pin `v1.1.15`. Destape classifica só `grill-card` / `apply-coluna` / `diff-reviewer` / `code-reviewer` / `qa-gate` / `design-autor` / `design-critic` / `Assessment A/B`. Sem needle novo o pai não destapa. T16 = `process_event fechar_release` no pai. Slugs internos vigentes (facto, não cartão do host): `cursor-grok-4.6-high`, `composer-2.5`, `composer-2.5-fast`.

UI impact: none
live_route: N/A
surface: new
Justificativa curta: harness Cursor only; zero rota de catálogo; sem HTML/protótipo. Nunca emprestar /monitor /favorites /combo/* ou landing.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Filhos Cursor deixam de herdar o picker. Lei = parâmetro `model` do Task nos dois caminhos de spawn (tipo nomeado **ou** `generalPurpose` com o corpo do agente colado).
- Mapa: grelha + Design (autor, crítico, A/B) → Grok 4.6 (`cursor-grok-4.6-high`). Apply, QA, os dois revisores, busca/exploração no mesmo card, filho de fecho de lote → Composer normal (`composer-2.5`). `composer-2.5-fast` FORA. Revisores no Grok FORA deste card. Sem reversão escrita do ensaio.
- Slug inválido: recusa visível; sem inherit silencioso; sem retry inventado. Troca de modelo = sessão nova (#430).
- `harness.mdc` 4–12 linhas aponta juízo/execução e o runbook; não vira runbook. `AGENTS.md` always-on não cresce.
- Handoff existente ganha proxy papel→modelo. `/kaizen release` lê. Sem parser/dashboard.
- Filho isolado de fecho de lote no Composer; o PAI chama `process_event fechar_release`; SEM aresta nova.
- Prova viva: Apply Composer + grill ou Design Grok, dois modos Cursor, host `completed`. Cloud/Auto FORA.
- Stubs Grok/OpenCode/dsh continuam inherit; ≤8 linhas; sem copiar a tabela.

**Non-Goals:**

- Produto / UI / HTML / protótipo. Emprestar rota de catálogo.
- Aresta, estado, evento, hook ou `enabled_tools` novos. Dual-write `.grok/` / `.opencode/` / `.dsh/`.
- Redesenhar isolamento, destape, sidecar, Q2–Q6, teto 1+1 dos filhos já existentes.
- Parser de usage Cursor, dashboard, preço no repo.
- Forçar picker do pai. Recomendar picker ao pai. Ensaio do pai em Composer.
- Revisores no Grok; `composer-2.5-fast`; Cloud; Auto.
- Deixar o fecho de lote só no pai. Reversão escrita do ensaio de review.
- Subir pin só por peles Cursor. Inventar needle de destape para o filho de lote.

## Decisions

1. **Lei = parâmetro `model` do Task, nos dois caminhos.** Spawn nomeado (`subagent_type` grill-card / design-autor / apply-coluna / diff-reviewer / …) **e** spawn genérico (`generalPurpose` com o corpo do agent file colado) passam o slug do papel. O cabeçalho YAML dos dois ficheiros em `.cursor/agents/` deixa de mandar herdar: passa a `model: composer-2.5` como pin redundante. Spawn genérico **não** lê o cabeçalho — se o parâmetro faltar, isso é recusa visível, não inherit silencioso.

   Mapa (rótulo no body / host; slug só no runbook e no parâmetro):

   | Papel | Rótulo | Slug |
   | --- | --- | --- |
   | grill-card, design-autor, design-critic, Assessment A, Assessment B | Grok 4.6 | `cursor-grok-4.6-high` |
   | apply-coluna, qa-gate, diff-reviewer, code-reviewer, explore/busca no mesmo card, fecho-lote | Composer 2.5 | `composer-2.5` |

   `composer-2.5-fast` MUST NOT aparecer no mapa, no spawn, nem como fallback. Revisores no Grok MUST NOT neste card. Sem porta de saída escrita.

   Rejeitado: inherit + «pedido explícito no chat». Rejeitado: lei no cabeçalho YAML. Rejeitado: um slug «fast» como barateamento.

2. **Texto exacto de `.cursor/rules/harness.mdc` (5 linhas de corpo; orçamento 4–12).** Frontmatter `alwaysApply: true` intacto. Corpo (linhas não-vazias depois do YAML):

   ```
   # Harness (Cursor)

   - Cliente: Cursor Agent. Hooks: `.cursor/hooks.json`.
   - Task: juízo = Grok 4.6; execução = Composer 2.5. Sem inherit do picker. Tabela = skill `covenant-flow`.
   - Always-on δ vive em `AGENTS.md`. Não invente aresta; use `process_event`.
   - Overlay on-demand; runbook = skill `covenant-flow`.
   ```

   Não lista papéis. Não cola slugs. Não vira runbook. Spec `cursor-harness` deixa de exigir a palavra `inherit` no corpo; passa a exigir juízo/execução **ou** Cursor hooks.

   Rejeitado: uma frase só «tabela no runbook» sem juízo/execução (o always-on ficaria mudo). Rejeitado: copiar a tabela para o harness. Rejeitado: crescer `AGENTS.md`.

3. **Proxy papel→modelo cabe no bloco de proxies já existente do handoff.** Spec `llm-flow-emission` «Handoff comments record cost proxies» ganha **uma linha própria por spawn**, depois de palavras de `design.md` / bytes HTML / número de spawns:

   `proxy modelo: <papel> → <rótulo> (<slug>)`

   Exemplo: `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`. Papel = o needle do spawn (`grill-card`, `design-autor`, `design-critic`, `Assessment A`, `Assessment B`, `apply-coluna`, `qa-gate`, `diff-reviewer`, `code-reviewer`, `explore`, `fecho-lote`). `/kaizen release` lê comentários REST do pacote e a skill kaizen passa a procurar `proxy modelo:`; compara com a tabela vigente do runbook. Sem parser de usage, sem dashboard, sem dinheiro.

   Rejeitado: campo novo no board. Rejeitado: ficheiro de métricas. Rejeitado: inferir o modelo a partir do transcript.

4. **Prova viva = Apply deste card + juízo deste card; não espera card de produto seguinte.** O pai, depois de T7, spawna Apply-coluna #904 com `model: composer-2.5` — esse filho **é** a prova de execução (host `completed`). Juízo: Design-crítico #904 com `model: cursor-grok-4.6-high` (este autor pode ter nascido ainda em inherit; o crítico já segue esta lei). Dois modos obrigatórios (terminal **e** Desktop+SSH): cada modo MUST mostrar host `completed` num spawn de juízo (grill ou Design) **e** num Apply. Se Design #904 só correu num modo, o grill do próximo card em Em Refinamento nesse modo completa o par de juízo. Cloud, Auto e `composer-2.5-fast` MUST NOT. Q2–Q6 / isolamento / destape dos filhos já existentes não se redesenham.

   Rejeitado: esperar um card de produto seguinte para ensaiar o Apply. Rejeitado: um único modo.

5. **Filho de fecho de lote: needle humano `fecho-lote`; o pai **não** espera destape; T16 já é o mesmo turno.** Sem needle novo no classificador. Sem `FOLLOWUP_*` novo. Sem sidecar `.cursor/tmp/awaiting-task.json` neste spawn. Sem pin.

   Spawn (pai, mesmo turno do pedido explícito de fechar lote / subir release):

   - `description`: string curta que **contém** `fecho-lote` e **não** contém needles do classificador vigente (`grill-card`, `apply-coluna`, `diff-reviewer`, `code-reviewer`, `qa-gate`, `design-autor`, `design-critic`, `Assessment A`, `Assessment B`, nem `\bqa\b` / `\bgrill\b` soltos). Título canónico: `fecho-lote kaizen`.
   - Caminhos: `generalPurpose` **ou** tipo nomeado, ambos com `model: composer-2.5`.
   - Prompt autocontido: és o filho isolado `fecho-lote`; MUST NOT `process_event`; MUST NOT arrastar Status; MUST NOT commit/push; Read overlay + `covenant-flow-environments`; corre `/kaizen release` (skill kaizen, read-only); devolve o relatório. O PAI chama `process_event fechar_release`.
   - Filho MUST NOT `move_agent_to_root`. Shell do fluxo com `required_permissions: ["all"]` no primeiro attempt (Q3 intacto, não redesenhado).
   - Pai: espera o Task nativo até `completed` + payload no **mesmo turno**; depois T16. Destape MUST NOT disparar (classificador devolve `None`; sem sidecar). Hang do host deste filho = falha visível deste closeout (já #879 para hang; este card não cura hang).

   Rejeitado: needle + FOLLOWUP em `subagent_stop.py` (núcleo; redesenharia destape; pin). Rejeitado: aresta/evento/hook/`enabled_tools`. Rejeitado: o filho a chamar T16. Rejeitado: fecho só no pai sem filho.

6. **Slug inválido e #430.** Se o host recusa o slug, o pai cola a recusa no chat e **não** re-spawna com `inherit`, sem `model`, nem com `composer-2.5-fast`. Sem retry inventado. Troca de modelo de subagent = sessão nova; spawns em voo ficam no antigo. Actualizar um slug vigente = card novo.

7. **Pin `v1.1.15` não sobe.** Apply = peles Cursor (`harness.mdc`, `covenant-flow` SKILL, agent files, kaizen SKILL, specs). Núcleo: MUST NOT editar `subagent_stop.py` / `process-fsm.yaml` / Guard. Goldens já existentes em `scripts/process-fsm/test_*.py` que needleiam `model: inherit` ou `Task inherit` nas peles Cursor MAY ser retunados — isso não é pin e não é aceite. Stubs `.grok/` / `.opencode/` / `.dsh/` intocados (continuam inherit, ≤8 linhas, sem copiar a tabela). Overlay `clients.*.auto` intocado.

   Rejeitado: pin no closeout só porque o golden do agent file mudou. Rejeitado: dual-write da tabela nos stubs.

8. **`impeccable-design-gate` recebe delta.** Assessment A/B são juízo: Grok 4.6, iguais ao Design-autor, MUST NOT herdar o picker do pai. Igualdade de modelo = entre autor e A/B, não entre A/B e o chat pai. Sem-tela deste card: A/B N/A; o delta evita contradição na spec.

9. **Destape/resume de filho Composer MUST manter `composer-2.5`.** Resume, destape (`subagentStop` followup) ou follow-up de um filho de execução (Apply-coluna, QA, os dois revisores, busca no mesmo card, `fecho-lote`) MUST NOT trocar o slug para `composer-2.5-fast`. Se o host retomar ou facturar `composer-2.5-fast`, o pai MUST NOT aceitar esse run: MUST NOT `resume` quando cair em fast; spawn **novo** com `model: composer-2.5` e prompt autocontido (schema Task: `resume` não aceita `model`). Busca no mesmo card MUST NOT usar `subagent_type` `explore` se o host mapear `explore` a fast; caminho = `generalPurpose` + `model: composer-2.5`. `fecho-lote` continua sem sidecar e sem destape; auto-resume do host para esse filho = ignorar.

   Rejeitado: aceitar follow-up fast como continuação do Apply. Rejeitado: `explore` como atalho de busca no card bound. Rejeitado: needle novo no classificador para lote.

10. **Chat de release/lote = Composer 2.5 no pai.** Única excepção ao silêncio sobre picker do pai: pedido explícito `subir a release` / fechar lote / T16 (`process_event fechar_release`) + spawn `fecho-lote`. Se o chat pai não é `composer-2.5` (p.ex. Grok 4.6), recusa visível: MUST NOT correr T16 nem `fecho-lote` neste chat; sessão nova em Composer 2.5. Grok 4.6 permanece só na lista de juízo (D1). MUST NOT forçar picker via git / `AGENTS.md` / overlay `clients.*.auto`. MUST NOT recomendar picker noutros chats de card `#<id>`.

   Rejeitado: T16 no transcript Grok que já fez restore/T16 prep. Rejeitado: ensaio «mude o picker» no harness.

## Prototype

N/A — harness Cursor only; zero rota de catálogo; sem HTML/protótipo. Impeccable / Playwright / `DESIGN.md` = N/A justificado. Nunca emprestar `/monitor` `/favorites` `/combo/*` ou landing.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana (Aprovação de Design → Pronto para Dev) permanecem.

## Apply contract

- `.cursor/rules/harness.mdc`: corpo exacto da D2 (5 linhas; orçamento 4–12).
- `.cursor/skills/covenant-flow/SKILL.md`: substituir «Task/subagent usa inherit» pelo mapa da D1; prompts autocontidos passam o slug no parâmetro; silêncio sobre picker do pai (exceto D10: chat pai Composer 2.5 para release/lote); filho `fecho-lote` (D5); destape/resume keep-slug Composer (D9); proxy no handoff (D3). MUST NOT copiar a tabela para `AGENTS.md`. MUST NOT dual-write stubs. MUST NOT adicionar needle ao classificador de destape. Pin citado permanece `v1.1.15` (corrigir o `v1.1.14` residual no S1 se o Apply tocar essa linha — detalhe de Apply, não aceite).
- `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` MAY notar se o closeout correu com chat pai não-Composer (achado de processo; sem parser de usage).
- `.cursor/agents/diff-reviewer.md` e `code-reviewer.md`: `model: composer-2.5`; `readonly: true` intacto; corpo (intervalo, schema FINDING, teto) intacto.
- `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` lê `proxy modelo:` nos comentários REST do pacote e compara com a tabela vigente.
- Specs delta desta change. Isolamento / destape / sidecar / Q2–Q6 / teto 1+1 / onda no mesmo turno **não** se reabrem.
- Goldens existentes que partirem (`model: inherit` nos agent files, `Task inherit` no harness) MAY ser retunados. MUST NOT `test_card_904_*` como aceite. MUST NOT editar `subagent_stop.py`.
- Prova viva (QA deste card, não pytest): Apply #904 Composer + Design-crítico (ou grill) Grok, host `completed`, nos dois modos Cursor. Cloud/Auto/fast fora.

## Risks / Trade-offs

- [Pai mudo no filho de lote sem destape] → aceite: T16 já obriga o pai a ficar no turno; hang = falha visível (#879), este card não cura hang. Mitigação: não gravar sidecar; não fingir que destapa.
- [Este Design-autor nasceu em inherit] → o crítico #904 e o Apply #904 são a prova; grill noutro modo se faltar o par.
- [Host recusa slug] → recusa visível; card novo para renomear; sem inherit silencioso.
- [Golden em `scripts/process-fsm/test_*.py` parte] → retunar o assert da pele; pin não sobe.
- [Operador lê «Composer 2.5» e spawna fast] → runbook e harness dizem Composer normal / `composer-2.5`; fast FORA; recusa se o slug fast for passado.

## Migration Plan

Peles Cursor no Apply desta branch. Sem migrate de dados. Sem rollback de ensaio de review (não há porta). Stubs dos outros clientes não migram. Pin permanece `v1.1.15` no closeout deste card.

## Open Questions

Nenhuma. Fronteira de operador vazia; *como* fechado acima. Não reabrir Qs do grill.
