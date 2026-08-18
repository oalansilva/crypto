## Context

O gate de Design exige autoria atribuível ao `design-planner`, execução runtime observável e critics sem capacidade de mutação. O contrato precisa usar somente fatos expostos pelo OpenCode `1.18.18`, falhar fechado em lifecycle incompleto e declarar honestamente o limite de confiança da evidência produzida no mesmo processo.

**UI impact: none** — a change altera exclusivamente contrato de agentes, plugin dedicado, custom tools, helper Linux, evidência e testes do host OpenCode. Não cria, remove nem modifica tela, componente, rota ou interação do produto.

### Problema

Prompt, configuração declarada e relato do agente não provam autoria, variante efetiva, isolamento dos critics nem correspondência entre alterações e chamadas autorizadas. Hooks observam tools dentro de um processo OpenCode, mas não formam um attestor externo e não controlam outro processo ou o usuário do sistema operacional.

### Hipótese

Se um processo OpenCode novo carregar componentes cujo `build_id` pré-build e bytes reais conferem com um `deployment-manifest.json` externo pós-build, vincular manifests single-use a child sessions e mensagens reais, limitar o author a um writer mediado por helper Linux, executar critics zero-tool com outputs estruturados e reconciliar journal, runtime DB, eventos e artefatos, então o gate pode rejeitar deterministicamente qualquer execução não demonstrada dentro desse limite de confiança.

### Resultado esperado

- Os quatro grupos (`proposal.md`, `specs/**`, `design.md`, `tasks.md`) e protótipos enumerados, quando houver, são escritos por child author vinculado.
- Author e critics têm agent e model observados; `high` precisa ser provado pela fixture runtime, não inferido de configuração.
- Assessment A/B usam child sessions distintas, packet idêntico, zero tools e schema estruturado obrigatório.
- Toda diferença persistente entre baseline e final é explicada por uma chamada autorizada de `design_artifact_write`.
- P0/P1 permanece bloqueante até recheck estruturado no mesmo lineage marcar o finding como `resolved` contra novo digest.
- Evidência é correlacionável e exportável para CI, mas não é autoridade de workflow nem prova contra o mesmo usuário do SO.

## Runtime Capability Map (OpenCode 1.18.18)

Este design se limita aos fatos já registrados para o runtime instalado:

- versão suportada: **exatamente `1.18.18`**;
- `AgentConfig` aceita `variant`, mas a execução atual de #550 observou variant/default e **não comprovou `high`**;
- o perfil atual fixa `model: openai/gpt-5.6-sol` e possui provider option `reasoningEffort: high`; isso não substitui evidência runtime de variant;
- `permission` aceita regras top-level/action e keys de tools/custom tools; a última regra correspondente vence;
- `edit` cobre `write`, `edit` e `apply_patch`;
- `chat.message` expõe session, agent, provider/model e variant; seu input aceita `messageID?`, que o adapter deve testar e correlacionar com a mensagem de input prealocada;
- `session.created` expõe `Session.id`, `parentID`, version e time;
- o SDK `client.session.create` aceita `body.parentID`, `body.title` e `query.directory`, e retorna a `Session` com ID;
- `client.session.prompt`/`promptAsync` aceita o ID no path e `body.agent`, `body.model`, `body.messageID?`, `body.parts` e `body.tools?`;
- variant vem do profile do agent e é observada em `chat.message`, não é argumento confiável de spawn;
- `tool.execute.before/after` expõe tool, `sessionID`, `callID` e args;
- o contexto da custom tool expõe `sessionID`, `messageID`, agent, directory e worktree;
- não existe `task_invocation_id` nem API documentada para suspender child antes da primeira mensagem;
- os hooks observam tools do mesmo processo; não interceptam edições de outro processo ou do usuário do SO.

Versão, schema, campo ou capability ausente/desconhecida produz `BLOCKED`. Similaridade de versão, hash atual de arquivo ou opção de configuração não substitui fato runtime.

## Goals

1. Tornar o planner designado o author canônico sem acesso geral ao filesystem.
2. Comprovar `openai/gpt-5.6-sol` e variant runtime `high` no author e nos dois critics após implementação.
3. Usar somente parent session, child session, message, call, nonces e digests observáveis.
4. Mediar tools do mesmo processo durante um stage lease e reconciliar diferenças persistentes.
5. Calcular síntese/verdict deterministicamente sem permitir reclassificação pelo author.
6. Ativar candidates e aliases canônicos por cutover quiescente entre processos novos.

## Non-Goals and Trust Boundary

- Não alterar defaults Flash/Pro, `small_model`, Hermes, `/opsx:apply`, `/opsx:verify`, workflow DB ou o attestor externo planejado em #555.
- Não dar ao planner acesso a Git, GitHub, board, serviços, banco, código de produção, rede ou delegação.
- Não usar evidência técnica como aprovação humana.
- Não alegar proteção tamper-proof contra o mesmo usuário, administrador ou outro processo do SO.

Escopo positivo fechado: guard dedicado, `design_artifact_write`, `design_spawn_stage`, `design_openspec_readonly`, native writer helper, readonly OpenSpec runner/adapter, schema/evidence e testes diretos. General plugins, defaults, #555, apply/verify e Hermes permanecem fora.

### Limite de confiança explícito

Para #550, o TCB é fechado e enumerado: (1) o processo OpenCode `1.18.18`; (2) a instância carregada do módulo `design-gate-guard`; (3) cada processo do native writer helper exato lançado pelo guard; e (4) cada processo do readonly OpenSpec runner exato lançado pelo guard. Para cada componente/invocação, a evidence registra PID, PPID, executable absoluto, digest real do executable/build, `build_id`, `module_instance_id`, protocol version e exit/result; o run registra também o `deployment_manifest_sha256` externo usado pelo verifier. Main, model e tools são sujeitos observados e restringidos, não componentes implícitos do TCB. Todo processo não enumerado permanece fora do TCB.

Owner-only permissions, sidecar e hash-chain detectam corrupção acidental, gaps e inconsistências de correlação; não impedem fabricação deliberada pelo mesmo usuário. Tampering pelo mesmo usuário ou por administrador permanece explicitamente fora do threat model. O verifier read-only de CI compara runtime DB, journal/eventos e artefatos e rejeita reconstrução, mas seu resultado é apenas exportável: não é autoridade para transição de workflow. #555 deverá prover attestation externa.

## Decisions and Alternatives

### D1. Plugin dedicado, tools enumeradas e packets completos

Será criado um plugin project-local dedicado, `design-gate-guard.ts`, sem ampliar plugins gerais. O primeiro author será `design-planner-candidate-v1`, `mode: subagent`, `model: openai/gpt-5.6-sol`; a implementação configurará `variant: high`, cuja efetividade será exigida na fixture independente.

A política efetiva usa broad deny primeiro e allow final apenas para `design_artifact_write`. O author não recebe `read`, `glob`, `grep`, `bash`, `task`, web/network, `edit`, `skill`, custom/MCP desconhecida ou qualquer outra tool. Sources, templates e instructions entram como bytes no packet; o author não depende de read tool.

O critic `design-critic-readonly-candidate-v1` também será Sol/high e terá zero tools. Um perfil author gravável nunca atua como critic apenas por instrução textual.

A main recebe somente as custom tools enumeradas `design_spawn_stage` e `design_openspec_readonly`, cada uma limitada à sua fase. Durante lease, qualquer tool/custom/MCP não enumerada é negada para toda sessão, respeitadas as capacidades específicas por papel. O native writer helper e o readonly OpenSpec runner não são tools do model: são executáveis exatos lançados pelo guard.

### D2. Manifest pre-spawn, packet completo e spawn SDK bound

Antes do spawn, o guard cria manifest com `run_id`, nonce criptograficamente único e single-use, stage, bytes/digests, paths exatos, artefatos esperados, agent/model/variant esperados, parent session, worktree, versão, `build_id`, `deployment_manifest_sha256` e config digests. O prompt contém o marker estruturado **e os bytes canônicos completos do packet**, em envelope determinístico (por exemplo, base64 com encoding e comprimento explícitos) ou text parts determinísticos:

```text
<design-gate manifest_nonce="..." manifest_sha256="..." packet_sha256="..." />
<design-packet encoding="base64" byte_length="...">...</design-packet>
```

O plugin hasheia os input-message parts reais observados em `chat.message`, decodifica/recompõe os bytes canônicos e exige igualdade com `packet_sha256` e com o manifest. Referência de path ou marker sem os bytes não é packet válido.

`design_spawn_stage` é custom tool main-only e a única operação de spawn autorizada pelo lease. Ela valida lease `CREATED`, parent session, manifest e directory; prealoca um UUID criptograficamente único como `input_message_id`; chama sem shell `client.session.create({ body: { parentID, title }, query: { directory } })`; registra o child ID retornado; e então chama `client.session.prompt` ou `promptAsync` com esse ID e `body.messageID = input_message_id`, `body.agent`, `body.model` e `body.parts` exatamente selados. Ela omite `body.tools`: não há override de tools, sobretudo nenhum que amplie o profile. O author/critic continua com `task: deny`, e main não usa Task durante o lease. Variant vem do profile candidate e é verificada no primeiro `chat.message`. Create/prompt vazio, erro, ID divergente ou qualquer mismatch finaliza `ABORTED/BLOCKED`.

Fluxo observado e binding em duas fases:

1. `session.created` registra child, `parentID`, version e time.
2. O input de `chat.message` do child só cria binding provisório quando seu `messageID` opcional está presente e é exatamente o `input_message_id` prealocado; session, agent, provider/model, variant, marker e packet bytes também precisam conferir. Ausência ou mismatch bloqueia o binding provisório.
3. Para author, `ToolContext.messageID` é denominado `assistant_message_id` somente depois que um adapter test de `1.18.18` comprovar essa semântica. Antes de qualquer ação de filesystem, o plugin consulta o registro runtime `AssistantMessage` correspondente e exige `sessionID` igual ao child, `parentID == input_message_id` e a correlação única do `callID`/`operation_nonce`; o marker e packet selados são verificados nos parts da mensagem de input. Sem essa semântica ou correlação, bloqueia.
4. Para critic zero-tool, após completion o adapter exige um único output `AssistantMessage` e seus parts/hashes/result, com `sessionID` igual ao child e `parentID == input_message_id`. Ausência, ambiguidade ou parent divergente bloqueia.
5. Em sucesso, consome o manifest nonce e vincula manifest, parent, child, `input_message_id` e `assistant_message_id`. Reuso ou mismatch em qualquer fase bloqueia.

Não há child suspenso, child ID pre-spawn ou `task_invocation_id`. `input_message_id` nunca é confundido com o ID da mensagem assistant/tool.

### D3. `build_id` pré-build e deployment manifest externo pós-build

Antes de qualquer compilação, o build pipeline escolhe um `build_id` independente dos outputs finais: UUID aleatório ou `commit+nonce` em formato canônico. O mesmo `build_id` e a protocol version são embutidos no guard, native writer helper e readonly runner. O `build_id` não é derivado de hash final nem de conteúdo que o contenha.

Somente depois de todos os builds, o pipeline gera `deployment-manifest.json` canônico contendo `build_id`, OpenCode version/digest, OpenSpec executable version/digest e hashes reais finais dos agent files, guard build, native writer helper, readonly runner/adapter e schema/config. Em seguida calcula `deployment_manifest_sha256` sobre esses bytes. Esse hash pós-build **não** é embutido em nenhum binário ou módulo.

O run manifest referencia `build_id` e `deployment_manifest_sha256` e inclui `run_id`, stage, manifest nonce, parent, worktree, exact paths, expected agent/model/variant, source bytes, packet digest, candidate profile digest, schema/config digest, OpenCode/OpenSpec versions e os seguintes fatos do TCB:

- PID e PPID;
- executable absoluto e seu digest real;
- `process_started_at`;
- module instance ID aleatório por load;
- `build_id`, `module_instance_id` e protocol version;
- exit/result terminal de cada helper/runner;
- session created/message times posteriores ao início do processo.

Cada componente runtime reporta `build_id` e `module_instance_id`. O verifier lê o `deployment-manifest.json` externo, confirma seu `deployment_manifest_sha256`, hasheia os bytes reais finais carregados/executados e exige igualdade com os hashes do manifest e com o `build_id` reportado/manifestado. File/manifest mismatch, `build_id` divergente, hash pós-build embutido ou hash solto do arquivo atualmente em disco bloqueia; este último não prova o módulo carregado.

Critics usam `exact_write_paths: []`. Instrução textual nunca amplia manifest ou permission.

### D4. `callID`, `operation_nonce` e writer single-flight

`design_artifact_write` exige `manifest_nonce`, `manifest_sha256`, `operation_nonce` single-use, `exact_path`, `base_sha256` e exatamente uma operação data-only:

- `full_content`: bytes completos com encoding explícito; ou
- `safe_patch`: replacements por byte range, ordenados, não sobrepostos, com digest dos bytes antigos e bytes novos.

No `tool.execute.before`, o guard valida o lease/binding e registra exatamente um mapping `(sessionID, operation_nonce, argsHash) -> callID`. Há no máximo uma chamada in-flight por session/manifest. Reuso de operation nonce, paralelismo, mapping ausente ou múltiplo e args divergentes bloqueiam o run.

No início da custom tool, antes de qualquer ação de filesystem, o contexto valida `sessionID`, agent, directory e worktree. `ToolContext.messageID` só é aceito como `assistant_message_id` após adapter test; o plugin consulta o `AssistantMessage` runtime e exige child `sessionID`, `parentID == input_message_id` e correlação única com o mapping de `callID`/`operation_nonce`. Depois valida marker/packet nos parts do input, finaliza o binding provisório e consome atomicamente o mapping; nonce/mapping consumido nunca é reutilizado, inclusive após falha. A tool não aceita `callID` declarado pelo model.

### D5. Helper Linux dedicado para filesystem

A escrita é executada por helper Linux dedicado, versionado e hashado, invocado pelo plugin por caminho absoluto com `shell: false`, argv fixo e protocolo binário/JSON canônico via stdin. O helper não aceita command strings, executable alternativo, shell syntax ou path fora do request já autorizado.

O helper usa APIs Linux nativas, não uma suposição de API TypeScript. Cada invocação registra os campos de identidade/result do TCB definidos em D3:

1. feature probe obrigatório de kernel, syscall e versão/build do helper;
2. abertura da worktree/parents via dirfd e `openat2` com `RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS`;
3. validação de owner, regular file, link count 1 e base digest;
4. temp no mesmo parent com `O_CREAT|O_EXCL|O_NOFOLLOW`, escrita completa, `fstat` e `fsync`;
5. revalidação do destino/base, instalação com `renameat2` quando disponível ou `renameat` sob as precondições testadas;
6. `fsync` do diretório e retorno estruturado de before/after digest.

Kernel/syscall/helper/build mismatch, ausência dos flags requeridos ou falha de probe é `BLOCKED`; não há fallback para resolução de path em TypeScript.

### D6. Lease state machine e recovery fail-closed

Cada run possui lease persistido com `run_id`, `owner` (OpenCode PID + module instance ID), `deadline`, manifest nonce e estado:

```text
CREATED -> BOUND -> FINALIZING -> CLOSED
                           \----> ABORTED
CREATED/BOUND -------------> ABORTED
```

- `CREATED`: journal e baseline duráveis; `design_spawn_stage` ainda pode criar exatamente um child. O input `chat.message` com `messageID == input_message_id` pode registrar binding provisório sem mudar a exigência de finalização.
- `BOUND`: child, input e assistant message finalizados pelo primeiro writer call do author ou pela correlação pós-completion do critic; tools permitidas conforme papel.
- `FINALIZING`: novas operações negadas; verifier reconcilia calls, DB/eventos e artefatos.
- `CLOSED`: journal finalizado com resultado terminal; lease pode ser liberado.
- `ABORTED`: journal finalizado com `BLOCKED`, motivo e cleanup; lease pode ser liberado.

Empty spawn, denial, crash observado, deadline, evidence failure ou qualquer mismatch inicia finalização para `ABORTED/BLOCKED`. Recovery no startup procura leases cujo owner não corresponde ao processo vivo/module instance, deadline expirou ou journal não é terminal; reconcilia fail-closed, anexa registro de recovery, finaliza `ABORTED`, fsynca journal/evidence e **só depois** libera o lease. Manifest e operation nonces são tombstoned e nunca reutilizados. Lease órfão que não possa ser reconciliado impede novos Design runs.

### D7. Escopo real da proteção concorrente

Durante lease, o guard aplica broad deny a toda tool nativa, custom tool e MCP desconhecida no **mesmo processo OpenCode**. Só permite por papel:

- author vinculado: `design_artifact_write`;
- main vinculada em `CREATED`: `design_spawn_stage`, single-use;
- main/helper vinculada na fase read-only: `design_openspec_readonly`;
- critics: nenhuma tool;
- qualquer outra sessão: nenhuma tool durante o lease.

O próprio author/critic mantém `task: deny`; main não usa Task durante o lease. Toda criação de child fora de `design_spawn_stage` é violação, mesmo que use a API nativa por outro caminho.

A garantia cobre o processo OpenCode e as tools que ele observa. Outro processo/usuário do SO está fora do threat model. O inventário baseline/final detecta diferença persistente sem call; não se alega detectar edição transitória externa restaurada antes da observação.

Operação exige staging worktree dedicada, sem outros agentes/processos de automação, e freeze humano documentado durante candidate/canonical validation. Isso reduz concorrência externa, mas não amplia a trust boundary.

### D8. OpenSpec read-only sem Bash

Não existe exceção de Bash. `design_openspec_readonly` aceita somente enum `status|instructions|validate`, parâmetros estruturados por schema e change/cwd canônicos. O plugin invoca executable OpenSpec absoluto, previamente validado contra `deployment-manifest.json`, com `shell: false`, argv construído sem concatenação e ambiente mínimo fixo. Cada processo registra PID, PPID, executable absoluto, digest real, `build_id`, `module_instance_id`, protocol version e exit/result. A tool rejeita subcomando, flag, cwd, env ou executable não enumerado e não aceita command strings.

Author e critics não recebem essa tool. Resultado e exit status entram no journal.

### D9. Evidência process-trusted e verifier read-only

O adapter `1.18.18` correlaciona journal do plugin com session/message/parts no runtime DB. O host grava sob:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/opencode/design-gate/<worktree-digest>/<run-id>/
```

O diretório owner-only contém journal hash-chained, evidence JSON e sidecar SHA-256. A evidência inclui identidade completa do TCB, `build_id`, `deployment_manifest_sha256`, bytes do deployment manifest externo, digests reais dos builds/executables, module instances, protocol versions, manifests/nonces, leases, bindings provisórios/finais, tool mappings, outputs, baseline/final, checks, exits/results e verdict.

Um verifier read-only de CI compara os bytes do journal, runtime DB/eventos e artefatos. Reconstrução pela main não é aceita pelo verifier; contudo, dentro da boundary declarada, o processo/plugin é trusted e o mesmo usuário do SO poderia fabricar os três lados. Portanto a evidência pode ser transportada, mas não promove workflow automaticamente e não é chamada de tamper-proof.

### D10. Findings estruturados, lineage e verdict determinístico

Assessment A/B retornam **somente** UTF-8 JSON canônico que valida contra schema versionado. Cada finding contém obrigatoriamente:

```json
{
  "finding_id": "A-R0-P1-001",
  "severity": "P0|P1|P2",
  "source_digest": "sha256:<normative_digest>",
  "summary": "texto",
  "disposition_required": true
}
```

O envelope inclui `schema`, `assessment`, `lineage_id`, `round`, `source_digest` e `findings`. IDs são únicos e imutáveis dentro do lineage. O guard preserva e hasheia os bytes integrais do output; o helper apenas valida/parsa esses mesmos bytes, sem redigir, resumir, ordenar novamente, omitir ou reclassificar.

Antes do spawn, o manifest pre-atribui **todo finding P0/P1 herdado a ambos A e B**; esta versão não possui applicability variável. Um recheck no mesmo `lineage_id` usa novo `source_digest` e registros estruturados `resolutions`, cada um com `finding_id` anterior, `prior_source_digest`, `source_digest` novo e `disposition: resolved|open`. Um finding herdado só é `resolved` quando **A e B** retornam structured `resolved` para o mesmo `finding_id`, mesmo lineage e mesmo novo normative digest, e o ID existe no ancestry. Omissão, conflito, unknown/duplicate ID, digest stale, lineage diferente ou `open` de qualquer critic vence conservadoramente e mantém `BLOCKED`.

O guard calcula verdict por regra fixa após validar os payloads e aplicar o merge conservador: qualquer P0/P1 introduzido ou herdado sem dupla resolução válida no digest atual => `BLOCKED`; P2 não bloqueia, mas permanece listado. Nenhum author escolhe verdict.

O guard/helper produz `generated_block_bytes` contendo, sem alterar bytes, os payloads A/B, seus hashes, lineage/resolutions, merge conservador e o verdict calculado. O author de síntese pode apenas substituir o intervalo entre os markers pelos `generated_block_bytes` recebidos e deve gravá-los verbatim. O verifier exige igualdade byte-a-byte. O author não classifica, omite, reordena ou edita findings/dispositions/verdict.

`normative_digest` usa proposal bytes; design bytes com o intervalo gerado substituído por token fixo; specs ordenadas por path+bytes; e tasks bytes. Atualização somente do bloco não muda o digest; qualquer outro byte exige novo digest e recheck.

### D11. Correções adicionais autorizadas por decisão humana

O limite automático anterior foi atingido após a correction round 2. Alan autorizou explicitamente a **correction round 3** em chat e no comentário [#550 issuecomment-5305576566](https://github.com/oalansilva/crypto/issues/550#issuecomment-5305576566). A/B resolveram no recheck dessa rodada os quatro P1 herdados e abriram `A-R3-P1-001`, `B-R3-P1-001` e `B-R3-P1-002`.

Após responder `continue`, Alan autorizou a correção final direcionada desses novos P1 no comentário [#550 issuecomment-5307214677](https://github.com/oalansilva/crypto/issues/550#issuecomment-5307214677). Essa decisão permite somente esta alteração normativa e o próximo recheck no mesmo lineage; não resolve findings, não concede `PASS` e não aprova o Design. Antes do próximo spawn, os três IDs são pre-atribuídos a ambos A e B. Se qualquer P1 permanecer, for omitido, conflitar ou surgir, o Design permanece `BLOCKED` para nova decisão humana.

### D12. Cutover quiescente, processo novo e rollback

Não se usa “transação atômica de filesystem”. Candidate validation ocorre em processo OpenCode separado e worktree candidate dedicada. Para ativação canônica:

1. bloquear novos Design runs e registrar freeze;
2. encerrar normalmente ou abortar/reconciliar todos os leases;
3. parar o processo OpenCode;
4. aplicar um único commit/build completo com profiles, plugin, helper, schema e tests coerentes;
5. validar offline schema/config, `build_id`, bytes do `deployment-manifest.json` e seu `deployment_manifest_sha256`;
6. iniciar processo OpenCode novo;
7. registrar PID/PPID, executable absoluto, digest real, `process_started_at`, `build_id`, module instance ID, `deployment_manifest_sha256`, protocol version e exit/result aplicável;
8. rodar toda a matriz canônica em sessions criadas depois desse process start.

Candidate success não ativa aliases. Só a matriz canônica no novo processo após o commit autoriza aceitação técnica.

Rollback também bloqueia runs, finaliza/aborta leases, para o processo, restaura commit/build e deployment manifest anteriores completos, valida offline e inicia outro processo. Os gates afetados permanecem `BLOCKED`; journals são preservados e não há fallback de modelo.

### D13. Bootstrap transitório honesto de #550

Nesta revisão, o planner atual tem model exato `openai/gpt-5.6-sol` e provider option `reasoningEffort: high`, porém variant runtime `high` não foi comprovada e foi observada como default. Esta é precisamente a falha que #550 corrige. A exceção transitória permite concluir a revisão Design sob a regra vigente; não satisfaz aceite técnico e não autoriza configurar runtime agora.

Após implementação, fixture independente deverá provar variant `high` para candidate e canonical em processos novos. O Git before/after histórico foi concluído: `proposal.md` `de8a7bee...`, design pré-recheck `c1a74c93...` e spec `9a4f870f...` permaneceram idênticos, com zero critic edits. Esses hashes provam somente a não mutação daquela rodada anterior; a correction round 3 já alterou design/spec e esta correção final direcionada volta a alterar os bytes normativos, exigindo novo digest/recheck.

## Capability Matrix

| Capability | Main/helper no lease | Candidate author | Candidate critic A/B | Guard/helper/verifier |
| --- | --- | --- | --- | --- |
| Manifest/packet | solicita fluxo enumerado | deny | deny | cria/valida |
| `design_spawn_stage` | única spawn em `CREATED` | deny | deny | SDK create/prompt e child ID |
| Filesystem geral | deny | deny | deny | helper Linux scoped |
| `design_artifact_write` | deny | única tool/exact path | deny | medeia |
| `design_openspec_readonly` | enum estruturado | deny | deny | medeia |
| Native/custom/MCP desconhecida | deny | deny | deny | intercepta no processo |
| Bash/process arbitrário | deny | deny | deny | helper usa spawn absoluto/shell false |
| Runtime DB | deny | deny | deny | read-only verifier |
| Outro processo/OS user | fora do threat model | fora | fora | não controla |
| Aprovação humana | deny | deny | deny | deny |

## Acceptance and Validation Strategy

### Positive fixture

1. Candidate author produz os quatro grupos em ordem com calls vinculadas e operation nonces single-use.
2. Helper Linux passa feature probe e exerce full write/safe patch via `openat2`, rename e fsync.
3. Lease percorre `CREATED -> BOUND -> FINALIZING -> CLOSED`; recovery fecha fixture órfã em `ABORTED` antes de liberar.
4. A/B têm sessions distintas criadas apenas por `design_spawn_stage`, packet bytes/digest idênticos, zero tools, JSON estruturado e Sol/high observado.
5. Guard pre-atribui todo P0/P1 a A e B, preserva output bytes, aplica merge conservador, produz bloco byte-identical e calcula verdict por lineage.
6. CI verifier read-only compara DB/event, journal e artefatos.
7. Candidate passa em processo/worktree separado; cutover quiescente instala commit completo e canonical passa em processo novo.

### Negative fixture

- runtime/schema/config/build/deployment-manifest/executable digest divergente, TCB/process fact ausente ou session anterior ao novo processo;
- variant default/mismatch;
- spawn fora de `design_spawn_stage`, Task durante lease, create/prompt/child mismatch ou tool override que amplie profile;
- marker sem packet bytes, parts/hash/packet divergentes, `input_message_id` ausente/divergente, `ToolContext.messageID` sem semântica comprovada de assistant, `AssistantMessage.parentID` divergente, nonce ausente/reusado, binding provisório/final ambíguo, `operation_nonce` repetido, calls paralelas ou mapping ambíguo;
- author/critic/main solicita tool não enumerada, custom/MCP desconhecida ou Bash;
- readonly tool recebe command string, argv/cwd/env/executable divergente;
- helper/kernel/syscall/feature probe incompatível, traversal, symlink, stale base, inode inseguro, rename/fsync failure;
- empty/denial/crash/evidence failure não finaliza `ABORTED` antes de release, ou orphan não reconciliado;
- diff persistente sem call (sem alegar detecção de edição transitória externa restaurada);
- A/B com schema/bytes/hash/digest/lineage inválido, finding omitido/reclassificado, unknown ID, conflito, `open` de qualquer critic ou resolução sem ancestry/dupla concordância;
- author altera um byte do generated block ou verdict;
- P0/P1 aberto após recheck final;
- cutover com processo ativo, leases abertos, build/deployment manifest parcial, processo reutilizado ou rollback sem stop;
- main reconstrói evidence para substituir bytes rejeitados pelo verifier.

Todos os negativos geram evidence ref quando disponível e `BLOCKED`.

### Validações deste artefato

- `openspec validate card-550-design-planner-contract`
- `git diff --check`

Esses comandos validam forma/whitespace; não substituem fixtures runtime nem o novo A/B. O Git before/after já concluído prova somente a rodada anterior e será repetido para o próximo recheck.

## Risks and Mitigations

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Config diz high, runtime usa default | Evidência falsa | Processo novo + variant observado + fixture independente |
| Race/symlink escape | Escrita fora do path | Helper Linux hashado, openat2/dirfd, feature probe, rename/fsync |
| callID ambíguo | Autoria indevida | operation nonce single-use, argsHash mapping e single-flight |
| Crash deixa lease órfão | Gate preso ou reaberto indevidamente | FSM durável, recovery ABORTED antes de release, nonce tombstone |
| Tool não classificada | Escape dentro do processo | Broad deny para toda native/custom/MCP não enumerada |
| Outro processo altera arquivo | Limite não coberto | Trust boundary explícita, worktree dedicada/freeze e diff persistente |
| Mesmo usuário fabrica evidence | Confiança excessiva | Não alegar tamper-proof; CI correlation + #555 externo |
| Author suaviza critique | P1 omitido | Outputs byte-preserved, schema, lineage, bloco/verdict gerados |
| Hot reload/file hash confundido com módulo carregado | Build errado aceito | `build_id` pré-build + deployment manifest pós-build + PID/PPID/executable/digest real/module instance |
| Cutover parcial | Perfis incoerentes | Stop, commit/build e deployment manifest completos, offline checks, processo novo |
| P1 restante após correção humana 3 | Design indevidamente liberado | Novo A/B no novo digest; qualquer P1/omissão/conflito mantém BLOCKED |

## Prototype

N/A — `UI impact: none`; não existe superfície visual ou interação de produto para prototipar.

## Prototype Validation

N/A — sem UI/protótipo, browser gate não se aplica. A validação relevante é de runtime, tools, filesystem, leases, evidence e processos novos.

## Impeccable Brief

N/A — mudança exclusivamente de contrato e infraestrutura OpenCode.

## Impeccable Critique

N/A — não há superfície visual; a crítica técnica independente está abaixo.

## Impeccable Audit

N/A — acessibilidade, responsividade, theming e performance visual não se aplicam.

## Impeccable Trace

N/A — não houve pipeline visual. A implementação produzirá evidence técnica process-trusted, não attestation externa.

## Design Critique

### Referência e bootstrap

- Change: `card-550-design-planner-contract`
- UI impact: none
- Prototype: N/A
- Handle A existente: `ses_ff76cec27ffelGg8Qa5qRdF8n8`
- Handle B existente: `ses_ff76cec00ffeyF4R2GBfrqEpfP`
- Runtime honesto: model Sol exato; `reasoningEffort: high` presente em provider option; variant runtime `high` não comprovada/observada default.
- Git before/after da rodada anterior: concluído; `proposal.md` `de8a7bee...`, design pré-recheck `c1a74c93...` e spec `9a4f870f...` permaneceram idênticos, com **zero critic edits**. Esses hashes provam apenas aquela rodada, não o próximo recheck após esta revisão normativa.
- Decisão humana anterior: Alan autorizou correction round 3 em chat e no comentário [#550 issuecomment-5305576566](https://github.com/oalansilva/crypto/issues/550#issuecomment-5305576566).
- Resultado do recheck round 3: A e B resolveram os quatro P1 herdados e abriram três novos findings P1.
- Decisão humana atual: após `continue`, Alan autorizou a correção final direcionada no comentário [#550 issuecomment-5307214677](https://github.com/oalansilva/crypto/issues/550#issuecomment-5307214677). Esta correção não aprova o Design.

<!-- BEGIN GENERATED DESIGN CRITIQUE EVIDENCE -->
### Round 4 — recheck A/B final

- Source digest combinado: `697ad556a3a0ec60bca6fe4df767a4d7740da8a4dd1524b7c7b313fc73ec7f05`.
- Assessment A: `ses_ff76cec27ffelGg8Qa5qRdF8n8`.
- Assessment B: `ses_ff76cec00ffeyF4R2GBfrqEpfP`.
- No mesmo lineage e contra o mesmo source digest, **ambos** os assessments resolveram `A-R3-P1-001`, `B-R3-P1-001` e `B-R3-P1-002`.
- Findings novos de A: `[]`.
- Findings novos de B: `[]`.
- P0 open: **zero**.
- P1 open: **zero**.
- Git before/after desta rodada permaneceu idêntico, com **zero critic edits**: `proposal.md` `de8a7bee...`, `design.md` `d9fd5894...` e spec `466d8733...`.
- UI impact: none. Prototype: `N/A`. Prototype Validation: `N/A`. Impeccable Brief/Critique/Audit/Trace: `N/A`.

### Alcance do PASS de Design

Este `PASS` é transitório e conclui somente a crítica do gate de Design para o material avaliado na round 4. Não constitui aceite técnico, não comprova implementação e não substitui aprovação humana. A implementação futura ainda deverá provar, em processos novos, os perfis candidates e aliases canonical, a variant runtime `high` do Sol, critics zero-tool e o funcionamento do guard, helper e evidence; depois, continuará sujeita à aprovação humana obrigatória.

**Design Agent verdict: PASS**
<!-- END GENERATED DESIGN CRITIQUE EVIDENCE -->
