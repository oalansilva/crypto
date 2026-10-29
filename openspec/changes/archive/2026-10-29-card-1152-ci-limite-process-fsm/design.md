## Context

Status: Design. Briefing copiado do issue #1152 (REST, 2026-10-29) em `proposal.md`. Decisões já fechadas no refinamento: limite de 10 minutos fixos, motivo num comentário ao lado, prova = PR sem rodada repetida + histórico medido no card. O issue deixou com o Design um ponto: a rodada cancelada em 5m16s não tem duração real conhecida, e o histórico só garante as rodadas que terminaram.

UI impact: none
live_route: N/A — card só de CI (limite de tempo do job `process-fsm` em `.github/workflows/ci.yml`); nenhuma tela muda
surface: none

Sem superfície: o card muda uma linha de workflow e registra um comentário no card. Nenhuma tela, componente ou texto de produto muda. Prototype: N/A. Impeccable: N/A (CI sem tela).

Estado verificado em 2026-10-29 (develop `a0c1f788`):

- `.github/workflows/ci.yml:241`: job `process-fsm`, `runs-on: ubuntu-24.04`, `timeout-minutes: 5`. Passos: checkout, setup-python 3.12, "Run process-fsm fixtures" (pip + `pytest -q scripts/process-fsm`), "Synthetic secret-remediation checks".
- Outros limites no arquivo: `backend-unit-tests` e `e2e-playwright` com `timeout-minutes: 30` (ficam). `backend/tests/contract/test_backend_unit_harness.py:148` confere o 30 do `backend-unit-tests`; nada confere o 5 do `process-fsm`.
- `qa-gate` tem `process-fsm` em `needs` e exige `success` de cada um. `concurrency` do workflow tem `cancel-in-progress: true`, então também há cancelamentos que não são por tempo.
- Workflow `CI/CD` (id `238530787`). Desde 2026-10-18: 45 rodadas, 54 tentativas do job `process-fsm` (contando as repetidas). Medição em D2.

## Goals / Non-Goals

**Goals:**

- `process-fsm` com `timeout-minutes: 10` e o motivo ao lado, sem mexer em mais nada do workflow.
- Card com o histórico medido, separando o que foi medido do que não foi.
- PR do card verde no `process-fsm` na primeira tentativa.

**Non-Goals:** os quatro itens de "Não entra" do issue: acelerar `test_codex_review_session.py`, aviso de proximidade do limite, `rerun` do T12 automático, limites dos outros jobs. Também fora: teste de contrato novo para o valor (D4).

## Decisions

### D1. A linha e o comentário

Em `.github/workflows/ci.yml`, job `process-fsm`, a linha 241 passa de:

```yaml
    timeout-minutes: 5
```

para:

```yaml
    timeout-minutes: 10  # #1152: a máquina do GitHub varia de velocidade e com 5 min o job era cancelado com os testes passando; 10 min ≈ 2x a rodada mais lenta medida.
```

O comentário fica na mesma linha ("ao lado", como decidido). O número do card leva ao histórico. O diff do arquivo é essa linha e nada mais.

Alternativas, para registro (decisão do Alan, não reaberta): 8 min deixaria pouca folga sobre a rodada mais lenta medida; tirar o limite cairia no padrão do GitHub (6 horas) e um travamento de verdade prenderia a máquina; 15 min só aumenta o custo de um travamento sem ganho medido.

### D2. Histórico medido e como apresentá-lo honestamente

**Fonte.** API do Actions, sem script novo no repositório (os comandos rodam no terminal do Apply):

1. Rodadas: `gh api --paginate "repos/oalansilva/crypto/actions/workflows/ci.yml/runs?created=%3E%3D2026-10-18&per_page=100" --jq '.workflow_runs[] | [.id,.event,.head_branch,.created_at] | @tsv'`.
2. Tentativas do job em cada rodada: `gh api "repos/oalansilva/crypto/actions/runs/<run_id>/jobs?filter=all&per_page=100"`, só `name == "process-fsm"`. `filter=all` traz as tentativas repetidas; sem `per_page=100` a página padrão corta tentativas (visto na rodada `40804875579`, que tem 5). Duração = `completed_at − started_at` do job, em segundos; anotar `run_attempt`, `conclusion` e a conclusão do passo "Run process-fsm fixtures".
3. Motivo de cada `cancelled`: `gh api repos/oalansilva/crypto/check-runs/<job_id>/annotations`. "The job has exceeded the maximum execution time of 5m0s" = tempo; "Canceling since a higher priority waiting request…" = `concurrency`, sem relação com tempo.
4. Cancelada no meio dos testes: `gh api repos/oalansilva/crypto/actions/jobs/<job_id>/logs`, última linha `[ NN%]` do pytest.

A duração do job conta alguns segundos a mais que o relógio do limite (as canceladas por tempo aparecem com 301–316 s para um limite de 5m00s). O erro é para cima: a medida é conservadora.

**Medição do Design (2026-10-29, 54 tentativas):**

| Grupo | Tentativas | Duração | O que se pode afirmar |
|---|---|---|---|
| A. Terminaram sozinhas | 47 (46 `success`, 1 `failure` de teste real, run `39135121895`) | 161–300 s (2m41s–5m00s) | Medido. Nenhuma passa de 10 min. |
| B. Cortadas por tempo depois dos testes | 5: `40396871086`/1 (#1122), `40739597304`/1 (#1123), `40804875579`/1, /2, /3 (#1135) | 301–308 s no corte | O passo dos testes já tinha terminado com `success`; faltava só o passo de secret-remediation (3–6 s nas outras rodadas) ou a limpeza. Duração real ≤ ~315 s. Nenhuma passaria de 10 min. |
| C. Cortada por tempo no meio dos testes | 1: `39270686134`/1 (#1130), 5m16s | desconhecida, ≥ 5m16s | Não medida. Ver abaixo. |
| D. Cancelada pelo `concurrency` | 1: `40804875579`/4 (#1135), 2 s | — | Fora da conta: não tem relação com tempo. |

Grupos B + C = as 6 canceladas por tempo em 4 cards que o issue cita.

**A rodada de 5m16s (grupo C).** O log mostra o pytest em 47% aos ~281 s do job, ainda sem fechar o bloco seguinte quando o limite cortou. A rodada do mesmo branch na véspera (`39178640009`, `success`, 297 s) levou 64 s do mesmo ponto (47%) até o fim dos testes. Para essa rodada passar de 10 min, o resto teria de levar mais de ~314 s, cerca de 5 vezes o que levou na véspera; a maior diferença de velocidade vista entre rodadas é de ~1,8 vez. Não houve outra rodada desse commit (o #1130 não voltou ao CI). Conclusão apresentada no card: **improvável que passasse de 10 min, mas não medida**. O comentário MUST NOT contá-la entre as medidas abaixo de 10 min.

**Texto do card.** A frase do Entra fica, no comentário, assim: "Das 54 tentativas do `process-fsm` desde 18/10, 52 têm duração medida ou limitada a no máximo ~5m15s, abaixo do limite de 10 min. 1 foi cancelada pelo `concurrency` (2 s, sem relação com tempo). 1 (`39270686134`, #1130) foi cortada aos 5m16s no meio dos testes: duração real desconhecida, estimativa pelo log em D2 do design." Seguem a tabela dos grupos, a lista de todas as tentativas (run, tentativa, evento, branch, conclusão, segundos, motivo do corte) e a rodada do PR deste card como primeira com o limite de 10 min. A janela vai de 2026-10-18 até a rodada do PR deste card; as rodadas novas entram no mesmo critério.

### D3. Critério de aceite do PR sem rodada repetida

No PR deste card, a rodada do CI do commit do topo (o que vai para o T14) cumpre:

- `gh api "repos/oalansilva/crypto/actions/runs/<run_id>/jobs?filter=all&per_page=100"` traz exatamente uma tentativa do `process-fsm`, com `run_attempt == 1` e `conclusion == "success"`;
- o `head_sha` da rodada é o topo do PR.

Commit novo no PR cria rodada nova; o critério vale para a última. Repetir o job (`gh run rerun`, botão "Re-run") não conta como prova. Se o `process-fsm` for cancelado por tempo mesmo com 10 min, não repetir: voltar ao Alan como P0 (a premissa do valor caiu). Se falhar por teste, é defeito real, fora deste card, e vai ao Alan.

### D4. Sem teste de contrato para o valor

Não se acrescenta assert ao `test_backend_unit_harness.py`. O Entra não pede; o diff de uma linha é conferido na revisão e na task 1.2. Alternativa considerada: assert de `timeout-minutes: 10` no teste de contrato. Rejeitada porque só repete o arquivo e amarra o número sem medir nada.

### D5. Ordem do Apply

1. Trocar a linha (D1) e conferir o diff.
2. Commit, push, PR para `develop`.
3. Conferir o critério D3 na rodada do PR.
4. Refazer a medição (D2) até a rodada do PR e comentar no card.

## Risks / Trade-offs

- [Um travamento de verdade ocupa a máquina 10 min em vez de 5] → aceito pelo Alan; o aviso de proximidade ficou fora.
- [A suíte cresce e volta a encostar no limite] → fora deste card (aviso e aceleração dos testes são cards futuros). O histórico no card deixa a referência para comparar.
- [A rodada do PR cair num runner muito lento] → improvável pelo histórico; se acontecer, D3 manda parar e voltar ao Alan, sem repetir.
- [Contar a rodada de 5m16s como medida] → D2 separa o grupo C e proíbe somá-la às medidas.

## Migration Plan

Merge em `develop` pelo fluxo normal. Reverter = voltar a linha para `timeout-minutes: 5`. Nada de banco, serviço ou DEV.

## Open Questions

Nenhuma bloqueia. Para o Alan ver na Aprovação de Design: o terceiro item do Entra fica cumprido com a ressalva do grupo C (a rodada de 5m16s é estimada, não medida), no texto exato de D2.

## Design Critique

Crítico sem-tela, rodada única (2026-10-29), conforme `design-critic`. Conferido com ferramentas: cópia do issue em `proposal.md` idêntica ao body por REST (diff vazio, só linhas em branco ignoradas); `ci.yml:241` = `timeout-minutes: 5`, outros limites 30/30, `cancel-in-progress: true`; medição D2 refeita (45 rodadas, 54 tentativas, grupos A–D batem: 47 terminaram em 161–300 s, 5 cortadas em 301–308 s com o passo dos testes `success`, 1 cortada aos 316 s no meio dos testes, 1 cancelada pelo `concurrency` em 2 s; annotations conferidas); `openspec validate --strict` válido.

- Gate (rubrica): `UI impact: none` / `live_route: N/A` + justificativa / `surface: none` em linhas próprias; `design_clone_gate.design_token_gap` = nenhum faltando e `evaluate_clone_gate` = True. Sem rota de catálogo emprestada. OK.
- P2 (produto) — o 3º item do Entra ("nenhuma das ~50 rodadas passaria de 10 min") não fica provado para 1 de 54 tentativas (`39270686134`, #1130): o dado não existe e nenhum rework o cria. Disposition: aceito com ressalva; o design não finge prova (grupo C separado, proibido somar) e já leva o ponto ao Alan na T7. Ao pedir a Aprovação de Design, citar a ressalva como decisão explícita do Alan (aceitar a frase de D2 ou reescrever o item 3 do Entra).
- P2 (produto) — a estimativa do grupo C usa o ritmo da rodada inteira (~1,8x), mas o log mostra o bloco em curso já ≥ 33 s depois do `[ 47%]` contra 11 s do bloco equivalente na véspera (≈3x local), e os dois commits têm contagens de teste diferentes, então "47%" não é o mesmo ponto exato. Disposition: aceito; no comentário do card (task 3.2), acrescentar esse fato ao lado do "improvável", mantendo "não medida".
- P3 (detalhe de Apply) — D3 diz que o critério vale para a última rodada do PR; deixar explícito no Apply que um corte por tempo em qualquer rodada do PR (não só a última) para e volta ao Alan, e que todas aparecem na lista da task 3.2. Aceito, resolvido no Apply.
- P3 (detalhe de Apply) — task 1.3 usa `python`; no host pode ser `python3`. Aceito, resolvido no Apply.
- P3 (detalhe de Apply) — "duração real ≤ ~315 s" do grupo B é aproximação (corte 308 s + passo de secret-remediation 5 s + limpeza); o número exato não muda a conclusão. Aceito, resolvido no Apply.

Verdict: aprovado para pedir Aprovação de Design. Sem P0/P1; sem rework do autor. Escopo, Não entra, linha única do workflow e critérios D1–D3 batem com o issue e com o `ci.yml` atual.
