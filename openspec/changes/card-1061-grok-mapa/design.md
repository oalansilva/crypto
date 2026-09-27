## Context

Card [#1061](https://github.com/oalansilva/crypto/issues/1061). Briefing = issue grelhado (Problema, História, Entra, Não entra), copiado no `proposal.md`. Status=Design. Tupla lida: `(q=Design, bound_card=1061, q_git=card-1061-grok-mapa)`. Sem-tela. Zero rota de produto.

Facto vigente: `.cursor/model-map.yaml` tem faixas de topo do Cursor (`juizo.slug=cursor-grok-4.6-high`, `execucao.slug=composer-2.5`) e sub-blocos `codex` (`gpt-6-sol` / high, `gpt-6-luna` / max). Não tem `juizo.grok` nem `execucao.grok`. O stub Grok (`.grok/skills/*/SKILL.md`, gerado por `scripts/process-fsm/grok_stubs.py`) manda mapear Task `inherit` para `spawn_subagent` inherit. O runbook canónico `.cursor/skills/covenant-flow/SKILL.md` ainda diz `Revisores no Grok MUST NOT neste card.` O host Grok só aceita `grok-4.5`, `grok-4.6`, `grok-4.7` e `grok-4.7-build-fast`. Spawn com slug do Cursor ou slug inválido é recusado. Fechar release no runbook exige o slug de topo `execucao` (Composer); no Grok isso deixa o fecho de fora.

UI impact: none
live_route: N/A
surface: new
Mapa de modelos do harness, sem rota de produto. Nunca `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` nem a landing.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Par do Grok no mapa compartilhado: `juizo.grok` = Grok 4.7 (`grok-4.7`); `execucao.grok` = Grok 4.6 (`grok-4.6`). O pai no Grok lê essas chaves. Não omite `model`. Não herda o picker. Não lê o par de topo do Cursor nem `*.codex`.
- Cursor permanece juízo `cursor-grok-4.6-high` e execução `composer-2.5`. Codex permanece `gpt-6-sol` / high e `gpt-6-luna` / max.
- Slug que o host não aceita, ou par `grok` em falta, continua falha visível. Sem troca silenciosa.
- Os dois revisores no Grok nascem em `grok-4.6`. A frase que ainda os recusa deixa de valer.
- No Grok, fechar release (T16 e `fecho-lote`) usa `grok-4.6` e entra neste card.
- Filho de execução no Grok retomado noutro modelo que não `grok-4.6`, inclusive `grok-4.7-build-fast`, falha e nasce de novo em `grok-4.6`.

**Non-Goals:**

- Trocar os pares do Cursor ou do Codex. OpenCode e dsh continuam inherit.
- Publicar o commit `b2cac2d5` por push forçado. Mover este card para Todo.
- Reabrir #1017, #904 ou #939 como pacote deste card. O fecho de release no Grok entra aqui, como o Entra diz.
- Rota de produto, HTML, protótipo, Impeccable pipeline, `DESIGN.md`. Emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` ou a landing.
- Crescer `AGENTS.md`. Aresta, evento, hook ou `enabled_tools` novo na FSM. Subir o pin `v1.1.19`. Overlay `clients.*.auto` (permanece `false`). Dual-write do runbook em `.grok/rules/`, `.opencode/` ou `.dsh/`.
- Mapa por papel (grill ≠ design-autor). Parser de usage. Modo Auto.

## Decisions

1. **Par do Grok = sub-bloco `grok` ao lado de `codex`, não faixa nova e não mapa por papel.** O ficheiro continua `.cursor/model-map.yaml`. Apply acrescenta, sem alterar label/slug de topo nem o bloco `codex` nem `forbid`:

   ```yaml
   juizo:
     label: Grok 4.6
     slug: cursor-grok-4.6-high
     codex:
       label: GPT-6 Sol
       slug: gpt-6-sol
       effort: high
     grok:
       label: Grok 4.7
       slug: grok-4.7
       effort: high
   execucao:
     label: Composer 2.5
     slug: composer-2.5
     codex:
       label: GPT-6 Luna
       slug: gpt-6-luna
       effort: max
     grok:
       label: Grok 4.6
       slug: grok-4.6
       effort: high
   forbid:
     - composer-2.5-fast
     - inherit
   ```

   `grok` fica depois de `codex` na mesma faixa. Os dois blocos `grok` levam `effort: high`. O campo fica no mapa; passar o effort ao filho depende de o host expor o argumento. Enquanto não expuser, o pai não omite o campo do mapa e não finge que o enviou. Papéis continuam na skill: juízo (grill-card, design-autor, design-critic, Assessment A, Assessment B) lê `juizo.grok`; execução (apply-coluna, qa-gate, diff-reviewer, code-reviewer, busca no mesmo card, fecho-lote) lê `execucao.grok`.

   Rejeitado: ficheiro `.grok/model-map.yaml`. Rejeitado: o pai Grok ler `juizo.slug` / `execucao.slug`. Rejeitado: herdar o picker quando o sub-bloco falta.

2. **Lei do spawn no Grok = parâmetro `model` do `spawn_subagent`.** O pai lê o mapa e passa o slug da faixa. Não omite `model`. Não herda o picker. Não faz troca silenciosa para o slug do Cursor, para o slug do Codex, nem para outro slug que o host aceite (`grok-4.5`, `grok-4.7` no lugar de execução, ou `grok-4.7-build-fast`). Host aceita só `grok-4.5`, `grok-4.6`, `grok-4.7`, `grok-4.7-build-fast`. Fora desse conjunto, ou par `grok` em falta / slug vazio / YAML ilegível = falha visível no chat; o filho não corre. `resolve_pair` / `pin_codex_map` em `codex_models.py` continuam a ler só `.codex` e MUST NOT apagar nem rejeitar `.grok`. `PIN_PAIRS` não muda.

   Rejeitado: hook novo ou aresta na FSM para impor o slug (Grok continua cooperativo; `clients.grok.auto` fica `false`). Rejeitado: retry com `inherit`.

3. **A frase que recusa revisores no Grok deixa de valer.** Sai de `.cursor/skills/covenant-flow/SKILL.md` o texto exacto `Revisores no Grok MUST NOT neste card.` Deixam de ser lei, nos deltas, `Reviewers on Grok MUST NOT be listed as a happy path of this change` e `Reviewers on Grok MUST NOT be used by this change`. No Grok, `diff-reviewer` e `code-reviewer` nascem com `model` = `execucao.grok.slug` (`grok-4.6`). No Cursor, os mesmos papéis continuam em `execucao.slug` (`composer-2.5`) e MUST NOT passar a usar `grok-4.6`. O pin YAML de `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` permanece `model: composer-2.5` (pin redundante do Cursor). Isolamento, intervalo colado, onda no mesmo turno e teto 1+1 não se reabrem.

   Rejeitado: pin dos agent files Cursor = `grok-4.6`. Rejeitado: deixar a frase no runbook «porque o spec antigo ainda a tem».

4. **Fechar release no Grok é execução deste card.** No cliente Grok Build, T16 (`process_event fechar_release`) e o filho `fecho-lote` exigem chat pai em `execucao.grok` (`grok-4.6`). O filho `fecho-lote` leva `model` `grok-4.6`, prompt autocontido, sem `process_event`, sem commit/push, sem sidecar de destape. Pai em `juizo.grok` (`grok-4.7`) ou noutro slug recusa visível e não chama T16 neste chat. No Cursor, o fecho continua a exigir o slug de topo `execucao` (`composer-2.5`); um pai Cursor que não seja esse slug continua recusado. Não se exige que o pai Grok seja Composer. Não se reabre #939 como pacote.

   Rejeitado: fecho Grok adiado para outro card. Rejeitado: alargar o fecho Cursor ao slug `grok-4.6`.

5. **Retomada de execução no Grok fica em `grok-4.6`.** Facto da lei já vigente, aplicado ao par fechado: se o filho de execução (Apply, QA, os dois revisores, busca no mesmo card, `fecho-lote`) é retomado noutro modelo que não `grok-4.6`, inclusive `grok-4.7-build-fast`, esse run não conta. Falha visível. Nasce de novo com `model` `grok-4.6` e prompt autocontido. A agulha `composer-2.5-fast` MUST NOT do Cursor permanece. Não se acrescenta `grok-4.7-build-fast` a `forbid` (isso não cobre retomada em `grok-4.5` ou `grok-4.7`; a regra é igualdade com `execucao.grok.slug`).

   Rejeitado: aceitar o modelo rápido porque o host o aceita. Rejeitado: tratar isto como decisão nova de produto.

6. **Stub Grok deixa de mandar inherit; não copia o runbook.** `stub_body()` em `grok_stubs.py` substitui a linha de inherit por uma ponte ≤8 linhas de corpo. Texto da segunda linha de corpo:

   `No Grok, spawn_subagent passa model de juizo.grok ou execucao.grok em .cursor/model-map.yaml. Não omite model. Não herda o picker. Do not copy the runbook here.`

   (com os backticks do código à volta de `spawn_subagent`, `model`, `juizo.grok`, `execucao.grok` e do path, como na ponte actual). Regenerar `.grok/skills/**/SKILL.md`. A primeira linha continua `MUST Read` do canónico. Sem tabela de papéis. OpenCode e dsh não mudam. `AGENTS.md` e `.grok/rules/00-harness.md` não crescem. O runbook canónico é que diz qual faixa.

   Rejeitado: dual-write da tabela juízo/execução em cada stub. Rejeitado: deixar a linha `spawn_subagent` inherit «porque o canónico corrige depois».

7. **Runbook canónico ganha a cláusula Grok e aponta ao ficheiro.** `.cursor/skills/covenant-flow/SKILL.md` passa a dizer: no Grok, juízo lê `juizo.grok` e execução lê `execucao.grok`; não omite `model`; não herda o picker; revisores e `fecho-lote` são execução; fecho de release no Grok exige pai `grok-4.6`; retomada de execução fora de `grok-4.6`, inclusive `grok-4.7-build-fast`, não conta. A fonte do slug é o ficheiro, não uma segunda tabela cravada. Needle `composer-2.5-fast` MUST NOT permanece. `AGENTS.md` não cresce.

   Rejeitado: skill como segunda fonte de slug, paralela ao YAML.

8. **Kaizen compara o proxy ao par do cliente.** Linha já existente `proxy modelo: <papel> → <rótulo> (<slug>)`. No Grok, juízo compara-se a `juizo.grok` e execução a `execucao.grok`. Não é achado um revisor Grok em `grok-4.6` por não ser `composer-2.5`. Sem parser de usage e sem dashboard.

   Rejeitado: capability nova. Rejeitado: comparar todo o proxy ao par de topo do Cursor.

## Prototype

N/A — mapa de modelos do harness, sem rota de produto. Sem HTML. Sem `frontend/public/prototypes/`. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` nem a landing.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e de aprovação humana (Aprovação de Design → Pronto para Dev, só Alan) permanecem. Este autor não aprova T7.

## P3 aceitos (detalhe de Apply)

- Ordem dos bytes YAML desde que `grok` seja irmão de `codex`, depois do bloco `codex`, com label/slug da D1. Não reabre como P0/P1.
- Ler o YAML no pai (`Read`) ou num helper que não vire fallback. Contrato: o `model` do spawn é o slug do par; falta, vazio ou recusa do host falha visível. Sem hook novo.
- Nome do campo de runtime que observa o modelo retomado. Contrato: se o modelo observado da execução não é `grok-4.6`, o run não conta e nasce outro filho com `model` `grok-4.6`.

## Risks / Trade-offs

- [Stub ainda a dizer inherit] → D6 regenera os stubs; o canónico sozinho não chega se a ponte mandar inherit.
- [Pin Codex a reescrever o mapa] → `pin_codex_map` hoje não mexe quando `.codex` já está igual; D2 proíbe apagar `.grok`. Apply confirma que um pin idempotente preserva `grok`.
- [Spec Cursor «MUST NOT use Grok» a continuar a recusar revisores no cliente Grok] → deltas separam Cursor (`composer-2.5`) de Grok (`grok-4.6`).
- [Fecho Cursor a ficar mais frouxo] → a excepção `grok-4.6` é só no cliente Grok Build. Cursor continua Composer.
- [Comparação kaizen contra o par de topo] → D8. Sem isto, revisor Grok válido vira achado falso.

## Migration Plan

- Apply nesta branch (`card-1061-grok-mapa`, base `origin/develop` em `7393c3d3`), que é a `develop` do GitHub. Não enviar `b2cac2d5` com push forçado. Não mover Status.
- Rollback = reverter o sub-bloco `grok`, a cláusula do runbook e a linha do stub. Sem migração de dados.
- Pin permanece `v1.1.19`. Overlay intocado.

## Open Questions

Nenhuma. O par, os revisores como execução, o fecho de release como execução e a retomada fora de `grok-4.6` estão fechados no issue. Não reentrevistar.

## Design Critique

Sem-tela. Teto 1+1+1: 1 autor + 1 crítico + 1 rework. O rework é a decisão de Alan depois de devolver o card: os dois pares do Grok levam `effort: high`. Sem nova crítica. Snapshot: N/A. Prototype: N/A. HTML generated: N/A. HTML copied: N/A.

**Veredito do crítico: PASS** (antes do rework; zero P0/P1)

**P0:** nenhum
**P1:** nenhum
**P2:** nenhum

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):** 3, já no design
- Ordem dos bytes YAML, desde que `grok` seja irmão de `codex`.
- Ler o mapa no pai ou num helper, sem hook novo; falta ou recusa do host falha visível.
- Nome do campo de runtime da retomada; se o modelo observado não é `grok-4.6`, o run não conta.

**Disposition:** aceite. Rework do dono aplicado: `juizo.grok.effort` e `execucao.grok.effort` = `high`. O spawn deste host ainda não tem argumento `effort`; o mapa grava o campo e o pai não finge que o enviou. P3 fica para o Apply.

Spawns: 3
proxy modelo: design-autor → Grok 4.7 (grok-4.7)
proxy modelo: design-critic → Grok 4.7 (grok-4.7)
proxy modelo: design-autor (rework) → Grok 4.7 (grok-4.7)
