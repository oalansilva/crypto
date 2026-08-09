# Design — card-421-design-approval-evidence

## Context

Cards #384 e #395 avançaram para implementação/QA sem evidência de aprovação de Design: #384 com `Design Agent verdict: BLOCKED` (gate de dois critics bloqueado por igualdade de LLM não observável) seguido de "Implementação pronta para QA"; #395 sem qualquer passagem visível pelo gate (tooling tratado como isento). O guardrail existe no board e nas regras, mas não é verificável no runtime: nada impede `/opsx:apply` sem o gate.

Decisão de produto: tornar o gate verificável por evidência registrada — comentário de Alan no card ou arraste `Aprovação de Design -> Pronto para Dev` no board — e exigir resolução documentada de `BLOCKED` no `design.md`.

## Escopo

- `AGENTS.md`/`rules.md`: regra explícita — implementação só após evidência de aprovação; BLOCKED exige resolução registrada.
- Checklist de gates no PR/commit de integração e no `/opsx:verify`.
- Validação da evidência na auditoria kaizen (sinal "sem evidência de aprovação" e "BLOCKED sem resolução").
- Fora de escopo: automação de leitura do board para validar o gate (melhoria futura se o padrão recorrer).

## UI impact

`UI impact: none` — mudança exclusiva de processo/regras/validação de fluxo; nenhuma superfície visual nova ou alterada. Prototype: `N/A` (sem tela; a entrega é documental/fluxo).

## Decisões

- **D1 — Evidência = comentário de Alan OU arraste no board.** O arraste é a autorização canônica; comentário explícito de Alan serve de evidência auditável quando o arraste não é registrável via API. Alternativa (check automatizado do board) fora de escopo: dependeria de API de timeline/approval não exposta hoje.
- **D2 — BLOCKED exige seção de resolução no `design.md`** com causa, correção e aprovador, antes de `Pronto para Dev`. Alternativa (regressar para Design sempre) mantida como comportamento quando a resolução não for possível sem novo design.
- **D3 — Checklist de gates no PR e no `/opsx:verify`** (design.md/verdict/evidência de aprovação) mesmo para tooling. Alternativa (só docs) insuficiente porque o padrão recorrente passou por docs.

## Riscos

- [Falso negativo: comentário genérico sem arraste] → Mitigação: exigir menção explícita de aprovação/`actor` identificável; auditoria valida presença de evidência, não só texto.
- [Sobrecarga de regras sem ganho operacional] → Mitigação: checklist curto e integrado ao fluxo existente (`/opsx:verify`, PR de integração), sem nova camada de processo.

## Design Critique

- **Escopo**: cobre cards UI/não-UI, remoções e tooling, fechando os dois gaps auditados (#384/#395).
- **Regressão de produto**: nenhuma — mudança de processo sem efeito em runtime/frontend.
- **Riscos operacionais**: risco principal é o check manual depender de disciplina; mitigado por checklist no PR/verify e auditoria kaizen recorrente (2+ auditorias sem recorrência = critério de aceite).
- **Pendências não bloqueantes**: automação futura de leitura do board (registrada no card como fora de escopo).
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
