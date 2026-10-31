## ADDED Requirements

### Requirement: O teste no DEV é etapa obrigatória quando ligado
Com `qa_dev.enabled` true no overlay, todo card SHALL passar pelo teste no DEV entre a integração em `develop` e o `Done`. O teste SHALL rodar em `environments.dev.url`, num navegador headless no servidor, dirigido passo a passo por um agente, a partir dos critérios de `## Entra` do issue e do protótipo aprovado, quando houver. O plano SHALL levar o protótipo ou registrar que não há. O agente MUST NOT mudar o Status do card, chamar `process_event`, homologar nem postar `/qa-dev-liberar`. O teste MUST NOT rodar em PROD. A skill SHALL transcrever a autorização do Alan de 28/10/2026: no DEV, o agente pode criar, alterar e apagar favoritos, estratégias, alertas e configurações, inclusive os que já existiam, sem devolver ao estado anterior.

#### Scenario: Card integrado fica em QA durante o teste
- **WHEN** a primeira chamada de `integrar_develop` termina com `qa_dev` ligado
- **THEN** o código do card está no DEV
- **AND** o Status continua `QA`

#### Scenario: Agente de teste não move o card
- **WHEN** um filho `qa-dev` termina um bloco, com qualquer resultado
- **THEN** o Status do card não muda por ação dele
- **AND** ele não chamou `process_event`

#### Scenario: Plano leva o protótipo aprovado
- **WHEN** o card tem protótipo em `frontend/public/prototypes/card-<N>-*`
- **THEN** o plano traz a URL dele no DEV
- **AND** o filho usa o protótipo como roteiro, junto com os critérios

#### Scenario: Card sem protótipo
- **WHEN** o card não tem protótipo
- **THEN** o plano registra `prototipo: N/A`

#### Scenario: Dado que já existia pode ser apagado
- **WHEN** um critério leva o agente a apagar um favorito anterior ao teste, no DEV
- **THEN** isso é permitido, sem restauração
- **AND** nada disso vale fora do DEV

### Requirement: A senha não passa pelo modelo
O login SHALL acontecer fora do agente, por um helper do consumidor que lê a senha do cofre dentro do próprio processo, autentica no DEV e grava um estado de sessão com permissão 0600 para o navegador. A senha MUST NOT aparecer em argumento de processo, variável exportada, arquivo, log, chat, issue, relatório, print ou vídeo. O agente MUST NOT digitar credencial válida no navegador. O helper MUST recusar origem diferente de `environments.dev.url` e MUST distinguir recusa de senha (401) de conta bloqueada (403). A varredura SHALL procurar a senha nas formas literal, JSON, JSON dentro de JSON, URL e URL com `+`, e devolver só `ausente` ou `PRESENTE` com o nome do arquivo, sem o valor. O nível dessa garantia é cooperativo, e a documentação MUST dizer isso.

#### Scenario: Sessão pronta sem senha no transcript
- **WHEN** o pai roda o helper de sessão
- **THEN** a saída é só `sessao_ok admin=<sim|nao>` ou um código de erro
- **AND** o navegador abre no DEV já logado

#### Scenario: Sessão cai no meio do run
- **WHEN** a tela de login aparece durante um bloco
- **THEN** o agente roda o helper de novo e reabre o navegador
- **AND** não digita senha

#### Scenario: Varredura encontra a senha
- **WHEN** o relatório ou outro arquivo varrido contém a senha, em qualquer uma das formas
- **THEN** a varredura devolve `PRESENTE` com o nome do arquivo, sem o valor
- **AND** o relatório não é postado

#### Scenario: Auto-teste da varredura
- **WHEN** a varredura roda com `--self-test`
- **THEN** ela semeia em arquivos temporários uma senha sintética com aspas, barra invertida, barra, `%`, `+`, espaço e acento, em cada forma
- **AND** devolve `PRESENTE` em todas
- **AND** a senha real não vai para arquivo

#### Scenario: Ação que invalidaria o cofre
- **WHEN** um critério exigiria trocar senha ou e-mail, apagar a conta ou digitar credencial válida na tela de login
- **THEN** esse ponto fica NÃO TESTADO, com motivo

#### Scenario: Ação administrativa sobre usuário
- **WHEN** um critério exigiria criar, editar, suspender, reativar, banir ou apagar usuário
- **THEN** esse ponto fica NÃO TESTADO, com motivo
- **AND** a página recebe resposta 403 local se tentar

#### Scenario: Conta bloqueada não se passa por senha recusada
- **WHEN** o login devolve 403
- **THEN** o helper devolve `conta_bloqueada`, não `senha_recusada`

### Requirement: Navegador do teste fixado e registrado na conta
O consumidor SHALL registrar o Playwright MCP com versão exata na conta do Claude Code, em modo headless e isolado, com o caminho do Chromium existente, o estado de sessão, pasta de saída fora do repositório, a capacidade de vídeo e o bloqueio das origens de PROD. O registro MUST ficar num script do consumidor, e o caminho do Chromium MUST NOT entrar em arquivo do produto `covenant-flow`. Esse script altera as permissões da conta, então MUST ser executado pelo Alan no terminal, e o agente MUST NOT executá-lo. O script SHALL negar `browser_run_code_unsafe` e `browser_start_tracing` em `permissions.deny`. Nesta entrega, o teste roda só no Claude Code. Em outro cliente, a T14 MUST parar em `qa_dev_pendente` com mensagem visível.

#### Scenario: Cliente sem navegador
- **WHEN** um cliente sem o navegador registrado chega à fase de teste
- **THEN** o card fica em `QA`
- **AND** a mensagem diz para abrir a sessão do card no Claude Code

#### Scenario: Conferência do registro
- **WHEN** `setup-dev.sh --check` roda e o executável do Chromium ou o registro não existe
- **THEN** ele falha com a causa visível

#### Scenario: Ferramenta fora do alcance da trava
- **WHEN** um filho `qa-dev` tenta `browser_run_code_unsafe`
- **THEN** a permissão da conta nega a chamada

### Requirement: Teste em blocos com critérios rastreados
O teste SHALL rodar em blocos sequenciais, cada um num filho `qa-dev` com contexto novo, com até 3 critérios e teto de 60 chamadas de ferramenta. A lista de critérios SHALL sair de `## Entra` por script. Cada bloco SHALL gravar resultado por critério e um campo de passagem para o bloco seguinte, numa pasta fora do repositório. Para cada critério, o agente SHALL testar o caminho feliz e tentar quebrar: campo vazio ou inválido, duplo clique, voltar, recarregar no meio do fluxo, tela de celular e esperar backtest ou worker terminar. SHALL olhar também erros de console e respostas 4xx/5xx. FAIL MUST citar o critério e trazer evidência; dúvida de interpretação MUST virar NÃO TESTADO, com motivo. O plano SHALL listar os cards com FAIL aberto, e sintoma ligado a eles MUST virar NÃO TESTADO, com motivo, nunca FAIL.

#### Scenario: Critério não coberto por bloco
- **WHEN** um critério da lista não tem resultado em nenhum bloco
- **THEN** o relatório o mostra como NÃO TESTADO, com motivo "sem bloco"

#### Scenario: Bloco estoura o teto
- **WHEN** um bloco atinge o teto de chamadas com critério sem resultado
- **THEN** esse critério passa para o bloco seguinte
- **AND** o campo de passagem diz o que já foi feito

#### Scenario: Dúvida de interpretação
- **WHEN** o agente não sabe se o comportamento visto viola o critério
- **THEN** o resultado é NÃO TESTADO, com motivo `interpretação: <dúvida>`

#### Scenario: Sintoma de defeito de outro card
- **WHEN** o card A tem FAIL aberto e o teste do card B encontra um sintoma ligado a ele
- **THEN** o resultado em B é NÃO TESTADO, com motivo `defeito de #A: <critério>`
- **AND** B não vai para T13 por causa disso

### Requirement: Relatório por critério com veredito calculado
O relatório SHALL ser montado por script, sem modelo, a partir dos blocos, e postado como comentário no issue do card. SHALL trazer PASS, FAIL ou NÃO TESTADO com motivo por critério, link de print de cada achado, link dos vídeos, o SHA testado, uma seção separada para achados fora dos critérios e a linha de runtime observado. O veredito SHALL ser calculado nesta ordem: `FAIL` se houver FAIL; `NADA_PARA_TESTAR` no caso de nada a testar; `INCONCLUSIVO` se nenhum critério tiver PASS ou se o DEV ou um serviço contínuo tiver falhado em qualquer checagem do run; `PASS` se todos passarem; `NAO_TESTADO` nos demais casos. O comentário SHALL levar o marcador `<!-- covenant-flow:qa-dev veredito=<V> sha=<SHA> run=<id> -->`. Como o repositório é público, o texto MUST citar tela e comportamento e MUST NOT trazer valores da conta do Alan (saldo, posição, quantidade, preço de entrada, nome, e-mail, chave). O campo de passagem e os passos MUST NOT entrar no comentário. Antes de postar, o texto SHALL passar por `--scan --publico`, que recusa senha, padrão de JWT e o e-mail de login.

#### Scenario: Um FAIL decide o veredito
- **WHEN** um critério está em FAIL e os demais em PASS
- **THEN** o veredito do marcador é `FAIL`

#### Scenario: Achado fora dos critérios
- **WHEN** o agente acha um bug fora dos critérios do card
- **THEN** ele aparece na seção separada
- **AND** não muda o veredito

#### Scenario: Reteste depois de correção
- **WHEN** o teste roda de novo depois de um FAIL corrigido
- **THEN** rodam os critérios em FAIL e os tocados pelo diff da correção
- **AND** os demais aparecem como PASS do run anterior, com o id do run

#### Scenario: Reteste de FAIL contestado
- **WHEN** o Alan discorda de um FAIL antes da T13
- **THEN** o teste roda de novo só nos critérios em FAIL, com a leitura dele no plano
- **AND** nada é integrado e o Status não muda
- **AND** o relatório novo registra a contestação e a leitura usada

#### Scenario: Nenhum critério passou
- **WHEN** nenhum critério tem PASS, por qualquer motivo, e nenhum tem FAIL
- **THEN** o veredito é `INCONCLUSIVO`

#### Scenario: Critérios parcialmente testados
- **WHEN** há pelo menos um PASS, nenhum FAIL, algum NÃO TESTADO e o DEV e os serviços contínuos estão de pé
- **THEN** o veredito é `NAO_TESTADO`

#### Scenario: Relatório com e-mail de login
- **WHEN** o texto do relatório contém o e-mail de login
- **THEN** `--scan --publico` devolve `PRESENTE` com o nome do arquivo, sem o valor
- **AND** nada é postado

#### Scenario: Achado sobre saldo
- **WHEN** o agente encontra um erro no saldo mostrado em `/monitor`
- **THEN** o relatório descreve a tela e o comportamento
- **AND** o valor fica só no print, no Drive

### Requirement: Evidência fora do repositório público
Prints e vídeo SHALL ficar em `QA/<card>/<run>/` na pasta do projeto no Drive, enviados por helper do consumidor, e o comentário SHALL apontar para eles por link. A pasta do run SHALL ser compartilhada só com a conta do Alan, cujo e-mail vem do cofre e MUST NOT entrar no repositório. O helper MUST NOT criar link aberto e MUST recusar enviar quando a pasta do run tiver acesso `anyone` ou `domain`, inclusive herdado. Evidência MUST NOT ir para commit, release ou Gist. Falha no envio MUST NOT prender o card e MUST aparecer no relatório, com o caminho local.

#### Scenario: Evidência publicada
- **WHEN** o relatório é montado com envio bem-sucedido
- **THEN** o comentário traz um link por print de achado, um por vídeo e o da pasta
- **AND** a conta do Alan abre esses links

#### Scenario: Envio falha
- **WHEN** o envio ao Drive falha
- **THEN** o relatório é postado dizendo que a evidência ficou no servidor e onde

#### Scenario: Pasta com acesso aberto
- **WHEN** a pasta do run tem acesso `anyone` ou `domain`
- **THEN** nada é enviado
- **AND** o relatório diz que a evidência ficou no servidor e por quê

### Requirement: Volta rápida pelas telas principais
Depois dos blocos de critério, um bloco final SHALL visitar as telas de `qa_dev.telas_regressao`, no desktop, conferindo tela, console e 4xx/5xx. Os achados SHALL ir para seção própria e MUST NOT mudar o veredito. O bloco MUST NOT rodar quando o veredito for `NADA_PARA_TESTAR`. Com `admin=nao` na sessão, telas `requireAdmin` SHALL ficar como NÃO TESTADO na seção, com motivo.

#### Scenario: Tela principal quebrada fora dos critérios
- **WHEN** a volta rápida acha erro numa tela que o card não toca
- **THEN** o achado aparece na seção da volta rápida
- **AND** o veredito não muda

#### Scenario: Usuário sem admin no DEV
- **WHEN** a sessão devolve `admin=nao`
- **THEN** `/combo/discovery` e `/combo/select` aparecem como NÃO TESTADO, com motivo
- **AND** o veredito não muda

### Requirement: Card sem nada para testar não fica preso
Quando todos os arquivos do PR casarem com `qa_dev.caminhos_sem_produto`, o relatório SHALL dizer "nada para testar no DEV", sem login nem navegador. Essa lista é própria, e `product_globs` MUST NOT ser alterado nem usado nessa decisão. Arquivo fora da lista ou falha ao listar o PR MUST levar ao teste. Quando o produto for tocado sem tela direta, o agente SHALL testar pelas telas que dependem da mudança, e só devolver "nada para testar no DEV" quando nada depender dela, citando o que examinou.

#### Scenario: PR só de processo
- **WHEN** todos os arquivos do PR casam com `qa_dev.caminhos_sem_produto`
- **THEN** o veredito é `NADA_PARA_TESTAR`
- **AND** nenhum filho `qa-dev` nasce

#### Scenario: Mudança em código fora de product_globs
- **WHEN** o PR toca `src/**`, `frontend/public/**`, `frontend/index.html` ou `frontend/package.json`
- **THEN** o card não é classificado como `NADA_PARA_TESTAR` sem filho `qa-dev`
- **AND** o agente testa pelas telas que dependem da mudança

#### Scenario: Não foi possível listar o PR
- **WHEN** a listagem dos arquivos do PR falha
- **THEN** o card não é classificado como `NADA_PARA_TESTAR`

#### Scenario: Mudança só de backend
- **WHEN** o PR toca só `backend/**` e uma tela consome o endpoint alterado
- **THEN** o agente testa por essa tela

### Requirement: Impedimento não aprova o card; ferramenta quebrada não vira relatório
O teste SHALL conferir a saúde do DEV e os serviços contínuos antes de abrir o navegador e de novo ao montar o relatório, e SHALL esperar backtest e worker de verdade, até `qa_dev.espera_max_min` por espera e `qa_dev.teto_total_min` por run. Espera ou teto estourado, com DEV e serviços de pé, SHALL gerar NÃO TESTADO com motivo, e o card segue se houver PASS. DEV fora do ar depois de 3 tentativas em 5 minutos, serviço contínuo parado ou nenhum critério com PASS SHALL gerar `INCONCLUSIVO`: o card fica em `QA` até o Alan decidir entre novo teste, T13 ou a linha exata `/qa-dev-liberar <run>`, escrita por ele. Senha recusada, conta bloqueada, navegador que não abre ou cliente sem navegador MUST NOT gerar relatório: o card fica em `QA`, com comentário dizendo o que falta. Um bloco interrompido por DEV fora do ar SHALL ser repetido uma vez quando a saúde voltar.

#### Scenario: DEV fora do ar
- **WHEN** a saúde do DEV falha nas 3 tentativas
- **THEN** os critérios restantes ficam NÃO TESTADO, com motivo e hora
- **AND** o veredito é `INCONCLUSIVO`
- **AND** o card fica em `QA`

#### Scenario: Serviço parado depois da integração
- **WHEN** um serviço contínuo está parado no início ou no fim do run, mesmo com critérios em PASS
- **THEN** o veredito é `INCONCLUSIVO`
- **AND** o card fica em `QA`

#### Scenario: Saídas do inconclusivo no comentário
- **WHEN** o veredito é `INCONCLUSIVO`
- **THEN** o comentário lista novo teste, T13 e a linha exata `/qa-dev-liberar <run>`
- **AND** o agente não posta essa linha

#### Scenario: Espera estoura
- **WHEN** um backtest não termina em `espera_max_min`
- **THEN** o critério fica NÃO TESTADO, com último estado, id do job e estado do worker

#### Scenario: Senha recusada
- **WHEN** o helper de sessão recebe recusa do login
- **THEN** não há relatório
- **AND** o card fica em `QA`, com comentário pedindo a atualização do cofre

### Requirement: Um teste por vez
O teste SHALL usar uma trava com card, run e início, criada de forma atômica. A fase 1 da T14 e o `plan`, ao iniciar ou reiniciar o teste, SHALL pegá-la. Trava do mesmo card SHALL ser renovada, trava vencida ou ausente SHALL ser tomada, e trava de outro card SHALL devolver `qa_dev_ocupado`. A trava SHALL ser solta quando o relatório é postado, na falha de ferramenta e na falha da fase 1. A trava SHALL vencer em `teto_total_min` + 15 minutos.

#### Scenario: Sessão morre com a trava
- **WHEN** a trava passa do vencimento
- **THEN** outro card consegue tomá-la

#### Scenario: Teste retomado depois do vencimento
- **WHEN** um card reinicia o teste e a trava dele venceu
- **THEN** `plan` pega a trava antes de qualquer bloco

#### Scenario: Teste retomado com outro card em teste
- **WHEN** um card reinicia o teste e a trava é de outro card
- **THEN** `plan` devolve `qa_dev_ocupado`
- **AND** nenhum bloco nasce

#### Scenario: Falha de ferramenta solta a trava
- **WHEN** o helper de sessão devolve `senha_recusada`
- **THEN** a trava é solta
- **AND** outro card consegue seguir

### Requirement: Branch sem a chave não integra com o teste ligado
Com `qa_dev.enabled` true na base, o `qa-gate` SHALL falhar em PR para `develop` cujo head não tenha essa chave ligada, com mensagem dizendo para atualizar a partir de `develop`. Antes de ligar, o Alan ou o pai SHALL conferir que nenhum outro card está em `QA`. Com a chave desligada na base, o passo MUST NOT bloquear.

#### Scenario: Branch anterior ao pin
- **WHEN** um PR para `develop` vem de branch sem `qa_dev.enabled` true e a base tem a chave ligada
- **THEN** o `qa-gate` falha com a mensagem de atualização
- **AND** a T14 antiga não roda nesse card

#### Scenario: Chave desligada
- **WHEN** a base tem `qa_dev` ausente ou `enabled: false`
- **THEN** o passo não reprova o PR

### Requirement: Modelo do agente vem da escolha local de execução
O papel `qa-dev` SHALL pertencer à faixa `execucao` em `.cursor/model-policy.yaml`. Arquivo versionado MUST NOT fixar modelo para o papel, e a escolha local MUST NOT ganhar chave própria de QA.

#### Scenario: Filho nasce com a faixa de execução
- **WHEN** o pai resolve a seleção para o papel `qa-dev`
- **THEN** o par vem de `execucao` do cliente na escolha local

### Requirement: Teste não envia ordem real
O navegador do teste SHALL recusar, com resposta local, o envio de ordem à Binance, a criação ou o cancelamento de stop e as escritas em `/api/admin/users`, antes de a requisição sair da página. A prévia de ordem SHALL continuar testável. O envio de ordem SHALL aparecer como NÃO TESTADO, com motivo. A prova dessa trava MUST usar só envios que o backend recusaria sem ela: `preview_token` falso e `stop_price` inválido.

#### Scenario: Agente aciona a tela de operar
- **WHEN** a página tenta `POST /api/monitor/spot-market-orders`
- **THEN** a requisição não chega ao backend
- **AND** a página recebe resposta 403 local

#### Scenario: Prévia continua funcionando
- **WHEN** a página pede a prévia da ordem
- **THEN** a requisição segue para o backend

#### Scenario: Prova sem risco de ordem
- **WHEN** a trava é comprovada no piloto
- **THEN** os envios usam `preview_token` falso e `stop_price: 0`
- **AND** nenhuma prévia real é usada

### Requirement: Piloto antes de ligar
`qa_dev.enabled` MUST continuar false até um piloto passar: relatório por critério postado no issue do card piloto, sem valor da conta, prints e vídeo acessíveis ao Alan, pasta do run sem acesso aberto, varredura `ausente` em transcripts, relatório, comentário, arquivos de página e journal do backend DEV, auto-teste `PRESENTE` em todas as formas, e trava de ordem comprovada. O piloto MUST NOT mover Status.

#### Scenario: Piloto reprova na varredura
- **WHEN** a varredura do piloto devolve `PRESENTE`
- **THEN** `qa_dev.enabled` continua false
- **AND** o card não segue para o T14 com o teste ligado
