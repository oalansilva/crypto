# Design — card-439-vision-path-check

## Context

Delegação visual do #413: 4× `File not found: /tmp/opencode/bl413/...` + re-delegações do mesmo prompt sem gerar os crops, e 3× webfetch 404 em URLs inexistentes do docs.github.com (F-3 da auditoria 2026-08-09). Cada respawn desperdiça custo e atrasa o QA visual.

## Escopo

- Skill/regra versionada: antes de passar arquivos ao vision, confirmar existência (`ls`/glob).
- Em falha de leitura do subagent, gerar o artefato antes de respawnar.
- Proibido webfetch em URLs não confirmadas/inexistentes no fluxo de QA visual.
- Critério: 0 erros `File not found`/`webfetch 404` em sessões de QA visual na próxima release.

## UI impact

`UI impact: none` — regra de fluxo do opencode (delegação ao vision); nenhuma superfície visual de produto. Prototype: `N/A`.

## Decisões

- **D1 — Path-check obrigatório na delegação.** O fluxo (AGENTS.md + skill de QA visual) exige `ls`/glob do arquivo antes de passá-lo ao vision; path inexistente bloqueia a delegação. Alternativa (deixar o vision reportar erro) é exatamente o padrão a eliminar.
- **D2 — Gerar antes de respawnar.** Em falha de leitura do subagent, o fluxo gera/recria o artefato (crop/screenshot) no caminho esperado e só então re-delega uma vez; sem repetição do mesmo prompt com mesmo path.
- **D3 — Validação de URL antes de webfetch.** URLs de documentação/externa só são acessadas após confirmação de existência (ex.: `gh api` para docs do GitHub, ou omitir o fetch se desnecessário).

## Riscos

- [Path-check adiciona passo manual e atraso] → Mitigação: é um `ls`/glob rápido; benefício (zero respawn) supera o custo.
- [Artefato gerado no caminho errado por convenção diferente] → Mitigação: fluxo define o caminho canônico (`/tmp/opencode/<slug>/`) antes de delegar; gerador do artefato escreve nesse caminho.

## Design Critique

- **Escopo**: elimina o padrão recorrente de respawn por path inexistente com regra simples e verificável.
- **Regressão de produto**: nenhuma — fluxo do opencode.
- **Riscos operacionais**: risco residual de convenções de caminho entre sessões; mitigado por caminho canônico documentado.
- **Pendências não bloqueantes**: nenhuma.
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
