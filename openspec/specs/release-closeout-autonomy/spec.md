# release-closeout-autonomy Specification

## Purpose
TBD - created by archiving change card-1059-codex-release-closeout. Update Purpose after archive.
## Requirements
### Requirement: Pedido explícito de release não reconfirma o que já está autorizado
Com pedido explícito de fechar a release, o agente SHALL executar as tarefas operacionais normais de fechamento até a conclusão ou até um bloqueio real explicado. O agente MUST NOT pedir nova confirmação de ação já autorizada por esse pedido nem de dado já disponível. A decisão humana de homologar, a aprovação de Design, o QA e T16 MUST permanecer obrigatórios. Este requisito MUST NOT acrescentar estado, evento, hook ou `enabled_tools` na FSM.

#### Scenario: Fechamento segue sem menu de reconfirmação
- **WHEN** Alan pede explicitamente fechar a release e a próxima tarefa operacional já está autorizada e os dados dela estão disponíveis
- **THEN** o agente executa essa tarefa sem pedir confirmação de novo
- **AND** não move card fora de `process_event`

#### Scenario: Gate humano continua obrigatório
- **WHEN** a homologação humana, a aprovação de Design ou o PASS de `release-guard post` ainda não existe
- **THEN** o agente para nesse bloqueio real
- **AND** não homologa em nome de Alan e não chama T16 como se o gate já tivesse passado

### Requirement: Comentário de evidência não é a decisão humana
Homologação humana já comprovada SHALL fazer o agente publicar o comentário canônico de homologação pelo helper existente, sem nova aprovação. O agente MUST NOT tratar esse registro como a decisão de homologar nem como a aprovação de Design, e MUST NOT pedir a Alan para escrever o comentário de card já homologado chamando essa exigência de T7.

#### Scenario: Homologação comprovada gera o comentário
- **WHEN** o card já tem a decisão humana de homologar comprovada e ainda não tem o comentário canônico
- **THEN** o agente publica o comentário pelo helper sem pedir outra aprovação

#### Scenario: Sem decisão humana não há comentário inventado
- **WHEN** não há decisão humana de homologar para o card
- **THEN** o agente não publica o comentário canônico e não chama essa ausência de T7

### Requirement: Reconciliação precede pergunta de campo
Antes de perguntar responsável ou classificação, o agente SHALL reconciliar as fontes disponíveis e registrar a origem de cada valor. Uma decisão humana explícita e atribuída sem ambiguidade àquele card MUST prevalecer sobre inferência. Valor já registrado e fonte inequívoca vêm antes de política de classificação. Resposta sem distribuição clara entre cards, ou fontes incompatíveis, MUST permanecer lacuna e MUST NOT ser apresentada como decisão de Alan.

#### Scenario: Decisão humana do card prevalece
- **WHEN** Alan atribuiu classificação explícita a um card e outra fonte sugere valor diferente
- **THEN** o manifesto guarda o valor de Alan e a origem humana
- **AND** o agente não pergunta de novo esse campo

#### Scenario: Resposta sem distribuição não vira decisão por card
- **WHEN** Alan responde uma classificação única sem dizer qual card recebe qual valor
- **THEN** o manifesto marca a lacuna por card
- **AND** o agente não grava a inferência como decisão de Alan

### Requirement: Lacunas saem numa consulta e não se repetem
As lacunas reais conhecidas do pacote SHALL aparecer numa única consulta, com o valor faltante identificado por card. Resposta já dada MUST NOT ser perguntada de novo após retomada ou compactação. Silêncio ou ausência de resposta MUST NOT resolver decisão pendente. Tarefa independente já autorizada MUST NOT ficar bloqueada por essa lacuna.

#### Scenario: Uma consulta lista o que falta por card
- **WHEN** dois cards do pacote têm campos diferentes em falta e não há resposta anterior
- **THEN** uma única consulta identifica cada card e o campo faltante

#### Scenario: Silêncio não preenche a lacuna
- **WHEN** a consulta consolidada não recebe resposta
- **THEN** a lacuna continua aberta
- **AND** uma tarefa operacional já autorizada e independente dessa lacuna pode seguir

### Requirement: Pergunta obedece ao schema do cliente
O agente SHALL validar a pergunta contra o schema real da ferramenta do cliente antes de enviá-la. Payload com campo incompatível ou campo duplicado MUST NOT ser enviado. Nenhuma das classes de falha de formato relatadas no issue (campo incompatível e campo duplicado) SHALL repetir-se. Se a ferramenta não estiver disponível, o agente SHALL apresentar as mesmas alternativas em texto, sem omitir opção e sem tratar a recomendação como aceite.

#### Scenario: Campo duplicado não é enviado
- **WHEN** o payload da pergunta repete um campo que o schema do cliente não aceita duplicado
- **THEN** o adaptador não envia esse payload
- **AND** a consulta segue por um payload válido ou por texto com as mesmas alternativas

#### Scenario: Sem ferramenta a recomendação não vale aceite
- **WHEN** a ferramenta de pergunta não está disponível e há uma alternativa recomendada
- **THEN** o texto lista todas as alternativas
- **AND** a recomendação não é registrada como resposta de Alan

### Requirement: Manifesto retomável sem segredo
A retomada SHALL preservar pacote, decisões, origem dos valores, referências de evidência e etapas concluídas, revalidar o que puder ter mudado e continuar na primeira etapa incompleta. O registo MUST NOT exigir que Alan transporte esse contexto à mão e MUST NOT voltar a buscar credencial já disponível. O registo MUST NOT conter segredo, transcript ou conteúdo de sessão. O registo MUST NOT ser commitado.

#### Scenario: Retomada continua na primeira etapa incompleta
- **WHEN** uma sessão nova retoma o mesmo pacote depois de compactação e a etapa de archive ainda não está concluída
- **THEN** o agente revalida o estado que pode ter mudado
- **AND** continua nessa etapa sem pedir a Alan os dados já registrados

#### Scenario: Segredo não entra no registo
- **WHEN** a credencial necessária já está disponível na sessão
- **THEN** o agente não a copia para o manifesto e não consulta outro cofre para obtê-la de novo

### Requirement: Archive de changes concluídas depende de #1022
Para changes concluídas do pacote Homologado, sync e archive em `release-*` SHALL seguir o fechamento pedido sem o menu genérico de reconfirmação, reutilizando o `decide()` publicado no #1022. Este card MUST NOT copiar uma segunda allow-list, MUST NOT alterar `guard.decide()` e MUST NOT formalizar worktree do card + cherry-pick. Conflito sem resolução, descarte ou exceção que exija decisão humana SHALL ser apresentado como tal. Até esse `decide()` estar na árvore, deny de archive MUST ser bloqueio real que aponta #1022 e MUST NOT virar procedimento paralelo. Texto do issue #1022 MUST NOT ser tratado como aprovação operacional nova. Este card MUST NOT liberar escrita de produto nem pacote ou card não resolvido.

#### Scenario: Caminho já permitido não pede aprovação extra
- **WHEN** a release foi pedida e o `decide()` do #1022 já está na árvore e permite o archive das changes do pacote Homologado em `release-*`
- **THEN** o agente faz sync e archive por esse `decide()`, sem menu genérico e sem segunda allow-list
- **AND** não pede a Alan uma aprovação operacional extra por causa do texto de #1022
- **AND** não abre worktree do card nem faz cherry-pick para furar o guard

#### Scenario: Pacote ou card não resolvido continua negado
- **WHEN** o guard nega a escrita de archive porque o pacote ou o card não está resolvido
- **THEN** a escrita não ocorre
- **AND** a mensagem aponta #1022 em vez de uma implementação paralela
- **AND** produto e esse pacote ou card continuam negados

#### Scenario: fail_closed em release unbound aponta #1022
- **WHEN** o pacote está resolvido, o contexto é `release-*` unbound e o guard nega o archive com `fail_closed` porque o `decide()` do #1022 ainda não está na árvore
- **THEN** a escrita não ocorre e o bloqueio aponta #1022
- **AND** o agente não abre worktree do card nem faz cherry-pick como caminho deste card

### Requirement: Preflight não se anuncia como etapa posterior
Antes da publicação, o agente SHALL verificar as pendências possíveis de comentários, campos, documentação, archive, duplicação, integração, contexto de trabalho e disponibilidade do modelo. Verificação que depende de deploy MUST continuar na etapa de deploy. O agente MUST NOT anunciar o preflight como execução de uma etapa que ainda não começou.

#### Scenario: Pendência de archive aparece antes do PR
- **WHEN** o preflight corre e uma change concluída do pacote ainda está ativa
- **THEN** o relatório lista essa pendência
- **AND** não afirma que o deploy ou T16 já começou

#### Scenario: Deploy não é antecipado
- **WHEN** a evidência de deploy PROD ainda não existe e o preflight está a correr
- **THEN** a verificação de deploy fica na etapa de deploy
- **AND** o preflight não a marca como executada

### Requirement: Negativa cita a operação avaliada e T16 propaga a causa conhecida
Uma negativa SHALL informar a operação e o contexto realmente avaliados, a causa e a ação corretiva. Uma operação negada MUST NOT ser apresentada como prova de que outra operação é proibida. Quando `fechar_release` rejeita por `M_lote`, o `reason` MUST permanecer `guard:M_lote` e a `message` MUST incluir a causa estruturada já produzida pelo `post`. O agente MUST NOT precisar repetir o `post` só para descobrir essa causa. O gate `M_lote` MUST NOT ser removido nem afrouxado.

#### Scenario: Deny de uma escrita não condena outra
- **WHEN** o guard nega uma escrita de produto e a operação seguinte é archive de change no contexto que o guard já permite
- **THEN** o diagnóstico da primeira negativa não afirma que o archive também está proibido
- **AND** a segunda operação é avaliada no próprio contexto

#### Scenario: T16 mostra o blocker do post
- **WHEN** `release-guard post` falha com um blocker e em seguida `fechar_release` é avaliado
- **THEN** o resultado é reject com `reason` `guard:M_lote`
- **AND** a mensagem contém esse blocker e a ação corretiva
- **AND** o card não vai para Pronto

### Requirement: Preflight, post e T16 compartilham o contexto
Preflight, `post` e T16 SHALL identificar o pacote e o contexto de validação, incluindo cwd, HEAD e refs usadas. Evidência produzida noutro contexto, ou invalidada por mudança posterior, MUST NOT autorizar o fechamento. A divergência SHALL ser explicada e a validação pertinente SHALL ser refeita no contexto que executa T16.

#### Scenario: PASS noutro cwd não fecha
- **WHEN** o `post` passou numa worktree e T16 corre noutra worktree com HEAD ou árvore diferente
- **THEN** o fechamento não usa esse PASS
- **AND** a mensagem explica a divergência e exige o `post` de novo no contexto de T16

#### Scenario: O mesmo contexto autoriza a transição
- **WHEN** preflight, `post` PASS e T16 observam o mesmo pacote, cwd, HEAD e refs
- **THEN** a identidade de contexto não bloqueia T16 por divergência de worktree

### Requirement: Sync e archive do pacote ficam provados antes de T16
Antes de T16, todas as changes concluídas dos cards do pacote SHALL ter as pós-condições de sync e archive verificadas, inclusive enquanto esses cards estão Homologado. Change concluída ainda ativa MUST fazer `release-guard post` falhar. Duplicação ativa e arquivada MUST impedir aceitar o fechamento. O check existente para card `Pronto` ou `Cancelado` MUST permanecer. Card fora de `RELEASE_CARDS` MUST NOT ser arquivado por este check.

#### Scenario: Change ativa de card Homologado bloqueia o post
- **WHEN** `RELEASE_CARDS` contém um card Homologado cuja change concluída ainda está em `openspec/changes/`
- **THEN** `release-guard post` falha com essa change identificada
- **AND** T16 não promove o pacote

#### Scenario: Duplicata ativa e arquivada continua blocker
- **WHEN** a mesma change existe em `openspec/changes/` e em `openspec/changes/archive/`
- **THEN** o `post` falha por duplicação
- **AND** o fechamento não aceita evidência inconsistente

### Requirement: Comentário de Pronto usa dados reais e é idempotente
T16 SHALL publicar o comentário de Pronto com o nome real do pacote, a lista real de branches e a evidência real de deploy, sem placeholders. Evidência existente incompleta SHALL ser atualizada de forma idempotente. Repetir a operação MUST NOT criar comentário duplicado e MUST NOT exigir correção manual posterior.

#### Scenario: Placeholder é recusado
- **WHEN** o helper de `pronto` é chamado sem a lista real de branches ou com o nome genérico de pacote usado no lugar dos dados do lote
- **THEN** o helper não publica o comentário
- **AND** o processo não trata essa chamada como evidência completa

#### Scenario: Repetição não duplica
- **WHEN** o card já tem o comentário de Pronto completo para o mesmo commit e T16 corre outra vez
- **THEN** o comentário existente permanece único
- **AND** nenhum comentário novo é criado

#### Scenario: Incompleto é atualizado
- **WHEN** o card já tem comentário de Pronto do mesmo commit com placeholder na lista de branches e a nova chamada traz a lista real
- **THEN** o comentário existente passa a ter a lista real
- **AND** não resta um segundo comentário de Pronto para esse commit

### Requirement: Runtime e modelo são conferidos sem alterar o mapa
A cada turno o agente SHALL conferir runtime, modelo e esforço a partir de evidência disponível e do `.cursor/model-map.yaml` vigente. Divergência ou indisponibilidade SHALL ser informada. O agente MUST NOT trocar o modelo em silêncio, MUST NOT alterar o mapa e MUST NOT reivindicar modo Auto. Quando o cliente suporta encaminhamento, a sessão adequada SHALL receber o contexto preservado. Quando não suporta, o bloqueio e o handoff necessário SHALL ficar explícitos, sem alegar que o encaminhamento ocorreu. Troca de modelo MUST NOT ser tratada como correção do archive.

#### Scenario: Divergência fica visível
- **WHEN** o runtime observado não é o slug e o esforço da faixa `execucao` do mapa para aquele cliente
- **THEN** o agente informa a divergência
- **AND** não edita `.cursor/model-map.yaml` e não segue T16 nesse runtime

#### Scenario: Sem encaminhamento não há alegação
- **WHEN** o cliente não oferece encaminhamento de sessão e o runtime não é o da faixa `execucao`
- **THEN** o agente declara o bloqueio e o handoff necessário
- **AND** não afirma que a sessão foi encaminhada

### Requirement: Integração é verificada antes da CI e a proteção atual permanece
O agente SHALL verificar a integração contra o alvo antes de abrir o PR e SHALL agrupar a documentação final do fechamento vigente nesse PR. A proposta de checks proporcionais para alteração estritamente documental SHALL explicitar a cobertura e a regressão necessárias. As proteções já exigidas, incluindo `qa-gate` e a allowlist documental do `release-guard`, MUST NOT ser desligadas nem ignoradas por esta proposta.

#### Scenario: Conflito aparece antes do PR
- **WHEN** a simulação de merge contra o alvo do PR encontra conflito
- **THEN** o agente não abre o PR
- **AND** o conflito é reportado antes de pedir a suíte de CI

#### Scenario: Proposta documental não remove qa-gate
- **WHEN** o diff do PR está só na allowlist documental já reconhecida pelo `release-guard`
- **THEN** a proposta nomeia a cobertura e a regressão que continuam obrigatórias
- **AND** não instrui desligar `qa-gate` nem a proteção de branch vigente

### Requirement: Replay preserva trabalho fora do pacote
O replay do cenário desta release SHALL incluir #1042 fora do pacote, duplicação ativa/arquivada da change de #1017 e alterações locais alheias. O fechamento MUST preservar esse trabalho e MUST NOT promover conteúdo não homologado. As regressões MUST cobrir continuidade, retomada, decisão ambígua, contexto divergente e evidência incompleta.

#### Scenario: Card fora do pacote não é promovido
- **WHEN** o replay corre com #1042 fora de `RELEASE_CARDS` e com alterações locais que não são do pacote
- **THEN** #1042 não é arquivado nem movido para Pronto por este fechamento
- **AND** as alterações locais alheias permanecem

#### Scenario: Duplicata do replay bloqueia evidência inconsistente
- **WHEN** o replay contém a change de #1017 ao mesmo tempo ativa e arquivada
- **THEN** o fechamento não é aceito enquanto a duplicata existir
- **AND** o archive histórico não é apagado para forçar o PASS

### Requirement: Cursor e Codex tomam a mesma decisão operacional
Um ensaio comparável em Cursor e Codex SHALL apresentar a mesma decisão operacional: zero perguntas evitáveis, consulta consolidada quando faltar decisão real, e continuidade até conclusão ou bloqueio externo explicado. Diferença de ferramenta MUST NOT criar gate humano novo. A regra compartilhada MUST ser uma só; a adaptação MUST limitar-se ao encoding da pergunta e à chave de modelo do cliente no mapa existente.

#### Scenario: Os dois clientes não perguntam o que já está autorizado
- **WHEN** a mesma tabela de decisão é avaliada para Cursor e para Codex com a release pedida e os dados presentes
- **THEN** ambos seguem sem pergunta
- **AND** nenhum dos dois introduz confirmação humana extra

#### Scenario: Lacuna real produz uma consulta equivalente
- **WHEN** a tabela tem uma lacuna real de campo por card
- **THEN** ambos pedem essa lacuna uma vez, com os mesmos cards e campos
- **AND** a diferença fica só no formato da ferramenta ou no texto equivalente

