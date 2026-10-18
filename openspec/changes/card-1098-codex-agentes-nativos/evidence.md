# Evidências de Apply — #1098

## Estado atual — correção CI e aceites CLI, 18/10/2026

Após T13 informado pelo pai, corrigidos somente o teste de paginação obsoleto e a frase do runbook sobre registro de hooks: **37 testes focados passaram**; adapter/manifesto/digest de confiança permanecem intactos. 5.2/5.4/5.7 reconciliadas com recusa real atual, onda de produto válida e matriz que distingue histórico/fixtures; **30/32**, sem QA global verde. 5.1 aguarda os controles reais observados por Alan. 5.3 permanece pendente: escrita/readback da fixture ignorada foram observados pela rota filha `functions.exec` → `exec_command`, inclusive com workdir=/tmp, mas o alvo absoluto continuava no mesmo card/etapa autorizados. Esse caso não comprova negativo fora do card/etapa, ausência de hook ou defeito. Faltam os negativos reais adequados em QA e fora do card seguro. Detalhes, hashes, patch mínimo do nucleus ainda não aplicado e receita segura para QA: [ci-and-cli-acceptance-20261018.md](evidence/ci-and-cli-acceptance-20261018.md).

## Histórico — recorte CLI aprovado e correção integrada, 18/10/2026

T7 real e T8 Pronto para Dev → Em desenvolvimento confirmados pelo pai. O operador aplicou a correção final: oito payloads nucleus → consumidor, receipt real e selo/bytes conferidos, manifesto consumidor válido e trust pertinente confirmado pelo pai. Registro conciso e hashes: [final-fix-distribution-20261018.md](evidence/final-fix-distribution-20261018.md).

**27/32 concluídas + três transferidas não concluídas ao #1128**. Somente 3.3/6.3 avançam pela qualificação completa da rota CLI atual, feita pelo pai e conferida documentalmente; nenhum coletor/qualificador foi executado por este filho. 5.1–5.4 e 5.7 permanecem pendentes, incluindo Review/QA de produto e verify-wave/checklist. Os registros seguintes preservam seus respectivos hashes/escopos históricos.

## Histórico — distribuição anterior concluída, 18/10/2026

O operador aplicou a entrega consolidada no nucleus e redistribuiu ao consumidor; receipt real e checagem direta `deliver.py --applied` confirmaram verified/applied=true/writes=false antes desta edição documental. A revisão de trust foi feita separadamente pelo operador e o pai confirmou reviewed=true/manifest=true, missing/divergent vazios, adapter `d174776e2c16a162b949a392fd56c4e9c73aea5ce235fa2be01856bb3a7b8d6c`. Docs, testes, mapeamentos, hashes, manifesto e limites estão em [distribution-complete-20261018.md](evidence/distribution-complete-20261018.md).

Tasks 4.5 e 6.4 reconciliadas como concluídas; **25/35**. Novo runtime/Review dos hashes finais, tasks 3.3/6.3 e 5.1–5.8 permanecem pendentes. Publicação/pin novo não ocorreram; `internal_context_attestation=unavailable`. Esta continuação altera somente tasks/evidence e registra o desvio documental intencional após a entrega, preservando pacote selado, before, código, docs compartilhados, skills, perfis, manifesto, Design e trust.

## Histórico — diagnóstico dedicado PASS anterior à entrega final

O pai integrou/revisou as correções e executou bootstrap, contexto próprio, ambos probes nomeados e qualificação de rota TUI → coordenador exec, todos PASS. Adapter informado `0d57a079ced29582fe4df656e05a718451af01ddd39d527524864e3eb78be669`. Provas sanitizadas, escopo, hashes, pendências e gates: [dedicated-diagnostic-pass-20261018.md](evidence/dedicated-diagnostic-pass-20261018.md). Tasks3.2/6.1/6.2 concluídas; **23/35**. Onda de produto/verify-wave/checklist, QA, demais superfícies e distribuição canônica nova permanecem pendentes. Atestação interna unavailable. Esta reconciliação não muda adapter/manifesto/skills/código/Design/trust.

As seções seguintes são históricas: estados Design, candidato inativo, rota qualificada/não qualificada e contagens anteriores se referem às respectivas rodadas, não ao estado atual acima. O diagnóstico anterior não qualifica o código final distribuído.

## Revisão de Design: coordenação automática de Review — 17/10/2026

Este bloco descreve o estado mais recente informado pelo orquestrador; as seções seguintes preservam a cronologia. Status real informado: Design após `process_event pedir_review` compilar T17/I4. A nova decisão explícita de Alan substitui o requisito de mesmo chat exclusivamente para coordenação Review por sessão dedicada automaticamente read-only, sem alternância manual de permissões. Esta autoria alterou somente proposal/design/spec/tasks/evidence, preservando Design Critique, snapshots, código, adapter, manifesto, conta, trust e FSM.

O pai informou integração do pacote `.cursor/tmp/card-1098-review-collection-opcao2`, adapter revisado pelo operador `c879d4b95952252bf90de1d3008bb53ba1694193a1e2fb20970b1907279cbe3c`, 550 testes e 34 focados. Esses testes são histórico informado; não foram reexecutados nesta autoria documental. Tasks preservadas: 20 concluídas, total ampliado de 31 para 35 por quatro tarefas pendentes da automação.

Diagnóstico 01: dois perfis nomeados recusaram probe por contrato que proíbe escrita e exige verificação não fornecida; sem execução nativa do helper, coleta recusou `review_probe_unavailable`. Não foi revisão de produto. Handoff: `.cursor/tmp/card-1098-readonly-diagnostic-handoff.md` (seu estado da onda 02 é anterior à atualização seguinte).

Diagnóstico 02: o pai informou coleta verified/completed dos receipts `70b0bf7c-19a4-4148-8937-fd6679903f73` e `cb6011e6-2a78-4dfb-87e8-22210e63d348`, seguida de `codex_review_probe.py qualify` com resultado qualified. Referência privada: `.cursor/tmp/codex-evidence/review-probe-qualification-5e0135b297ba800a7f73eca30e9ab14f3893a3bef609056e7e0ffe8fa21aebc1.json`. Leitura do mesmo SHA, tentativa negada errno30 e readback preservado foram reportados. Escopo estrito: dois agentes default diagnósticos na superfície TUI e no mesmo chat; não qualifica perfis nomeados, exec dedicado, nova cadeia de receipts ou review de produto. Não se alterou source trace nem se promoveu relato a prova adicional.

A automação proposta continua não implementada/não qualificada. O Design exige pacote e envelopes pendentes explícitos, binding resolvido de fonte autoritativa do coordenador real, sandbox contínuo, dois filhos no mesmo turno, contratos explícitos do probe e verificação agregada pelo principal. Atestação interna permanece unavailable; opção 2 e gates humanos não foram reabertos. Nenhum spawn por este autor; HTML gerado/copiado N/A. Captura de autoria: `.cursor/tmp/card-1098-design-automatic-review.capture.json`; coleta após retorno cabe ao pai e não é antecipada aqui.

Validação documental desta autoria: `openspec validate card-1098-codex-agentes-nativos --strict` PASS; `git diff --check -- openspec/changes/card-1098-codex-agentes-nativos` PASS. Uma tentativa inicial de edição por script shell foi recusada pelo Guard (`unsupported_targets`); nenhuma escrita dessa chamada ocorreu. As edições seguintes usaram patches com alvos explícitos autorizados no OpenSpec.

## Nova entrada Apply da opção 2 — 17/10/2026

Este bloco atualiza o estado; os registros anteriores abaixo são históricos. Pai informou T7 da opção 2 e executou T8 antes deste filho único. Binding: worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos`, branch `card-1098-codex-agentes-nativos`. Nenhum `process_event`, commit/push, spawn, trust, conta ou permissão foi alterado por este filho. Não foi lida a árvore `.impeccable/critique/`.

**Contexto real reconciliado (1.7–1.9):** `codex_context.verify_qualification` ativo revalidou a qualificação do pai diretamente das fontes privadas: tentativa `7739e34e-0611-40db-be29-e26e015bd5a4`, child `01a14a96-b8e5-79f1-b701-f69723c6b90a`, pai `01a14a14-8ad0-78b2-8278-c14aec2b4bf8`, `result=passed`, chamada nativa `fork_turns=none`, `internal_context_attestation=unavailable`, scope SHA-256 `808517ea469fcc399ed841230697f54df6593f8be7cbd9cefe9063e6ed1fd0c7`. A saída foi explicitamente sanitizada; nenhum C/S foi lido em saída, publicado ou encaminhado. Referência privada: `.cursor/tmp/codex-evidence/context-qualification-a5687a8312654b11-7739e34e-0611-40db-be29-e26e015bd5a4.json`. O ensaio real é do pai; os testes deste Apply são provas de contrato. Tasks atualizadas para **20/31**, sem promover a qualificação a garantia de Review.

**Candidato inativo concreto:** `.cursor/tmp/card-1098-review-collection-opcao2/README.md`, com dez arquivos finais em `files/`, sete snapshots existentes em `before/`, `review-collection.patch`, `manifest.json`, `verify_package.py` e resultados reproduzíveis. Ele corrige a repetição runtime idêntica de `turn_context` preservando toda origem e recusando qualquer divergência, inclusive campo extra; não altera rollouts ou envelopes reais. Implementa helper canônico e coleta por `event_msg/item_completed/CommandExecution`: a estrutura com thread/turno, argv, cwd `file://`, exit/status e aggregated_output foi observada neste Apply TUI 0.163.0. Planos vinculam captura/papel/onda, helper/intérprete/hash, diff/path/SHA e fixture owner-writable preparada gravável. O filho deve receber o diff integral pela saída do comando fixo, registrar errno real de escrita negada e readback inalterado. Declarações ou saídas inventadas não contam.

O contrato separa qualificação diagnóstica de dois papéis/filhos da futura onda real, evitando dependência circular. Receipts são preparados graváveis com `--defer-review-turn --review-probe-plan`; o turno real só vem da chamada nativa posterior read-only. `pedir_review` inspeciona sem probe de escrita; o pai mantém read-only até ambos retornos. `verify-wave` exige mesmo path/SHA, dois filhos/papéis, mesmo chat/turno e persistência posterior gravável. `aceitar_sha` verifica essa onda histórica em vez de exigir read-only no turno posterior. Native settings intermediárias invalidam o intervalo; perfil observado `disabled` não equivale a read-only. Não se infere read-only de nomes de perfil desconhecidos.

**Validação do candidato:** regressão combinada **550 PASS**, incluindo contexto, coleta, fluxo Review, adapter, proxy, Guard, seleção, account e process_event. Saída em `.cursor/tmp/card-1098-review-collection-opcao2/test-results.txt`; quatro warnings são opções pytest não instaladas no ambiente. São 40 testes/casos a mais que a baseline anterior de 510. Positivos controlados cobrem preparo gravável → diagnósticos mesmo turno read-only → persistência gravável → qualificação independente → preflight normal sem escrita → preparo da onda produto → runtime read-only → retorno de ambos → persistência gravável → proxies/verify-wave/preflight aceitar_sha. O critério independente de contexto é substituído por stub somente nesse teste de fluxo; a suíte de contexto verifica suas fontes próprias. Negativos cobrem divergência de payload repetido, ausência/declaração, comando/cwd/thread/turno/path/diff diferentes, truncamento/JSON inválido, falta de errno, readback alterado, duplicação, capture/helper/plan adulterados, onda incompleta, mesmo papel/child, turno divergente e mudança de permissões. Fixtures não qualificam o host.

```bash
PYTHONPATH=.cursor/tmp/card-1098-review-collection-opcao2 python3 -m pytest -p candidate_pytest_plugin .cursor/tmp/card-1098-review-collection-opcao2/files/scripts/process-fsm/test_codex_evidence.py .cursor/tmp/card-1098-review-collection-opcao2/files/scripts/process-fsm/test_codex_context.py .cursor/tmp/card-1098-review-collection-opcao2/files/scripts/process-fsm/test_codex_review_probe.py scripts/process-fsm/test_process_event.py scripts/process-fsm/test_codex_review.py scripts/process-fsm/test_codex_proxy.py scripts/process-fsm/test_codex_adapter.py scripts/process-fsm/test_guard.py scripts/process-fsm/test_account_registration.py scripts/process-fsm/test_model_selection.py scripts/process-fsm/test_model_selection_adapters.py -q --disable-warnings --tb=short
python3 .cursor/tmp/card-1098-review-collection-opcao2/verify_package.py
git apply --check -- .cursor/tmp/card-1098-review-collection-opcao2/review-collection.patch
openspec validate card-1098-codex-agentes-nativos --strict
python3 scripts/process-fsm/adapter_manifest.py check --root /srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos
```

Todos esses checks passaram. Uma checagem final do helper isolado `python -I` identificou a necessidade de resolver dependências pinadas do próprio consumidor ao executar candidato inativo; essa correção e a CLI real sem user paths passaram em **34 testes focados finais**, incluindo o fluxo/negativos de Review, registrados em `probe-final-tests.txt`. Adapter/manifesto ativos ficaram intactos: SHA-256 do manifesto ativo `a5a4a5ea8d5acb92a727acee51260692e21542984b5db77ed4596f377d815476`. O pacote confere os hashes before/after e o Design aprovado `ec65518e3196267e603a5f80886d41089ebd357a5b4026070f642c227c9d7936`. O pai integra somente após coletar este retorno; Alan revisa confiança quando exigida. Nenhuma sincronização fora do worktree: Guard `target_outside_binding` informado pelo pai permanece, sem contorno. Pin-base v1.1.22, sem publicação nova.

**Negativo vivo adicional:** o preflight ativo `--review --stage 'Code Review'` neste filho TUI 0.163.0 retornou `blocked`, card1098, `parent_sandbox_mismatch`, garantia `parent_read_only`. Fonte privada sanitizada `.cursor/tmp/card-1098-review-collection-opcao2/live-review-refusal.json`. Nenhum reviewer nasceu e nenhuma sessão externa foi iniciada. Isso não é positivo de Review nem encerra automaticamente 5.2 após QA.

**Pendências/P0 de capacidade:** 3.2 aguarda integração/validação do candidato. 3.3/5.4 exigem contexto nativo read-only real no mesmo chat, diagnóstico e onda de ambos os reviewers; não há ferramenta de mudança de permissões neste Apply. A sequência concreta do operador está no README do pacote. 4.5 permanece parcial pela sincronização canônica negada fora do binding. 5.1–5.8 exigem seus positivos/fatos próprios: UI do operador/Guard vivo, refinamento interativo, exec revisado, App/IDE e matriz por etapa. A substituição integral não foi concluída; recusa correta, fixtures e contexto C/S não substituem os aceites restantes.

Handoff/proxies: 3366 palavras no `design.md` preservado; HTML gerado/copied=N/A, sem protótipo; spawns deste Apply=0. Captura de nascimento `.cursor/tmp/card-1098-apply-opcao2.capture.json`, receipt `.cursor/tmp/codex-evidence/b976362e-f780-4fb1-9421-048058cafec3.birth.json`; observação lifecycle/final do filho cabe ao pai após o retorno. proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol), esforço high solicitado conforme captura, sem inferir completed antecipado.

## Revisão documental do critério de contexto — opção 2 escolhida por Alan

Em 17/10/2026, Alan escolheu explicitamente substituir a exigência de um sinal interno completo de isolamento pelo conjunto **contrato documentado aplicável ao runtime + chamada nativa registrada `fork_turns=none` + ensaio complementar não secreto de herança indevida**. O conjunto é evidência contratual e empírica de escopo limitado; não atesta o contexto interno completo entregue ao modelo. Essa atestação continua `unavailable`, separada e não exigida somente para o critério de contexto escolhido. Guard, seleção observada, permissões efetivas, leitura/deny/readback por reviewer, dois reviewers/mesmo diff, lifecycle e gates humanos continuam exigidos.

Esta continuação mudou exclusivamente `design.md`, `specs/codex-harness/spec.md`, `tasks.md` e este registro. Não executou o ensaio, não implementou o critério novo, não alterou o adapter integrado ou seu manifesto e não mudou trust/conta/permissões/Status. O briefing de `proposal.md` e o bloco histórico de crítica foram preservados. O pai havia revalidado a continuação pela captura/receipt originais com `model_proxy.verify_continuation`, lifecycle successful e `gpt-6.1-sol/high`; isso não constitui o novo ensaio de contexto.

O ensaio definido no Design exige C entregue ao filho e S exclusiva do contexto anterior do pai, sem disponibilizá-la por prompt, steering, arquivos compartilhados, fixtures, nomes, ambiente ou outros canais. Não foram criados valores C/S nesta continuação. Controle exato, completed/payload, chamada/filiação/proveniência válidos e ensaio não contaminado são condições obrigatórias; ausência de S sozinha é insuficiente. S devolvida sem entrega autorizada ou chamada divergente bloqueia. Controle ou origem incompletos, silêncio/interrupção e contaminação não contam como positivos. O resumo futuro separa as três evidências e a atestação interna unavailable, sem publicar os marcadores.

As referências oficiais consultadas descrevem contextos próprios de subagentes no âmbito de [Responses Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) e os contratos de threads/histórico do [app-server](https://learn.chatgpt.com/docs/app-server). Não se inferiu que uma documentação de outro produto qualifica automaticamente TUI/exec/App/IDE. Em especial, `excludeTurns` em respostas/paginação do app-server não equivale a `fork_turns=none` nem atesta não herança.

A integração 4.4 permanece concluída; a baseline correta é 17/27. Foram acrescentadas quatro tasks pendentes para o novo critério (1.7–1.9 e 4.5), resultando em **17/31** no plano revisto. 3.2, 3.3 e os aceites vivos continuam pendentes. O novo contrato não foi atribuído retroativamente aos testes ou proxies históricos.

**Digest e estado:** o Design mudou, portanto a crítica/aprovação anteriores não cobrem automaticamente o novo digest. O pai informou que o dry-run canônico `process_event.py pedir_review --card 1098 --change card-1098-codex-agentes-nativos --client codex --dry-run` rejeitou `codex_evidence:stage_capability_missing` (context_isolation, parent_read_only, review_diff_read, review_write_denial_readback) **antes** de avaliar digest/I4. Nenhuma transição foi executada. Essa limitação existente é registrada; não foi contornada, não se inventou aresta e a escolha de wording não foi tratada como T7. O pai conduzirá publicação/revalidação pelo processo canônico.

Validação desta revisão documental: `openspec validate card-1098-codex-agentes-nativos --strict` PASS; `git diff --check` no escopo da change PASS; parser de tasks confirmou 17 concluídas de 31. Não foram executados novos testes de código ou ensaios de herança, pois nenhum código foi alterado e a execução do ensaio continua pendente.

As seções abaixo preservam a cronologia da entrega e integração anteriores. As afirmações históricas sobre o critério antigo não descrevem uma implementação do critério revisto.

## Atualização de integração pelo orquestrador — 17/10/2026

Esta atualização substitui somente o estado de cópia pendente e a contagem registrados historicamente abaixo. O pai coletou o retorno Apply antes da cópia: tentativa `40bcdd55-f3a0-4f83-a62a-3039ad9df906`, filho `01a14a28-2482-7580-9090-d1ebb2dd8890`, modelo/esforço observados `gpt-6.1-sol/high`, bound_card `1098`, completed com payload e proxy lifecycle successful. Isso não comprova isolamento de contexto.

Os 14 arquivos destinados ao consumidor foram conferidos contra os hashes do pacote; 13 exigiram cópia. O manifesto candidato não passou no consumidor porque o gerador do nucleus ainda incluía `route-landmarks.yaml` e fixtures que o gerador do consumidor exclui. A cópia dos arquivos foi concluída, mas essa primeira verificação de manifesto falhou. Alan regenerou o manifesto com o gerador local, obteve PASS e registrou pessoalmente a confiança no novo adapter. O agente não registrou trust.

Manifesto ativo confirmado com PASS: SHA-256 `9612ee6517ebe1d74113ab4236f97ab7bb85f237591bf4499e67a7cecaecc7c0`. Digest de adapter revisado pelo operador: `8bebf3c13e23ce5002beeb100e2ba4a27d033f3208ce40fb282870903b3239d3`. Pin-base continua `v1.1.22`; o delta é local, sem nova release/pin publicado. A distribuição local e a conferência encerram 4.4; publicação, review e commit continuam pendentes.

Validação no consumidor após integração: **143 testes passaram** em adapter/evidence/proxy/review; houve quatro avisos de opções pytest desconhecidas (`asyncio_mode`, `timeout`, `timeout_func_only`, `timeout_method`). OpenSpec strict e `git diff --check` passaram. Manifesto e confiança não são mais o impedimento.

Progresso atualizado: **17/27 tarefas**. Permanecem pendentes 3.2, 3.3 e 5.1–5.8. O preflight real desta sessão pai continua `stage_capability_missing: context_isolation`; a barreira diagnóstica também está unavailable. Não houve novo filho, revisão, commit ou avanço de coluna. O #1098 permanece Em desenvolvimento. Uma nova confirmação de confiança não supre a fonte autoritativa de isolamento nem as provas de leitura/deny/readback dos reviewers exigidas pelo Design.

Status informado pelo pai: Em desenvolvimento, após T8. Este é o único filho Apply da entrada. O pacote implementável foi preparado e verificado no nucleus do mesmo card. O retorno ocorre com P0 visível de capacidade, após concluir o trabalho independente; não significa implementação integral, revisão aprovada ou aceitação viva concluída.

## Procedência e pacote

- Nucleus: `/srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos`, branch homônima, base `origin/main` em `14aa9d6`.
- Consumidor: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos`, branch homônima, pin-base `v1.1.22`. Bootstrap anterior preservado.
- Pacote revisável: `/tmp/card-1098-apply-package-20261017/manifest.json`; bytes em `files/`, manifesto candidato em `candidate/.covenant-flow/adapters.json`, diff do nucleus em `nucleus.patch`.
- O adapter ativo e seu manifesto no consumidor permanecem intactos neste Apply, para o pai coletar a conclusão com o código atualmente confiado. Após essa coleta, o pai integra os bytes e confere os hashes/manifesto; o operador revisa o novo adapter. Nenhum trust é registrado automaticamente. Por isso 4.4 permanece pendente.
- `install.sh` pertence somente ao nucleus; a distribuição inclui preflight do novo módulo antes da cópia. O pacote registra esse arquivo separadamente de payload consumidor. Não foi executado pin, install na conta, release ou trabalho em `/source`.

## Implementação

`codex_binding.py` normaliza command/cmd e workdir sem substituir a identidade nativa. Verifica cwd de hook contra turn_context quando disponível, recusa identidades divergentes, alvos reais fora do vínculo, escapes por symlink, checkout misto e card OpenSpec distinto. Cada target suportado de patch/edição ou shell estático passa pelo Guard. Status injetado é descartado; branch/card e board continuam independentes da entrada do agente. O evento original é preservado. Shell dinâmico reconhecido ou alvo ambíguo recebe recusa; efeitos internos de scripts/hosted tools não são anunciados como interceptados.

O preflight diferencia capacidades comprovadas de unavailable. `prepare` de etapa e os eventos Codex já existentes em process_event recusam garantias ausentes antes de nascimento/transição. O coletor conserva os envelopes legados; receipts diagnósticos novos registram contrato, argumentos reais, identidades, paths, seleção/captura, fontes e limites. `fork_turns=none` é pedido obrigatório, sem promoção a isolamento efetivo. Interrupção nativa é interrupted; falha de observação/terminal/payload é failed; origem irrecuperável depois de nascimento fica unverified em vez de afirmar ausência de trabalho. Completed continua exigindo payload vinculado ao filho e revalidação de todos os turnos.

`verify-wave` mantém dois papéis/filhos, mesma sessão/turno e digest, proveniência e seleção; também recusa as garantias efetivas indisponíveis. Runbook Codex e docs/model-selection retiram a recomendação de sessão externa para delegar; a garantia read-only de #1049, os gates humanos, AGENTS.md curto e os outros clientes foram preservados. Perfis de reviewers deixam explícito que configuração não é prova de isolamento. Não foi adicionado estado/evento à FSM.

## Verificação

No nucleus:

- 406 testes passaram na regressão ampliada: adapter/evidence/proxy/review, model_selection e adapters, process_event, guard, account_registration e codex_agents.
- Após ajustes adicionais: 142 testes focados de adapter/evidence/proxy/review passaram; os últimos ajustes do coletor e o CLI de interrupção foram revalidados em 69 testes do coletor.
- 14 testes de codex_installer e account_installer passaram.
- `git diff --check`, `bash -n install.sh` e py_compile dos módulos alterados passaram.

No consumidor: `openspec validate card-1098-codex-agentes-nativos --strict` passou. O manifesto do adapter ativo passou antes da preparação do pacote. O candidato recebe verificação própria sem substituir o ativo. Os testes usam fixtures descartáveis e não qualificam nenhuma superfície ou etapa viva.

Houve uma chamada de pytest com path de teste inexistente (`test_adapter_manifest.py`), que não executou testes; foi corrigida para os dois arquivos de installer existentes e os 14 testes passaram. Não se conta essa chamada como validação.

## Fatos vivos e negativos reais

O código preparado no nucleus revalidou as fontes privadas dos dois filhos Design: autor `01a14a21-1780-7da2-b600-bf0ca66fbd7d` e crítico `01a14a23-e9af-70d1-8ccd-394c2ab40cae`, no chat `01a14a14-8ad0-78b2-8278-c14aec2b4bf8`. Seleção, cwd, filiação, completed e payload históricos continuam válidos. Isolamento efetivo sem transcript não foi observado. Resumo sanitizado: [historical-design-verification.json](evidence/historical-design-verification.json).

Foram executados probes somente de leitura para um nascimento futuro nesta sessão Apply `01a14a28-2482-7580-9090-d1ebb2dd8890`, host `codex-tui/0.163.0`, sem iniciar outro filho ou trabalho de etapa:

- [preflight-stage.json](evidence/preflight-stage.json): `stage_capability_missing`, especificamente context_isolation; demais capacidades de lifecycle da qualificação são distinguidas.
- [preflight-review.json](evidence/preflight-review.json): `parent_sandbox_mismatch`; runtime atual danger-full-access. Nenhuma onda nasceu.
- [shell-workdir-is-not-rebind.json](evidence/shell-workdir-is-not-rebind.json): `worktree_mismatch` ao pedir root do nucleus a partir de um shell nesse diretório, pois o turn_context nativo continua no consumidor. Um workdir/--root não reconfigura o chat.

A investigação app-server gerou apenas o schema do binário 0.163.0, sem iniciar servidor, sessão, turno ou inferência. Há contratos de leitura de thread/itens e entradas de cwd/modelo/effort/sandbox; faltam instâncias App/IDE qualificadas e prova efetiva das garantias. Matriz detalhada, digests do schema e controles documentados: pacote `docs/codex-native-capabilities.md`. Lista/inspeção/interação visual do operador não foram observadas por este Apply.

## P0 e pendências

O rollout atual não oferece fonte autoritativa de isolamento efetivo sem transcript nem prova de leitura do mesmo diff e deny/readback de cada reviewer. Também não foi comprovada uma barreira efetiva para liberar trabalho de etapa somente após diagnóstico. O preflight preparado recusa novos nascimentos de etapa. Task 3.2 permanece parcial e pendente; task 3.3 e revisão dependente permanecem bloqueadas. Mudar permissões nativas no mesmo chat pode resolver o turno gravável, mas não preenche automaticamente as outras fontes ausentes.

4.4 aguarda integração do pacote após coleta. 5.1–5.8 continuam pendentes, incluindo refinamento interativo completo, regressão exec pós-adaptação, escrita Guard viva, UI do operador, app e IDE e onda read-only completa. Nenhum negativo vale como positivo. Tasks implementáveis concluídas: 16/27. Não foi pedido review nem feito commit/push, trust, alteração de conta, bypass, sessão externa ou edição/leitura de snapshots Impeccable.

Proxy deste nascimento Apply deve ser coletado pelo pai depois do retorno, com captura `/tmp/card-1098-apply-20261017.json` e receipt `.cursor/tmp/codex-evidence/40bcdd55-f3a0-4f83-a62a-3039ad9df906.birth.json`. Este documento não antecipa seu status completed ou successful.

Proxies de autoria: HTML gerado/copiado N/A; nenhum protótipo; spawns deste filho = 0. O pai registra o proxy de modelo deste Apply pela captura original e a telemetria após o retorno.

Pacote gerado e conferido: 15 arquivos canônicos (14 para consumidor, dos quais 13 diferem; `install.sh` somente nucleus). SHA-256 de `manifest.json`: `f72397bbe7cc72a7d65ec60726f844eb7a9329e3ac806768b7cad391a8d9750e`. SHA-256 do manifesto candidato: `3e7b207cec7617ee1d15a46010521b9faeaa5188433f21ec9619e530af843ab4`. O manifesto candidato passou e os bytes do manifesto ativo permaneceram idênticos durante a preparação. Isso prepara a cópia, mas não conclui 4.4.

proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol). Par solicitado por captura: high; observado e conclusão dependem da coleta pelo pai após este retorno.


## Correção consolidada após T10 — 18/10/2026

[Registro do candidato, checks, hashes e limites](evidence/final-review-fix-20261018.md). Pacote inativo `.cursor/tmp/card-1098-final-review-fix/`, manifesto SHA-256 `0edd927633381eeb863ee9161db1d0ebdfc4c706d635e1b0d76d0882da8ea8ff`, 148 testes focados PASS e dry-run real de ambos os destinos. Nenhum apply/trust/Review/QA novo; 25/35 preservado. A única mudança em Design foi a nota factual de recorte autorizada após o selo, com hash anterior/posterior registrados, sem mudar `.design-digest`. Docs OpenSpec seguem fora dos oito payloads e serão preservados na futura aplicação, após revalidação pelo pai.
