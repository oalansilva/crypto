## Why

O job `process-fsm` do CI é cancelado pelo limite de 5 minutos mesmo com todos os testes passando, porque a máquina do GitHub varia de velocidade. O CI fica vermelho sem defeito, o merge (T14) trava e alguém tem de rodar o job de novo à mão.

O texto abaixo, de `## Problema` até `## Não entra`, é cópia integral do body do issue #1152 (lido por REST em 2026-10-29). O *como* está em `design.md`.

## Problema

O job `process-fsm` do CI (`.github/workflows/ci.yml`) tem `timeout-minutes: 5`. A máquina do GitHub que roda o CI varia de velocidade: o mesmo commit levou 159 s numa rodada e 278 s em outra (cerca de 1,8 vez mais lento). Quando passa de 5 minutos, o GitHub cancela o job **com todos os testes passando**.

No PR do #1135, isso aconteceu três vezes. Cada vez o CI ficou vermelho sem defeito, o merge (T14) travou, e alguém teve de rodar o job de novo à mão (a ação `rerun` do T12 não roda sozinha). A rodada que passou levou 4m25s, a 35 s do limite. Os dois testes mais lentos (`test_codex_review_session.py::test_product_wave_persists_in_source_bound_principal_without_toggles`) levam uns 40 s cada.

Não é só o #1135. Nas ~50 rodadas do job desde 18/10 (PRs e pushes no `develop`), 6 foram canceladas por tempo em 4 cards diferentes (#1130, #1122, #1123 e #1135), e cerca de metade das que passaram terminou entre 4m45s e 5m (o push do #1135 no `develop` passou com 4m59s). A mais rápida levou 2m41s. Quase todo o tempo é o passo dos testes de `scripts/process-fsm` (instalação + pytest); checkout e o passo de secret-remediation somam uns 15 s. O merge trava porque o `qa-gate` depende do `process-fsm`. O T12 (`rerun_infra`) hoje só registra o evento no quadro (QA → QA); não roda o job de novo no GitHub.

## História

Como Alan, quero que o CI só fique vermelho no `process-fsm` quando um teste falhar de verdade, para não travar merges nem gastar tempo rodando o job de novo por causa da lentidão da máquina.

## Entra

- [ ] O limite de tempo do job `process-fsm` passa a 10 minutos (cerca de 2 vezes a rodada mais lenta vista), com o motivo num comentário ao lado.
- [ ] O CI do PR passa no `process-fsm` sem nenhuma rodada repetida.
- [ ] O card registra o histórico medido: nenhuma das ~50 rodadas recentes do `process-fsm` passaria do novo limite de 10 minutos.

## Não entra

- Acelerar os testes lentos do `test_codex_review_session.py` (pode virar outro card).
- Avisar quando o job encosta no limite de tempo (pode virar outro card, junto com acelerar os testes lentos).
- Fazer a ação `rerun` do T12 rodar sozinha no `process_event`.
- Mudar os limites de tempo dos outros jobs do CI.

Origem: achado de infra do #1135 (QA, 29/10).

## What Changes

- `.github/workflows/ci.yml`, job `process-fsm`: `timeout-minutes: 5` passa a `timeout-minutes: 10`, com o motivo num comentário na mesma linha. Nenhuma outra linha do workflow muda.
- O card #1152 recebe um comentário com o histórico medido de todas as tentativas do `process-fsm` desde 18/10 até o PR deste card, separando as que terminaram (duração medida) das que foram canceladas (duração real desconhecida), conforme `design.md`.
- O PR deste card passa no `process-fsm` na primeira tentativa, sem rodada repetida.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ci-testing-hardening`: novo requisito sobre o limite de tempo do job `process-fsm` (10 minutos, com o motivo registrado ao lado).

## Impact

- `.github/workflows/ci.yml`: uma linha (`timeout-minutes` do job `process-fsm`).
- `qa-gate`: sem mudança de `needs` nem de lógica; continua dependendo do `process-fsm`.
- Testes, `scripts/process-fsm/` e limites dos outros jobs: sem mudança.
- Custo: um job travado de verdade passa a ocupar a máquina do GitHub até 10 minutos em vez de 5 antes de ser cancelado.
