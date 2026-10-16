## Context

Status: Design. Briefing integral copiado do issue #1093 via REST em 2026-10-13. Alan escolheu recuperação automática limitada e incluiu a correção da estratégia original neste card. Esta revisão altera somente OpenSpec; o Apply parcial precedente já alterou código e parou o worker DEV antigo, sem instalar a unit nova ou operar PROD. Os limites de memória aprovados permanecem.

UI impact: none
live_route: N/A
surface: none

Impeccable: N/A — execução interna e diagnóstico pelos canais operacionais existentes, sem tela/componente/interação redesenhados. Prototype: N/A. HTML generated/copied: N/A. Estado terminal e motivo usam o contrato existente de falha operacional.

Na baseline anterior ao Apply parcial, `combo_optimizer.py` materializa argumentos/batches/futures/resultados, soma planejadas como testadas antes dos retornos e absorve exceções do pool. R1 e R2–R4 têm caminhos distintos. `discovery_tasks.py` incrementa attempts em exceções além do claim e precisa cercar a persistência por posse. `discovery_service.py` usa TTL 300 s; owner por geração de outbox não identifica tentativa única. Unit DEV usa solo/concurrency=1 e Restart=always/5s: isso não limita ProcessPoolExecutor.

## Goals / Non-Goals

Conter árvore inteira DEV; manter busca, ranking, normalização e desempates; impedir sucesso incompleto; recuperar no máximo duas vezes e rejeitar escrita tardia. Incluir somente a correção explícita das referências RSI/ADX da estratégia original. Fora: mais RAM/VM, outras alterações de estratégias, UI nova, operar/publicar PROD ou atribuir incidentes do Codex ao OOM. Valores são proposta de Design, ainda sem medição de aceite.

## Decisions

### Referências da estratégia original e mudança observável

Fixture `backend/tests/fixtures/discovery_memory/original_template.json`: `long_ma_pullback_rsi_adx`, metadata 2026-10-03, RSI/ADX declarados com length=14 sem alias, grid varia 10..20. Entrada usa RSI_14<rsi_oversold e ADX_14>adx_threshold; saída usa RSI_14>rsi_overbought. `ComboStrategy._evaluate_logic_vectorized` já tenta compatibilidade após um preflight que rejeita referências ausentes; esse ordenamento impede alcançar a compatibilidade em 10/10. Teste pequeno confirma calculation_error em 10/10, cálculo em 14/14 e R1=492.480.

Decisão: resolução runtime com política explícita versionada `long_ma_pullback_rsi_adx/effective-indicators-v1`, sem migração/edição do template persistido. Ativação pelo nome exato e validação da declaração original: uma única instância RSI e uma ADX, ambas sem alias e length original 14. Preservar a identidade dessas instâncias antes de aplicar overrides. Vincular apenas identificadores inteiros RSI_14 e ADX_14 das expressões à série produzida por essas instâncias após resolver os parâmetros efetivos. Construir o contexto de avaliação antes de validar identificadores desconhecidos. Em candidato rsi_length=10/adx_length=20, RSI_14 significa TA-Lib RSI(length=10) e ADX_14 significa TA-Lib ADX(length=20); entrada e saída compartilham o mesmo binding de RSI. 14/14 continua referindo exatamente às séries históricas de 14.

Não substituir strings/substrings na expressão nem preencher coluna artificial com máscara falsa. Manter nomes físicos RSI_10/ADX_20 e mapear símbolos no contexto; não sobrescrever colunas existentes. Colisão de RSI_14/ADX_14 com outra origem, indicador duplicado, declaração divergente, produtor ausente ou token desconhecido causam erro explícito `indicator_reference_error`, tratado como calculation_error determinístico, sem retries operacionais nem resultado bem-sucedido. RSI_140, ADX_99 e outros tokens não ganham binding por semelhança. Uma referência literal existente fora dos dois bindings conserva seu significado atual; aliases estáveis e acesso pontuado já suportados continuam válidos. Não generalizar heurística a outros templates; seus caminhos/resultados permanecem inalterados. Mudança futura na declaração incompatível exige política explícita, nunca escolher a primeira instância encontrada.

Aplicar a mesma política compartilhada na otimização, cálculo final de treino, holdout com burn-in, Deep e fallback, e em consumidores que executam esse template. Transportar a identidade original/política junto do contexto, evitando reconstruí-la de DataFrame ou de indicadores já alterados. Fingerprint/chave de cache inclui versão da política, identidade do binding e parâmetros efetivos; cold/hot e A→B→A não cruzam períodos. Alternativas rejeitadas: reduzir grid a 14/14, calcular sempre RSI/ADX de 14, atualizar SQL do template ou mover toda heurística global antes do preflight sem restringir origem/ambiguidade.

Intenção preservada: avaliar o RSI e ADX configurados por cada candidato, com thresholds, comparadores, SMA/pullback, stop, fórmulas TA-Lib, custos, direção, score e desempates inalterados. Mudança observável submetida à aprovação: candidatos antes inválidos agora produzem sinais/trades/métricas; vencedor, ranking de candidatos e GO/NO-GO da busca completa podem mudar pela cobertura válida restaurada. Não alegar equivalência com uma busca antiga incompleta nem preservar seu falso resultado. Nenhum resultado histórico é reescrito.

Baseline em duas partes: (1) congelar 14/14 válido e outros templates existentes, exigindo igualdade exata de indicadores, máscaras, trades/métricas/holdout; (2) para candidatos antes inválidos, criar oracle independente usando TA-Lib com períodos efetivos e as expressões explícitas da fixture, sem chamar o resolver novo. Comparar cada par de períodos presente no grid original (10..20), combinações mistas 10/14/20, entrada/saída e thresholds, sem tolerância/rounding. Aquecimento NaN mantém semântica histórica; referência desconhecida nunca vira série False. Versionar manifesto/hash dessa nova referência semântica antes do benchmark. A referência do ranking completo usa o oracle corrigido com todos os candidatos e normalização global; otimização por memória deve ser exatamente equivalente a ela.

### Orçamento externo e admissão

DEV: MemoryAccounting=yes, MemoryHigh=5G, MemoryMax=6G, MemorySwapMax=512M, OOMPolicy=kill, KillMode=control-group, TimeoutStopSec=30s, SendSIGKILL=yes. Todos os filhos permanecem no cgroup, inclusive supervisor/pool. Verificar cgroup v2, limites efetivos, memory.oom.group e suporte systemd antes de admitir trabalho; ausência falha fechada. Limite cobre memória anônima, page cache e IPC, não só RSS. MemoryHigh é pressão; MemoryMax é contenção final.

VM descrita (~23 GiB): reservar ≥16 GiB físicos aos demais serviços e 1 GiB fora do máximo de 6 GiB. Confirmar MemTotal e inventário agregado não-Discovery no Apply, não só memória livre instantânea. Admissão exige MemAvailable≥8 GiB e swap disponível≥1 GiB. Orçamento incompatível mantém fila sem execução e emite resource_budget_unavailable; nunca elevar teto automaticamente. MemAvailable<2 GiB por 30 s aborta tentativa controladamente. Não se promete conter serviços alheios sem limites.

Paralelismo explícito por ambiente: DEV requested_workers=1; effective_workers=min(requested, floor((MemoryMax−2 GiB)/3 GiB)), mínimo admissível 1. Reserva de 2 GiB cobre pai/supervisor/serialização/page cache; envelope 3 GiB por worker inclui temporários. Configuração inválida recusa início. Sem CPU−1, sem elevar Celery concurrency/prefetch ou combinações simultâneas. Retries usam um worker sem elevar RAM/swap. Outros consumidores conservam defaults até optarem por perfil; proteções algorítmicas são compartilhadas.

### Cache, perfil e #1091

LRU agregado por processo/execução: 64 MiB de bytes retidos, 4.096 entradas e 32 snapshots, conforme limite mais restrito de #1091. Inclui fingerprint/indicadores/índice/intraday/coverage; não somar 64 MiB para cada cache. A hipótese de 256–512 MiB do briefing não é usada como piso. Chaves/valores/referências fortes contam; ndarray inclui backing buffers retidos, DataFrame inclui índice/deep memory/overhead conservador; não subcontar views. Item maior não entra; recalcular não invalida tentativa. Eviction mantém imutabilidade e identidade completa por dados/janela/parâmetros. Limpar na troca/fim de execução, inclusive pai. Bytes de cache não equivalem a RSS.

Medir tracemalloc/buffers conhecidos, RSS/PSS pai+filhos e memory.current/peak: memória nativa pandas/NumPy/TA-Lib não é coberta apenas por tracemalloc. Amostrar preparação, cálculo, serialização, flush e cleanup. Causa cache continua hipótese até perfil. #1091 está Em desenvolvimento segundo consulta viva do pai; compatibilidade/ordem de integração são dependência técnica, não espera obrigatória de entrega. Reutilizar sua API LRU sem substituição concorrente; se ainda ausente, limitar estruturas atuais e reconciliar na integração, mantendo sublimite mais restrito, identidade e fallback. Numba não é pré-requisito. Outro worktree foi apenas lido.

### Batches incrementais e ranking global

Enumerar candidatos em ordem idêntica, mesmos filtros, trial_index estável por etapa/ramo. Planned vem de passagem leve pelo gerador, sem materializar argumentos/DataFrames. Batch máximo 200 trials; janela máxima 2×effective_workers futures submetidos e não consumidos, limitada também a 64 MiB serializados pendentes. Reduzir batch por bytes sem mudar candidatos. Transportar dataset por contexto/worker quando viável; nunca copiá-lo para todo o grid.

Consumir resultados em spool local privado por tentativa/etapa/ramo, em disco fora de tmpfs e com permissão restrita. RAM de retenção ≤128 MiB, spool ≤2 GiB por tentativa; admissão exige 4 GiB livres. Quota/I/O falha operacionalmente, nunca trunca candidatos. Limpar no sucesso/falha e órfãos encerrados; spool não é checkpoint de retry.

Primeira passagem em trial_index computa mínimos/máximos exatos por domínio atual: R1 por etapa e R2–R4 por etapa de cada ramo, nunca por batch ou entre ramos. Segunda passagem aplica expressão atual 0.7*ns+0.3*nr e ordem float. Proibido top-k antes dos extremos globais. Preservar empates, return_top_n*2 e entrada integral necessária à diversidade/_select_top_candidates. Quando preciso, ordenação externa limitada em RAM; representação preserva floats/NaN/inf/tipos/ordem. Casos não finitos exigem igualdade com ordenação Python atual, sem saneamento silencioso. Representação/algoritmo são P3 de Apply, condicionados a goldens completos.

### Supervisor e cleanup no solo

Celery solo permanece. Não depender de soft_time_limit/max_tasks_per_child/revoke do Celery. Cada combinação usa supervisor descartável com spawn e grupo POSIX próprio; este cria ProcessPoolExecutor com spawn explícito. Celery acompanha canal limitado de eventos e vida do supervisor. Heartbeat usa sessão PostgreSQL própria; não compartilhar Session/conexões herdadas.

BrokenProcessPool, filho perdido, MemoryError, pressão persistente, timeout sem progresso, spool inválido ou retorno incompleto abortam tentativa inteira. Parar submissão, cancelar pendentes, SIGTERM ao grupo exclusivo, esperar até 10 s, SIGKILL remanescentes e reap até 20 s totais. Validar identidade/grupo da tentativa para não sinalizar outro serviço. Não abrir pool antes de provar grupo vazio. Cleanup sem prova encerra principal com falha; systemd limpa cgroup antes do restart. OOM inteiro usa OOMPolicy/KillMode e ledger durável. Python 3.12 shutdown(cancel_futures=True) não mata iniciados; não depender de APIs posteriores como terminate_workers nem de with-executor bloqueante como única proteção.

### Contadores e resultado incompleto

Distinguir combinações do sweep e trials internos. Por tentativa/etapa: planned, executed, succeeded, failed, unknown, remaining. executed=succeeded+failed significa conclusões confirmadas por trial; unknown são submetidos sem conclusão confirmada após perda; remaining=planned−executed−unknown. Não afirmar CPU executada exatamente após SIGKILL. Planned nunca vira executed antecipadamente. Dedupe por attempt/etapa/ramo/trial_index. Progresso em memória pode antecipar flush; apenas ledger confirmado é durável.

Etapa avança apenas com executed=planned, unknown=0 e nenhuma falha. success=False por erro de cálculo também impede vencedor de busca parcial; ausência válida de sinais continua sucesso. Erro determinístico não ganha retries operacionais adicionais: falha com motivo específico. Sem fallback de candidato para pool quebrado, sem novo resultado/GO-NO-GO incompleto. Resultados anteriores do sweep permanecem. Esforço repetido fica em histórico de tentativas, sem inflar resultados lógicos.

### Recuperação durável e intervenção

Máximo 3 tentativas por combinação (inicial+2), backoffs mínimos 60 s e 300 s. Antes do spawn, transação de claim grava attempt_seq monotônico, owner UUID, lease_generation, started_at/heartbeat_at/progress_at, perfil e contadores. attempts incrementa uma vez por começo autorizado, nunca na exceção/ACK/reentrega. Persistir next_attempt_at, last_failure_code e histórico por tentativa. Morte antes de reportar consome slot. Retry refaz combinação inteira, snapshot congelado, sem resultados provisórios; resultado commitado é reconhecido sem recálculo.

Reconciler no runtime-worker existente, fora do cgroup Discovery, a cada 30 s e startup/dispatch. Expiração sob lock encerra tentativa interrompida, revoga geração, grava backoff e agenda outbox deduplicado se houver orçamento. DB indisponível impede admissão/persistência; quando volta, reparar ledger. Publicação respeita next_attempt_at/recursos. Broker, autoretry e restart não são orçamento independente: todo início passa pelo claim durável; retirar autoretry genérico que contorne o gate.

Terceira falha recuperável: combinação failed, sweep failed com terminal_reason=operational_failure e terminal_code=resource_recovery_exhausted; preservar resultados e marcar demais não iniciadas skipped na reconciliação transacional. Mensagem operacional: “Recuperação automática esgotada após 3 tentativas. Intervenção necessária; revise os recursos antes de iniciar nova busca.” Usar estado/motivo existentes e alerta journal, sem frontend/canal externo novo. Cancel impede retry; pause conserva prazo/contador até resume. Restart não reseta orçamento; novo sweep explícito tem novo orçamento.

Restart=on-failure, RestartSec=60s, StartLimitIntervalSec=900, StartLimitBurst=3. Circuito persistido por ambiente abre após 3 falhas de recursos/interrupções operacionais em 15 min, bloqueando inclusive novos sweeps até comando administrativo local autenticado de reconhecimento, condicionado a grupo vazio, nenhum lease ativo e admissão saudável; registrar ator/motivo/data. O comando fecha o circuito, mas não zera tentativas nem reinicia sweeps terminais. Claim pré-spawn conserva contagem através de OOM; lease expirado sem causa comprovada é interrupção operacional, não OOM presumido. Circuito/start-limit complementam o limite por combinação.

### Lease, progresso e fencing

TTL 300 s, heartbeat 30 s independente de batch, relógio PostgreSQL. Renovar somente owner+lease_generation+attempt_seq atuais, lease ainda válido. Claim de uma combinação por vez, não reservar 20 enquanto só primeira executa. Atualizar progress_at por trial concluído/mudança verificável de fase; heartbeat não comprova progresso. Aviso após 120 s sem avanço, aborto após 600 s. Etapa >30 min válida com avanços regulares. Download/preparo/relatório têm progresso verificável ou mesmo deadline; callback vazio não reseta progresso.

Antes de flush ou persistência de sucesso/failed/insufficient_sample/final: lock sweep→combinação, refresh, CAS geração/owner/attempt, lease não expirado, combinação running. Pause/cancelling permitem assentar tentativa já iniciada conforme contrato atual; terminal bloqueia nova escrita. Resultado final exige manifesto completo de etapas. Reconciler usa mesma ordem de locks e unicidade. Perda de posse encerra execução e descarta saída tardia sem alterar nova tentativa. Geração de outbox é separada de lease.

## Validation

Após T8: unitários e integração PostgreSQL em banco descartável/role sem acesso a crypto_app/crypto_app_dev; Redis/fila exclusiva e fixtures sem HTTP de exchange. Nunca destruir fila discovery real. OOM em unit transitória isolada MemoryMax=512 MiB/MemorySwapMax=0, grupo próprio, dados sintéticos; comprovar cgroup antes de alocar e abortar se ausente.

Cobrir morte de filho/supervisor/Celery e OOM inteiro; restart entre claim/spawn, commit/ACK e agendamento/publicação; redelivery até terceira falha, cleanup sem órfãos, heartbeat >30 min, DB indisponível, persistência tardia, cancel/pause concorrentes, unknown e bloqueio da próxima rodada. Reconciler externo deve convergir mesmo com Discovery em start-limit. Verificar alerta/circuito entre sweeps.

Comparação exata contra a referência aplicável (histórica válida ou oracle semântico corrigido acima): candidatos, parâmetros, métricas, trades, score, ordem, diversidade, treino/holdout e GO-NO-GO sem tolerância/rounding. Incluir empate, extremos no último batch, NaN/inf conforme referência, R1/R2–R4, cache fria/quente/eviction, três workers isolados e um DEV.

Após ensaios reduzidos, DEV contido reproduz carga exata 492.480 com manifesto dados/grid/SHA. O journal identifica BTC/USDT 15m long, 2025-10-06..2026-10-06, treino 24.528/holdout 10.513/burn-in 250 e quatro rodadas. 492.480 é o tamanho confirmado de R1; executar R1 integral e as rodadas seguintes geradas, não parar na primeira. Preservar manifesto/hash dos candles para reprodução; não fabricar carga apenas pela contagem. Ausência de manifesto é bloqueio da evidência de reprodução no Apply. Fazer 3 buscas consecutivas; cache volta a zero lógico; pós-cleanup terceira−primeira≤128 MiB e sem crescimento monotônico >64 MiB por execução. Registrar cgroup memory.current/peak/swap/events, RSS/PSS, cache/spool/futures, duração, contadores, reinícios e tempo sem progresso. Aceite: ≤6 GiB/512 MiB, zero OOM global, busca integral e igualdade. Sem SLA novo de velocidade.

## Risks / Trade-offs

- Um worker/spool aumentam duração/I/O → medir sem mudar busca.
- Temporários/allocator retêm RSS → supervisor descartável e cgroup; não elevar teto.
- Page cache compete com RAM → spool limitado contabilizado no cgroup.
- Retry repete trabalho → duas recuperações, backoff e ledger; checkpoint parcial fora.
- #1091 toca arquivos comuns → LRU única e goldens após integração; benchmark dele com três workers não altera DEV.

## Migration Plan

Migração aditiva PostgreSQL para tentativas/fencing/circuito/contadores. Bloquear admissão DEV e drenar/interromper coordenadamente árvore antes de aplicar teto; não reduzir MemoryMax sobre os 14 GiB relatados. Capturar/reconciliar claims antigos; backfill conservador de attempts (≥3 não reinicia). Não coexistir worker antigo sem fencing com novo. Migrar, instalar perfil na unit DEV do overlay, validar propriedades efetivas e liberar execução controlada. Não operar PROD; release futura pelos gates.

Rollback mantém cgroup e admissão bloqueada, limpa filhos e preserva ledger/resultados. Não voltar a worker sem fencing sobre leases novas. Reversão algorítmica exige adapter compatível/limites iguais; alternativamente manter Discovery parada até correção. Sem downgrade destrutivo de histórico.

## Open Questions

### Fronteira preservada do Apply parcial (2026-10-13)

Alan solicitou incluir neste card a correção da incompatibilidade entre referências dos indicadores e períodos do grid, para permitir completar a carga original de 492.480 trials. O contrato aprovado anteriormente excluía alterar regras de estratégia. A seção de resolução runtime acima é o contrato revisado a criticar/aprovar antes de retomar implementação; nenhum critério de reprodução foi reduzido.

Evidência read-only do DEV: o template `long_ma_pullback_rsi_adx`, atualizado em 2026-10-03, referencia `RSI_14`/`ADX_14`, enquanto o grid varia `rsi_length`/`adx_length` de 10 a 20. A fixture pequena versionada comprova `calculation_error` para períodos 10/10 e cálculo válido para 14/14; a geração da etapa R1 mantém exatamente 492.480 trials. Journal identifica BTC/USDT 15m, long, janela 2025-10-06 a 2026-10-06, treino 24.528/holdout 10.513/burn-in 250, quatro rodadas. Não houve correção do template nem redução do grid durante este Apply.

A implementação de memória/recuperação foi preservada parcialmente. Evidência prévia: 20 testes + 1 fixture PASS e OOM isolado 512 MiB contido; ensaio supervisor 2 PASS/1 FAIL, filho perdido retornou em ~30 s ante teto de 20 s. Esse defeito de Apply continua pendente, sem aumentar o teto ou reabrir decisão de produto. A reprodução integral e as três buscas consecutivas permanecem sem aceite. O worker Discovery DEV antigo foi parado, com MainPID=0; nenhuma unit/banco/fila PROD foi operada. Os demais itens pendentes e evidências estão em `apply-evidence.md` nesta change.

Nenhuma decisão de produto pendente. P3 aceitos para Apply: representação spool/LRU, nomes de campos/helpers, versões/cgroup/inventário reais, manifesto da carga e medição de envelopes. Evidência insuficiente não vira aceite. Crítica independente posterior pelo pai, teto 1 autor+1 crítico+1 rework.

## Design Critique

- P0/P1/P2: nenhum achado na crítica independente do escopo revisado.
- P3 — Identidade do binding/cache e oracle independente exigem os testes previstos. Disposition: aceito para Apply.
- P3 — Cleanup observado em aproximadamente 30 s continua pendente; teto permanece 20 s. Disposition: corrigir no Apply.
- P3 — Cleanup/spool após OOM e goldens de LRU/ordenação permanecem aceitos para Apply.
- Disposition: revisão aprovada sem rework obrigatório; 1 autor + 1 crítico nesta revisão de escopo.
- Verdict: APPROVED_WITH_ACCEPTED_P3.

## Technical references

[Python 3.12](https://docs.python.org/3.12/library/concurrent.futures.html) documenta cancelamento de futures; [Celery](https://docs.celeryq.dev/en/stable/userguide/concurrency/index.html) documenta limites dos pools alternativos. Manual systemd web retornou 403; confirmar contrato na versão instalada durante Apply. Fontes locais/overlay foram lidos; valores vivos não foram presumidos como medição atual.
