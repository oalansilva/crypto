## Why

O guardrail anti-bypass do Design existe nas regras e no board, mas não é verificável no runtime: cards avançaram para implementação/QA com veredito `BLOCKED` (#384) ou sem qualquer passagem visível pelo gate de Design (#395). Sem evidência registrada, o processo não consegue auditar onde a aprovação falhou.

## What Changes

- Exigir no fluxo operacional que nenhum código seja aplicado sem evidência registrada de aprovação de Design (comentário de Alan ou arraste no board), inclusive em cards `UI impact: none`, remoções e tooling.
- Quando o veredito for `BLOCKED`, exigir registro da resolução no `design.md` (o que bloqueou, como foi resolvido, quem aprovou) antes de mover para `Pronto para Dev`/implementação.
- Adicionar checklist de gates no PR/commit de integração: o PR deve listar `design.md`/verdict mesmo para mudanças de tooling (validação em `/opsx:verify`).

## Capabilities

### New Capabilities

- `design-approval-evidence`: evidência obrigatória e verificável de aprovação de Design antes de qualquer implementação, incluindo resolução registrada de veredito `BLOCKED`.

### Modified Capabilities

- `multiagent-operating-standard`: o modelo operacional passa a exigir evidência registrada de aprovação de Design antes de `Pronto para Dev`, com resolução documentada de `BLOCKED`.
- `kaizen-continuous-improvement`: a auditoria passa a verificar a presença de evidência de aprovação (comentário/arraste) e de resolução de `BLOCKED` em cards fechados.

## Impact

- `AGENTS.md` e `rules.md`: regra explícita de evidência de aprovação antes de implementação.
- Fluxo OpenSpec `/opsx:verify`: checklist de gates.
- Template/fluxo de PR de integração: checklist com `design.md`/verdict.
- Sem mudanças de runtime, banco ou frontend.
