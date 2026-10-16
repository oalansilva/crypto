# Snapshot Design Critique — #1093

Data: 2026-10-13. Rodada: crítico único sem tela; teto 1 autor + 1 crítico + 1 rework. Sem nova rodada solicitada.

## Contexto e autorização

Issue: https://github.com/oalansilva/crypto/issues/1093. Briefing lido via REST. Consulta GraphQL pontual confirmou Project 1, Status=Design. Branch/worktree: `card-1093-discovery-memory`, `/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory`. Ação limitada à crítica e a este snapshot; nenhum produto, OpenSpec, serviço ou Status alterado.

Skills canônicas lidas: `.cursor/skills/design-critic/SKILL.md`, `.cursor/skills/covenant-flow/SKILL.md`; consulta pontual conforme `github-project-board`. Overlay lido por envolver contrato de banco e ambiente DEV. Precedência mantida: FSM/Guard e skill canônica acima das instruções legadas conflitantes do overlay.

## Rubrica e evidências

- Pacote completo lido: `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md` e os três deltas `combo-optimizer`, `discovery-sweep`, `discovery-resource-budget`. Validação strict anterior informada pelo pai; esta crítica não constitui execução dos testes futuros.
- Briefing preservado no proposal, inclusive a decisão de recuperação limitada e a distinção entre hipóteses e valores ainda não medidos. Reproduzir a carga original depende explicitamente do manifesto, sem fabricar evidência pela contagem.
- Tokens parseáveis presentes em linhas próprias: `UI impact: none`, `live_route: N/A`, `surface: none`. Justificativa sem tela adequada: diagnóstico operacional e contratos existentes; não há rota emprestada ou protótipo necessário.
- Intervenção usa mensagem de journal e estado/motivo existentes. `frontend/src/pages/DiscoveryPage.tsx` já mostra o motivo terminal e os contadores; o design não promete exibir a nova frase na interface. Portanto a mensagem operacional é compatível com UI impact none.
- `openspec/specs/discovery-sweep/spec.md`, requisito de lifecycle, permite terminal `failed/operational_failure` com sucessos anteriores preservados; `partial_failure` restringe-se à reconciliação normal sem falha operacional. O terceiro fracasso proposto não contradiz esse contrato. A combinação encerrada falha, demais pendentes são ignoradas, resultados commitados permanecem e processed=total representa disposições, não trials executados.
- Limites DEV abrangem cgroup e descendentes, RAM/page cache/IPC e swap. 5/6 GiB, 512 MiB e um worker são propostas de Design sujeitas à validação do host; ausência de limites/reserva impede admissão. Não se afirma que as medições de aceite já existem.
- Cache único agregado de 64 MiB por processo, com 4.096 entradas/32 snapshots, evita ampliar o orçamento informado de #1091. Reutilização da API e goldens de integração estão previstas. Esta crítica não inspecionou nem alterou o worktree de #1091 e não certifica sua implementação.
- Spool de duas passagens mantém domínio global por etapa/ramo, expressão float, diversidade, ordem e desempates; proíbe truncamento/top-k prematuro e inclui não finitos nos goldens. Representação e algoritmo ficam corretamente em Apply.
- Três tentativas totais são contadas duravelmente antes de spawn; morte pré-report consome slot, reentrega não cria orçamento, restart não reseta ledger e novo sweep não contorna circuito aberto. Backoff e reconhecimento administrativo não apagam histórico.
- Reconciler no runtime-worker, fora do cgroup Discovery, cobre morte do Celery/OOM total e start-limit. Heartbeat separado de progresso, prazo de posse, owner/attempt/geração e ordem de locks impedem escrita tardia. Cleanup do grupo precede substituição, com systemd como contenção quando não há prova de limpeza.

## Design Critique

- P0/P1/P2: nenhum achado de produto, escopo ou contrato visível.
- P3 — Detalhe de Apply: concretizar a limpeza de spools órfãos e a emissão deduplicada da intervenção no reconciler externo; o ensaio de OOM total/start-limit deve provar ambos sem depender do worker morto. Disposition: aceito; coberto pelas tasks 2.4, 3.5, 4.2 e 5.3, sem novo requisito de produto.
- P3 — Detalhe de Apply: concretizar a ordenação externa e contabilização conservadora de referências/buffers na LRU compartilhada; usar os goldens já previstos, incluindo NaN/inf, empates e extremos no último batch. Disposition: aceito; coberto pelas tasks 2.2, 2.4 e 5.1, sem reabrir fórmulas ou ranking.
- Disposition: aprovado com P3 aceitos para Apply; nenhuma correção obrigatória de Design nem nova rodada.
- Verdict: APPROVED_WITH_ACCEPTED_P3.

## Metadata e limites

Papel: design-critic. Faixa: juízo. Captura de nascimento: `/tmp/card-1093-design-critic-birth-20261013.json`, attempt_id `158ef54a-d7ca-4ec4-8d21-9c834e9bc4dc`, capture_sha256 `2d6f234bcb266bcd76f65cb3ad0645eda69e69104fb811ca93c966c3623a9468`.

Requested, lido da captura: GPT-6 Astra (`gpt-6-astra`), reasoning_effort `medium`. Observed, informado pelo pai a partir do trace autoritativo: `gpt-6-astra`, effort `medium`, Codex CLI `0.162.1`, sandbox `danger-full-access`, agent_path `/root/design_1093_critic`, session id `01a132e1-3267-7060-aa5b-05ee59863071`. Trace indicado pelo pai: `/home/ubuntu/.codex/sessions/2026/10/13/rollout-2026-10-13T01-29-41-01a132e1-3267-7060-aa5b-05ee59863071.jsonl`. O crítico não inferiu observado da configuração; verificação de runtime/proxy final pertence ao pai.

proxy modelo: design-critic → GPT-6 Astra (gpt-6-astra)

Spawns pelo crítico: 0. HTML generated/copied: N/A. Sem teste de produto, benchmark ou alteração de infraestrutura nesta crítica. Aprovação de Design por Alan e posterior T8 continuam necessários para Apply.
