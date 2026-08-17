# Design: Divergência board/issue em rename pós-Done — nota + warn no guard

## Context

No #463, o título do board divergiu do título da issue após rename pós-`Done`; `Title` de item vinculado a issue não é editável via API Projects v2, então a sincronização foi registrada por nota no card sem fluxo documentado. O `release-guard audit` não detecta essa divergência hoje.

UI impact: **none** (doc de processo + check no guard; nenhuma superfície visual).

## Goals / Non-Goals

**Goals**
- Documentar no `AGENTS.md` o fluxo de rename de issue com card no board (nota de divergência obrigatória no card, motivo + aprovação).
- `release-guard audit` emite warn quando board title ≠ issue title sem nota de divergência.
- Nota do #463 preservada como registro histórico.

**Non-Goals**
- Não sincronizar títulos automaticamente (API não permite editar título de item de issue no board).
- Não mudar modos `pre`/`post` (warn somente em `audit`).

## Decisions

### D1 — Detecção: `gh project item-list` (title do card) vs `gh issue view` (title da issue)
Para cada card vinculado a issue do repo, compara `content.title` (issue) com o `title` do item do board. Divergência → procurar nota de divergência nos comentários do card (regex por "divergência"/"divergencia" + padrão `## Nota de divergência` ou similar documentado no AGENTS.md).
- Alternativa: usar `gh api` com GraphQL de items do board — mais frágil e sem ganho; `item-list` JSON já contém ambos os títulos. Rejeitado.

### D2 — Formato da nota de divergência (contrato auditável)
Documentar formato canônico da nota no AGENTS.md: comentário no card contendo `Nota de divergência` + motivo + aprovação (ex.: `Aprovado por: Alan`). O guard procura esse padrão no texto dos comentários.
- Alternativa: campo customizado no board para divergência — adicionaria campo novo; rejeitado (comentário é auditável e não muda o schema do board).

### D3 — Warn em `audit` apenas
Igual ao card kaizen irmão (#481): check roda somente no modo `audit`, não muda pre/post.

## Risks / Trade-offs

- [Nota postada com redação diferente do padrão não é reconhecida] → Mitigação: padrão documentado e simples (`Nota de divergência`); falso negativo vira warn informativo, não blocker.
- [Cards sem issue vinculada não são verificados] → Mitigação: check só aplica a itens com `content.type == Issue`; resto fora de escopo.

## Migration Plan

1. Documentar fluxo de rename no `AGENTS.md` (seção Kanban/board).
2. Adicionar bloco `board_issue_title_sync` ao guard (modo `audit`).
3. Rodar `scripts/release-guard audit` e validar que o #463 aparece como divergência com nota (sem warn) e que um card sem nota dispara warn.
4. Rollback: remoção do bloco não afeta pre/post.

## Open Questions

- Formato exato da nota: `Nota de divergência` com `Motivo:` e `Aprovado por:` — suficiente? (proposta; validar com Alan na aprovação de design).

## Prototype

**N/A** — mudança de documentação (`AGENTS.md`) + check de diagnóstico no `release-guard audit`; nenhuma superfície visual nova ou alterada.

## Impeccable

- `Impeccable Brief`: N/A — `UI impact: none` (justificativa: doc de processo + check de script; zero superfície visual).
- `Impeccable Critique`: N/A — sem superfície visual para criticar.
- `Impeccable Audit`: N/A — sem UI para acessibilidade/performance/responsividade/theming.
- `Impeccable Trace`: N/A — nenhum CLI/payload de UI aplicado.

## Design Critique

**Escopo:** 1) regra de rename documentada no `AGENTS.md` (nota de divergência obrigatória no card); 2) bloco `board_issue_title_sync` no `release-guard audit` (warn quando board title ≠ issue title sem nota).

**Achados por dimensão:**
- **Escopo:** claro e enxuto (S). Check restrito ao modo `audit` — sem regressão em `pre`/`post`. OK.
- **Regressão de produto:** nenhuma superfície de produto afetada; regra documental alinha `AGENTS.md` com comportamento observado (rename pós-Done no #463). O spec `board-issue-title-sync` foi atualizado via delta (MODIFIED) mantendo o requisito de troca de modelo de subagent intacto. OK.
- **Riscos operacionais:** falso negativo se a nota usar redação fora do padrão → warn informativo (não blocker), mitigado por formato canônico simples (`Nota de divergência` + `Motivo:` + `Aprovado por:`). Check aplica-se somente a itens vinculados a issues. OK.
- **Superfície visual:** confirmado `UI impact: none` — nenhum componente, rota ou estilo alterado. Nenhuma superfície visual ficou sem classificação. OK.

**Correções realizadas:** nenhuma necessária após a crítica (padrão da nota e escopo por tipo Issue já definidos no design).

**Pendências não bloqueantes:** formato canônico da nota é proposta; Alan pode ajustar a redação na aprovação — mudança de formato não afeta a implementação (regex simples, documentado).

**Design Agent verdict: PASS** — `UI impact: none`, sem achados bloqueantes, formato da nota validável por Alan na aprovação.
