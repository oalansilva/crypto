## Context

A skill global `alan-workflow-ambientes` ainda manda OpenClaw e um mapa DEV/PROD incompleto. Agentes usam isso para escolher path, service e se podem mexer em PROD.

## Goals / Non-Goals

**Goals:**
- Mapa real: Cripto DEV/PROD, Clara DEV/PROD, Hermes por componente.
- OpenClaw só como histórico.
- Restart: `./restart` no Done DEV; intermediário direcionado; Hermes por componente.
- PROD fail-closed; release com evidência completa.
- Smoke read-only sem secrets.

**Non-Goals:**
- Migrar código de produto (isso é #553).
- Ligar workers de Discovery em PROD (#566).
- Apagar paths temporários sem autorização.

## Decisions

1. **Uma skill, mapa único.** Atualizar `~/.codex/skills/alan-workflow-ambientes/SKILL.md` e espelhos Cursor/opencode que apontam para o mesmo arquivo.
2. **Inventário no apply, não chute no design.** O design fixa a estrutura; números de porta/unit vivos são conferidos no apply com `systemctl`/`ss` read-only.
3. **UI impact: none.**

## UI impact

`none` — skill/docs de operação.

## Prototype

N/A. Justificativa: não há superfície de produto; Alan valida o texto da skill contra units reais.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Skill global fora do repo crypto] → OpenSpec no card documenta o contrato; apply edita a skill global e, se o repo ainda copiar trechos, alinha `AGENTS.md` só onde estiver falso.
- [Portas mudarem no host] → Apply faz smoke read-only e corrige o mapa; design não congela porta errada de memória.

## Migration Plan

1. Publicar OpenSpec no #554; aguardar Pronto para Dev.
2. Inventariar units/portas/URLs reais.
3. Reescrever a skill; smoke read-only.
4. QA visual do produto inalterada (baseline).

## Open Questions

Nenhuma.

## Design Critique

- Escopo: skill global de ambientes; sem UI de produto.
- Crítica isolada: PASS. Mapa real fica no apply com smoke read-only.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
