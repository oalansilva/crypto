# Apply parcial — #1093, 2026-10-13

> Registro histórico do primeiro Apply. A retomada aprovada e as evidências novas constam ao fim deste arquivo; nenhum resultado histórico abaixo foi reescrito como sucesso posterior.

## Fronteira e bloqueio

Apply único desta entrada em Em desenvolvimento, interrompido por steering explícito de Alan: incluir correção da estratégia no mesmo card, revisar o Design antes de alterar suas regras e completar a busca original. Não houve alteração do template/estratégia nem redução de critérios/grid. Open Questions registra a lacuna factual e exige revisão/aprovação antes desse novo código. Pai conduz a FSM; este filho não executou process_event, commit, push, review ou spawn.

Baseline do worktree: `99a3070cd9d117539fe6de734361f07d5e1c4611`, branch/change `card-1093-discovery-memory`. Captura de nascimento: `/tmp/card-1093-apply-birth-20261013.json`. UI none; HTML/protótipo N/A. O snapshot Impeccable não foi lido nem alterado.

Tasks: 3/22 completas (2.1, 2.3, 4.1). As outras 19 continuam abertas; código escrito não equivale a todos os contratos/ensaios concluídos.

## Trabalho preservado

- `discovery_resources.py`: perfil DEV 5/6 GiB, swap512 MiB, requested/effective worker1, admissão fail closed e amostras RSS/PSS/tracemalloc/cgroup.
- `discovery_budget_cache.py`: bridge opcional para a API `Cache/BUDGET` de #1091, com fallback agregado para as estruturas antigas. O worktree #1091 foi somente lido; sua API não foi substituída. Fixture de composição copiada para testes, ainda não executada.
- `discovery_stream.py` + `combo_optimizer.py`: geradores em ordem estável; batches≤200, janela≤2W/64MiB; spool privado SQLite, extremos globais em trial order e segunda passagem com a mesma expressão de score; contadores honestos/barreira em erro. Goldens finitos/NaN/inf/empates/extremo final e caminhos R1/R2–R4 passaram. Retenção/cleanup órfão, medição ampla e equivalência completa de holdout/diversidade ainda pendentes.
- `models_discovery.py` + migração `20261013_0001`: ledger e campos de posse/backoff/circuito. Migração escrita com predecessor `20261002_0001`; não executada. Modelos foram criados somente no cluster descartável para os ensaios PostgreSQL.
- `discovery_recovery.py`, `discovery_supervisor.py`, service/tasks/runtime: claim único pré-spawn, owner/geração, heartbeat separado de progresso, fencing, três tentativas/backoff60/300, circuito e reconciler externo. Snapshot congela datas/metadata, mas congelamento completo dos dados de mercado e caminhos de falha/commit/ACK/DB indisponível ainda precisam fechamento. Cleanup de filho não atende o teste de20s; não declarar segurança desse contrato concluída.
- Unit/instalador DEV versionados: MemoryHigh5G/MemoryMax6G/MemorySwapMax512M, OOMPolicykill, KillModecontrol-group, timeout30s, on-failure60s, três starts/900s e recusa a árvore antiga coexistente. Templates PROD não alterados; instalador não executado.
- Scripts isolados, testes e fixture do template original preservados. Comando administrativo do circuito e rollback/cutover ainda sem ensaio completo.

## Evidências terminadas

1. `python -m compileall -q` / `py_compile` dos módulos implementados: exit0 nas invocações registradas antes das últimas alterações. Não equivale a teste da versão final inteira.
2. `python -m pytest -q backend/tests/unit/test_discovery_memory.py backend/tests/integration/test_discovery_memory_recovery.py`: **20 PASS**, 1 warning Pydantic, 4.26s. Rodada anterior encontrou falhas nas fixtures, corrigidas antes desse resultado. Unidade:11 casos; PostgreSQL:9 casos (claim concorrente único, redelivery/attempt budget, backoff/exaustão, lease/counters, stale writer, passo iniciado há31min com heartbeat, progresso600s, pause/cancel, erro determinístico sem retry e circuito entre sweeps/ack auditado).
3. Fixture original `test_original_492480_template_has_deterministic_invalid_length_trial`: **1 PASS**, 1 warning, 1.40s. Dataset sintético400 candles, template original versionado. Períodos10/10 retornam `calculation_error`;14/14 calcula validamente. A geração do grid original permanece492480.
4. `test_discovery_supervisor.py` em unit transitória `card-1093-process-tests-2.service`: **2 PASS / 1 FAIL**, 33.11s. Supervisor/principal perdidos encerraram grupos; teste de filho perdido levou cerca de30s até retorno, falhando teto<20s. Unit2G/swap0, pico119.8MiB, duração33.871s, exit1. Nenhuma tentativa de corrigir após a instrução de parar.
5. OOM sintético em `card-1093-oom.service`: o script verificou seu próprio cgroup **MemoryMax512MiB/MemorySwapMax0/memory.oom.group1 antes de alocar**. Unit result esperado `oom-kill`, pico512.0MiB, swap0, duração1.771s. Kernel às01:59:20UTC: `constraint=CONSTRAINT_MEMCG`, `oom_memcg=/system.slice/card-1093-oom.service`. Nenhum `global_oom` no intervalo de consulta. Cgroup de ensaio descartado após término; nenhuma alocação OOM global feita.
6. Redis isolado: PING→PONG, container`card-1093-redis`, `--network none`, memory/memory-swap128MiB. Não houve publicação em discovery real.

Comandos pytest usaram:

```sh
DATABASE_URL='postgresql+psycopg2://card1093@/crypto_card1093_test?host=/tmp/card-1093-integration-20261013&port=55493'
WORKFLOW_DATABASE_URL="$DATABASE_URL"
PYTHONPATH=/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory:/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory/backend
/srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m pytest -q <testes acima>
```

A unit de processo recebeu esses envs explicitamente e WorkingDirectory deste worktree; unitOOM executou somente `backend/scripts/discovery/isolated_oom.py` via `/usr/bin/python3` com os limites acima. Logs continuam no journal dos nomes transitórios informados.

## Manifesto original recuperado parcialmente

Journal12/10/2026 às15:02:26–15:02:33UTC: sweep`9debda606c134d66aaebd07825030dfb`, combinação3718, template`long_ma_pullback_rsi_adx`, BTC/USDT15m, long, janela2025-10-06..2026-10-06. Listing35041 candles, train24528, holdout10513, burnin250. **492480 corresponde à etapaR1**, 2463 batches, quatro rodadas adaptativas. Schema inclui ma_long_length/pullback_pct, rsi_length/oversold/overbought, adx_length/threshold e stop_loss.

Consulta read-only do DB DEV confirmou o snapshot/janela, resultados anteriores12/18 e attempts legados7 para as seis combinações restantes. Template atualizado2026-10-03 (antes do incidente): entry/exit fixam RSI_14/ADX_14, mas schema varia os períodos10..20; fixture em `backend/tests/fixtures/discovery_memory/original_template.json`. Não há digest histórico dos bytes originais do parquet, e não foi fabricada equivalência dessa fonte. Reprodução integral/carga492480 e três buscas consecutivas **não executadas**.

## DEV e inventário

Python3.12.3, Celery5.6.3, systemd255, cgroupv2 unified. MemTotal25,137,336,320 bytes (≈23.4GiB). Antes de parar, Discovery DEV usava13,461MB sem MemoryHigh/Max/SwapMax; MemAvailable≈5.9–6.1GB, swap livre≈0.7–2.0MB, abaixo da admissão aprovada.

Parada coordenada autorizada somente de `criptofarol-dev-discovery-worker.service`: systemctl stop iniciouSIGTERM; o pool antigo não drenou. Finalizada exclusivamente a árvore dessa unit com `systemctl kill --kill-whom=all --signal=SIGKILL`. Depois: MainPID0, ActiveStatefailed/SubStatefailed/Resultsignal; **permanece parado**, sem reiniciar o worker ilimitado. MemAvailable após parada19,188,768,768 bytes, swap livre3,331,985,408 bytes. Nova unit não instalada e migração não aplicada no DEV real. Outros serviços/runtime-worker/PROD não reiniciados nem modificados.

Isolamento: PostgreSQL16 privado em `/tmp/card-1093-integration-20261013/pg`, socket na pasta pai0700, port55493, sem listenerTCP, rolecard1093 e DBcrypto_card1093_test. Este role não foi criado no cluster compartilhado. Redis privado conforme acima. Teardown fecha somente esses recursos próprios; diretórios/container preservados, sem remoção de artefatos/filas/bancos reais.

## Pendências para próxima entrada autorizada

Revisão/aprovação do novo Design; corrigir estratégia somente depois disso. Fechar cleanup20s/perda de filho e órfãos/semaphores; dados congelados em retry; fencing/manifesto integral em todos os commits; recuperação sob DB indisponível; cgroup/circuito/ack e cutover/rollback com ledger preservado; migração isolada efetiva; goldens full optimizer/trades/holdout/diversidade/composição1091; perfis memória nativa/serialização; reprodução original e3execuções contidas. Black, checks backend finais e `openspec validate --strict` ainda **não executados** nesta interrupção. Nenhum PASS final, deploy, release ou completude foi alegado.

## Apply retomado após aprovação do Design revisado — 2026-10-13

T8 executado pelo pai; Apply único desta nova entrada. Baseline/branch/worktree acima preservados. Captura de nascimento `/tmp/card-1093-apply-revised-birth-20261013.json`, modelo solicitado/observado pelo pai GPT-6.1 Sol (`gpt-6.1-sol`), high. Gist aprovado `e2b7d63aec5c3c9287fda61ad99c1e34`. Filho não executou process_event, commit/push, review nem spawn; trabalho #1091 permaneceu somente leitura. UI impact none, HTML/protótipo N/A, crítica Impeccable não lida, nenhum asset gerado/copied.

Estado deste marco: **24/27 tarefas completas**, pendentes 5.4/5.5/6.4 até comparação final e término das três buscas/checks. Não é retorno de controle nem aceite parcial da carga. Runbook: `docs/discovery-memory-operations.md`.

### Implementação final em execução

- Binding runtime `long_ma_pullback_rsi_adx/effective-indicators-v1`, restrito ao nome/declaradores originais únicos RSI14/ADX14 sem alias; identidade capturada antes dos overrides. Contexto resolvido antes do preflight, usado por entrada/saída/worker/final/holdout/Deep/fallback. Colisão/ambiguidade/identificador desconhecido falha explicitamente. Sem SQL de template, replace global ou redução de grid. Chaves incluem política, identidade, dados, parâmetros e expressões.
- Inputs parquet privados congelados/hash/fsync antes do preflight, manifesto durável no ledger; retries reutilizam exatamente os arquivos. SHA do candle é persistido em campo de 64 caracteres (migração aditiva). GC conserva manifests e só remove arquivos próprios quando terminal/owner comprovadamente morto.
- Stream mantém 200 por batch, 2W futures/64 MiB pendentes. Medição pickle incremental preserva tamanho real sem serializar cada prefixo. Spool SQLite privado e ordenação indexada limitados a 2 GiB incluindo inputs/IPC; segunda passagem usa extremos globais exatos, score/tie order Python. NaN/inf têm caminho limitado de ordenação compatível; retenção ≤128 MiB. Falha de pool/cálculo/quota/I/O não produz resultado parcial.
- Ledger/CAS conserva um claim pré-spawn, geração/owner, heartbeat30/TTL300, aviso120/aborto600 sem progresso, inicial+2/backoff60/300 e circuito. Reconciler externo no runtime-worker conserva pause/cancel/commit e rejeita escrita tardia. Reconhecimento administrativo auditado exige árvore parada/sem leases e probe de admissão; sem reset de tentativas.
- Correção de cleanup: Future de ProcessPoolExecutor podia reportar morte ~30 s depois, embora filho estivesse morto em ~0,2 s. Roster PID/start/grupo permite detectar independente de Future em poll ≤1 s. TERM/KILL/reap elimina grupo e semáforos próprios; cleanup pós-diagnóstico medido ~15 ms. Shutdown normal do pool é distinguido de perda durante trabalho.
- Bridge reaproveita a API LRU #1091 quando presente; fallback conserva limite agregado 67108864 bytes/4096 entradas/32 snapshots. Amostra `cache_bytes=66004399` =62,95 MiB, dentro do teto; não são 66 MiB. Perfis explicam RSS/PSS/cgroup e tracemalloc; piloto final pico826990592 bytes, pós-cleanup194510848 bytes de cgroup, cache0, swap0, zero OOM.
- Unit/instalador DEV preservam 5/6 GiB/512 MiB, OOMPolicykill/KillModecontrol-group e restart60/start-limit3/900; `--discovery-only` não reescreve runtime/backend. Defaults de outros consumidores são preservados até opt-in; ensaio isolado usou três workers reais. Paths de spool do dispatcher/backend/Discovery convergem por ambiente.

### Checks terminados desta retomada

Todos usaram o worktree e venv compartilhado somente para execução, banco/fila privados, sem alterar dependências:

- `pytest` dos regressivos fastpath/finalmode/parser/binding/inputs/memory/composição: **156 PASS, 19,07 s**. Execução ampla anterior terminou123 PASS +1 FAIL estrutural (teste buscava `ComboOptimizer` no wrapper que agora delega ao supervisor); assert estrutural adaptado para verificar o novo contrato, sem alterar oracle/tolerância numérica. Goldens numéricos históricos dessa rodada já haviam passado.
- Memória/binding/composição **142 PASS, 17,18 s**; binding todos121 pares/aliases/cache A→B→A **130 PASS, 11,73 s**; stream/inputs/composição após quota **15 PASS, 7,69 s**.
- PostgreSQL recovery + migração aditiva efetiva: **13 PASS, 3,90 s**, incluindo interrupção real do cluster privado e retomada, morte antes do commit de claim, commit antes de ACK, fencing tardio, lease31min, progresso600s, pause/cancel, backoff/exaustão/circuito. Migração usa schema próprio e recusa downgrade destrutivo; banco compartilhado não migrado.
- Supervisor final em `card-1093-cleanup-proven.service`: **4 PASS, 5,26 s**, duração unit6,09 s, pico120,1 MiB/swap0; filho perdido, filho silencioso com Future deliberadamente atrasado30s, supervisor e principal/GC. Sem aviso final de vazamento de semáforos. Ensaios anteriores que emitiram avisos são preservados como diagnóstico, não evidência da versão final.
- Morte Celery real com Redis/socket/queue privada: **1 PASS, 6,24 s**, pico288,7 MiB. Nunca consumiu/publicou fila Discovery compartilhada.
- Três workers spawn reais, unit2 GiB/swap0/cgroup pré-verificado: **1 PASS, 5,74 s**, três PIDs distintos/ranking oracle, pico557,9 MiB.
- Reconhecimento administrativo/probe isolado `card-1093-ack-probe`: **PASS**,659 ms. Não reconheceu circuito DEV compartilhado.
- OOM sintético512 MiB/swap0 da entrada anterior permanece válido: memcgconstraint, zero globalOOM, sem mudança semântica no injector.
- Golden real janela recuperada: histórico14/14 **exato**, todos121 pares RSI/ADX10..20 em treino24528 e holdout com burn-in10763 com TA-Lib direto, máscaras/sinais/trades exatos. `semantic_goldens.json` SHA256 `2990a2622714daa17c5e86d5ab1b3db415f64902a532a9dc94395c97d880003d`. Oracle não usa o resolver/cache novo; posição congelada do baseline. Custos/Deep/metrics são contratos compartilhados inalterados e comparados ao oracle histórico14/14.
- Piloto pipeline completo final **44,6607 s**, quatro estágios completos, claim/ledger/result persistidos no banco privado, cache0/cleanup; grid reduzido privado não conta como busca original. Piloto inicial362s diagnosticou custo tracemalloc depth10; depth1 mantém medição e reduziu overhead sem alterar cálculo.
- Verificação independente do vencedor final do piloto em `card-1093-final-oracle-pilot-5`: **PASS, 2,517 s**. Sinais/trades treino e holdout, todas as métricas persistidas e veredito NO-GO exatos. `pilot_final_verification.json` registra hashes; o mesmo checker será aplicado aos três relatórios integrais. Seleção/diversidade congelada do baseline em `historical_diversity.json`, AST SHA256 `71b5486051cbbf5787e6f35763df4c4f573c157a54ca205796cb25d58b2b738e`: método atual idêntico e seleção comparada em401 candidatos/empates/distância0,5. Primeiras chamadas do checker falharam por envs ausentes e ownership Git do processo root; fixture congelada read-only elimina dependência de Git no processo, sem configurar safe.directory/bypassar hooks.
- Black aplicado aos arquivos alterados, shell syntax, diff whitespace e OpenSpec strict passaram antes da carga; fechamento final permanece pendente após novos artefatos.
- Check após novos scripts: Black **9 modificados +26 novos PASS**; `cache_1091_reference.py` é fixture congelada copiada do trabalho alheio e preservada byte a byte, excluída da formatação (check global sinalizou que a formataria). `openspec validate card-1093-discovery-memory --strict`, `git diff --check`, `bash -n` dos dois scripts shell e dry-run `--discovery-only` **exit0**. Novos scripts adicionais recebem Black antes do fechamento.

### Manifesto e carga integral em curso

Fixture original/template preservada. Candles35041 da janela histórica recuperados do cache DEV gravado12/10: arquivo `original_candles.parquet` SHA256 `cbac63c0b7819408a1c9db0c08e01a4ecf3ad39935183b94e09506965e6e8bc1`; valores de candles SHA256 `e289e0c22e7e8c5fd2633456f87b6d9fd1ab017a5c777ff13f47234d1e0693f1`. Source hash e timestamps constam em `original_manifest.json`. **Não há digest histórico dos bytes originais: identidade binária histórica não comprovada**, apesar de janela/contagem e fonte rastreáveis. Isso não foi convertido em equivalência fabricada nem em descarte dos dados recuperados.

Às03:46:27 UTC iniciou `card-1093-original-validation.service`, invocation `b52ca2f34a2642bfa68bbfee2b2f4e55`, `original_workload.py --runs 3`. Cgroup efetivo verificado antes da carga: High5368709120/Max6442450944/Swap536870912, oom.group1, worker1. Banco/role/queue privados; nenhum HTTP de exchange. Cada trial é comparado ao oracle semântico e a seleção global ao ranking independente. Primeira busca também é a reprodução original; depois duas consecutivas, cada qual R1492480 mais rodadas adaptativas completas. `original_progress.json`, `original_snapshots.jsonl`, runtime manifest/code hashes e journal registram avanço. Às03:53:08:16800 trials corretos/zero falhas, 2 futures/4574592 bytes, pico612757504 bytes/swap0/NRestarts0; estes números são progresso, não aceite.

### Contenção DEV e recursos

Uma operação externa de backend reativou o worker legado após a primeira parada. Paradas/restarts de02:34–02:36 foram diagnosticados por PID/cgroup/journal antes de qualquer ação; não disputamos backend. Conforme autorização explícita do pai, máscara runtime somente da unit Discovery criada, mas ineficaz por precedência de unit `/etc`. Hold efetivo exclusivo exige marcador ausente; `ConditionResult=no`, MainPID0, inactive, ControlGroup/Job vazios confirmados antes da carga. Drop-in `/run/systemd/system/criptofarol-dev-discovery-worker.service.d/card-1093-hold.conf`; rollback coordenado/remove-own-dropin/unmask-runtime descrito no runbook. Não voltar ao worker ilimitado. Nova unit não instalada/migração não aplicada no DEV compartilhado; outros serviços/PROD não operados.

`dev_inventory.json` registra cgroups disjuntos dos demais serviços, sem somar pai+filho, MemTotal25137336320 bytes e reserva real17 GiB fora do teto6 GiB; admission mínima8 GiB livres/1 GiB swap. PostgreSQL privado e Redis privado foram retomados para os ensaios e seguem ativos apenas durante a carga. Teardown conserva seus diretórios/container ao fim; worker DEV legado permanece parado/hold.

## Fechamento da carga original e checks finais — 2026-10-15

Apply-coluna (filho) sobre a árvore não commitada; branch já fast-forward para `origin/develop` 88b65ca8. Sem commit/stash/reset/checkout, sem `process_event`, sem tocar serviços DEV reais ou PROD, sem relançar a carga. Nenhum deploy PROD é alegado.

### Carga original 492.480 × 3 buscas (task 5.4)

Unit isolada `card-1093-original-validation.service`, invocation `b52ca2f34a2642bfa68bbfee2b2f4e55`, 1 worker, MemoryHigh 5368709120 / MemoryMax 6442450944 / MemorySwapMax 536870912, início 2026-10-13 03:46:27 UTC, fim 23:39:05 UTC (`Result=success`, `NRestarts=0`, CPU 20 h 8 min; journal `journalctl -u card-1093-original-validation.service`). Fontes: `original_run_{1,2,3}.json`, `original_progress.json`, `original_snapshots.jsonl` (1401 snapshots), `original_runtime_manifest.json`.

| Busca | Sweep | Duração | R1 | R2 | R3 | R4 | Pico cgroup |
|---|---|---|---|---|---|---|---|
| 1 | 182436f09acf411dbd6b6b95e495a5f9 | 23.676,0 s | 492.480 | 292.500 | 148.500 | 72.000 | 1.808.859.136 B |
| 2 | 893dad0cac1d40c69970dbff3c841dc9 | 23.830,0 s | 492.480 | 292.500 | 148.500 | 72.000 | 1.810.759.680 B |
| 3 | 0a7cc17187d04a17a466d70cbed4d78d | 24.050,2 s | 492.480 | 292.500 | 148.500 | 72.000 | 1.825.865.728 B |

Cada rodada: planned=executed=succeeded, failed=unknown=remaining=0 (barreira de completude satisfeita). Agregado dos 1401 snapshots: pico 1.825.865.728 B (≈1,70 GiB, abaixo de MemoryHigh 5 GiB), memory.current máx. 1.792.311.296 B, swap 0, `high/max/oom/oom_kill/oom_group_kill` = 0, NRestarts 0, uma única invocation; spool máx. 689.147.923 B (≤2 GiB), futures pendentes ≤2, bytes pendentes ≤4.578.913 (≤64 MiB), cache máx. 66.689.801 B (≤67.108.864) com 274.516 evictions na última etapa da busca 3. Cada trial foi comparado ao oracle semântico durante a execução e cada ranking global ao ranking independente (`ORACLE_RANKING_PASS`).

Crescimento pós-cleanup entre buscas (telemetria ao fim de cada busca, mesmo PID 1772037, cache 0): RSS 263.892.992 → 281.174.016 → 282.238.976 (+17.281.024; +1.064.960; total +18.345.984 B); PSS 216.541.184 → 233.703.424 → 234.768.384; memory.current 196.907.008 → 214.274.048 → 215.379.968. Limites do checker: total ≤128 MiB e não dois incrementos consecutivos >64 MiB — atendidos; o crescimento se estabiliza na 3ª busca.

Observação: a cada busca, `discovery_no_progress` (aviso a 120 s; idades 120–169 s) aparece uma vez na passagem global de ordenação/oracle entre R1 e R2 (ex.: 07:02:31–07:03:19 UTC na busca 1); o limite de aborto (600 s) nunca foi alcançado e o progresso retomou. As durações incluem a verificação por oracle de cada trial (a amostra de throughput `original_throughput.json` mediu 53,3 trials/s), portanto não representam a latência de produção.

### Oracle independente e equivalência (task 6.4)

Comando: `backend/scripts/discovery/verify_original_results.py` (wrapper com `PYTHONPATH` do worktree, venv compartilhado, `DATABASE_URL` fictício pois o script não conecta) → `original_final_verification.json` (sha256 `a4ceeb2d2b4bb4ecea3964c3aa4fdff9a06ba698a4b3d91e29aa522a68d42ae1`), exit 0, 2,5 s. Resultado: as 3 buscas elegeram o mesmo vencedor (`ma_long_length=160, pullback=1.0, rsi_length=18, rsi 30/59, adx_length=10, adx_threshold=24, stop_loss=0.01`), com sinais, trades de treino/holdout e todas as métricas persistidas exatos contra TA-Lib + oracle sem usar o resolver/cache novo (metrics_sha256 `c56bc4fc33dd3ff629aa53d2e84db773aaf7c2811eeacef375aa215dc9f8464c`, trades treino `121669196cc66be5c7ffea0c346332c09063a7de793e97882818c9f295d5092a`, holdout `a0baf7078a5ebd406e6f05e792904dbf05f478c88a2270eeeea5fb1b004bc730`); método de diversidade idêntico por AST ao baseline `99a3070c…` com seleção idêntica; cache 0 ao fim de cada busca. Equivalência histórica válida: goldens 14/14 e 121 pares RSI/ADX já registrados acima (`semantic_goldens.json` `2990a262…003d`).

Ajuste do checker (sem afrouxar valores): a primeira execução falhou porque comparava as métricas persistidas com as completas do oracle. O contrato de persistência remove valores não finitos (`calmar_ratio=inf`, JSONB) e o `oos_verdict` de resultados `low_sample`. O checker agora aplica exatamente essas duas remoções ao esperado, exige `eligibility` coerente com <30 trades de treino e continua exigindo igualdade exata do restante; o veredito independente (NO-GO) segue registrado no hash.

Vencedor/veredito alterado pela cobertura restaurada: **não é demonstrável**. O incidente original (combinação 3718) nunca terminou (OOM), não existe vencedor/veredito histórico dessa combinação para comparar. O resultado final é low_sample (2 trades de treino, 1 de holdout), logo sem veredito persistido; o veredito independente do mesmo vencedor é NO-GO (Sharpe OOS 0 ≤ 0; Calmar de treino não finito). Nenhuma alteração de vencedor é alegada nem negada.

### Limitações

- Manifesto dos candles: identidade binária histórica **não comprovada** (sem digest da fonte de 2026-10-12); foram usados 35.041 candles recuperados do cache DEV com hashes `cbac63c0…e8bc1` (parquet) e `e289e0c2…93f1` (valores). A `candle_version` persistida (`ec8ce812…b85a`, igual nas 3 buscas) é o SHA do parquet congelado reserializado com índice, diferente do hash da fixture.
- Banco, broker e cgroup eram privados/descartáveis; sem tráfego de exchange. Equivalência com a carga de PROD não é alegada.
- `test_discovery_celery_loss.py` ficou **skipped** nesta rodada (exige Redis em socket unix do host; o container `card-1093-redis` está parado e isolado por `--network none`). Última execução real: 1 PASS, 6,24 s (2026-10-13), antes do merge do develop.
- Residual de design a revisar (não alterado): uma combinação reclamada e ainda não iniciada continua sendo iniciada se o sweep entrar em `cancelling`/`paused` entre claim e início (design.md: pause/cancelling permitem assentar tentativa já iniciada); o pré-check do #853 foi substituído por fencing de ledger + reconciler. O claim é de uma combinação por vez, só sem outra `running`. Sweep inexistente deixa a combinação `running` até o lease vencer (sem FK; o reconciler itera sweeps existentes).

### Checks backend após o fast-forward para develop (task 5.5)

Todos via venv compartilhado, worktree, cluster PostgreSQL 16 privado recriado (`/tmp/card-1093-integration-20261013`, socket, role `card1093`; `max_connections` elevado a 100 neste cluster privado após `too many clients` com 12), nunca o banco compartilhado. Wrapper com `DATABASE_URL`/`PYTHONPATH` fora do repositório.

- Conflitos com develop/#1087 e contratos antigos corrigidos (escopo do card):
  - `test_discovery_celery_tasks.py`: o teste de janela de calendário agora verifica (a) a janela congelada em `claim_attempt` e (b) que `run_supervised` recebe exatamente essa janela; os fakes dos orquestradores passam `lease_owner` e neutralizam `reconcile_expired` (coberto por integração PostgreSQL). Antes: 6 FAIL; depois 43 PASS.
  - `test_discovery_insufficient_sample.py` e `test_discovery_ranking_metrics.py`: seeds com posse válida do ledger e fronteira `run_supervised` substituída; falha de fetch passa a esperar retry durável (`pending`, attempts=1, `next_attempt_at` definido) em vez de `failed`. Antes: 6 FAIL + hang por sessão vazada; depois 17 e 13 PASS.
  - `integration/test_discovery_service.py`: testes 4.7 e “sweep inexistente” adaptados ao fencing (escritor rejeitado; lease vencido → `skipped` pelo reconciler; nunca `pending` sob cancelamento/terminal).
  - `discovery_service.dispatch_outbox`: a retenção do wake-up por “sem pendente reclamável” bloqueava o finalizador de sweep `cancelling` com lease `running` (teste 4.5). Agora só retém se há pendentes aguardando backoff (`_has_pending`).
  - `test_inventory.json` +5 entradas (`indicator_binding`, `inputs`, `memory`, `memory_composition`, `supervisor`) e contagem 83→88 em `test_backend_unit_harness.py`.
- Resultados finais: unit (celery_tasks, supervisor, runtime/restart/status, actor_create_lock, favorite_metrics, go_nogo, insufficient_sample, ranking_metrics, favorite_operational_period, walk_forward, short_execution, execution_costs, inputs, memory_composition, indicator_binding, logic_parser, final_execution_mode, card_1086) **401 PASS, 1 skipped**; execução ampla anterior de fastpath/goldens/memory/composição/binding/inputs/1086/parser/final mode **436 PASS** (+6 FAIL de celery_tasks, depois corrigidos); integração (`test_discovery_service`, `deleted_favorite`, `favorite_metrics`, `memory_recovery`, `memory_migration`, `celery_loss`, `combo_backtest_data_source_inference`) + `contract/test_backend_unit_harness.py` **115 PASS, 1 skipped**; `test_discovery_supervisor.py` isolado 4 PASS, 5,09 s.
- `black --check` nos arquivos alterados: exit 0. `openspec validate card-1093-discovery-memory --strict`: válido. `git diff --check`: sem saída. Sem deploy, release ou alteração de PROD; revisão/QA podem prosseguir com as limitações acima.



## Correção pós-review (onda 1)

Quatro achados mecânicos corrigidos, sem commit, sem alterar Status, sem migração nova e sem mudar o formato persistido de `input_snapshot`.

1. **P2 `telemetry()`** (`discovery_resources.py`): `systemctl show` agora é best-effort; `OSError` (inclui `FileNotFoundError`) e `subprocess.SubprocessError` (inclui `TimeoutExpired`) degradam para `systemd = {}` e a falha é lembrada pela janela de 30 s (sem repetir o subprocesso a cada chamada). Testes em `test_discovery_memory.py`: timeout, binário ausente, `PermissionError`, `SubprocessError` e caso feliz (5 PASS).
2. **P2 `reconcile_expired`** (`discovery_recovery.py`, `discovery_tasks._reconcile_locked`): sem `sweep_id`, só entram sweeps não terminais, ou com combinação `running`/`pending`, ou com manifesto de entrada ainda não limpo (`inputs_cleaned` ausente); sweeps terminais limpos não são travados com `FOR UPDATE` nem reescritos. A query de manifestos seleciona só `input_snapshot['candle_manifest']`/`['inputs_cleaned']` (e `sweep_id`/`id`), não o JSON inteiro; a releitura das combinações a limpar é restrita aos ids sujos; `_reconcile_locked` passa a diferir a coluna `input_snapshot` e só grava `sweep.updated_at` quando contadores/estado mudam ou há `pending→skipped`. Chamada com `sweep_id` explícito continua reconciliando aquele sweep. Testes PostgreSQL privados em `test_discovery_memory_recovery.py`: terminal limpo não bloqueia sob lock concorrente (`lock_timeout`) e `updated_at` intacto; sweep em execução sem mudança não é reescrito; lease expirado de sweep não terminal continua reconciliado em varredura global; entradas não limpas de sweep terminal são descartadas uma vez e depois o sweep deixa de ser tocado.
3. **P3 `host_memory_pressure`** (`discovery_supervisor.py`): dois testes em `test_discovery_supervisor.py` com `host_memory` e relógio monotônico simulados (+12 s por sondagem) rodando `run_supervised` real com filho ocioso: MemAvailable<2 GiB contínuo aborta com `host_memory_pressure` na 4ª sondagem (36 s simulados; 24 s não aborta); recuperação antes de 30 s zera a janela e não aborta.
4. **P3 texto obsoleto**: `tasks.md` — bloco “Fronteira segura do Apply” reduzido a “Evidências do Apply” com uma linha apontando para este arquivo; `docs/discovery-memory-operations.md` — seção renomeada “Estado ao final do Apply (13/10/2026)” com a carga integral concluída em 13/10 às 23:39 UTC (3 buscas, pico ≈1,70 GiB, sem OOM, `Result=success`) e remoção das frases “em curso”. `ops/systemd/discovery-runtime-hold.conf` permanece como residual, sem decisão.

Inventário: nenhum arquivo de teste novo (casos adicionados a arquivos já inventariados), então a contagem 88 do harness não mudou; apenas o campo `evidence` de `test_discovery_memory.py` e `test_discovery_supervisor.py` em `test_inventory.json` foi atualizado.

Comandos (venv compartilhado, PostgreSQL privado `/tmp/card-1093-integration-20261013`, nunca o banco compartilhado; wrapper com `DATABASE_URL`/`PYTHONPATH` fora do repositório):

- Integração `test_discovery_service`, `deleted_favorite`, `favorite_metrics`, `memory_recovery` (16 casos, 4 novos), `memory_migration`, `celery_loss` + `contract/test_backend_unit_harness.py`: **110 PASS, 1 skipped** (celery_loss exige Redis em socket unix, container privado parado).
- Unit + `integration/test_combo_backtest_data_source_inference.py` (celery_tasks, supervisor 6 casos, restart/status/runtime worker, actor_create_lock, favorite_metrics, go_nogo, insufficient_sample, ranking_metrics, favorite_operational_period, walk_forward x2, short_execution, execution_costs, inputs, memory 17 casos, memory_composition, indicator_binding, logic_parser, final_execution_mode, card_1086 x2, card_945 fastpath/goldens): **572 PASS, 1 skipped**, 378,96 s.
- `black --check` nos 6 arquivos Python tocados: sem alterações pendentes. `openspec validate card-1093-discovery-memory --strict`: válido. `git diff --check`: sem saída.

Limitações: o ensaio de `host_memory_pressure` usa relógio e `/proc/meminfo` simulados (não esgota memória real); `celery_loss` segue skipped por exigir o Redis privado; não houve execução em systemd real, DEV compartilhado ou PROD.
