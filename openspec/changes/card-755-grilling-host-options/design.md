## Context

Card [#755](https://github.com/oalansilva/crypto/issues/755) (kaizen P2 Operacao). Briefing = body grelhado (fronteira vazia, rodada 1). Não reabre [#667](https://github.com/oalansilva/crypto/issues/667) (porta `grill-card`) nem [#668](https://github.com/oalansilva/crypto/issues/668) (adapters / gerador de stubs).

Hoje a TUI do host só pinta `options[]` como linhas escolhíveis. Se a lei ficar só no markdown vendor (`❓` corpo + `➡️` recomendação) ou se o **pai** no relaying reapresentar só a recomendada, o card colapsa. O operador confirma a seta ou escreve Other.

**UI impact: none.** Skills/runbook/specs/testes de processo. Nenhuma superfície de produto (nenhuma rota, shell, componente ou copy). Prototype N/A. Impeccable N/A neste card. T7 permanece.

## Goals / Non-Goals

**Goals:**

- Q fechada: N≥2 alternativas **reais** no card da ferramenta do host, nos dois clientes; recomendada primeiro com `(Recommended)`; Other não conta no N.
- Q aberta: markdown e/ou Other; **proibido** `options[]` fictícias.
- Fallback markdown Matt: escolhas no **corpo**; `➡️` só recomenda.
- Relaying: pai chama a ferramenta do host com as N options que o filho listou; não colapsa.
- Comentário canônico idempotente.
- Lei em `grill-card` + uma linha de relay no `alan-workflow`. Vendor Matt e stubs Grok intactos.

**Non-Goals:**

- Reescrever `.cursor/skills/grilling/SKILL.md`.
- Mudar TUI vendor (Grok/Cursor).
- Gate/hook/evento na FSM; mexer `.cursor/process-fsm.yaml`.
- Reabrir #667/#668; alterar `scripts/process-fsm/grok_stubs.py`; nomear a ferramenta nos stubs `.grok/skills/*`.
- Dual-write Hermes / `~/.codex`.
- Sessão real Grok+Cursor como gate de QA / Done técnico.
- `AGENTS.md` always-on não cresce.

## Decisions

1. **Lei no adapter `grill-card`, não no vendor Matt.**  
   `.cursor/skills/grilling/SKILL.md` permanece a cópia Matt (`❓` corpo com escolhas + `➡️` recomendação). A lei dos dois clientes mora em `.cursor/skills/grill-card/SKILL.md`. Alternativa rejeitada: patchar o vendor para falar da TUI — quebraria a cópia e #667.

2. **Q fechada = `options[]` com N≥2 reais.**  
   Cada pergunta da fronteira com alternativas mutuamente exclusivas MUST listar **todas** em `options[]`. N conta só alternativas reais; Other automático do host **não** conta. Recomendada = primeira option; label com `(Recommended)` (padrão já usado em `openspec-continue-change`). Proibido 1 option só. Cursor: `AskUserQuestion`. Grok: `ask_user_question`. Alternativa rejeitada: 1 option + Other como “segunda via”.

3. **Q aberta = sem `options[]` fictícias.**  
   Texto livre: markdown e/ou Other do host. Proibido inventar A/B só para o card aparecer. Alternativa rejeitada: sempre fechar a Q com opções dummy.

4. **Fallback markdown Matt só se o host tool faltar.**  
   Corpo da Q fechada lista as escolhas; `➡️` é só a recomendação. Proibido só a seta. A TUI vendor **não** muda neste card.

5. **Dump filho→pai (residual fechado aqui, não reentrevista).**  
   O filho isolado **não** chama a ferramenta do host (o operador está no chat do pai). Cada Q fechada que o filho devolve MUST listar as alternativas A/B/… (N≥2) **e** a recomendação, na ordem em que o pai deve pintar. O pai mapeia **1:1** para `options[]` na mesma ordem, recomendada primeiro com `(Recommended)`. Não colapsa à `➡️`. Q aberta: o filho não manda `options[]`; o pai não inventa. Forma do dump (já usada na prática):

   ```
   Q<n>. <título>
   <corpo>
   Opções:
   - <label A> (Recommended)
   - <label B>
   - …
   ```

   Alternativa rejeitada: filho devolve só o bloco Matt e o pai extrai a seta.

6. **Quem chama o host = o pai → delta mínimo `cursor-harness`.**  
   O cenário de relay **não** cabe só em `grill-card`: a linha nova é no runbook do orquestrador. `.cursor/skills/alan-workflow/SKILL.md` seção Grill-card ganha **uma linha**: o pai chama a ferramenta do host com **todas** as options da Q fechada e não colapsa à recomendada. Spec `cursor-harness` ganha só esse cenário. Sem delta `process-harness`. Sem `enabled_tools` / evento / hook.

7. **Stubs Grok e gerador #668 intactos.**  
   `.grok/skills/grill-card/` e `.grok/skills/grilling/` continuam “MUST Read o canônico”. **Não** nomear `ask_user_question` / `AskUserQuestion` nos stubs. **Não** editar `scripts/process-fsm/grok_stubs.py`.

8. **Comentário canônico idempotente.**  
   Texto exato: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` No máximo um por issue. Fronteira reabre → não postar segundo. Fronteira zera de verdade: se o existente já é o texto exato, deixar; se o texto está errado, editar/minimizar o existente. Neste #755 já há um comentário canônico prematuro — Apply/grill **não** postam outro.

9. **Needles no pytest; sessão real = Homologado.**  
   Apply/QA estendem `scripts/process-fsm/test_grill_card.py` (e/ou arquivo novo no mesmo dir). Needles: nomes das ferramentas, `N≥2`, Other não conta, vendor Matt intacto (sem nomes de ferramenta), linha de relay no `alan-workflow`, stubs Grok sem nome de ferramenta. Sessão real nos dois clientes confirma N≥2 no card = Homologado (Alan), **não** gate de QA.

10. **Este card é `UI impact: none`.**  
    Sem Impeccable/Playwright/protótipo. Crítica isolada: escopo, regressão de produto/processo, riscos operacionais, ausência de superfície. Snapshot N/A justificado.

## Apply contract

- Editar só `.cursor/skills/grill-card/SKILL.md` e **uma linha** na seção Grill-card de `.cursor/skills/alan-workflow/SKILL.md`, mais os deltas OpenSpec e os testes listados nas tasks.
- Zero `frontend/src/`, zero produto `backend/`, zero `.cursor/process-fsm.yaml`, zero `scripts/process-fsm/grok_stubs.py`, zero stubs `.grok/skills/*`, zero `.cursor/skills/grilling/SKILL.md`.
- `grill-card`: Q fechada N≥2 na ferramenta do host; recomendada primeiro `(Recommended)`; Other não conta; Q aberta sem options fictícias; fallback Matt com escolhas no corpo; filho devolve opções listadas (dump D5); comentário canônico idempotente; deixar explícito que **quem chama** `AskUserQuestion` / `ask_user_question` é o pai.
- `alan-workflow` Grill-card: uma linha — pai chama o host com **todas** as options da Q fechada e não colapsa.
- Pytest (`scripts/process-fsm`, allow-list): needles abaixo. Não implementar pytest neste Design; Apply escreve os testes.
- Needles explícitos (strings):
  - `AskUserQuestion` e `ask_user_question` em `.cursor/skills/grill-card/SKILL.md`
  - `N≥2` (ou equivalente `N>=2` se o ficheiro não usar ≥) em `grill-card`
  - Other não conta no N (`não conta` junto de `Other`) em `grill-card`
  - `.cursor/skills/grilling/SKILL.md` ainda contém `❓` e `➡️` e **não** contém `AskUserQuestion` nem `ask_user_question`
  - seção Grill-card de `alan-workflow` contém a linha de relay (`todas as options` / não colapsa)
  - `.grok/skills/grill-card/SKILL.md` e `.grok/skills/grilling/SKILL.md` **não** contêm `AskUserQuestion` nem `ask_user_question`

## Prototype

N/A — `UI impact: none`. Nenhuma rota, shell, componente ou copy de produto. Harness/skills/docs de processo. Impeccable N/A (justificativa: sem superfície visual nova ou alterada).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Risks / Trade-offs

- [Modelo ignora a skill e manda 1 option] → contrato curto e explícito no canônico + linha no pai; needles não provam o TUI.
- [TUI trunca `description`] → o **label** carrega o nome da alternativa.
- [Other automático parece terceira via] → a lei diz que não conta no N≥2.
- [Filho chama o host tool] → D5/D6: filho devolve dump; pai chama. Needle de relay no `alan-workflow`.
- [Comentário duplicado em #755] → D8: idempotente; não postar outro.
- [Relaying colapsa de novo] → spec `cursor-harness` mínima + linha única no runbook, não um segundo protocolo.

## Migration Plan

Apply na branch `card-755-grilling-host-options`. Sem migração de dados. Rollback = reverter as duas skills + testes. Cards já grelhados não são re-grelhados.

## Open Questions

Nenhuma. Dump filho→pai = D5. Delta `cursor-harness` = D6 (mínimo, exigido pela linha de relay no `alan-workflow`).

## Design Critique

- P0: nenhum.
- P1: nenhum.
- P2 residual (não bloqueia): needles não cobrem “filho não chama o host” / dump D5 / idempotência; `cursor-harness` assume host sempre disponível (fallback Matt fica no filho); `test_grill_card.py` ainda tem needle `bound_card` (Apply conserva/reescreve no 3.1).
- P3: schema Grok é `questions[].options[]`; batch da rodada não especificado; “Impeccable N/A” = detector/Playwright, não skip de A/B.
- Disposition: recorte alinhado ao issue; T1/T7/FSM/vendor/stubs intactos; P2 vai para Apply/Homologado.
- Prototype: N/A — `UI impact: none` (sem rota, shell, componente ou copy).
- Snapshot: N/A justificado (sem superfície). Evidência A/B: `.impeccable/critique/755-card-755-grilling-host-options-A.md` e `-B.md`.
- Design Agent verdict: PASS.
