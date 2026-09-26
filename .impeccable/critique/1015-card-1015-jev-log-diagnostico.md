# Relatório do autor — Design #1015 · card-1015-jev-log-diagnostico

Filho **Design-autor** (spawn isolado, cliente dsh). Worktree `crypto-worktrees/card-1015-jev-log-diagnostico`, branch `card-1015-jev-log-diagnostico`. Briefing grelhado copiado verbatim em `proposal.md`; sem reentrevista; SEM-TELA. Nenhum código de produto escrito (`backend/**` / `frontend/src/**` intocados).

## Tokens do gate (rubrica D4)

- `UI impact: none`
- `live_route: N/A registo de diagnóstico em ficheiro de log; sem tela de produto`
- `surface: new`

Justificativa curta da ausência (sem-tela): o contrato visível é um ficheiro de log de diagnóstico lido no runtime-worker DEV; sem rota autenticada, sem landing, sem HTML. Nunca emprestar /monitor /favorites /combo/discovery /combo/select landing. Prototype N/A. Impeccable N/A.

## Contagem de palavras de `design.md`

**2212 palavras** (`wc -w`).

## Resumo das decisões-chave (o *como*)

1. **Registo nas costuras existentes, sem camada nova de telemetria:** entrada e retorno da chamada dentro de `request_jev` (`scalp_jev.py`) — o que se loga é o que se enviou; recusa num único helper no fecho de `tick_user` (`scalp_service.py`) com o token `skip_reason` tal como nasce em `scalp_engine`. Rejeitado: log só no ciclo, decorator/proxy no loop, base de dados nova.
2. **Conta resumida e zero segredos na formatação do registo, nunca no payload:** `state.account` → boleanos `has_position`/`has_balance`; `inventory_btc`/`t`/`remaining_to_t`/saldos fora do ficheiro; chave TypeSafe e `Authorization` nunca registados; corpos de erro truncados + `_redact`. Rejeitado: regex pós-facto, mascarar só dígitos.
3. **Nível configurável por env (logger dedicado):** INFO para envio/retorno, WARNING para erros. Rejeitado: nível fixo (flood a ~1/s) e «só WARNING» (perdia a chamada de sucesso, que é o problema).
4. **Ficheiro dedicado com rotação por tamanho:** ao encher cai o mais antigo; sem prazo fixo. Rejeitado: rotação por tempo, `full_execution_log.txt` sem teto, só journald.
5. **`skip_reason` token cru, pré- e pós-chamada, em todo ciclo sem ordem**; painel e `/api/scalp/status` intocados (motivo da recusa só no log). Rejeitado: só gates pós-Jev, copiar para o painel.
6. **Só DEV nesta entrega** (runtime-worker DEV, `RUN_SCALP_LOOP=1`; unit PROD sem flag); evidência = log real com várias chamadas (sucesso + uma recusa) observável no runtime-worker. Rejeitado: ligar em PROD, expor em `/api/logs/tail`/Ver logs.
7. **Inalterados por contrato e teste:** payload SystemOne byte-a-byte igual; cadência ~1 s (`JEV_TARGET_MS`), hurdle `expected_move_bp > 2×fee_bp + spread_bp`, alvo 35 bp / stop −28 bp, fail-closed 1,5 s (`JEV_LATE_MS`) e 500 ms (`age_ms`). Rejeitado: enriquecer o payload, registar dentro do módulo puro `scalp_engine`.

## Riscos / pontos para a crítica

- O registo de entrada tem de substituir `account` no acto de formatar (o wire payload já leva valores exactos) — teste de regressão que falha se algum valor exacto aparecer no ficheiro.
- Volume ~1/s por utilizador ligado mesmo com token estável (`jev_target` entre perguntas) — aceite como o diagnóstico pedido; o knob de nível + rotação por tamanho são o filtro.
- Nome exacto do logger/envs, formato das linhas, mecanismo/teto da rotação, tamanho do corpo de erro resumido e correlação entrada↔retorno ficam como **P3 detalhe de Apply** (lista em `design.md`).

## Verificação deste autor

- `/usr/bin/openspec validate card-1015-jev-log-diagnostico --type change` → `Change 'card-1015-jev-log-diagnostico' is valid` (também com `--strict`).
- Artefactos: `proposal.md` (superset verbatim do issue + Como), `design.md` (Context/Decisions/tokens/D4), `tasks.md` (checkboxes, aviso T8), `specs/scalp-jev-diagnostic-log/spec.md` (deltas em inglês), `.openspec.yaml`.
- Spawns deste filho: 0 (nenhum filho criado). Sem `process_event`, sem edição do issue/board, sem Gist/comentários, sem commit/push.
