# Design — card-440-card-close-todos-session-title

## Context

Sessão "Casual greeting" 4.1M tokens $0.38 sem título descritivo (F-4); reincidência (2ª auditoria) de todos `in_progress` eternos (card-399) e comentário OpenSpec duplicado no card #413/#385 (família #423 — F-5).

## Escopo

- `/opsx:verify`/Done exige todos `completed` (0 todos `in_progress`/`pending` em sessões de cards Done).
- Helper `publish-openspec-card-artifacts` atualiza gist/comentário existente em vez de republicar (sinergia #423).
- Sessões com custo > $0.10 têm título descritivo (card/contexto).
- Elevar #423 de P2 para P1.

## UI impact

`UI impact: none` — fluxo OpenSpec/auditoria/helper; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — Todos completos como gate do `/opsx:verify`.** O verify consulta o estado de todos das sessões associadas ao card (`opencode.db`, read-only) e exige `completed`; pendentes = blocker com lista. Alternativa (confiança no relato do agente) foi o padrão que falhou em 2 auditorias.
- **D2 — Título descritivo para sessões caras.** Regra: sessões com custo > $0.10 (ou produção relevante) recebem título com card/contexto; auditoria kaizen valida. Alternativa (renomear retroativamente) depende de ferramenta; regra vale para sessões novas.
- **D3 — Publicação única do comentário OpenSpec.** Vínculo direto com #423: helper com `--gist-id` atualiza gist/comentário existente; sem duplicação. Implementação única atende ambos (implementar #423 e validar aqui).
- **D4 — Elevar #423 a P1.** Ação de PO no board (mudança de label/prioridade do card #423), refletindo a reincidência do achado.

## Riscos

- [Gate de todos completos bloqueia fechamentos por sessões legadas com todos pendentes] → Mitigação: o check aplica às sessões da release/card ativo; sessões legadas são classificadas na auditoria, não no gate de cards novos.
- [Custo > $0.10 como limiar arbitrário] → Mitigação: limiar razoável para sessão de trabalho ativa (cards normais ficam abaixo); auditoria reporta custo real junto.
- [Mudança de prioridade #423 sem aprovação] → Mitigação: elevação é decisão PO registrada no card #440 (label priority); mantida como parte do escopo aprovado por Alan no fluxo do card.

## Design Critique

- **Escopo**: fecha F-4/F-5 com gates verificáveis no verify/Done e na auditoria, e ação PO de priorização.
- **Regressão de produto**: nenhuma — processo.
- **Riscos operacionais**: dependência de leitura do `opencode.db` no verify (read-only, já usada pela auditoria); mitigado por declaração de fonte indisponível.
- **Pendências não bloqueantes**: renomear sessões antigas é inviável; regra vale para novas.
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
