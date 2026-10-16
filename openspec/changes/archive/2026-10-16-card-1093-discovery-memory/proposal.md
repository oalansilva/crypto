## Why

Conter o consumo de memória da Descoberta e impedir conclusão falsa ou repetição ilimitada após falha operacional em VM compartilhada.

## Problema
Em 12/10/2026, às 12:00:48 e 12:36:30 (São Paulo), ocorreram dois OOMs globais na VM. O kernel matou processos Celery do discovery DEV; restavam 196 KiB e 244 KiB da swap de 4 GiB. Alan e os demais operadores sofreram lentidão, com risco aos serviços de produção que compartilham a VM.

Na investigação, discovery DEV ocupava aproximadamente 14 GiB, com pico de 20 GiB numa VM de aproximadamente 23 GiB, sem MemoryHigh/MemoryMax. A busca tinha 492.480 combinações, 2.463 batches e três processos internos, apesar de Celery concurrency=1. Após o primeiro OOM, houve restart automático e nova execução da carga.

O otimizador mantém cache de DataFrames/indicadores por processo sem teto explícito e submete todos os batches ao executor. O cache é hipótese forte para o crescimento, ainda dependente de perfil de alocações. Após quebra do pool, os logs mostraram 32.000 combinações processadas, mas contabilizaram 492.480 como testadas e avançaram à rodada seguinte. Dois filhos permaneceram grandes; serviço active não comprovava progresso.

## História
Como operador do Cripto Farol, quero executar discovery com consumo de recursos limitado e recuperação confiável, para que uma busca pesada ou um processo interrompido não comprometa a VM nem apresente execução incompleta como concluída.

## Entra
- Corrigir a incompatibilidade preexistente entre referências de indicadores e períodos variáveis do grid da estratégia original, para permitir completar a busca de 492.480 combinações na primeira rodada e suas rodadas seguintes. Alan incluiu esta correção no mesmo card em 13/10/2026 UTC; detalhar a semântica no Design revisado antes de implementar esse escopo. Preservar ranking, cobertura e intenção da estratégia; explicitar qualquer alteração observável para aprovação.
- Definir orçamento de memória/swap para o serviço inteiro e seus filhos, inicialmente em DEV, considerando reserva para PROD, banco e demais serviços.
- Tornar o paralelismo interno configurável por ambiente e orçamento, sem depender somente de CPU - 1 ou concurrency do Celery.
- Medir alocações; limitar cache por bytes com descarte; controlar geração/submissão de batches e retenção de resultados, preservando ranking, normalização e desempates.
- Tratar pool quebrado/OOM como falha operacional: interromper etapa, encerrar filhos, reconciliar estado e impedir sucesso silencioso ou avanço com trabalho faltante.
- Separar contadores de planejadas, executadas, bem-sucedidas e falhas.
- Após interrupção por falta de memória ou falha de processo, tentar recuperar automaticamente a execução com tentativas limitadas, sempre respeitando o orçamento de recursos. Esgotadas as tentativas, interromper e informar ao operador a necessidade de intervenção. A quantidade de tentativas, os mecanismos de recuperação e seus parâmetros serão definidos no Design; não foram aprovados nesta decisão.
- Verificar lease padrão de 300 segundos diante de etapas superiores a 30 minutos; definir heartbeat, detecção de falta de progresso e validação de posse antes de persistir.
- Monitorar memória, swap, OOM, reinícios e tempo sem progresso; validar compatibilidade das proteções com o pool solo.

### Critérios de aceite
- [ ] Orçamentos e paralelismo documentados e validados em DEV, com margem explícita para os demais serviços.
- [ ] Reexecutar a carga de 492.480 combinações dentro do orçamento, sem OOM global; registrar pico, duração e progresso.
- [ ] Buscas consecutivas não apresentam crescimento contínuo de memória além do orçamento.
- [ ] Interrupção controlada de filho comprova detecção, encerramento dos filhos restantes, estado reconciliado e ausência de conclusão falsa.
- [ ] Excesso de orçamento em teste isolado fica contido no serviço, com recuperação automática limitada que respeita o orçamento e sem ciclo de OOM/restart.
- [ ] Após interrupção por falta de memória ou falha de processo, a execução tenta se recuperar automaticamente dentro dos limites definidos no Design; esgotadas as tentativas, interrompe e informa ao operador a necessidade de intervenção, sem declarar conclusão falsa.
- [ ] Contadores distinguem trabalho planejado de executado; falhas de infraestrutura não são ocultadas como sucesso.
- [ ] Comparação com referência determinística comprova preservação de ranking, normalização e desempates.
- [ ] Leases/heartbeat, reentrega e persistência tardia são validados sem duplicação efetiva ou sobrescrita por executor sem posse.
- [ ] Alertas distinguem processo ativo de tarefa progredindo, com evidências registradas.

### Fora do escopo
- Aumentar RAM/swap ou migrar VM como substituto da correção.
- Alterar ranking, reduzir silenciosamente o espaço de busca ou mudar outras regras da estratégia além da correção explícita da incompatibilidade entre referências de indicadores e períodos do grid incluída por Alan.
- Operar ou publicar em PROD no refinamento; eventual rollout segue release.
- Atribuir timeouts do Codex ao OOM sem evidência específica.

### Hipóteses para o Design
Avaliar MemoryHigh=5 GiB, MemoryMax=6 GiB, MemorySwapMax=512 MiB, um processo interno em DEV e cache de 256–512 MiB por processo. Valores não aprovados nem validados: calibrar com medições. Aplicar teto abaixo do consumo atual exige contenção coordenada e recuperação da tarefa.

### Referências e evidências
- backend/app/services/combo_optimizer.py: cache, batches, exceções e executor.
- backend/app/tasks/discovery_celery_tasks.py e backend/app/celery_app.py: orquestração, retries e reentrega.
- backend/app/tasks/discovery_tasks.py e backend/app/services/discovery_service.py: estado, claims e leases.
- Journal do kernel e discovery DEV de 12/10/2026, 15:00–15:37 UTC; systemctl show e processos consultados por volta de 22h de São Paulo.

Prioridade proposta: P0, pela recorrência de OOM global em VM compartilhada. Nenhum código ou serviço foi alterado na investigação. Implementação após Design e Aprovação de Design.



## What Changes

- Corrigir no runtime de long_ma_pullback_rsi_adx o vínculo de RSI_14/ADX_14 aos períodos efetivos, sem migração do template nem alteração de thresholds. Candidatos antes inválidos passam a ser calculados, podendo alterar vencedor/resultados finais.

- Orçamento DEV de serviço/filhos, paralelismo explícito, cache agregado por bytes e processamento incremental.
- Falha operacional com tentativas duráveis limitadas, heartbeat e fencing de persistência.
- Contadores separados e evidência isolada de memória, equivalência e recuperação.

## Capabilities

### New Capabilities
- `discovery-resource-budget`: limites de serviço, memória interna, recuperação e observabilidade.

### Modified Capabilities
- `combo-optimizer`: resolução explícita de indicadores da estratégia original e baseline semântico aprovado; batches limitados, retenção externa exata, paralelismo configurável e busca incompleta sem sucesso.
- `discovery-sweep`: posse renovável, tentativas duráveis e reconciliação cercada por geração.

## Impact

Backend: ComboStrategy e consumidores da estratégia original, combo_optimizer, discovery_tasks, discovery_celery_tasks, discovery_service, modelos/migração PostgreSQL, configurações e testes. Operação: unit discovery DEV e instalador; sem alteração operacional de PROD nesta entrega DEV. Sem frontend/protótipo. Depende de reconciliação técnica com #1091, cujo orçamento de cache de 64 MiB é preservado; Numba não é pré-requisito. Status: Design; Apply somente após aprovação humana e T8.
