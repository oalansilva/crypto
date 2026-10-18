## Why

Concluir a rota CLI interativa com delegação nativa e revisão automática somente leitura comprovada, separando ensaios adicionais sem declarar suporte universal. Briefing vigente do #1098, copiado abaixo após a decisão explícita de Alan em 18/10/2026.

## Problema

Alan precisa acompanhar os agentes nativos do Codex no trabalho do card e executar a revisão com isolamento comprovado, sem alternar permissões manualmente no uso diário. A entrega ficou acumulada com ensaios de outras interfaces e etapas ainda não comprovadas.

## História

Como operador do Covenant Flow na CLI interativa, quero delegar o trabalho a agentes nativos com identidade, estado e retorno verificáveis e ter a revisão iniciada automaticamente em uma sessão somente leitura, para concluir o card com segurança sem configurar permissões a cada revisão.

## Entra

- Entregar e validar a rota CLI interativa no worktree do card, com filhos nativos nas etapas executadas neste fluxo. No Review, a exceção aprovada é um coordenador Codex exec dedicado que nasce somente leitura e inicia os dois reviewers nativos no mesmo turno; o principal permanece gravável.
- Preparar diff exato e SHA, capturas, prompts, planos e vínculos; comprovar a cadeia principal/coordenador/filhos, a leitura integral do mesmo diff, deny/readback de escrita dos dois reviewers e ambos completed com payload. `verify-wave` e checklist devem passar antes do commit; QA da CLI permanece obrigatório.
- Preservar seleção local por faixa, modelo/esforço observados, origem nativa, vínculo ao card/worktree/etapa e Guard. Demonstrar o caminho permitido e recusas pertinentes à rota entregue, distinguindo ensaios reais de fixtures.
- Preservar o critério de contexto escolhido: contrato aplicável, chamada nativa registrada com `fork_turns=none` e ensaio complementar completo. Atestação interna completa permanece `unavailable`; ausência isolada de sentinela não prova isolamento universal.
- Corrigir os defeitos identificados na revisão e concluir testes, documentação, procedência nucleus → consumidor e manifesto. Confiança do operador continua separada da instalação, somente quando o conteúdo confiado mudar.
- Registrar os controles realmente expostos na CLI para localizar responsáveis, acompanhar estados e receber retornos. Falha, interrupção e limitação devem ser visíveis; não contam como conclusão nem autorizam fallback silencioso.
- Conservar os gates humanos, dois pareceres independentes e isolamento somente leitura desde o nascimento. Não exigir alternância manual de permissões na rotina e não afirmar modo Auto.
- Preservar evidências históricas com seu escopo e hashes; uma qualificação antiga não comprova o código final.

## Não entra

- Ensaios de App/IDE, refinamento interativo completo, cobertura integral de todas as etapas/superfícies e rotas com principal exec independente/App/IDE: transferidos para #1128 por decisão explícita de Alan em 18/10/2026. Continuam pendentes, sem declaração de suporte universal.
- Retirar Review ou QA da rota CLI, dispensar evidências, executar etapas no pai como substituição, relaxar Guard ou confiar hooks automaticamente.
- Alterar modelos silenciosamente, mudar FSM/gates humanos, ampliar para outros clientes ou implantar em produção.

## What Changes

- CLI interativa no worktree: filhos nativos nas etapas do fluxo; somente Review usa coordenador exec dedicado automático read-only e dois filhos no mesmo turno.
- Manter contexto, seleção, binding, Guard, permissões, diff integral, verify-wave/checklist e QA; qualificar hashes finais sem promover diagnósticos históricos.
- Transferir 5.5/5.6/5.8 e partes multissuperfície de 5.1/5.7/6.3 ao [#1128](https://github.com/oalansilva/crypto/issues/1128), em Em Refinamento. 25/35 → 25/32 + três transferidas é mudança de escopo, não progresso de implementação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `codex-harness`: delegação nativa e coordenação Review CLI interativa → exec dedicado, com aceites reais e recusa quando faltar garantia.

## Impact

Harness Covenant Flow, documentação e evidências Codex; procedência nucleus → consumidor, manifesto e confiança separada permanecem obrigatórios. Sem alteração da UI Cripto, FSM, outros clientes ou produção. Pacote final inativo não é runtime validado. O recorte exige crítica independente, publicação e T7 humana; wording não autoriza implementação.

## Histórico anterior ao recorte CLI

Proposta anterior preservada abaixo, não normativa para o recorte vigente. Obrigações multissuperfície migram para #1128; a exclusão absoluta de sessões externas já fora substituída somente para coordenação Review.

<details>
<summary>Proposta anterior — histórico</summary>

## Why (histórico)

**Revisão de produto por Alan em 17/10/2026:** somente para a coordenação de Code Review, o requisito de mesmo chat abaixo é substituído por sessão Codex dedicada que nasce automaticamente read-only no mesmo worktree/card. O principal permanece gravável, prepara o diff e os receipts, lança o coordenador e coleta suas provas. O coordenador inicia dois reviewers NATIVOS no mesmo turno. Não há alternância manual de permissões no uso diário, troca de cliente ou review executado pelo principal/coordenador. As restrições históricas a sessões externas abaixo continuam valendo para as demais etapas e para alternativas ocultas; esta exceção é explícita e rastreável. A solução ainda precisa ser implementada e qualificada por superfície.

A delegação externa fragmenta o acompanhamento do card. A ocorrência do #1116 também revelou uma restrição pelo nome do host que impede Codex interativo sem avaliar todas as capacidades da sessão.

## Problema

Alan perde a visibilidade e o controle dos agentes na lista de subagentes do chat quando a orquestração abre sessões Codex CLI externas para executar etapas do card. No #1095, essa alternativa foi usada para contornar a limitação de vínculo do diretório da sessão, fragmentando o acompanhamento.

## História

Como operador do Covenant Flow, quero que todas as etapas delegadas usem subagentes nativos vinculados ao chat do card, sem abrir sessões externas de orquestração, para acompanhar seu andamento, identificar o responsável e interagir com a execução na mesma interface.

## Entra

- **Suporte aos clientes Codex (orientação de Alan em 17/10/2026):** o fluxo deve funcionar nas interfaces Codex usadas pelo operador, incluindo terminal interativo, execução não interativa e app/IDE via app-server, sem exigir troca para `codex exec` apenas por causa do nome do host. A compatibilidade deve ser estabelecida pelas capacidades e evidências verificáveis da sessão; identificar o host para diagnóstico, não usar uma comparação exclusiva com `codex_exec` como substituto da validação. Implementar as adaptações necessárias por superfície e demonstrar o caminho positivo; não declarar suporte universal sem ensaios reais. Se uma superfície não expuser uma garantia necessária, informar precisamente qual evidência/capacidade falta, preservando o estado, sem aprovação fictícia.
- Aceite adicional: uma sessão interativa Codex consegue iniciar e concluir o refinamento com filho nativo e evidência válida, sem abrir sessão externa; exec continua funcionando; app/IDE têm ensaio equivalente ou limitação específica documentada. Evidência ausente, vínculo incorreto, modelo/esforço divergentes e isolamento insuficiente continuam sendo recusados.

- Executar refinamento, Design, implementação, Code Review e QA por subagentes nativos vinculados ao chat do card, visíveis na lista de subagentes da sessão. Para cada etapa delegada, Alan consegue localizar o responsável, acompanhar seu estado, interagir com ele e receber seu retorno no mesmo chat.
- Eliminar a abertura de sessões externas como caminho normal ou alternativa silenciosa para delegação das etapas. A comprovação deve abranger tanto uma delegação concluída quanto uma tentativa impedida por limitação do host.
- Garantir que cada agente opere no worktree correto do card e que uma escrita autorizada não seja recusada por herdar o diretório de outro checkout. Demonstrar uma escrita permitida no card e na etapa corretos, além da recusa de tentativas fora do card ou da etapa autorizada.
- Preservar a seleção local de modelo e esforço por faixa e o isolamento do contexto dos filhos. Na delegação, a seleção aplicada deve corresponder à seleção prevista; indisponibilidade ou divergência deve ser informada antes da execução, sem substituição silenciosa. A ausência de evidência não conta como comprovação de isolamento ou de seleção aplicada.
- Comprovar nascimento, execução, conclusão e conteúdo retornado de cada filho, relacionando as evidências ao card, à etapa e ao agente responsável. Solicitar uma delegação não comprova que o filho nasceu ou concluiu; falhas e interrupções devem aparecer como tais, sem serem apresentadas como conclusão.
- Preservar os dois pareceres independentes do Code Review, sobre o mesmo diff verificado, com isolamento somente leitura comprovado no contexto que efetivamente governa pai e filhos; configuração ou prompt sozinhos não são prova. Demonstrar que ambos conseguem ler o material da revisão, que uma tentativa de escrita de cada revisor é recusada e que os dois pareceres retornam ao chat vinculados ao mesmo material revisado.
- Quando o host não permitir o vínculo ao chat, o diretório ou o isolamento exigidos, informar a limitação antes de iniciar o trabalho afetado, identificando a etapa impedida e a garantia que falta, sem recorrer a uma sessão externa oculta nem relaxar o gate. A etapa impedida não pode ser registrada como executada ou aprovada.
- Demonstrar no host real que o operador consegue localizar os subagentes na interface, acompanhar seus estados e receber seus retornos no chat, incluindo a revisão sem permissão de escrita. As evidências devem distinguir o que foi observado do que permanece não comprovado.
- Atualizar o processo e a documentação para refletir o caminho comprovado e o comportamento diante de limitações. O Design deve resolver as capacidades reais do host antes de prometer uma substituição integral; uma etapa sem garantia comprovada permanece explicitamente bloqueada e não conta como substituição concluída.

## Não entra

- Remover subagentes, executar as etapas no pai como substituição ou apenas renomear processos externos como agentes nativos.
- Dispensar evidências de runtime, alterar modelos silenciosamente, reduzir o isolamento da revisão ou contornar confiança/permissões do host.
- Alterar gates humanos, pular etapas ou implantar mudanças em produção.
- Migrar ou interromper automaticamente agentes já em andamento; a execução atual do #1095 permanece separada deste trabalho.
- Ampliar a mudança para os demais clientes sem escopo explícito.

## What Changes

- Qualificar terminal interativo, execução não interativa e app/IDE via app-server pelas capacidades e evidências da própria superfície; manter host/versão como diagnóstico.
- Executar as etapas delegadas com filhos nativos do mesmo chat, com vínculo ao worktree, seleção local, contexto isolado e ciclo de vida verificáveis.
- **BREAKING**: retirar sessões externas como alternativa de delegação, inclusive no Code Review; sem isolamento equivalente comprovado no mesmo chat, recusar a etapa.
- Preservar dois pareceres independentes, diff exato, gates humanos e evidência de runtime; demonstrar positivos e negativos reais, separando fixtures de ensaios.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `codex-harness`: delegação nativa no chat do card, qualificação por superfície, contexto efetivo autorizado e revisão somente leitura comprovada.

## Impact

Harness Covenant Flow: coletor, proxy, revisão, adapter, testes, runbook canônico e documentação Codex. A distribuição mantém procedência do nucleus e manifesto do consumidor; pin-base v1.1.22, bootstrap local ainda não publicado. Sem alteração do produto Cripto, da FSM ou de outros clientes. O bootstrap autorizado em 17/10 destravou a investigação, sem T7/T8 ou implementação concluída do card.

</details>
