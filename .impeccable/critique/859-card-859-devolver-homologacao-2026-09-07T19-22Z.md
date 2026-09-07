# Snapshot — crítico isolado (sem-tela) · card #859 `card-859-devolver-homologacao`

- Card: #859 — kaizen: ao homologar, Alan precisa poder não aprovar e devolver o mesmo card
- Change: `openspec/changes/card-859-devolver-homologacao/`
- Critic: 1 isolado sem-tela (sem transcript do pai/autor; sem nested spawn)
- UTC: 2026-09-07T19-22Z
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-859-devolver-homologacao`
- Digest `design.md`: sha256 `bdac345c84aab0210bb1982bc86c1158e62c041eae46ce4fb26c196d8245fbbb` · 493 palavras · 3616 bytes · 46 linhas
- Issue: REST `GET /repos/oalansilva/crypto/issues/859` (não `gh issue view`); grelha no body q1–q4=A
- Write desta onda: só este ficheiro em `.impeccable/critique/**`

## Rubrica sem-tela

- **Escopo vs issue grelhado:** recorte só Done; destino Em desenvolvimento; motivo visível obrigatório; Homologado já promovido fora. Design D1–D7 + Non-Goals + spec T18 batem Entra/Não entra. Não reabre #852 produto, T6/T7, priorizar, desfazer Homologado, coluna à escolha.
- **Regressão de produto:** nenhuma tela. MUST NOT `backend/` `frontend/src/` HTML proto. Zero `frontend/public/prototypes/*859*`.
- **Riscos operacionais:** T18 só Alan + `motivo_visivel`; Agent/`process_event` reject; overlay fura só o gesto humano; pós-T18 Write continua I1 (não develop/main); não T8; caminho existente até Done; T15 intacto; Homologado sem inversa.
- **Tokens parseáveis:** `design.md` L3–L5 linhas próprias — `UI impact: none` / `live_route: N/A card de processo sem tela` / `surface: new`. Forma canónica sem-tela (ausência + justificativa; `surface: new` = não-existing, não ecrã novo). Sem rodada extra de parser.
- **Prototype N/A:** justificado (processo/harness; sem clone; Impeccable visual N/A).
- **Rota de catálogo:** nenhuma (`live_route` não é `/…` nem `landing`; texto recusa emprestar `/combo/discovery`).
- **Agent vs gate humano:** `nao_homologar` em HUMAN_EVENTS; actor Alan; I2 inclui T18; Agent reject `reason=actor`.
- **Overlay anti-regressão:** furo só T18 humano com motivo; Agent/archive/commit/PR/merge/closeout continuam proibidos.

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: Mapeamento `motivo_visivel` → `EvalContext` / `NAMED_GUARDS` (comentário com `Não homologar:` + texto; não chat; não Agent-only). Autor já marcou detalhe de Apply. Disposition: **aceito**.
- P3: Overlay live tem duas frases («nunca mova… durante homologação, archive…» e «o card só avança Done → Homologado → Pronto»). Apply MUST exceptuar T18 nas duas, senão a segunda desfaz o furo. Disposition: **aceito**.
- P3: Skill/runbook MUST cobrir reentrada pós-T18 (reabrir/criar `card-<id>-*` a partir do `develop` actual; não `iniciar_apply`/T8; seguir pedir_review…T14). Task 4.2 hoje só nomeia o par de eventos. Disposition: **aceito**.
- P3: Arraste GitHub sem comentário é fora-de-δ; Risks já mandam restaurar Done. Apply implementa o predicado + restore; não é pre-check na UI do board. Disposition: **aceito**.
- P3: Slug `devolver-homologacao` ≠ evento `nao_homologar`. Apply MUST NOT inventar aresta inversa em Homologado. Disposition: **aceito**.

## Disposition

Zero P0/P1. Recorte q1–q4=A intacto; contrato visível (par em Done, destino fixo, motivo obrigatório, Agent fora, Homologado intocado, sem tela) está no pacote. Residuais P3 são Apply (guarda, overlay, runbook de reentrada, restore, nome do evento). Teto 1+1+1: sem segundo rework.

Tokens do autor **passam** a rubrica (linhas próprias parseáveis; ausência justificada; sem catálogo emprestado).

## Verdict

**PASS**
