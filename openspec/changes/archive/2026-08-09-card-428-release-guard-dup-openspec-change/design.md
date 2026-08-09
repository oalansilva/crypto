# Design — card-428-release-guard-dup-openspec-change

## Context

O archive da change `card-420-kaizen-agent` na branch de release (main-side) seguido do sync back `main -> develop` (#426) adicionou `archive/2026-08-09-card-420-kaizen-agent/` sem remover `openspec/changes/card-420-kaizen-agent/`, deixando a change ativa e arquivada simultaneamente (F-1 da auditoria 2026-08-09). Corrigido manualmente (PR #427) sem automação.

## Escopo

- `release-guard post`: detectar change ativa em `openspec/changes/` com correspondente em `openspec/changes/archive/*/`; blocker com instrução de correção.
- Aplicar o mesmo check no fluxo de sync `main -> develop` pós-publicação.
- Fora de escopo: correção retroativa de duplicações existentes.

## UI impact

`UI impact: none` — script bash de guard; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — Detecção por correspondência de nome de pasta.** Compara `openspec/changes/<name>` com `openspec/changes/archive/*/<name>`; duplicação = blocker. Alternativa (comparar conteúdo/digest) mais custosa e desnecessária — a existência da pasta ativa + arquivada é o defeito observado.
- **D2 — Check no `post` e documentado no sync `main -> develop`.** O guard é a ferramenta existente; o fluxo de sync passa a rodá-lo (modo post) após o merge de sync. Alternativa (check separado no PR de sync) duplicaria lógica.
- **D3 — Instrução de correção no output.** Blocker lista o comando de remoção da pasta ativa (git rm) quando o conteúdo arquivado é idêntico, para execução consciente pelo agente.

## Riscos

- [Falso positivo por pasta com mesmo nome em archive mas conteúdo legítimo distinto] → Mitigação: instrução exige verificação de conteúdo/digest antes de remover; guard apenas sinaliza.
- [Sync futuro reintroduzir duplicação por merge] → Mitigação: check roda no `post` após todo sync de release (critério de aceite).

## Design Critique

- **Escopo**: fecha o F-1 com detecção automatizada, sem tocar no arquivamento em si.
- **Regressão de produto**: nenhuma — guard de processo.
- **Riscos operacionais**: blocker do `post` pode aparecer em releases com duplicações herdadas; mitigado por instrução clara de correção e escopo "fora de escopo" para retroativo.
- **Pendências não bloqueantes**: nenhuma.
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
