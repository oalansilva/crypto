## 1. Baseline e isolamento

- [x] 1.1 Confirmar T8 e baseline SHA; reconciliar integração #1091 sem substituir sua API de cache; registrar versões Python/Celery/systemd/cgroup e inventário/reserva real do DEV.
- [x] 1.2 Recuperar manifesto original da carga 492.480 (dados, grid, janela, etapa/rodadas); versionar baseline determinístico e harness reproduzível sem banco/fila PROD.
- [x] 1.3 Preparar PostgreSQL/role, broker/fila e cgroup descartáveis com acesso segregado; demonstrar limites antes de qualquer injeção de OOM.

## 2. Orçamento e memória do motor

- [x] 2.1 Implementar perfil configurável, admissão por reserva/limites e worker efetivo; DEV um worker, sem fallback CPU−1 ou aumento automático em retries.
- [x] 2.2 Medir alocações Python/nativas/serialização e RSS/PSS/cgroup; aplicar LRU agregado 64 MiB/4.096 entradas/32 snapshots compatível com #1091, eviction e limpeza por execução.
- [x] 2.3 Substituir materialização de candidatos/futures por geradores e janela limitada em R1 e R2–R4; máximo 200 por batch, 2×workers futures e 64 MiB pendentes.
- [x] 2.4 Implementar spool privado ≤2 GiB e retenção ≤128 MiB, duas passagens globais por domínio e seleção idêntica; quotas/cleanup e erros de I/O sem truncamento.
- [x] 2.5 Retirar sucesso/fallback após pool quebrado ou erro de cálculo; contadores planned/executed/succeeded/failed/unknown/remaining e barreira de completude antes de rodada/resultado.

## 3. Posse e recuperação

- [x] 3.1 Criar migração aditiva de ledger de tentativas, owner/geração, heartbeat/progresso, next_attempt_at/failure e circuito; backfill conservador e uma contagem por claim pré-spawn.
- [x] 3.2 Executar combinação em supervisor spawn/grupo próprio com ProcessPoolExecutor spawn; canal limitado e cleanup TERM/KILL/reap comprovado em até 20 s, incluindo perda de filho/principal.
- [x] 3.3 Implementar heartbeat 30 s/TTL 300 s com sessão própria e CAS; aviso 120 s/aborto 600 s sem progresso real; cercar toda persistência e contagem por posse válida.
- [x] 3.4 Implementar retries duráveis inicial+2, backoff 60/300 s e snapshot congelado; integrar reentrega/outbox/Celery sem orçamento paralelo ou ressurreição terminal.
- [x] 3.5 Integrar reconciler externo ao cgroup Discovery no runtime-worker (30 s/startup/dispatch); preservar pause/cancel/resultados commitados e rejeitar escritor antigo.
- [x] 3.6 Fechar terceira falha como operational_failure/resource_recovery_exhausted, reconciliar contadores e emitir intervenção; circuito por ambiente e reconhecimento administrativo auditado sem reset de tentativas.

## 4. Operação DEV e observabilidade

- [x] 4.1 Versionar unit/instalador DEV com MemoryHigh=5G/MemoryMax=6G/MemorySwapMax=512M, OOMPolicy=kill, KillMode=control-group e restart/start-limit do Design; não operar unit PROD.
- [x] 4.2 Expor métricas de cgroup/RSS/PSS/cache/spool/futures/OOM/restart/progresso e alertas de admissão/intervenção; usar motivos e canais existentes sem novo frontend.
- [x] 4.3 Documentar e ensaiar parada de admissão/drenagem/cleanup antes do teto, migração, validação efetiva e rollback conservando ledger/limites; impedir worker antigo coexistente.

## 5. Validação e evidência

- [x] 5.1 Executar goldens exatos contra baseline histórico válido ou oracle semântico corrigido de 6.1, de ranking/normalização/desempates/diversidade/holdout, extremos no último batch, NaN/inf, cache fria/quente/eviction, ambos caminhos de rodadas e composição com #1091.
- [x] 5.2 Executar integração PostgreSQL de morte antes/depois de claim/commit/ACK, reentrega/backoff/exaustão, lease >30 min, escrita tardia, indisponibilidade DB e cancel/pause concorrentes.
- [x] 5.3 Executar injeção isolada de morte de filho/supervisor/Celery e excesso de 512 MiB no cgroup de ensaio; provar cleanup, counters honestos, circuito e nenhuma conclusão falsa/OOM global.
- [x] 5.4 Só após ensaios seguros, reproduzir no DEV contido a carga original 492.480 e três buscas consecutivas; registrar pico/duração/progresso e limites de crescimento pós-cleanup. Manifesto dos candles ausente bloqueia este aceite; fixture do template e tamanho R1 já foram recuperados.
- [x] 5.5 Rodar checks backend proporcionais e openspec validate estrito; anexar comandos, manifests, resultados terminados, limitações e handoff para revisão/QA sem alegar deploy PROD.


## 6. Correção da estratégia original — executar após aprovação do Design revisado

- [x] 6.1 Congelar golden válido 14/14 e referência independente TA-Lib para todos os pares de períodos do grid 10..20, com manifesto/hash; preservar fixture original e evidência do defeito anterior, adaptando teste de regressão somente após aprovação.
- [x] 6.2 Implementar política runtime explícita de binding RSI_14/ADX_14 por identidade original e período efetivo antes do preflight, sem migração de template/string replace/redução de grid; incluir política/identidade na chave de cache.
- [x] 6.3 Aplicar resolução compartilhada em entrada/saída, otimização, final/holdout, Deep/fallback e consumidores do template; testar aliases/referências existentes, outros templates, colisões, desconhecidos, produtores duplicados e A→B→A sem máscaras falsas.
- [x] 6.4 Validar outputs corrigidos contra oracle independente, manter equivalência histórica válida e completar R1=492.480 mais rodadas seguintes na carga original antes de aceitar a reprodução 5.4; registrar qualquer vencedor/veredito alterado pela cobertura restaurada.
- [x] 6.5 Corrigir defeito já observado em 3.2/5.3 (perda de filho ~30 s), repetindo ensaio até comprovar cleanup dentro do teto original de 20 s, sem ampliar orçamento.

## Evidências do Apply

Estado e evidências finais do Apply estão em `apply-evidence.md`.
