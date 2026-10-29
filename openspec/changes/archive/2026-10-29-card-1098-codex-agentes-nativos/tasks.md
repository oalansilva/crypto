Estado vigente após QA factual de 18/10/2026: **32/32 tasks concluídas + três transferidas não concluídas**. 5.3 foi comprovada pela criação nativa autorizada em Em desenvolvimento e pelos denies reais de etapa/vínculo em QA, com readbacks e hashes preservados. 5.1 foi reconciliada após Alan confirmar abertura/inspeção do filho e fornecer a tela real: estado e interrupção visíveis, entrada direta desabilitada; orientação foi demonstrada por pedido humano explicitamente encaminhado pelo pai ao QA final e resposta devolvida por essa rota, prevista no Design/documentação. Não houve mensagem humana nativa direta ao filho. A interrupção anterior é aborto, sem promover seu completed histórico; o novo QA será coletado pelo pai após o retorno, antes do gate dependente. CI do SHA `bf7baf6f4bb16e051f467dc759cc06ae0b25ebc1`: 14 checks aplicáveis PASS no run `39148761164`, deploy-staging skipped, conforme watcher único do pai. Onda final `ee97fca8ba6b7a1bc83bb36f`, sincronização real dos dois arquivos corrigidos no nucleus e limites em [evidence/qa-cli-20261018.md](evidence/qa-cli-20261018.md). Este checklist não antecipa lifecycle final, integração ou Done; 5.2/5.4/5.7 e transferências ao #1128 preservadas.

## Histórico — correção CI e reconciliação anterior, 18/10/2026

Estado então vigente após reconciliação de aceites CLI e correção CI de 18/10/2026: **30/32 tasks concluídas + três transferidas não concluídas**. 5.2 tem recusa real atual revalidada; 5.4 tem onda final de produto com verify-wave/checklist PASS informados pelo pai; 5.7 separa positivo atual, recusas reais atuais/históricas e fixtures. Evidência e hashes: [evidence/ci-and-cli-acceptance-20261018.md](evidence/ci-and-cli-acceptance-20261018.md). **5.1 e 5.3 continuavam pendentes**: controles vistos por Alan e Guard vivo com negativos adequados fora do card/etapa, respectivamente. O ensaio com workdir=/tmp escreveu somente na fixture absoluta do mesmo card autorizado; não é negativo fora do card/etapa nem comprova ausência de hook ou defeito. O recorte preservou 25 concluídas (25/35 → 25/32); 3.3/6.3 conservam a qualificação completa da rota CLI. 5.5/5.6/5.8 seguem pendentes no [#1128](https://github.com/oalansilva/crypto/issues/1128), em Em Refinamento, com IDs preservados. Gates do delta CI e QA da CLI permanecem obrigatórios; não é aprovação global.

Tasks 4.5/6.4 conservam a distribuição anterior verificada e agora também a integração real de `.cursor/tmp/card-1098-final-review-fix/`: oito payloads nucleus → consumidor, receipt/manifesto conferidos e trust pertinente confirmado pelo pai, conforme [evidence/final-fix-distribution-20261018.md](evidence/final-fix-distribution-20261018.md). Os 148 testes focados e a distribuição não substituem Review/QA de produto; a qualificação atual da rota fundamenta somente 3.3/6.3. 3.2/6.1/6.2 conservam seu histórico diagnóstico. As 25 tasks marcadas registram realizações com o escopo e hashes de suas evidências, inclusive investigação multissuperfície; não significam suporte universal. As notas datadas conservam contagens e estados históricos.

Bootstrap de 17/10: 118 testes e qualificação real TUI em `/source` registrados em `docs/codex-bootstrap-1098.md`. Nenhuma task abaixo é concluída automaticamente por esse bootstrap; retomada nativa/preflight ready também não substituem os aceites. Implementação depende de T7/T8.

## 1. Preflight e contrato de evidência

- [x] 1.1 Registrar matriz por superfície interativa, exec e app/IDE via app-server e por etapa: ferramenta nativa, vínculo ao chat, identidade, isolamento de contexto, worktree/Guard, modelo/esforço observados, versão e permissões efetivas; separar comprovado, não comprovado e bloqueado, sem usar configuração como runtime.
- [x] 1.2 Implementar preflight Codex que recuse capacidade ausente antes do spawn/trabalho, com card, etapa e garantia na mensagem; se verificação requer nascimento, permitir apenas diagnóstico com barreira efetiva ou recusar.
- [x] 1.3 Integrar captura de nascimento local e verificação de argumentos reais/observados, mantendo mudança de seleção, continuidade e ondas conforme #1080; não alterar escolha local.
- [x] 1.4 Implementar registro de tentativa ligado a chat/parent/child, papel, card/Status, paths, captura, origem dos fatos, eventos e payload; ausência permanece unavailable e completed sem payload falha.

- [x] 1.5 Revisar e completar driver/coleta do bootstrap: validar schema/origem/capacidades sem comparação exclusiva com codex_exec, manter qualificação real por superfície e compatibilidade legada exec; testar cópia de qualificação, reclassificação de host e ausência de campos obrigatórios como recusas.
- [x] 1.6 Investigar fonte de evidência real do app/IDE via app-server e adaptar coleta quando suportada; registrar por superfície qual garantia falta quando não houver caminho verificável, sem trocar para exec ou prometer suporte universal.

As tasks 1.1–1.6 acima registram a entrega do critério anterior; a revisão abaixo não transforma esse código em implementação do novo critério.

- [x] 1.7 Implementar, após revalidação do Design/digest pelo processo canônico, o critério de contexto escolhido por Alan: contrato documentado aplicável à superfície/ferramenta + chamada nativa registrada fork_turns=none + qualificação por ensaio complementar completo; registrar atestação interna completa unavailable sem exigir nem afirmar sua existência, preservando todos os outros gates.
- [x] 1.8 Implementar e executar o diagnóstico não secreto com controle C entregue ao filho e sentinela S exclusiva do contexto anterior do pai, sem vazamento por prompt/steering/arquivos/env; validar origem e ausência de contaminação, controle exato/completed/payload e filiação; S devolvida ou chamada divergente bloqueia, controle/proveniência incompletos não contam como positivo.
- [x] 1.9 Persistir e verificar separadamente evidência contratual, chamada real e resultado empírico com escopo/proveniência/digests, sem publicar marcadores ou sintetizar telemetria; testar positivos controlados e negativos de silêncio, controle errado, sentinela vazada/devolvida, fork divergente, origem incompleta, contrato de outra superfície e uso indevido de excludeTurns. Ausência de S sozinha não comprova isolamento.

## 2. Contexto correto das operações

- [x] 2.1 Normalizar payloads nativos realmente suportados em codex_adapter, incluindo variantes de comando/diretório observadas, preservando o evento original e a identidade autorizada independente de workdir.
- [x] 2.2 Validar worktree/branch/card e caminhos reais de todos os alvos antes do Guard; não permitir que cwd, prompt, symlink ou alvo misto concedam outro card/etapa.
- [x] 2.3 Ensaiar regressão source/develop versus worktree vinculado, Design OpenSpec permitido, Todo/Design produto negado e produto permitido somente após T8; provar targets inalterados nos denies em fixtures.
- [x] 2.4 Ensaiar divergência/ausência de vínculo e cobertura/trust do hook: falha visível sem sessão externa, sem correção silenciosa de permissões e sem alegação Auto.

- [x] 2.5 Validar retomada NATIVA do mesmo chat pelo operador: turn_context atual no worktree prevalece sobre cwd histórico; metadata de nascimento e todos os turnos do filho devem corresponder. Testar que workdir/--root sozinhos continuam recusados; preservar receita de recuperação sem API fictícia de rebind.

## 3. Revisão nativa com garantia equivalente

- [x] 3.1 Implementar caminho de recusa da onda quando não houver contexto nativo somente leitura comprovado para pai e filhos; preservar verify-wave e checklist sem exceção para metadata unavailable.
- [x] 3.2 Implementar contrato de coleta/verificação de evidência efetiva read-only, leitura do diff e deny de escrita por reviewer, vinculado ao mesmo path/SHA-256, dois papéis e dois child ids; ensaiar negativos de evidência ausente, divergente ou apenas declarativa.
- [x] 3.3 Implementar orquestração automática dedicada: principal prepara diff/capturas/prompts/receipts, lança coordenador Codex que nasce read-only no mesmo worktree, dois reviewers nativos no mesmo turno do coordenador, ambos completed/payload e coleta pelo principal gravável. Qualificar a rota suportada codex exec read-only sem alternância manual; capacidade ausente mantém bloqueio, sem inventar API ou executar review no pai.
- [x] 3.4 Ensaiar onda incompleta, child interrompido, completed sem payload, mudança de seleção, digest divergente e metadata sintética; confirmar que nenhum caso libera aprovação da revisão.

## 4. Documentação e verificação local

- [x] 4.1 Atualizar runbook canônico Codex e docs/model-selection.md para caminho nativo comprovado ou recusa, removendo recomendação de sessão externa para delegação e preservando gates humanos e a garantia de #1049; manter AGENTS.md curto e outros clientes intocados.
- [x] 4.2 Documentar como Alan localiza responsável, acompanha estado, inspeciona/interage e encontra retorno usando controles reais da superfície observada; não prometer controles não expostos.
- [x] 4.3 Rodar testes focados de adapter/proxy/review/seleção e validar OpenSpec; registrar resultados, origem canônica das mudanças e limitações sem misturar testes de contrato com prova viva.

- [x] 4.4 Conferir procedência nucleus → consumidor, cópia byte a byte e manifesto do delta; documentar pin-base v1.1.22 e publicação pendente. Distribuir pelo processo autorizado, sem confiar hooks automaticamente, mudar conta ou tratar bootstrap como novo pin.

- [x] 4.5 Após revalidação canônica e implementação do critério revisado, atualizar runbook/docs/matriz/preflight/proxy/verify-wave para a separação contratual versus empírica versus atestação interna unavailable, reexecutar testes e distribuir o novo delta nucleus → consumidor com hashes/manifesto/revisão de trust pelo operador quando exigidos; não reutilizar a integração 4.4 ou a aprovação anterior como prova do novo código.

## 5. Aceitação viva e handoff

- [x] 5.1 Demonstrar na CLI interativa do worktree uma delegação nativa concluída com nascimento/execução/completed/payload, par observado válido e contrato/chamada real fork_turns=none/ensaio complementar completo; atestação interna completa unavailable. Mostrar lista nativa, estado, inspeção/interação e retorno no chat pelos controles reais. Recorte multissuperfície transferido ao #1128. <!-- covenant-flow:after-qa -->
- [x] 5.2 Demonstrar tentativa impedida por limitação do host antes do trabalho, com razão exata e nenhuma sessão externa; preservar interrupção/falha como estados distintos de conclusão. <!-- covenant-flow:after-qa -->
- [x] 5.3 Demonstrar escrita autorizada pelo Guard no card/etapa corretos e denies fora do card/etapa por rotas suportadas, com contexto efetivo e readback; não usar a escrita deste Design como substituto da prova. <!-- covenant-flow:after-qa -->
- [x] 5.4 Demonstrar onda dedicada automática read-only: cadeia principal/coordenador/dois filhos, runtime do coordenador e filhos, leitura do mesmo diff, deny/readback de cada reviewer nomeado, ambos retornos e verify-wave/checklist válidos, sem alternância manual. Sem capacidade comprovada, manter pendente e revisão bloqueada. <!-- covenant-flow:after-qa -->
- [x] 5.7 Repetir positivo real da CLI interativa → coordenador exec após adaptação e recusas de evidência ausente, vínculo incorreto, modelo/esforço divergentes e contexto insuficiente/divergente; distinguir negativos reais de fixtures e não afirmar atestação interna completa. Principal exec independente e demais superfícies transferidos ao #1128. <!-- covenant-flow:after-qa -->

### Transferências para #1128 — pendentes, não concluídas

Itens abaixo são registro de transferência, não checkboxes executáveis deste card:

- **5.5:** completar matriz integral de refinamento, autor/crítico Design, Apply, ambos reviewers e QA por superfície com provas reais; não declarar substituição integral diante de lacunas.
- **5.6:** refinamento interativo autorizado completo, com captura, filiação, contexto contratual/chamada/ensaio, par observado e payload; diagnóstico /source ou autoria não o substitui.
- **5.8:** ensaios App/IDE por capacidades reais via app-server; positivos equivalentes ou limitações específicas, sem promover limitação documentada a positivo.
- **Partes de 5.1/5.7/6.3:** aceites das outras superfícies e rotas com principal exec independente/App/IDE. Coordenador exec lançado pela CLI interativa permanece no #1098.

As anotações after-qa somente definem quando revalidar evidências finais; não dispensam preflight, não autorizam revisão/commit com onda ausente e não transformam tarefa bloqueada em concluída. O trabalho de implementação só inicia após T7/T8; este checklist não move a FSM.

## Histórico antes da nova entrada Apply da opção 2 em 17/10/2026

Os requisitos de mesmo chat e proibição absoluta de exec nos registros históricos seguintes foram substituídos somente para coordenação Review pela decisão de Alan descrita no Design seção 4; não representam o contrato atual.

A entrega anterior e a integração local correspondem a **17/27 tasks concluídas**, incluindo 4.4, conforme evidência do orquestrador. Essa entrega é preservada. A revisão autorizada acrescenta quatro tasks de implementação/verificação ainda pendentes (1.7–1.9 e 4.5): o total passa a **17/31**, sem fabricar implementação ou ensaio do critério novo. As tasks já realizadas não são reclassificadas retroativamente.

- 3.2 continua parcial e pendente: contexto passa a usar o critério contratual/chamada/ensaio escolhido, mas efetividade read-only e leitura do diff/deny de escrita/readback de cada reviewer mantêm suas exigências originais.
- 3.3 permanece pendente: a onda exige o mesmo chat e todas as provas de permissões e reviewers; esta revisão não concede controle de permissões ao agente.
- 5.1–5.8 seguem pendentes. Provas históricas e a ausência isolada de sentinela não encerram os aceites.
- O adapter integrado continua exigindo o critério antigo. O pai informou que o dry-run canônico de pedir_review recusa no preflight antes da avaliação de digest/I4; não houve mudança de Status.
- Novo digest exige revalidação pelo processo canônico e aprovação humana pertinente; a escolha da opção 2 não vale como T7 de um digest novo nem autoriza código nesta revisão.

Pin-base v1.1.22 e publicação pendente são preservados. Esta continuação alterou somente Design/spec/tasks/evidence; não alterou código, adapter, manifesto, conta, trust, permissões, FSM ou snapshots de crítica.

## Nova entrada Apply da opção 2 em 17/10/2026

Após T7 da opção 2 e T8 executada pelo pai, o critério novo integrado/revisado foi revalidado neste Apply. Tasks 1.7–1.9 reconciliadas com implementação ativa, testes de contexto e qualificação nativa real do pai: tentativa `7739e34e-0611-40db-be29-e26e015bd5a4`, filho `01a14a96-b8e5-79f1-b701-f69723c6b90a`, verificação sanitizada `passed`, `fork_turns=none` e `internal_context_attestation=unavailable`. Nenhum marcador foi publicado. Progresso: **20/31**.

3.2 recebe candidato inativo de coleta por eventos nativos `CommandExecution`, leitura exata de diff e deny/readback em fixture descartável, sem positivo vivo neste turno gravável. Permanece pendente até integração e validação exigidas. 3.3 e 5.4 dependem de controle nativo de permissões e onda real no mesmo chat. 4.5 continua parcial: critério ativo e trust revisado informados pelo pai; sincronização nucleus foi negada pelo Guard `target_outside_binding`, sem contorno. 5.1–5.8 permanecem pendentes; não se promove prova parcial a aceite integral. Design aprovado preservado byte a byte.

## 6. Revisão automática dedicada — nova decisão de produto em 17/10/2026

Estado informado pelo pai: Design após T17/I4. Preservadas as 20 tasks concluídas. O pacote de coleta foi integrado; positivo diagnóstico default TUI informado pelo pai não conclui 3.2, 3.3 ou 5.4.

- [x] 6.1 Implementar schema de pacote/envelopes pendentes e vínculo autoritativo principal → coordenador real → dois filhos; adaptar prepare/coleta/proxy/verify-wave à identidade e turno reais, rejeitando receipt ligado ao principal, cadeia ausente/ambígua, origem adulterada e envelope usado como prova final.
- [x] 6.2 Atualizar explicitamente os dois perfis nomeados para probe fixo descartável antes do parecer, sem escrita de produto/escalada e sem dependência circular de verify-wave final; demonstrar ambos perfis e negativos de escrita permitida, alvo divergente e prova ausente.
- [x] 6.3 Qualificar lançamento e retorno automáticos CLI interativa → coordenador exec: nascimento read-only, mesma onda/turno, capturas estáveis, contexto opção 2, sandbox contínuo até dois payloads, coleta pelo principal e falhas sem alternância manual, sobre o código final. Rotas com principal exec independente/App/IDE transferidas ao #1128; positivo diagnóstico anterior não qualifica esta versão.
- [x] 6.4 Atualizar runbook/docs/matriz e testes das garantias novas, validar OpenSpec, conferir distribuição nucleus/consumidor e manifesto; revisão humana de trust somente se adapter mudar. Preservar conta, FSM, gates humanos, evidências históricas e internal_context_attestation unavailable.

Progresso após esta revisão: **20/35 tasks**, sem novos checks de implementação marcados. Crítica e T7 do novo digest continuam necessárias.

## Entrega da nova entrada Apply após T7/T8 — revisão automática, 17/10/2026

T7/T8 desta entrada foram confirmados pelo pai. Entrega implementável em pacote **inativo** `.cursor/tmp/card-1098-automatic-review-fix/`: 17 arquivos candidatos, snapshots before, patch, manifesto SHA-256, verificador e integração em comando único usando o gerador preservado do consumidor. Adapter ativo e Design aprovado permanecem preservados durante a execução deste filho.

3.2/3.3/6.1 recebem implementação candidata: envelopes pending sem parent fictício, vínculo principal→coordenador→filhos por fontes nativas, bootstrap/contexto/probes com retomadas nativas da mesma sessão read-only, persistência externa pelo principal e verify-wave dedicado. O ciclo não exige gravação de receipts no coordenador nem copia qualificação TUI. 6.2 recebe perfis nomeados explícitos e negativos de escrita permitida, alvo divergente/probe ausente; a demonstração real de ambos continua pendente. 6.3 exige lançamento/retorno e qualificação reais por rota, ainda não executados neste filho. 4.5/6.4 recebem documentação/testes/validação, mas integração, distribuição nucleus/consumidor e confiança pertinente permanecem no pai/operador; a recusa anterior target_outside_binding não foi contornada.

Regressão candidata: 511 passed / 7 skipped; ajuste final de classificação de falha/interrupção/indisponibilidade recebeu verificação focada separada. Evidência detalhada em `evidence/apply-automatic-review-20261017.md`. Nenhum checkbox foi promovido por código inativo ou prova viva ausente: progresso conservado **20/35** até integração/reconciliação cabíveis pelo pai. P0 dependente: falta de qualificação viva da nova rota dedicada impede Review/QA/commit; roteiro executável entregue. Este filho não abriu sessão externa, reviewers ou QA e não realizou process_event/commit/push/trust.

### Continuação do mesmo Apply — settings iniciais do coordenador

O ensaio real do pai encontrou falso negativo: `thread_settings_applied` inicial compatível com o turno read-only era recusado incondicionalmente. Correção inativa em `.cursor/tmp/card-1098-coordinator-settings-fix/` valida o schema nativo observado, perfil efetivo/turno/captura/binding e fronteira anterior às ferramentas; permite reaplicação completa idêntica antes do trabalho em retomadas, mantendo recusas de ampliação, divergência, unknown e aplicação tardia. Fontes settings/turnos ficam ligadas por hashes à tentativa sem promover append posterior a retuning histórico.

Foram inspecionados somente metadados dos ordinais 0/7/8 e tipos/ordinais necessários; conteúdo dos marcadores/prompts do trace real não foi exposto nem copiado. A projeção sanitizada passou no validador candidato; isso não executou binding/C-S/qualificação da rota nem substitui o próximo ensaio. 33 novos testes passaram; regressão e hashes constam da evidência `evidence/coordinator-settings-fix-20261017.md`. Adapter ativo/trust/Design/trace preservados. Novo bootstrap será necessário após integração pertinente, pois os hashes de código do pacote anterior não devem ser editados. Nenhum checkbox de aceite vivo foi alterado.

### Continuação do mesmo Apply — ordenação da retomada e preflight de contexto, 18/10

Após nova integração/trust pelo pai, bootstrap/binding e recusa de rota funcionaram. A continuação real mostrou settings idênticos após terminal25 e antes de started28/context31. O candidato consolidado `.cursor/tmp/card-1098-coordinator-resume-fix/` aceita esse intervalo somente com configuração idêntica/readonly e atribui refs26/27 ao próximo turno, conservando refs7/8 do bootstrap. Mudança transitória, ampliação, unknown ou trabalho sem novo contexto continuam recusados.

Também foi observado um segundo obstáculo: comando49 executou inspect com pacote context e falhou antes do filho. O prompt context passa a fornecer preflight exato, exigir ready/context/diagnostic_only e nomear a ferramenta nativa direta; inspect em fase incorreta recebe erro próprio e runtime ativo sem v2 impede nascimento. Não houve spawn nativo no trace disponível; custom execs eram shells e não foram promovidos a origem de filho. Projeção real sanitizada validada apenas quanto à ordem/permissões. Pacote/testes/limitações em `evidence/coordinator-resume-fix-20261018.md`. Captura/birth originais, adapter ativo, conta, trust, Design, pacotes/digests e trace preservados. Nenhum aceite vivo marcado sem prova.

### Nova entrada Apply via T10 — preflight produto somente leitura, 18/10

A reconciliação diagnóstica do pai confirmou 3.2/6.1/6.2, total **23/35**. A tentativa de produto seguinte falhou no preflight antes dos reviewers: provider de Status exigiu temporário/cache/rede no coordenador read-only; exit0 do launcher não foi revisão bem-sucedida. T10 `achar_bloqueante` foi confirmado pelo pai, sem novo T8.

Candidato inativo `.cursor/tmp/card-1098-readonly-preflight-fix/`: consulta autoritativa em stage-check nativo do principal, reconsulta Code Review no launch, receipt exclusivo ligado à tentativa/origem, verificação RO de binding/hashes/frescura no coordenador e coleta histórica pelos horários nativos. Falha do preflight conserva código específico. Seleção do pacote novo não exige revalidar contra código atual todos os pacotes históricos preservados. Testes de contrato incluem preflight produto completo em subprocesso com escrita/cache/rede negadas e importações frias; não equivalem a reviewers reais ou qualificação nova.

Evidência: `evidence/readonly-preflight-fix-20261018.md`; receita/testes/hashes no pacote. Adapter/manifesto ativos, conta, trust, permissões, Design e traces preservados. Integração/revisão pertinente e novo ciclo bootstrap/contexto/probes/rota ficam no pai. Tasks 3.3/5.4/6.3 e demais aceites permanecem pendentes; distribuição 4.5/6.4 segue impedida por `target_outside_binding`, sem contorno. Nenhum checkbox foi promovido por código inativo: **23/35**.

### Continuação do mesmo Apply T10 — service tier da retomada, 18/10

Após integrar/revisar o pacote anterior, o novo coordenador `01a14c8d-0db5-7b60-8f6d-c3ae88480673` recusou o preflight de contexto por `review_coordinator_settings_changed`, antes de qualquer spawn. A inspeção restrita confirmou única diferença: settings 8 tier default → 26/27 priority. O contrato oficial trata tier como preferência independente dos turnos; política local e Design autorizam modelo/esforço, contexto, binding e permissões.

Candidato inativo `.cursor/tmp/card-1098-service-tier-fix/` classifica somente service_tier como metadado não autorizador após validar o schema completo. Não afirma igualdade dos settings completos: conserva valores e hashes de origem por turno. Demais campos e fronteiras de eventos permanecem estritos. Projeção sanitizada real PASS; contexto/CLI e ciclo diagnóstico cobertos por fixtures, sem promover a tentativa recusada ou aceites vivos. Evidência e limites em `evidence/service-tier-fix-20261018.md`; nenhum novo checkbox marcado, **23/35**. Adapter ativo/trust/conta/Design/FSM/trace preservados; integração e ensaio com hashes novos permanecem no pai.

### Nova entrada Apply via T10 — onda inválida e diff grande, 18/10

T10 da nova entrada foi confirmado pelo pai após tentativa produto `dedicated-review-508bcdce41382b390ddf5589.package.json`. O launcher retornou exit0, mas a coleta recusou `review_launch_source_unavailable`: dois preflights nativos no mesmo turno. O code-reviewer também informou repetição do probe após truncamento. A tentativa é tecnicamente inválida; nenhum parecer foi promovido a review válida.

Pacote inativo `.cursor/tmp/card-1098-review-wave-fix/`: preflight/probe explícitos uma única vez, budgets de saída, leitura posterior sem escrita em chunks de 4096 caracteres vinculados ao mesmo artefato, cobertura nativa integral/reconstrução de SHA e recusa de partes ausentes/truncadas/sintéticas. Os dois perfis deixam explícita a verificação inicial pelo helper e o `verify-wave` final somente no principal, sem dispensar prova antes do parecer. Restaurados os gates removidos de outros clientes: detecção implícita Cursor/OpenCode com registro de conta, par observado do pai Claude em T16 e tokens parseáveis de Design em T5, preservando o preflight Codex/I4 novo.

Testes e limites constam de `evidence/review-wave-fix-20261018.md`. Integração/manifesto pelo gerador do consumidor, revisão pertinente e novo bootstrap/contexto/probes/rota/review reais pertencem ao pai. Nenhum checkbox vivo ou de distribuição foi promovido: **23/35**. Tasks 3.3/5.4/6.3, 4.5/6.4 e aceites QA continuam pendentes; `target_outside_binding` do nucleus não foi contornado. Design, conta, trust, permissões, fontes runtime e pacotes históricos preservados.


### Continuação do mesmo Apply — distribuição consolidada e paginação viável, 18/10

Depois da integração/trust do pacote anterior, o pai confirmou Status vivo Em desenvolvimento às 01:52 UTC e continuidade da captura/birth originais, sem novo T8. O trabalho passou a priorizar distribuição antes de outro ciclo vivo.

Entrega inativa `.cursor/tmp/card-1098-consolidated-delivery/`: before/candidatos completos de dois destinos, patches e manifestos distintos, preservação do install.sh e dos geradores/particularidades de cada árvore, auditoria de imports canônicos, helper exclusivo do operador para aplicar primeiro no nucleus e redistribuir os payloads compartilhados ao consumidor a partir da fonte real. Não foi tentada escrita no nucleus nem contorno de target_outside_binding; o pacote não constitui distribuição já executada, publicação ou pin novo.

No diff informado (SHA-256 226eb571d1d5883ac5171e006101ead3da32b4b755efe93fa1fa669865042c95, 700740 bytes), paginação limitada por JSON UTF-8/envelope reduziu 170 para 52 leituras por reviewer (340→104, -69,41%). Aspas/controles/Unicode ajustam o tamanho; não há aumento fixo sem limite. Permanecem probe/deny/readback únicos, mesmos bytes/SHA e prova completa em CommandExecution e retorno entregue ao modelo, com recusas de truncamento/omissão/duplicata e nenhuma exclusão de conteúdo da revisão.

Resultados/limites em `evidence/consolidated-delivery-20261018.md` e no README selado do pacote. Nenhum aceite vivo foi promovido: **23/35**. Tasks 3.3/4.5/6.3/6.4 permanecem pendentes dos fatos reais de distribuição/qualificação/revisão e dos demais aceites. Contexto/interfícies não observados não são declarados; internal_context_attestation permanece unavailable.

### Reconciliação documental após distribuição real — 18/10

O operador executou a entrega consolidada em terminal comum e depois registrou trust separadamente. Receipt real `distribution-receipt.json`, pacote `83d27a47eed4f91966d92acf2785f9dbb120a0cefe7233bce829f318cfe2678b`; verificação direta antes desta edição: `deliver.py --applied` → verified/applied=true/writes=false. Mapeamentos e hashes reais dos dois destinos conferidos; manifesto consumidor `bfcf715275cb5e7be42df69c2d9db6ca6b4a8d6419331dbe997ba7b13888f15b`. Trust do adapter final confirmado pelo pai como reviewed=true/manifest=true, sem missing/divergent. Evidência completa em `evidence/distribution-complete-20261018.md`.

Os aceites documentais, testes, distribuição, manifesto e revisão humana de 4.5/6.4 foram cumpridos; somente esses dois checkboxes avançam: **25/35**. Tasks 3.3, 6.3 e 5.1–5.8 seguem pendentes do novo ciclo real e aceites próprios; diagnóstico anterior não é promovido à versão final. Esta reconciliação posterior altera intencionalmente tasks/evidence em relação ao payload documental entregue; não reescreve pacote/manifestos/before, não repete aplicação e não muda código, docs compartilhados, skills, perfis, Design ou trust.


### Correção consolidada após T10 — 18/10/2026

Candidato inativo `.cursor/tmp/card-1098-final-review-fix/` corrige seleção da tentativa de contexto mais recente, regressão Claude Desktop, espera do preflight assíncrono e orientação de capacidade nos nascimentos imutáveis. Checks focados: **148 passed**; dry-run das duas árvores e invariantes ativos PASS. Nenhum payload aplicado nem novo aceite vivo: **25/35**. Nota factual autorizada de recorte para #1128 acrescentada a Design depois do selo; specs/checklist e `.design-digest` preservados, sem T7 implícita. Pai fará revalidação/autor e o ciclo final; estados dos checkboxes não foram reclassificados. Evidência: `evidence/final-review-fix-20261018.md`.


### Integração real da correção final — 18/10/2026

Após T7/T8 confirmados pelo pai, o operador aplicou o pacote final-review-fix. Receipt, selo e oito payloads nucleus → consumidor conferidos; manifesto consumidor e trust pertinente confirmados pelo pai. Registro: [evidence/final-fix-distribution-20261018.md](evidence/final-fix-distribution-20261018.md). Progresso **27/32 + três transferidas não concluídas** após a qualificação atual da rota: somente 3.3/6.3 avançam. Não houve promoção por distribuição ou por ensaio antigo. 5.1–5.4/5.7, Review/QA de produto e verify-wave/checklist continuam dependentes de provas próprias; esta continuação altera somente a reconciliação documental.
