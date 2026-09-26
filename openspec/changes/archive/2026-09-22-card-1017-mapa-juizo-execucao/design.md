## Context

Card [#1017](https://github.com/oalansilva/crypto/issues/1017). Briefing = issue grelhado (Problema, História, Entra/não entra). Status=Design. Cliente desta sessão: Cursor Agent. Sem-tela. Zero rota de produto.

Facto técnico vigente: a tabela de slugs está cravada em `.cursor/skills/covenant-flow/SKILL.md` (fonte que o pai lê no spawn) e o ponteiro curto em `.cursor/rules/harness.mdc` diz `juízo = Grok 4.6; execução = Composer 2.5`. Specs `cursor-harness`, `llm-flow-emission`, `impeccable-design-gate` e `kaizen-continuous-improvement` (e as Cursor irmãs `covenant-flow`, `cursor-code-review`, `developer-tooling`) repetem os literais `cursor-grok-4.6-high` / `composer-2.5`. Agent files `diff-reviewer` / `code-reviewer` pinam `model: composer-2.5` (pin redundante; lei = Task `model`). Overlay `pin: v1.1.16`. `clients.*.auto: false`. Grok Build, OpenCode e dsh continuam inherit.

UI impact: none
live_route: N/A
surface: new
harness Cursor; ausência de superfície; nunca rota de catálogo.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Um ficheiro Cursor-only versionado `.cursor/model-map.yaml` com duas faixas (`juizo` / `execucao`: rótulo + slug) e `forbid` (`composer-2.5-fast`, `inherit`).
- Papéis ficam na skill; o ficheiro só resolve rótulo + slug. Não é mapa por papel.
- Runbook `covenant-flow` deixa de cravar slugs; aponta para o ficheiro e lista só o agrupamento.
- `harness.mdc` 4–12 linhas aponta para o ficheiro + skill.
- Specs Cursor e kaizen comparam `proxy modelo:` ao mapa vigente (o ficheiro).
- Testes que assertam o literal na skill passam a ler o ficheiro; needle `composer-2.5-fast` MUST NOT permanece.
- Lei intacta: sem `inherit`; ficheiro em falta ou slug inválido = recusa visível; destape/resume de execução permanece no slug vigente; host a facturar fast = aborto + spawn novo; T16 / chat pai de lote usa `execucao.slug`; troca de modelo = sessão nova (#430); git não força picker do pai.

**Non-Goals:**

- Grok Build, OpenCode, dsh (continuam inherit). Dual-write `.grok/` `.dsh/` `.opencode/`.
- Overlay; `clients.*.auto` fica `false`. Env var / picker / `clients.cursor.auto`.
- Crescimento de `AGENTS.md` ou aresta nova na FSM.
- Mapa por papel (grill ≠ design-autor).
- Parser de usage Cursor nem dashboard.
- Produto / UI / HTML / protótipo. Emprestar rota de catálogo (`/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, landing).
- Parser de YAML no núcleo `scripts/process-fsm/` (além de goldens). Subir pin só por peles Cursor.

## Decisions

1. **Ficheiro = duas faixas, schema exacto do Entra.** Path versionado `.cursor/model-map.yaml`. Conteúdo vigente no Apply (byte-idêntico ao Entra):

   ```yaml
   juizo:
     label: Grok 4.6
     slug: cursor-grok-4.6-high
   execucao:
     label: Composer 2.5
     slug: composer-2.5
   forbid:
     - composer-2.5-fast
     - inherit
   ```

   O ficheiro resolve só rótulo + slug. MUST NOT mapear papel→slug (grill ≠ design-autor). Chaves extra ignoradas no Apply; chaves `juizo` / `execucao` / `forbid` em falta = recusa visível. Sem env var. Sem parser no núcleo: o pai `Read` o ficheiro antes do spawn.

   Rejeitado: mapa por papel. Rejeitado: overlay / `clients.cursor.auto`. Rejeitado: dual-write noutros clientes.

2. **Texto exacto de `.cursor/rules/harness.mdc` (5 linhas de corpo; orçamento 4–12).** Frontmatter `alwaysApply: true` intacto. Corpo (linhas não-vazias depois do YAML):

   ```
   # Harness (Cursor)

   - Cliente: Cursor Agent. Hooks: `.cursor/hooks.json`.
   - Task: juízo/execução = `.cursor/model-map.yaml`. Sem inherit do picker. Papéis = skill `covenant-flow`.
   - Always-on δ vive em `AGENTS.md`. Não invente aresta; use `process_event`.
   - Overlay on-demand; runbook = skill `covenant-flow`.
   ```

   Não cola slugs. Não lista papéis. Não vira runbook.

   Rejeitado: manter `juízo = Grok 4.6; execução = Composer 2.5` no always-on. Rejeitado: crescer `AGENTS.md`.

3. **Runbook lista agrupamento; slugs saem do ficheiro.** `.cursor/skills/covenant-flow/SKILL.md` substitui a tabela `| Papel | Rótulo | Slug |` por ponteiro ao ficheiro + grupos:

   - juízo (lê `juizo`): grill-card, design-autor, design-critic, Assessment A, Assessment B
   - execução (lê `execucao`): apply-coluna, qa-gate, diff-reviewer, code-reviewer, busca no mesmo card, fecho-lote

   Lei = parâmetro `model` do Task nos dois caminhos, com o slug da faixa. Destape/resume de execução permanece no slug vigente de `execucao`. T16 / chat pai de lote usa o slug vigente de `execucao` (única excepção ao silêncio do picker). Needle `composer-2.5-fast` MUST NOT permanece no runbook (não é o mapa; é a proibição). MUST NOT cravar `cursor-grok-4.6-high` nem `composer-2.5` como lei na skill.

   Rejeitado: skill a continuar a ser a fonte dos slugs. Rejeitado: apagar o needle `composer-2.5-fast`.

4. **Agent files: pin YAML continua redundante.** `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` mantêm `readonly: true` e `model: <execucao.slug>` (no Apply vigente = `composer-2.5`). Lei = Task `model` + ficheiro. MUST NOT `inherit`. Corpo (intervalo, FINDING, teto) intacto.

   Rejeitado: lei no cabeçalho YAML. Rejeitado: tirar o pin.

5. **Specs Cursor e kaizen apontam ao mapa vigente.** Deltas em `cursor-harness`, `covenant-flow`, `cursor-code-review`, `developer-tooling`, `llm-flow-emission`, `impeccable-design-gate`, `kaizen-continuous-improvement`. Cenários deixam de exigir o literal `cursor-grok-4.6-high` / `composer-2.5` como lei: exigem o slug da faixa no ficheiro. `/kaizen release` compara `proxy modelo: <papel> → <rótulo> (<slug>)` a `juizo`/`execucao` do ficheiro, não à tabela cravada na skill. Formato do proxy não muda. Specs dos outros clientes intocadas.

   Rejeitado: capability nova. Rejeitado: kaizen a continuar a ler a tabela na skill.

6. **Goldens lêem o ficheiro.** Asserts em `scripts/process-fsm/test_*.py` que needleiam o slug vigente na skill passam a `yaml.safe_load` de `.cursor/model-map.yaml`. Needle `composer-2.5-fast` MUST NOT permanece (literal na skill). Pin dos agent files compara-se a `execucao.slug`. MUST NOT `test_card_1017_*` como aceite. MUST NOT editar `subagent_stop.py` / `process-fsm.yaml` / Guard.

   Rejeitado: parser de usage. Rejeitado: golden novo como aceite do card.

7. **Lei que não muda (só a fonte do slug).** Sem `inherit`. Ficheiro em falta, YAML ilegível, chave em falta, ou slug em `forbid` / recusado pelo host = recusa visível; MUST NOT omitir `model`; MUST NOT retry com `inherit` ou com slug de `forbid`. Destape/resume de execução permanece no slug vigente; host a facturar `composer-2.5-fast` (ou outro `forbid`) = aborto + spawn novo com `execucao.slug` e prompt autocontido (`resume` não aceita `model`). Troca de modelo = sessão nova (#430); spawns em voo ficam no slug antigo. Git não força picker do pai. Isolamento / destape needles / sidecar / Q2–Q6 / teto 1+1 intactos.

   Rejeitado: inherit silencioso quando o ficheiro falta. Rejeitado: aceitar follow-up fast.

8. **Pin `v1.1.16` não sobe.** Apply = peles Cursor (`model-map.yaml`, `harness.mdc`, skill `covenant-flow`, agent files, kaizen skill, specs, goldens). Overlay `clients.*.auto` intocado. Stubs `.grok/` `.opencode/` `.dsh/` intocados (continuam inherit, ≤8 linhas, sem copiar o mapa).

   Rejeitado: dual-write. Rejeitado: aresta/evento/hook/`enabled_tools`.

## Prototype

N/A — harness Cursor; ausência de superfície; nunca rota de catálogo. Sem HTML. Sem `frontend/public/prototypes/`. Nunca emprestar `/monitor` `/favorites` `/combo/discovery` `/combo/select` nem landing. Impeccable / Playwright / `DESIGN.md` = N/A justificado.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana (Aprovação de Design → Pronto para Dev) permanecem.

## Apply contract

- `.cursor/model-map.yaml`: conteúdo exacto da D1.
- `.cursor/rules/harness.mdc`: corpo exacto da D2 (5 linhas não-vazias após o frontmatter; orçamento 4–12).
- `.cursor/skills/covenant-flow/SKILL.md`: D3 (agrupamento; ponteiro ao ficheiro; sem slugs cravados; needle `composer-2.5-fast` MUST NOT; destape/resume e T16 leem `execucao`). MUST NOT crescer `AGENTS.md`. MUST NOT dual-write stubs.
- `.cursor/agents/diff-reviewer.md` e `code-reviewer.md`: pin YAML = `execucao.slug` do ficheiro; `readonly: true` intacto; corpo intacto.
- `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` compara `proxy modelo:` ao mapa vigente no ficheiro.
- Specs delta desta change. Isolamento / destape / sidecar / Q2–Q6 / teto 1+1 / onda no mesmo turno **não** se reabrem.
- Goldens existentes que partirem (literal de slug na skill) MAY ser retunados para ler o ficheiro. MUST NOT `test_card_1017_*`. MUST NOT editar `subagent_stop.py`.
- Pin citado permanece `v1.1.16`. Overlay intocado.

## Risks / Trade-offs

- [Pai spawna sem Read do ficheiro] → recusa visível se o slug não bater; skill aponta o path. Mitigação: goldens exigem o ponteiro na skill e o ficheiro no git.
- [Skill ainda contém `composer-2.5-fast`] → aceite: é o needle MUST NOT, não o mapa.
- [Pin YAML dos agent files desalinha do ficheiro] → golden compara os dois; lei continua a ser o Task `model`.
- [Operador muda o YAML a meio de um spawn] → #430: sessão nova; spawns em voo ficam no slug antigo.
- [Golden em `scripts/process-fsm/test_*.py` parte] → retunar o assert para ler o ficheiro; pin não sobe.

## Migration Plan

Peles Cursor no Apply desta branch. Sem migrate de dados. Rollback = reverter o ficheiro e as peles. Stubs dos outros clientes não migram. Pin permanece `v1.1.16`.

## Open Questions

Nenhuma. Fronteira de operador vazia; *como* fechado acima. Não reabrir Qs do grill.

## Design Critique

Sem-tela. Crítico: [design-critic 1017](20ca2e88-7325-419d-a6fb-969d1853b33b). Autor: [design-autor 1017](ac2b6917-2081-49c1-8818-70dc5627886c).

**P0:** nenhum

**P1:** nenhum

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):**
- Corpo exacto de `harness.mdc` (5 linhas)
- Goldens a `yaml.safe_load` do mapa; MUST NOT `test_card_1017_*`
- Pin YAML dos agent files = `execucao.slug` (lei = Task `model`)
- Pin overlay permanece `v1.1.16`; needle `composer-2.5-fast` fica MUST NOT, não mapa

**Disposition:** P3 → Apply. Sem rework. Prototype N/A.

**Tokens (rubrica):** `UI impact: none` · `live_route: N/A` · `surface: new`. Justificativa: harness Cursor; ausência de superfície; nunca rota de catálogo.

Spawns: 2
proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: design-critic → Grok 4.6 (cursor-grok-4.6-high)
