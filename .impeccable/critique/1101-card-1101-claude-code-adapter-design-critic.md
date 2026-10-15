# Snapshot de crítica — #1101

Data: 2026-10-13. Papel: design-critic; faixa: juizo. Rodada sem tela: um autor, um crítico e um rework (teto 1+1+1). Snapshot de conteúdo; não certifica execução runtime, T5 ou aprovação humana.

## Contexto

- Card: oalansilva/crypto#1101, «Harness: adapter Claude Code — fluxo completo com a mesma FSM, skills e seleção de modelos».
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1101-claude-code-adapter`; change `card-1101-claude-code-adapter`.
- Exceção registrada: autor, crítico e rework nasceram no Claude Code, que ainda não é cliente do fluxo; `model_selection.py` recusa `--client claude`, então não houve captura. Autorizado por Alan. Observado: autor em `claude-opus-5-5` effort medium (sem `effort` explícito); crítico e rework pedidos em Opus 5.5 effort high.

## Validações do crítico

- `design_clone_gate`: `UI impact=none`, `live_route=N/A — harness de processo, sem tela`, `surface=none`; `clone_gate_ok=True`.
- `proposal.md` copia Problema/História/Entra/Não entra do body (diff sem diferença).
- Cada critério observável do Entra tem requisito + cenário; T0–T18 e gates humanos intactos; nada duplica a lei em `.claude/`.
- `openspec validate card-1101-claude-code-adapter --strict`: válido.

## Achados (veredito: REWORK)

- P1-1 (contrato): oficialização dentro do #1101 sem aresta legal com piloto empilhado → disposition: Alan moveu a oficialização para card de seguimento; resolvido no rework (adapter não oficial).
- P1-2 (contrato): cenário "integrado sem piloto" contraditório e sem mecanismo → resolvido: cenário reescrito ("pai não chama `integrar_develop`"), exceção local ao T14 no mesmo turno, item `pilot_evidence` no checklist postqa.
- P2-1 (contrato): base do review e rebase dos cards empilhados → resolvido: review sobre HEAD revisado do #1101; prova `patch-id`/digest após rebase; só qa-gate; conflito = causa visível.
- P2-2 (contrato): esforço por filho lido do campo errado → resolvido: só `tool_input.effort`; ausente = `unsupported_schema`; `effort` explícito por spawn.
- P2-3 (contrato): divergência de modelo detectada tarde → resolvido: verificação antes da primeira escrita do filho; `model_mismatch`.
- P3 (detalhe de Apply): renderer/pin do AGENTS.md; agents curtos/ponte; `/opsx:*` via pontes; precedência `CLAUDECODE=1` aninhado; specs base "five clients"; "hooks sem diálogo em `-p`" a provar → aceitos em `design.md` § P3 aceitos.

## Decisões de Alan incorporadas

Piloto empilhado; janela curta com demais cards pausados; troca de cliente provada por segundo card real; oficialização em card de seguimento.
