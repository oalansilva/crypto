# #1130 — implementação do candidato e limites factuais

O delta foi preparado em candidato inativo derivado do nucleus. A ativação não ocorreu: adapter, manifesto e trust ativos permanecem íntegros. A matriz de aceitação mantém pendências vivas por rota/etapa, impedindo alegação de fluxo integral. Este relatório não é Review, QA ou prova de publicação.

## Delta concreto

O pacote tem 16 arquivos distribuíveis: cinco módulos de execução (incluindo delta em `codex_evidence.py`), cinco arquivos novos de testes, installer, skill canônica e quatro documentos. Ele implementa índice privado atômico de capacidade por superfície/schema; reabertura das fontes originais; descoberta explícita/índice/legado com recusa por conflito/corrupção/symlink; referência/identidade congeladas por nascimento; vínculo explícito de grill-card em source com Estado vivo revalidado; checkpoints TUI/exec, pergunta/resposta humana nativa e recuperação finita; preparo automático da cadeia read-only de Review com comandos nativos, persistência no principal, verify-wave e gate de checklist pré-commit; continuação dos contratos canônicos de correção, QA, T18 e release.

O controller não executa trabalho delegado nem eventos/Git/produção. Perguntas em exec retornam checkpoint e comando literal de retomada; só mensagem humana nativa do mesmo UUID, no root esperado, libera a ação. O helper não afirma capacidade de rebind automático não observada. Release verifica o pedido próprio e modelo/esforço observados da operação, recusa retunar o principal vivo e preserva os guards/overlay do fluxo canônico.

Origem: nucleus `/srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos`, HEAD `14aa9d6`, com delta #1098 não commitado preservado. Base consumidor `1a06caec`; pin continua `v1.1.22`. Esse HEAD nucleus sozinho não reproduz a base dirty; hashes de cada arquivo de origem/destino constam em `implementation/provenance-base.json` e `implementation/package.json`. Nenhuma nova tag/revisão foi presumida.

| Artefato | SHA-256 / verificação |
| --- | --- |
| `implementation/package.json`, após primeira correção P1 | `de599a368b2b2d8214906af0ec1d28690cff4701d576ac449db2c02fe6d7e5af` |
| `.cursor/tmp/card-1130-delivery/nucleus.patch` | `2e7047ed3346704dc5af394346ca7f7bb7e35c2aabf22651846784028a82efd3`, 110308 bytes, `git apply --check --whitespace=error` PASS na origem real |
| `.cursor/tmp/card-1130-delivery/consumer.patch` | `c6ae9c2bc30234701d602cd3b21d66b837d38a8ec9cdcad7eabf354571b1e8b4`, 114434 bytes, `git apply --check --whitespace=error` PASS no consumidor; exclui installer |
| Manifesto ativo, preservado | `3a90add2ddffa07963d28196b495e3ff435356a2d6a980c7e1a33d63dc28e0cb`; `adapter_manifest.py check --root .` PASS |
| `codex_evidence.py` ativo, preservado | `79fc746a254f64987c7aa3686584921a2df083f446e6376410075042a42d375e` |

Os patches gerados são privados e reproduzíveis por `implementation/build_package.py`; código/documentação candidatos e manifesto permanecem versionáveis, sem duplicar todo o conteúdo nos patches do próprio diff. `implementation/README.md` contém os comandos concretos de reprodução/entrega. O build verifica as bases e recusa sobrescrever origem alterada.

## Evidência viva, separada de fixtures

No runtime nativo deste filho (`codex-tui/0.163.0`, UUID `01a150a8-7727-7820-8bd0-3b7bd88ba0b3`), foram observados:

- Origem TUI original #1098 íntegra reaberta pelo novo verifier: `verified_reference`, exit0; attempt `d382e438-f456-48ba-b3fa-69ceefbdafc4`, evidence selo `19da10f07b0ea025e69f095af0789cd07a01ea11a1b6350c58e19765f740c551`.
- Destino vazio sem referência: `unverified` com `qualification_cause=qualification_reference_missing`, exit2, antes de qualquer filho/escrita/transição.
- Mesmo destino com origem explícita válida: capacidade verificada e recusa distinta `stage_capability_missing` por `context_isolation=unavailable`, exit2. Prova de outro chat não forneceu o contexto deste filho.
- Root solicitado source diferente do cwd nativo worktree: `worktree_mismatch`, exit2. `--root` não fez rebind.
- #1117 revalidado às 20:33:58Z por REST (title/body/state=open) e GraphQL pontual (oalansilva/project1, Em Refinamento, HTTP200, remaining4945). Nenhuma edição. A primeira leitura via `gh issue view` não seguiu a skill e foi preservada como ocorrência histórica; a base operacional foi corrigida pelas superfícies suportadas. #1128 também foi relido por REST.

Projeção privada R01–R05: `.cursor/tmp/card-1130-live-0afd3d4f9d103c13.json`, SHA-256 `8606d6eeb00f279e101e6790521228d23068c9f8a98d08352e72153c98bd170f`. Ela guarda seis referências de comandos nativos com ordinal/hash original, códigos e localizadores dos receipts, sem prompts, sentinelas ou controles. Não copia receipts nem cria qualificação atual. As fontes originais continuam sendo autoridade.

Os nascimentos Design autor/crítico #1130 já têm evidências verified. O pai informou a coleta do primeiro retorno deste mesmo Apply: `verified/completed`, observado `gpt-6.1-sol/high`. Esta continuação conserva captura/birth e requer recoleta após o novo retorno; `terminal_unavailable` enquanto ativa não invalida o snapshot histórico. #1098 comprova historicamente Review/QA TUI → exec no seu recorte, não principal exec independente, refinamento integral ou todas as sessões novas/retomadas. A [matriz](acceptance-matrix.md) conserva essas diferenças.

## Validação

A cópia descartável de testes foi montada a partir do nucleus e do candidato em `.cursor/tmp/card-1130-candidate-test`; o adapter ativo não foi substituído. Fixtures usam contas/rollouts/targets descartáveis e não qualificam o runtime invocador. Installer foi exercitado em alvo limpo, com manifests/digests e redescoberta das fontes controladas, sem confiança gravada. A tag `v1.2.0` dos fixtures não é publicação real.

Histórico anterior à primeira correção P1: primeira rodada 159 PASS; ampliada anterior 631 PASS e uma falha do teste que pressupunha que o último evento do journal ainda era o pacote, corrigido para selecionar o evento por tipo. Regressão ampliada então final: **639 PASS em 316,66s**, incluindo vínculos explícitos, seleção de release, installer limpo, evidence/context, Review/probe/session, process_event, release_closeout e checklist. Depois dos checkpoints antes de T3/T8/T11, suite focada do controller **16 PASS em 3,69s**, incluindo três casos novos que impedem nascimento antes do evento existente. Esses resultados não são reexecução dos bytes corrigidos posteriormente. Os quatro avisos são opções pytest não instaladas (`asyncio_mode` e opções de timeout); não houve teste pulado nessas execuções. As contagens se sobrepõem; não são 655 testes únicos.

`openspec validate card-1130-codex-cli-fluxo-completo --strict`: PASS, exit0. `git diff --check`: PASS nos arquivos rastreados; candidato é novo/untracked e sua validação efetiva inclui testes e os dois `git apply --check --whitespace=error`. Não foi rodado QA de produto nem release. Testes existentes de Review/probes, process_event, release_closeout e checklist são regressão de contrato, não novas provas vivas dessas etapas.

## Pendências e ações concretas

As tasks de ensaio vivo 3.4, 3.5, 4.3 e 4.4 permanecem abertas. Principal exec independente, novas sessões/retomadas nas duas raízes, refinamento pergunta/resposta/body e negativos de uma onda válida precisam de sessões/cards/etapas autorizados. Este filho não pode spawnar mais agentes, operar outro card no chat #1130 ou mover Status para fabricar esses ensaios. #1117 tem história estruturada e só deve ser grelhado no seu próprio chat quando explicitamente autorizado. Nenhuma prova foi movida ao #1128.

**Não há P0 de produto identificado. Implementação aplicável a precommit concluída; aceitação viva pendente, 19/26.** A continuação atual resolveu a dependência temporal pelo Design decisão 6 e pelo contrato de fases do checklist: 3.4/3.5/4.3/4.4 seguem abertas em after-pin porque a prova restante depende de exercitar o novo suporte instalado. [Resolução por tarefa](phase-resolution.md) registra os trabalhos pré-commit já feitos, o pré-requisito de cada ensaio e a fase mínima, sem adiamento genérico para QA. O [registro anterior](continuation-blockers.md) preserva a recusa correta quando essas linhas não tinham fase. Nenhuma fixture virou prova viva; T9 não está automaticamente liberado.

A procedência continua nucleus HEAD `14aa9d6` + base dirty #1098 por hash; aquele checkout não tem overlay de consumidor e seu binding #1130 não foi estabelecido. Não foi inventada uma tag, contexto autorizado ou autorização para repetir bootstrap histórico. Alterar adapter ativo exige revisão humana A/R e `/hooks` aplicável; este Apply não grava confiança nem contorna Guard/shim.

## Continuação: negativos reais e barreira de encerramento

Foram executadas seis consultas nativas adicionais sem alterar fontes: receipt Review #1098 expirado (`review_stage_status_expired`, exit1); digest esperado errado contra diff original preservado (exit2); Status vivo #1098 Homologado contra exigência Code Review (`review_stage_binding_mismatch`, exit1); preflight Review deste filho gravável (`parent_sandbox_mismatch`, exit2); extração em memória da QA interrompida #1098 (`child_interrupted`, exit1); extração deste turno Apply ainda ativo (`terminal_unavailable`, exit1). São negativos de escopos diferentes, não uma onda válida nova nem todas as recusas reviewer de 4.3.

Projeção privada `.cursor/tmp/card-1130-continuation-0a18a05b90ba19a4.json`, SHA-256 `967fd568f6100b3591224153bd74dddb575047488d70ae35769a0a051b972402`, guarda comandos nativos, ordinais e hashes originais, sem prompts/controles. Detalhes e limites em `continuation-blockers.md`. O digest do diff histórico permaneceu `f7e1f980d17baf219f290e7d2c9d81d75c76faa30d6595a6f232f7e12ec8a118`.

Readback adicional dos dois reviewers históricos #1098, somente ordinais 15/16: fontes e registros coincidem com hashes prévios; cada stdout nativo tem 65275 caracteres/JSON inválido e o retorno entregue 24105 caracteres/JSON inválido com rótulo de truncamento. Projeção privada `.cursor/tmp/card-1130-historical-delivery-readback.json`, SHA `65993f4a74d3b2be039962f07af85dcce1bf8107f88c34fa78113e7782adc90d`. Essa recusa de entrega histórica não é ensaio novo de chunk omitido no controller/rota independente exec. Fontes intactas, extrator histórico não executado.

`review_process_checklist._check_tasks(..., phase="precommit")` retornou `tasks.md pending`; não é execução do checklist inteiro. A ajuda do controller candidato carregou no test tree sem ativação. Metadados nativos do principal registram literalmente `originator=codex-tui` e `source="vscode"`; não comprovam sozinhos a tela terminal. Nenhum código de execução mudou naquela continuação diagnóstica anterior; a correção P1 posterior e os testes de seus bytes estão registrados abaixo.

## Continuação: faseamento da aceitação instalada

O retorno `tasks.md pending` acima precede o faseamento fundamentado de 3.4/3.5/4.3/4.4. Elas continuam abertas e vencem em postpin; 6.1 vence em postcommit e 6.2 em postqa. Essa separação não altera os gates obrigatórios da onda pré-commit: dois payloads, coleta/proxy, verify-wave e checklist verdes antes de commit. O subcheck de tasks não comprova esses demais requisitos.

O pai informou conclusão do diagnóstico desta sessão: bootstrap read-only/binding e contexto PASS; ambos probes verified/completed/read-only; `codex_review_probe qualify=qualified`; `qualify-route` exit0, integrity SHA `a1d389d87a5ea35ddbe18f7a799c9219e4ede281add2a40f8736eca8c9fbfa5b`. Recusa nativa anterior `review_route_unqualified`, exit1, preservada. Coordenador `01a150d1-7438-7f01-ab8f-2dbaed690996`; pacotes/plan e identificadores dos filhos em [resolução de fases](phase-resolution.md), sob `.cursor/tmp/codex-evidence`. Evidência atribuída ao pai, sem ler controles/prompts: somente diagnóstico TUI→exec do adapter ativo, não produto/candidato ou principal exec independente. Não houve mudança em runtime, pacote, trust, instalação ou Git nesta continuação de faseamento.

Verificação do faseamento com a função real `_check_tasks`: precommit `None`, postcommit recusa 6.1, postpin/postqa recusam 3.4, strict recusa tasks pendentes. Isso verifica apenas a barreira de tasks, não checklist/onda completos. OpenSpec strict e links/whitespace dos seis documentos PASS naquela coleta; nenhum dos sete checkboxes abertos foi marcado. A correção P1 posterior altera apenas o candidato e não essas fases.

## Primeira correção após T10

O pai confirmou T10 → Em desenvolvimento e retomou este mesmo Apply/captura. O P1 verificado da onda `7bf356e19cca59aa59b4ae63` foi corrigido no candidato: lançamento bootstrap → binding completo → recusa nativa de rota → contexto/probes/qualificação. A regressão nova parte de checkpoint vazio nas duas superfícies e usa retornos dos helpers reais sobre fontes controladas. Suite focada corrigida: **7 PASS em 120,84s**, quatro avisos de configuração conhecidos, sem skips. O reviewer que falhou `Selected model is at capacity` não entregou payload; a onda anterior continua incompleta e não é prova de contexto excedido.

Regressão ampliada dos bytes atuais: **439 PASS em 236,92s**, quatro avisos conhecidos, exit0 e sem skips; cobre dez arquivos de teste de índice/controller/installer/refinamento/evidence/context/Review/probe/session/checklist, sem repetir o arquivo da suite focada. Log privado `.cursor/tmp/card-1130-correction-1-regression.txt`, SHA `623c958982023bc97d60276c7c5c2236d985ace2c1f20a31942e2700ffd15d5f`.

Arquivos, limites e verificação dos bytes novos estão em [review-correction-1.md](review-correction-1.md). Pacote/patches atuais na tabela acima foram regenerados após os testes, conservaram seus digests e passaram checks de aplicabilidade, sem aplicar nenhum deles. As tasks after-pin e a matriz integral permanecem pendentes; a nova onda do pai ainda é necessária.

Tasks 5.5 (after-pin), 6.1 (after-commit) e 6.2 (after-qa) não foram antecipadas. O critério de verify-wave/checklist pré-commit foi separado como obrigação normativa do pai, sem checkbox circular no próprio diff. Onda produto/commit/closing/QA e atos humanos/release futuros atualizam a mesma matriz. Seus comandos operacionais continuam no runbook, no estado correto e pelo ator correto.

Spawns deste filho: **0**. UI impact: none; HTML gerado/copiado: **N/A**. Proxy de palavras de `design.md`: **2260**. Proxy modelo solicitado: `apply-coluna → GPT-6.1 Sol (gpt-6.1-sol), high`; primeiro retorno observado `gpt-6.1-sol/high` conforme coleta verified/completed informada pelo pai; continuação aguarda recoleta. Sem commit, push, process_event, deploy, trust ou leitura de `.impeccable/critique` por este filho.
