## Context

Contrato vigente de 18/10/2026: Alan escolheu concluir CLI e separar os ensaios restantes no [#1128](https://github.com/oalansilva/crypto/issues/1128), em Em Refinamento. O briefing literal está no início de `proposal.md`. Status informado pelo pai: Design após I4/T17. Esta autoria não concede T7, implementação ou aprovação do novo digest; `.design-digest` permanece preservado.

UI impact: none
live_route: N/A — processo operacional na CLI Codex, sem tela ou rota Cripto alterada.
surface: none

## Goals / Non-Goals

Entregar CLI interativa no worktree do card, com filhos nativos identificáveis, estado e retorno verificáveis. Demais etapas continuam delegadas no chat do card; somente Review usa coordenador exec dedicado automático, read-only desde o nascimento, principal gravável e dois reviewers nativos no mesmo turno. Principal e coordenador não executam pareceres. Não há alternância manual de permissões, fallback oculto, modo Auto ou suporte universal prometido.

App/IDE, principal exec independente, refinamento interativo completo e matriz integral de todas as etapas/superfícies pertencem ao #1128. A capacidade de usar exec como coordenador da CLI permanece requisito do #1098. Gates humanos, seleção, contexto, Guard, permissões, Review e QA não foram transferidos nem relaxados.

## Decisions

### 1. Rota e preflight verificáveis

Validar schema, origem, capacidades e qualificação da rota CLI interativa → coordenador exec, não uma igualdade exclusiva de nome de host. Host/versão são procedência; prova de outra superfície não qualifica esta rota. Preflight confere card/Status, branch/worktree efetivo, ferramenta nativa, captura local, observabilidade do par e permissões. `workdir` de shell, prompt ou configuração não concedem binding nem autorização. Guard verifica identidade e todos os alvos reais, inclusive caminhos mistos/symlinks; cobertura ausente não é proteção.

Garantia conhecida ausente recusa antes do spawn/trabalho, informando card, etapa e motivo. Verificação que exige nascimento só permite diagnóstico com barreira efetiva antes de trabalho de etapa. Falha ou interrupção permanece tal; `completed` exige payload da mesma identidade. Captura por nascimento e par observado ficam separados; unavailable/divergência não passa. Mudança efetiva de seleção na onda exige nova tentativa; continuação conserva a captura original.

### 2. Contexto: opção 2 preservada integralmente

Exigir conjuntamente contrato documentado aplicável à ferramenta/superfície, chamada nativa real registrada com `fork_turns=none` e qualificação complementar íntegra. Preservar fonte, identidades, escopo e digests de cada parte. `internal_context_attestation=unavailable`: não atesta contexto interno completo e não dispensa qualquer outra prova.

No diagnóstico, controle não secreto C é entregue ao filho; sentinela não secreta S existe somente no contexto anterior do pai. S não entra em prompt, steering, nomes, arquivos, env ou outros canais do filho; transcript do pai não é consultado. Exigir controle exato, filiação, completed/payload e origem sem contaminação. Sentinela herdada ou chamada divergente bloqueiam; silêncio, controle errado, fonte incompleta e contaminação não são positivos. Ausência isolada de S não prova isolamento. A tentativa diagnóstica mais recente aplicável rege a qualificação: falha/incompletude nova impede reutilizar positivo antigo. Fixtures, outro contrato/superfície e paginação `excludeTurns` não substituem o conjunto.

### 3. Review automático e prova integral

1. Principal prepara diff exato completo pré-commit/closing, path/SHA-256, pacote imutável, capturas distintas e estáveis da onda, prompts autocontidos, planos/fixtures e envelopes pendentes. Nenhum parent fictício ou receipt pendente conta como prova final.
2. Lançamento automático da CLI para `codex exec --sandbox read-only` e retomadas nativas da mesma sessão precisam de fonte nativa completa, JSONL/rollout, identidade, binding e permissões contínuas. Bootstrap → diagnóstico de contexto → persistência pelo principal → probes dos perfis nomeados → qualificação da rota precedem produto. Configuração não prova sandbox; coordenador não grava receipts nem herda qualificação do principal.
3. Em Code Review, coordenador verifica pacote, Status e preflight vivos e inicia **ambos** os papéis `diff-reviewer` e `code-reviewer` no mesmo turno, filhos distintos com captura própria, `fork_turns=none` e mesmo diff/SHA. Os perfis autorizam somente a tentativa do helper fixo na fixture descartável vinculada; escrita de produto, alvo arbitrário e escalada continuam proibidos.
4. Cada reviewer precisa de leitura integral do mesmo artefato, deny de escrita e readback inalterado antes do parecer. Prova deve cobrir bytes completos em `CommandExecution` **e** retorno entregue ao modelo; resumo, manifesto, truncamento, páginas ausentes/duplicadas ou leitura fora de ordem não bastam. Preflight/probe executam uma vez; execução assíncrona aguarda o mesmo processo/célula até saída completa, sem repetir a tentativa de escrita. Capacidade insuficiente bloqueia, sem inferir tokens/janela internos.
5. Coordenador e filhos permanecem read-only até ambos completed/payload. Principal coleta e persiste pelas capturas/envelopes originais, resolvendo cadeia real principal → coordenador → filhos da fonte autoritativa. Não editar traces ou fabricar receipt retroativo. `verify-wave` final e `review_process_checklist.py` passam antes de commit; QA da CLI continua obrigatório no fluxo canônico. Um reviewer de cada onda diferente nunca forma o par exigido.

### 4. Aceitação e rastreabilidade

Conservar 25 realizações históricas com seus hashes; não qualificam automaticamente código final. Checklist vigente: **25/32**, sete pendentes (3.3, 5.1–5.4, 5.7, 6.3), mais três transferidas **não concluídas**. O total anterior era 25/35; não houve progresso de implementação nesta revisão.

| Origem | Destino e obrigação |
| --- | --- |
| 5.5 | #1128: matriz integral de etapas/superfícies |
| 5.6 | #1128: refinamento interativo completo |
| 5.8 | #1128: ensaios App/IDE |
| 5.1 | #1098: delegação e controles reais da CLI; #1128: demais superfícies/etapas integrais |
| 5.7 | #1098: positivo/recusas da CLI → coordenador exec; #1128: principal exec independente e demais superfícies |
| 6.3 | #1098: lançamento/retorno e qualificação CLI → exec; #1128: principal exec independente/App/IDE |

Aceites CLI mostram delegação concluída e impedida, par/contexto válidos, escrita autorizada/denies do Guard com readback, controles nativos para localizar responsável/estado/interagir/retorno e onda completa Review/QA. Separar fixtures, runtime e observação de interface. Não marcar aceite enquanto faltar a prova; documentação de uma limitação não conclui positivo requerido.

## Evidências e estado atual

Distribuição anterior e tasks 4.5/6.4 estão registradas em `evidence/distribution-complete-20261018.md`. Diagnóstico anterior da rota passou, mas não qualifica hashes finais. Último diff de produto informado: `df57a803a0e4f4d2cacca2541517c612c1af637ed96fcdfe42f96722432a5604`; nenhum par válido na mesma onda/turno. Leitura completa por um papel em cada onda diferente não é aprovação.

Pacote `.cursor/tmp/card-1098-final-review-fix/` permanece **inativo e selado**, com 148 testes focados e dry-run das duas árvores PASS conforme README/evidência `evidence/final-review-fix-20261018.md`. Corrige contexto antigo reutilizado, regressão Claude Desktop, coordenação assíncrona e capacidade. Não foi aplicado nem prova runtime final. Código ativo/trust informado `d174776e2c16…` permanece preservado. Esses fatos não autorizam Review/QA/commit ou T7.

## Risks / Trade-offs

- Reduzir escopo entrega uma rota; suporte universal e substituição integral continuam não comprovados e rastreados no #1128.
- Schema, binding, seleção, contexto, capacidade de leitura ou permissões ausentes mantêm a etapa bloqueada; não há fallback silencioso.
- Teste ou qualificação anterior pode divergir do código final: revalidar fontes/hashes e tentativas mais recentes antes de dependentes.

## Migration Plan / Apply contract

Após crítica independente, publicação e T7 humana pelo processo canônico, continuar Apply somente no estado autorizado. Integrar candidato/distribuição pelo fluxo pertinente, conferir procedência nucleus → consumidor e manifesto; confiança do operador permanece ato separado quando necessária. Reexecutar qualificação/bootstrap/contexto/probes/rota e onda final sobre o diff integral vigente, depois checklist e QA. Checks antigos de distribuição permanecem fatos históricos, não recibos do pacote novo. Preservar evidências, capturas, agentes vivos, gates, FSM e contratos dos demais clientes. Nenhuma instalação, trust, pacote selado ou código é alterado nesta revisão documental.

## Open Questions

Não há decisão de produto pendente. Sete tarefas CLI dependem de execução e provas finais reais; as lacunas transferidas permanecem no #1128 e não são aceites positivos do #1098.

## Prototype

N/A — sem tela; HTML generated/copied: N/A.

## Impeccable

- P3 — disposition: N/A; justificativa: processo operacional sem tela do produto.
- verdict: N/A para UI/protótipo.

## Design Critique

- P0–P2: nenhum achado na crítica independente deste recorte.
- P3 — disposition: aceito para Apply; as sete pendências CLI e a qualificação final permanecem obrigatórias. Código inativo, testes focados e provas de ondas diferentes não encerram esses aceites.
- P3 — disposition: N/A para UI; tokens parseáveis e justificativa sem tela presentes.
- verdict: recorte CLI consistente; nenhum rework necessário. Não concede T7 nem comprova runtime final. Snapshot: `.impeccable/critique/card-1098-codex-agentes-nativos-cli-20261018.md`.

## Histórico anterior ao recorte CLI — não normativo

Preservado integralmente abaixo para rastrear decisões, evidências e críticas anteriores. Expressões como “atual”, tarefas pendentes, exigência multissuperfície e verdicts no apêndice referem-se às respectivas datas e versões. O contrato vigente é o texto acima; o histórico não representa crítica ou aprovação deste digest.

<details>
<summary>Design e críticas anteriores ao recorte CLI</summary>

## Revisão do critério de contexto — decisão de Alan em 17/10/2026

Alan escolheu explicitamente a opção 2: avaliar isolamento operacional por **contrato documentado aplicável ao runtime + chamada nativa registrada com `fork_turns=none` + ensaio complementar não secreto de herança indevida**. Este conjunto é evidência contratual e empírica de escopo limitado; **não atesta o contexto interno completo entregue ao modelo**. Essa atestação permanece `unavailable` e deixa de ser requisito deste critério específico. Não é uma dispensa de filiação, seleção observada, Guard, permissões efetivas, leitura/deny/readback dos reviewers ou dos gates humanos.

Esta revisão altera o contrato e o digest do Design. A crítica histórica abaixo é preservada e cobre a versão anterior; não equivale a crítica ou T7 do novo digest. A decisão autoriza preparar os artefatos revisados, sem alterar FSM ou autorizar implementação pelo wording. O pai precisa publicar e revalidar pelo caminho canônico antes de qualquer Apply dependente deste critério. O adapter integrado ainda aplica o critério anterior.

## Context

**Revisão atual de produto, 17/10/2026:** a decisão 4 substitui exclusivamente as referências anteriores a Review no mesmo chat e à exclusão absoluta de sessões externas. O pai informou Status real Design após T17/I4. A opção 2 já implementada permanece válida; o novo escopo é automatizar coordenação dedicada read-only, bindings e contratos dos perfis. Os relatos de preflight antigo e bloqueio antes de I4 abaixo são históricos. Novo digest exige crítica e T7 humana; nenhuma implementação é autorizada por esta autoria.

O #1098 exige preservar visibilidade e controle de Alan sobre os filhos do card. O briefing literal está em `proposal.md`. O problema do #1095 expôs a diferença entre diretório de uma chamada shell e vínculo da sessão/hook. O #1049 corrigiu revisão sob permissões herdadas por meio de sessão dedicada somente leitura; este Design não apaga essa garantia.

UI impact: none
live_route: N/A — não existe rota Cripto para a lista de agentes do host Codex.
surface: none

Sem alteração de interface do produto. A experiência operacional acontece na lista nativa de subagentes e nas mensagens do chat; este repositório não implementa essa lista.

### Evidências disponíveis em 2026-10-17

Esta autoria substitui a versão de 13/10 porque o briefing passou a incluir todas as superfícies Codex e a coleta TUI foi recuperada. Não é nova rodada de polish. Fontes locais: `docs/codex-bootstrap-1098.md` e `docs/codex-runtime-evidence.md`.

| Fonte | Fato comprovado ou informado | Limite |
| --- | --- | --- |
| Bootstrap explicitamente autorizado por Alan | 118 testes focados passaram; delta local preserva schema, integridade, filiação, seleção e permissões | Não é T7/T8, implementação concluída, pin publicado ou aprovação humana |
| Ensaio TUI 0.163.0 em `/source` | Nascimento nativo, par observado, filiação, execução, completed/payload, coleta/proxy e qualificação; recusa real `birth_mismatch` antes do nascimento | `danger-full-access`; não prova worktree do card, revisão, interação visual ou app/IDE |
| Retomada nativa do mesmo chat no worktree | Pai informou preflight ready e preparou receipt válido para este autor, após retomada pelo operador | Coleta deste nascimento ocorrerá após o retorno; receipt não comprova completed/payload antecipadamente |
| Exec 0.162.1, evidência #1095 | Ensaio nativo documentado de coleta, seleção e retorno | Workspace-write; exige regressão após adaptação; não qualifica TUI ou app |
| App/IDE via app-server | Fixtures de contrato | Sem ensaio real; suporte não comprovado e qualificação própria obrigatória |
| Ferramenta spawn desta sessão | Aceita modelo/esforço e `fork_turns`; não expõe cwd nem sandbox | `workdir` do shell não altera o nascimento; não inventar API |
| Turno deste autor | Worktree informado é o do #1098, permissões `danger-full-access` | Não comprova Guard nem read-only; escrita documental não vale como ensaio de autorização |

O par e a versão do ensaio TUI deixaram de ser `unavailable`; isso não preenche observações de outros filhos. O receipt deste autor referencia a captura própria, e o pai verificará sua fonte após o retorno. Na versão original, isolamento efetivo exigia um sinal interno adicional a `fork_turns=none`; essa exigência foi substituída para o critério de contexto pela decisão de Alan descrita nesta revisão. Os ensaios antigos continuam comprovando apenas os fatos coletados e não são promovidos ao novo conjunto de evidências. A revisão nativa permanece bloqueada neste turno gravável. Interação visual, escrita autorizada/denies vivos, refinamento interativo completo e app/IDE seguem pendentes.

## Goals / Non-Goals

**Goals:** suportar terminal interativo, exec e app/IDE conforme suas capacidades comprovadas, sem exigir troca para exec pelo nome do host; delegar refinamento, Design, Apply, os dois reviewers e QA no chat do card; tornar responsável, estado, interação e retorno localizáveis; conservar worktree autorizado, captura por nascimento, contexto operacional avaliado pelo critério revisado, sem fornecer transcript do pai, e revisão sobre o mesmo diff. Recusar antes do trabalho quando falta capacidade, com etapa e garantia explicitadas. Publicar evidências separadas de solicitações e testes sintéticos.

**Non-Goals:** executar etapas no pai, esconder CLI externa atrás de wrapper, trocar modelos ou confiança, mudar FSM/T1/T7/T15/T18, tocar PROD ou outros clientes, migrar/interromper agentes do #1095. Não desenvolver uma UI de subagentes nem modificar o host fornecedor neste card.

## Decisions

### 1. Delegação nativa condicionada à capacidade da superfície

O driver valida schema e origem, não uma igualdade exclusiva com `codex_exec`. Terminal interativo, exec e app/IDE via app-server passam pelos mesmos requisitos de evidência; cada superfície precisa de qualificação real própria e revalidada. Host e versão identificam diagnóstico e procedência. Versão diferente com schema compatível não reprova sozinha; schema incompatível ou campo obrigatório ausente produz `unsupported_schema`, qualificação ausente produz `unverified`. Prova exec não qualifica TUI/app, mesmo copiada; receipts legados exec permanecem legíveis sem permitir reclassificá-los. Remover a comparação de host sem verificar o resto é insuficiente.

O bootstrap já prepara essa adaptação; o Apply deve revisar sua procedência, completar cobertura e ensaios, não marcá-lo automaticamente como entrega. O positivo obrigatório inclui refinamento interativo completo e regressão exec. App/IDE precisam de ensaio equivalente ou limitação específica por garantia ausente, nunca suporte universal inferido de fixtures.


O orquestrador prepara um registro da tentativa ligado a card, Status, papel, faixa, chat, worktree e captura de seleção. Antes do spawn verifica: ferramenta nativa disponível e vinculada ao chat, documentação aplicável e qualificação empírica do critério de contexto descrito na decisão 3, argumentos preparados com `fork_turns=none`, capacidade de aplicar e observar modelo/esforço, vínculo efetivo ao worktree, cobertura necessária do Guard e permissões da etapa. Ausência conhecida recusa o spawn. A chamada nativa de cada nascimento deve ser posteriormente revalidada na fonte; divergência invalida a tentativa, sem convertê-la retroativamente em bloqueio antes do spawn. Se outra garantia obrigatória só puder ser observada após o nascimento, o filho inicia restrito a diagnóstico e não recebe liberação para trabalho da etapa antes da verificação. Se o host não puder assegurar essa barreira antes do trabalho, recusa já no preflight.

Resultado operacional: `bloqueado` com razão ou tentativa nativa rastreável. Não são novos estados da FSM. Exemplo de mensagem: “Code Review do #1098 impedido: o host não oferece prova do contexto somente leitura que governa pai e filhos. Nenhum reviewer iniciou a revisão; etapa não executada.” Uma etapa executada cujo retorno falhou é `falhou`/`interrompido`, nunca `bloqueado antes do spawn` retroativamente.

Alternativa externa é excluída pelo briefing. Executar no pai ou renomear processo externo não atende ao vínculo. Quando a capacidade aparecer, repetir preflight explicitamente; nada de retry com modelo alternativo, migração automática ou retomada de filho interrompido.

### 2. Vínculo ao card não deriva de um path arbitrário

Na futura implementação, separar identidade autorizada da sessão/tentativa, diretório efetivo da ferramenta e alvos da escrita. O vínculo contém card, worktree canônico, branch e ação permitida, obtidos do contexto verificado e da FSM; prompt e `workdir` não concedem autorização. Resolver caminhos reais e conferir todos os alvos contra esse vínculo antes de chamar `guard.decide()`.

O adapter pode normalizar o schema efetivamente observado (`cmd`/`command`, `workdir`, paths de edição), mantendo o evento original e a decisão auditáveis. Uma sessão inicialmente em `source` só poderá operar no worktree declarado quando o vínculo ao mesmo card estiver comprovado e a ferramenta/hook usar esse contexto validado. `workdir` de outro card, caminho que escapa por symlink, mistura de alvos, identidade ausente ou divergente devem receber deny. Não trocar cegamente `event.cwd` por entrada fornecida pelo agente. Se o hook ainda resolver checkout errado, mostrar o conflito e interromper o trabalho afetado.

O contrato não presume API de rebind nem parâmetro cwd no spawn. O caminho observado é o operador retomar nativamente o mesmo chat com `codex resume <id> --cd <worktree>`; isso não é uma sessão externa de delegação. Validar o efeito real no `turn_context` ativo antes do nascimento: `session_meta.cwd` inicial é histórico e não prevalece sobre uma retomada nativa comprovada. Conferir ainda metadata de nascimento e todos os turnos do filho no worktree esperado. `--root`/`workdir` não reconfiguram o chat; divergência mantém `worktree_mismatch`, com diretórios observados e recuperação precisa. A retomada não altera card, Status ou confiança automaticamente. Vínculo runtime e decisão do Guard são provas distintas; ambos precisam passar. Para refinamento, sem worktree criado, vale cwd do contexto vinculado à issue conforme regra existente. Depois de T1, cada filho usa worktree `card-<id>-*`.

### 3. Seleção e contexto têm evidências próprias

Reusar resolver e captura local por nascimento, sem fallback ao mapa histórico ou picker. Passar literalmente o par capturado e `fork_turns=none` na ferramenta deste host, prompt autocontido sem fornecer transcript do pai. Seleção de modelo/esforço continua exigindo metadata autoritativa observada, separada do pedido; texto do filho não a substitui.

O critério de contexto revisado exige cumulativamente:

1. **Contrato aplicável:** identificar fonte oficial ou schema nativo documentado da ferramenta, superfície, host/versão e semântica pertinente à herança de turnos. Conservar URL ou referência verificável, data e digest da fonte/schema usado. Contrato genérico de outro produto não qualifica esta superfície por analogia. A documentação [Responses Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) descreve contexto próprio por subagente no seu âmbito; a documentação [app-server](https://learn.chatgpt.com/docs/app-server) descreve threads e consulta de histórico. Nenhuma delas fornece atestação do contexto interno completo deste filho. `excludeTurns` de uma resposta app-server não equivale a `fork_turns=none` nem prova que o histórico não foi herdado.
2. **Chamada registrada:** conservar na fonte nativa a chamada real com `fork_turns=none`, seu call id, parent/chat/turno e child id, captura de seleção e referências/digests de origem. Configuração, receipt preparado, texto do prompt ou declaração do filho não substituem os argumentos realmente registrados. Ausência, `all`, divergência ou fonte inconsistente impedem validar a tentativa.
3. **Ensaio empírico complementar completo:** qualificar o mesmo contrato, ferramenta e superfície por diagnóstico sem trabalho de produto, com controle positivo e sentinela exclusiva do pai conforme protocolo abaixo. Uma prova de outra superfície, fixture ou ensaio incompleto não qualifica. Mudança relevante de contrato/schema/comportamento exige revalidação; o número da versão isoladamente continua diagnóstico.

O preflight da etapa deve conferir contrato aplicável, qualificação empírica íntegra e argumentos a enviar antes do trabalho; cada nascimento mantém verificação posterior da chamada real e demais fatos runtime. A falta de uma atestação interna completa não reprova sozinha este critério revisado. Em contrapartida, falha de qualquer uma das três partes, ou de qualquer outra garantia obrigatória da etapa, continua bloqueando o caminho dependente.

#### Protocolo do ensaio de herança indevida

- O pai estabelece **antes do nascimento** dois valores novos, distintos e não secretos: uma sentinela de herança `S`, presente somente em seu contexto anterior, e um marcador de controle `C` entregue explicitamente no prompt autocontido do filho. Não usar valores reais de produção ou exemplos fixos deste documento.
- O valor de `S` não entra no prompt do filho, mensagens de steering, títulos, nomes de arquivos, fixtures, arquivos compartilhados, variáveis de ambiente, capturas ou outros payloads disponibilizados ao filho. Não fornecer o transcript nem sua localização ao filho. Logs nativos preservam sua procedência privada; não copiá-los como contexto do diagnóstico. Se houver vazamento por um desses canais, o ensaio fica inválido e não qualifica a superfície.
- O filho recebe `C` e uma tarefa diagnóstica clara: devolver o controle exato e informar qualquer sentinela de herança que realmente tenha recebido; se não tiver uma, declarar ausência sem adivinhar. Não recebe trabalho de etapa nem acesso a fontes para procurar `S`. A origem deve confirmar que não houve consulta a transcript, arquivos ou outros canais que contaminem o diagnóstico.
- O controle correto retornado com completed/payload e filiação/call id válidos comprova que a instrução e o canal de retorno do diagnóstico funcionaram. Controle ausente ou incorreto, silêncio, interrupção, falta de payload, fonte incompleta ou contaminação tornam o resultado `incomplete`/inválido; não contam como positivo.
- Sentinela do pai devolvida sem entrega autorizada é resultado divergente e bloqueia a qualificação e o trabalho dependente. Chamada registrada diferente de `fork_turns=none` também diverge. Não repetir com outro modelo para apagar o resultado nem converter falha em sucesso.
- Somente contrato aplicável + chamada registrada correta + controle exato/retorno íntegro + ausência de `S` no resultado de um ensaio não contaminado satisfazem o **critério operacional escolhido**, no escopo observado. A ausência de `S` isoladamente não prova não herança; mesmo o conjunto positivo **não atesta o contexto interno completo** nem ausência universal de acesso a todo o histórico.

Persistir separadamente evidência contratual, chamada nativa e resultado empírico, cada qual com escopo e proveniência. O resumo sanitizado registra identificadores, digests dos marcadores, controle conferido, resultado da sentinela, integridade/contaminação e `passed|failed|incomplete`; omite os valores de `S` e `C` do relatório público. `S` não é transferida ao filho; `C` é entregue explicitamente no prompt do diagnóstico. `internal_context_attestation=unavailable` permanece explícito, separado do resultado operacional. Esses nomes são metadados do registro a implementar, não campos alegadamente expostos pelo provedor ou novos estados da FSM.

Registro mínimo: tentativa, chat/parent id e child id, papel, card/Status, worktree pedido/efetivo, captura/digest, argumentos reais, par requested/observed, fonte de cada observação, host/versão, política efetiva, nascimento/execução/conclusão/interrupção e payload ou referência verificável. Ausente = `unavailable`, nunca campo sintetizado. A exceção de exigibilidade é apenas a atestação interna completa: sua indisponibilidade permanece registrada e não é convertida em uma garantia; o critério operacional de contexto usa as três partes acima. O conteúdo retornado precisa ser vinculado ao mesmo child id. Evento de spawn não prova execução; completed sem payload não passa. Mudança de escolha entre reviewers invalida a onda; filhos vivos conservam sua captura de nascimento.

### 4. Review automático em sessão dedicada conserva a garantia de #1049

Alan substituiu explicitamente o requisito de mesmo chat somente para coordenação de Review: não aceita alternar permissões manualmente no uso diário. Esta decisão prevalece sobre referências anteriores a Review no mesmo chat ou proibição absoluta de sessão externa. Demais etapas continuam nativas no chat do card. O principal permanece gravável; um coordenador Codex dedicado nasce read-only e inicia dois reviewers NATIVOS no mesmo turno. Principal e coordenador não executam review. Não há troca de cliente nem promessa de modo Auto.

**Sequência proposta, ainda sem qualificação integral:**

1. Principal verifica Status/ação na FSM existente e prepara pacote por tentativa: diff exato pré-commit ou closing, path canônico/SHA-256, card, branch/worktree, wave id, identidade principal, captura local de execução do coordenador e capturas distintas dos reviewers da mesma onda, prompts autocontidos, planos e fixtures descartáveis. Preserva hashes e referência do lançamento; não entrega transcript.
2. Lançador automático usa a interface candidata documentada `codex exec --sandbox read-only`, com diretório explícito do mesmo worktree e seleção local. O comando não comprova suporte nesta instalação. Validar fonte autoritativa, sandbox efetivo desde o nascimento, identidade, worktree, par observado e critério de contexto opção 2 antes de liberar trabalho. Não alterar permissões da sessão principal, conta ou confiança; falta de capacidade recusa, sem pedir alternância manual.
3. Receipts precisam vincular os filhos ao coordenador real. O preparo antecipado grava envelopes pendentes ligados ao pacote/lançamento, sem fingir parent id conhecido. O schema proposto admite esse estado explicitamente: preflight do coordenador confere o pacote e sua identidade nativa antes dos spawns; coleta final resolve o parent id exclusivamente da fonte autoritativa do lançamento e das chamadas nativas. Não reutilizar receipt ligado ao principal, aceitar parent arbitrário, editar source trace ou fabricar receipt retroativo. O vínculo pendente não vale como prova e só pode ser habilitado depois de implementação/teste desse protocolo. Fonte que não permite resolver cadeia inequívoca bloqueia antes do trabalho dos reviewers.
4. Coordenador verifica pacote, digest, Status e captura de onda em modo somente leitura. Inicia `diff-reviewer` e `code-reviewer` no mesmo turno, filhos distintos, `fork_turns=none`, pares literais das capturas e mesmo path/SHA. Cada nascimento relê a escolha local; mudança efetiva invalida a tentativa parcial. Coordenador e filhos permanecem efetivamente read-only até ambos completed com payload. Cada reviewer executa o probe antes do parecer; falha bloqueia o review. Coordenador apenas reúne retornos.
5. Principal coleta e persiste depois dos retornos, revalidando fontes/digests e cadeia principal → coordenador → dois filhos, card/worktree/diff, captura e modelo/esforço observados. O turno comum é o do coordenador, não o turno do principal; o schema registra essa diferença. `verify-wave` e `review_process_checklist.py` devem passar antes do commit. Interrupção, timeout, falta de payload, digest divergente ou sandbox/fonte inválidos impedem sucesso e dependentes.

**Contrato explícito do probe.** Perfis nomeados devem permitir somente a tentativa controlada do helper fixo sobre fixture descartável própria preparada pelo principal e vinculada ao plano/digest. Autorizar tentar não autoriza escrita bem-sucedida, produto, git, fixture arbitrária ou escalada. Helper comprova leitura do diff e registra tentativa, deny e readback com bytes preservados em eventos nativos. Escrita bem-sucedida invalida a onda; eventual restauração da fixture cabe ao principal após encerramento, preservando evidência. Não exigir `verify-wave` final antes de o reviewer produzir suas provas: fornecer verificação prévia de pacote/preflight; a agregada fica para o principal após ambos retornos. Mudança dos perfis exige implementação explícita após T7/T8; agentes default diagnósticos não substituem os papéis de produto.

**Superfícies e limites.** Qualificar separadamente origem principal (TUI, exec, app, IDE), transporte de lançamento/retorno e coordenador exec. Prova TUI não qualifica exec dedicado. Cada rota precisa de ensaio real sem alternância manual, com cadeia, seleção, duas chamadas nativas no mesmo turno, leitura/deny/readback e retorno verificável. App/IDE sem transporte ou telemetria ficam bloqueados com garantia ausente identificada. Não prometer suporte por existir comando shell. A opção 2 permanece contrato/chamada/ensaio; `internal_context_attestation=unavailable`. Prompt/TOML/configuração e testes unitários não provam sandbox.

**Estado desta revisão:** implementação da automação e qualificação dedicada pendentes. O pacote de coleta opção 2 foi integrado, mas a onda 01 com perfis nomeados recusou probe e a coleta recusou `review_probe_unavailable`. O pai informou onda 02 default TUI coletada verified/completed e qualificada: leitura do mesmo diff, errno30 e readback preservado. Esse positivo não qualifica perfis nomeados, sessão exec dedicada nem revisão de produto.

### 5. Experiência do operador e aceitação no host real

Usar nome nativo contendo papel e card, por exemplo `design-autor 1098`; vínculo de chat e child id permitem Alan encontrar o responsável. Evidência viva inclui lista da interface, estado em execução, abertura/inspeção do filho, mensagem de orientação entregue e retorno no chat; interrupção aparece como tal. Não prometer botão específico: testar controles realmente disponíveis na superfície do operador e registrar se interação ocorre pelo chat pai ou pelo thread.

A matriz de aceitação cruza superfície (interativo, exec, app/IDE) com refinamento, autor/crítico Design, Apply, diff-reviewer, code-reviewer e QA. Cada linha identifica host/versão, schema, chat/card/child, prova e limite; app e IDE são identificados separadamente quando expõem capacidades distintas. Por linha registrar suportado/provado/bloqueado, evidências e motivo. Demonstrar uma delegação concluída e uma impedida, escrita autorizada na etapa correta, denies fora de card/etapa, pares reais, isolamento e a onda completa de revisão. Unit tests não encerram linhas runtime. Enquanto faltar garantia, manter linha bloqueada e task correspondente pendente; não anunciar “substituição concluída” nem fazer avançar etapa afetada. Recusa correta é critério de comportamento, não substitui a prova positiva exigida pelo card.

## Apply contract

UI impact: none. O trabalho desta revisão se limita a proposal/Design/spec/tasks/evidence. A crítica histórica e a entrega integrada 4.4 são preservadas. Não alterar código, adapter, manifesto, trust, conta ou permissões nesta revisão. A implementação futura deve automatizar a coordenação dedicada da decisão 4 e seus bindings/perfis, conservar o gate de contexto contratual/empírico já aprovado, manter atestação interna unavailable e preservar Guard, seleção observada, read-only, leitura/deny/readback dos reviewers, duas identidades/mesmo diff e os gates humanos.

O novo digest precisa de revalidação canônica; não há T7 nova implícita. O pai informou reabertura real em Design via T17/I4. A próxima implementação deve preservar a opção 2 já aprovada e implementar a decisão 4, sem contornar checks ou inventar transição.

## Risks / Trade-offs

- Host sem telemetria de seleção ou sem contrato/chamada/ensaio de contexto completos → bloqueio persiste. Atestação interna completa permanece unavailable e não é prometida; um positivo empírico não estabelece garantia universal.
- Normalização de diretório pode autorizar outro card → validar identidade independente, caminho real e todos os alvos no Guard, com negativos antes de ativar.
- Hooks hospedados podem não executar → documentar cobertura por rota; não anunciar Auto nem confiança implícita.
- Registro recebido pode só repetir configuração → conservar proveniência e distinguir pedido de runtime; ausência reprova gate.
- Remover CLI externa reduz caminhos disponíveis → consequência deliberada do escopo; o operador vê a limitação e a etapa permanece pendente.

## Migration Plan

Após T7 e T8, implementar adapter, verificação de evidências e ensaios; atualizar apenas documentação Codex e referências operacionais afetadas. Revisar e completar no nucleus o delta do bootstrap; distribuir cópias verificadas e manifesto pelo processo existente, mantendo o pin-base v1.1.22 até publicação autorizada. Não editar instalação da conta, registrar confiança ou anunciar novo pin automaticamente; não duplicar lei em stubs. Ativar capacidades por qualificação íntegra de schema/superfície e preflight atual; uma versão nova compatível não exige recusa só pelo número, nem autoriza copiar sucesso entre superfícies. Agentes já vivos permanecem associados à captura original. Rollback de código conserva evidências, capturas e agentes vivos; não torna permissões mais amplas nem autoriza caminho externo automaticamente. Sem deploy de produto neste card.

## Open Questions

Não há decisão de produto pendente: caminho nativo ou recusa. Permanecem capacidades a ensaiar: refinamento interativo completo, regressão exec, ensaio completo do critério operacional de contexto revisado, vínculo Guard/worktree em escrita autorizada e recusada, controle read-only no mesmo chat e interface do operador. App/IDE via app-server exigem descobrir fonte verificável, schema e capacidades reais, adaptar o driver quando possível e registrar a garantia específica ausente quando não for. Nenhuma dessas lacunas sai do escopo: mantém tarefa e etapa dependentes bloqueadas; recusa correta não vale como positivo exigido nem como substituição integral concluída.

## Prototype

N/A — nenhuma tela Cripto é alterada; não há HTML gerado ou copiado nem rota emprestada.

## Impeccable

- P3 — disposition: N/A; justificativa: mudança de processo operacional sem interface do produto; preservados Design, crítica independente e T7 humano.
- verdict: N/A para protótipo/UI; crítica independente ainda pendente.

## Design Critique

- P0–P2: nenhum achado novo na crítica independente da revisão automática em 17/10/2026.
- P3 — disposition: aceito para Apply; implementar e qualificar coordenação dedicada, bindings, perfis nomeados e provas previstas nas tarefas pendentes. Snapshot: `.impeccable/critique/card-1098-codex-agentes-nativos-review-automatico-20261017.md`.
- verdict: contrato revisado consistente; nenhum rework necessário. Substitui a pendência de autoria/crítica registrada abaixo. Não concede T7 nem comprova implementação ou qualificação da sessão dedicada. Histórico anterior preservado.

- P1 — disposition: reabertura solicitada por Alan em 17/10/2026 após ensaio real; o fluxo exige alternância manual de permissões, incompatível com o requisito operacional agora explícito. Alan escolheu revisão automática em sessão dedicada nativa somente leitura, com dois revisores e provas preservadas. Esta nota registra a mudança de requisito, não uma nova crítica independente nem implementação.
- verdict: aprovação anterior precisa ser revalidada para o contrato revisado; autoria e crítica da sessão dedicada pendentes. Preservar implementação e evidências anteriores, sem promover diagnóstico a revisão de produto.

- P0–P2: nenhum achado novo na retomada do crítico sobre a opção 2 em 17/10/2026.
- P3 — disposition: aceito para Apply; implementar e verificar o conjunto contrato/chamada/ensaio conforme tasks pendentes. Snapshot da revisão: `.impeccable/critique/card-1098-codex-agentes-nativos-opcao2-20261017.md`.
- verdict: opção 2 consistente; nenhum rework necessário. Não concede T7 nem comprova qualificação ou implementação. Os bullets seguintes preservam a crítica histórica anterior à opção 2.

- P0–P2: nenhum achado na crítica independente de 17/10/2026.
- P3 — disposition: aceito para Apply; barreira diagnóstica, normalização de caminhos e coleta read-only permanecem sujeitos aos ensaios exigidos.
- P3 — disposition: histórico substituído; o parecer de 13/10 avaliou briefing anterior e segue preservado no snapshot histórico. O novo snapshot é `.impeccable/critique/card-1098-codex-agentes-nativos-20261017.md`.
- P3 — disposition: evidência operacional verificada para esta autoria e crítica; ambos os filhos nativos retornaram com modelo/esforço observados correspondentes à captura, vínculo ao #1098 e payload completo. Essa prova não certifica app/IDE, revisão read-only ou substituição integral.
- verdict: proposta adequada; nenhum rework necessário. Não comprova substituição integral nem concede T7. Aprovação de Design permanece exclusiva de Alan.

## Decisão de recorte registrada em 18/10/2026 (revalidação pendente)

Alan escolheu “Concluir CLI e separar os ensaios restantes”. O seguimento [#1128](https://github.com/oalansilva/crypto/issues/1128), confirmado Em Refinamento pelo pai, recebe 5.5/5.6/5.8, as partes multissuperfície de 5.1/5.7 e as rotas de 6.3 com principal exec independente/App/IDE. #1098 conserva CLI interativa → coordenador exec, 3.3, 5.1–5.4/5.7 dessa rota, 6.3 CLI e QA. Decisão registrada no [comentário do #1098](https://github.com/oalansilva/crypto/issues/1098#issuecomment-6244962285). Esta nota registra o fato informado pelo pai; não reescreve specs/tasks, não declara T7 nem aprova o novo recorte. O pai fará a revalidação de escopo pela FSM e delegará a atualização dos artefatos antes da aplicação humana do candidato.

</details>
