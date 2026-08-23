---
name: grill-card
description: "Grelha a história de um card em Em Refinamento no body do GitHub issue. Use when bound_card is set, Status=Em Refinamento, and Alan asks to grill/afiar or the issue body lacks the DoD sections. Not for Todo, Design, OpenSpec, or unbound sessions."
disable-model-invocation: false
---

# grill-card

Porta de refinamento **deste repo**. Primitivo: `.cursor/skills/grilling/SKILL.md` (vendor; fronteira, uma rodada, recomendação, fato ≠ decisão). Ledger = **body do issue**, não `CONTEXT.md`.

Não é `grill-with-docs`. Não é `to-spec`.

## Precondição

Só corre se **as duas** forem verdade:

1. `bound_card` = número do issue (sessão bound a `card-<id>-*`).
2. Project 1 `Status=Em Refinamento` **desse** issue.

Senão: recusar. Não editar issue de outro card. Não grelhar em Todo ou Design.

## Quando disparar

- **Sim:** Alan pede grelhar/afiar, **ou** o card bound está em Em Refinamento **e** o body não tem as 6 seções do DoD. Oferecer; não arrastar coluna.
- **Não:** automático em todo T0; não em Todo/Design; cards já nítidos (DoD completo) podem T1 sem grill.

## Como

1. Ler `.cursor/skills/grilling/SKILL.md` e aplicar o loop (árvore, fronteira, uma rodada, recomendação).
2. Fatos (código, specs, board): buscar com tools. Decisões: Alan responde. Uma rodada por turno; esperar.
3. Despejar no **body** do issue bound (PT-BR), via `gh issue edit`, as 6 seções do DoD:

   1. **Problema** — uma frase, quem sofre.
   2. **História** — Como / quero / para.
   3. **Entra** / **não entra**.
   4. **Vocabulário** — `Termo`: definição curta; `_Avoid:` sinônimos.
   5. **Critérios de aceite** — observáveis (Given/When/Then ou lista comportamental).
   6. **Riscos / perguntas abertas**.

4. Se a fronteira **não** zerou: o card **fica** em Em Refinamento. Não comentar o handoff T1. Não ir para Todo com furo bloqueante.
5. Se a fronteira **zerou** e o body tem as 6 seções: um único comentário canônico (exato):

   `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`

## Proibido

- `gh project item-edit` no campo Status
- `process_event priorizar` (T1 é só Alan)
- Write `CONTEXT.md`
- `docs/adr/`
- `/opsx:new`, `/opsx:ff`, `/opsx:explore`, `/opsx:apply` (e qualquer `/opsx:*`)
- Dual-write para Hermes, `/srv/knowledge/hermes-second-brain/skills/`, `~/.codex/skills/`
