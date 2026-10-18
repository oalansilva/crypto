# #1130 — fase dos ensaios do suporte instalado

## Decisão e fundamento aprovado

**Implementação aplicável a precommit concluída; aceitação viva continua pendente.** As tasks 3.4/3.5/4.3/4.4 permanecem abertas e recebem `<!-- covenant-flow:after-pin -->`. Essa é a primeira fase que pode aceitar o comportamento distribuído novo. Não existe dependência necessária de QA nessas quatro tasks; colocá-las em after-qa permitiria atraso sem causa e não foi adotado. 6.1 continua after-commit, 5.5 after-pin e 6.2 after-qa.

A decisão 6 do [Design aprovado](../design.md) determina literalmente: “Tasks de implementação, testes, matriz preparada e provas possíveis vencem em precommit”; em seguida distingue “instalação canônica em postpin” e permite publicar o suporte necessário para exercitá-lo, sem dispensar etapas. As specs exigem provas próprias por rota, sem aceitação por bootstrap/fixture, e não impõem que ensaios de uma instalação ainda inexistente precedam sua distribuição. A decisão 7 exige procedência nucleus → consumidor e trust separado. Nenhuma cláusula temporal aprovada foi removida ou alterada.

O contrato já existente do [checklist](../../../../scripts/process-fsm/review_process_checklist.py) define `precommit=0`, `postcommit=1`, `postpin=2`, `postqa=3`; uma task after-pin aberta é admitida apenas nas fases anteriores a postpin. Em postpin e postqa bloqueia; strict exige todas marcadas. A anotação usa o mecanismo suportado e não muda código de gate. A seção Checklist de review do [runbook](../../../../.cursor/skills/covenant-flow/SKILL.md) reconhece exatamente essas três anotações e exige rechecagem posterior.

## Dependência por tarefa

| Task | Trabalho já concluído antes do commit | Prova ainda aberta e por que precisa do pin |
| --- | --- | --- |
| 3.4 | Controller/checkpoints TUI e exec implementados e testados; preflight destino vazio e root divergente exercitados; nascimentos/contextos #1130 e interrupção histórica têm escopos documentados. | Nova sessão sem arquivos locais precisa descobrir o **novo índice instalado**; retomada precisa executar o **novo controller/prepare** com filiação/contexto/payload reais nas duas raízes e rotas. O adapter ativo ainda é o anterior. Test tree não comprova seu caminho de hooks. Após pin real e revisão humana aplicável, pai/operador exercitam sessões e preservam UUID/turn_context; nenhuma fase autoriza rebind presumido. |
| 3.5 | Correção de binding explícito de refinamento e checkpoint/resposta humana implementada/testada; estado/body #1117 revalidados por REST/GraphQL, sem edição. | A regressão do incidente deve atravessar o **prepare/guard novo instalado**, uma sessão principal real e o diálogo/body do card autorizado. Um grill pelo helper antigo não aceita a correção nova. Depois do pin, revalidar #1117 em seu próprio chat; se inapto, caso equivalente autorizado, sem retroceder ou fabricar decisão/resposta. Pin não concede essa autorização nem dispensa a precondição grill-card. |
| 4.3 | Tests de TTL/Status/digest/chunks/sandbox/interrupção/payload já passaram. Negativos nativos adicionais verificaram TTL/Status/digest/sandbox; interrupção QA e entrega truncada dos reviewers históricos foram reabertas com fontes intactas, sem promovê-las a prova nova. | O que resta é observar recusas/recuperação da **cadeia do controller novo instalado**, sobretudo chunk omitido e lifecycle/payload nas rotas faltantes. Rodar o verificador antigo ou fixture novamente não exercita sua orquestração. Depois do pin, pai conduz diagnósticos permitidos sem produto/transição e conserva fontes de cada falha e resultado; gates/sandbox permanecem vigentes. |
| 4.4 | Suporte às etapas e cadeia de Review implementado/testado; Design autor/crítico #1130 verified e primeiro Apply verified/completed informado pelo pai; produto Review/QA #1098 é histórico. Review real do diff #1130 continua obrigação pré-commit separada. | Aceitação exige Design/crítica/Apply e Review de produto nas duas rotas com o **suporte novo distribuído**, além da mera onda que revisa o próprio pacote ainda inativo. Após pin, cards/chats/estados elegíveis e autorizações reais fornecem esses ensaios; a prova antiga não se transfere. Nenhum novo card/status foi inventado. Células ainda dependentes de gate continuam abertas e bloqueiam postpin; não são reduzidas a relatório de lacunas. |

Essa separação não oculta código por implementar: o candidato, 16 arquivos distribuíveis, testes e patches com digests permanecem os mesmos. A pendência é executar o comportamento no consumidor instalado; rodar código em cópia descartável, mudar `--root` ou copiar receipts não satisfaz isso. Pela inspeção dos helpers, o caminho de spawn ativo revalida o helper/plan ativo; não foi usado clone para contornar essa identidade. O manifesto/adapter ativos permanecem inalterados.

## Ordem dos gates e limites

1. Pai concluiu os diagnósticos autorizados da base integrada para sua própria cadeia: informou bootstrap read-only/binding PASS, contexto próprio PASS, ambos probes verified/completed/read-only, `codex_review_probe qualify=qualified` e `qualify-route` exit0. Coordenador `01a150d1-7438-7f01-ab8f-2dbaed690996`, bootstrap `dedicated-bootstrap-09fd9867bde8d981a84f46af.package.json`, context plan `97232d1a-74d5-4f5a-91d0-4649b96c2db8.birth.context-plan.json`, probe package `dedicated-probe-34b14f1e27b1eb80ba071818.package.json`; identificadores informados dos dois filhos `342d285f-27e0-43be-ac0c-5cf2eb48e5b2` e `a5fd9835-1639-4c4a-84fe-394037182dd0`. Paths sob `.cursor/tmp/codex-evidence`; integrity SHA `a1d389d87a5ea35ddbe18f7a799c9219e4ede281add2a40f8736eca8c9fbfa5b`. Recusa anterior nativa `review_route_unqualified`, exit1, preservada. Este registro é atribuído à coleta do pai, sem leitura de controles/prompts pelo filho: diagnóstico TUI→exec do adapter ativo, não produto/candidato ou principal exec independente.
2. A tarefa de **implementar** está pronta para inspeção/review; o pai avalia T9 pelos gates reais. O faseamento remove somente a exigência circular de ensaiar a instalação futura antes de disponibilizá-la. Não emite evento nem declara T9 automático. Onda real do diff, dois payloads, coleta/proxy, `verify-wave` e checklist **precommit** continuam vencendo antes de commit, como o Design decisão 5 exige.
3. Pai conduz commit e fechamento 6.1 na fase correta. Entrega source/consumer exige resolver binding real e base dirty #1098 preservada; não há tag presumida. Pin/manifest reais e trust humano aplicável antecedem aceitação dos ensaios anotados. Nenhuma operação de produção é autorizada por esse faseamento.
4. Em **postpin**, 3.4/3.5/4.3/4.4/5.5 abertas devem bloquear o checklist. Concluir cada uma com fontes reais do suporte instalado antes de declarar esse gate/fechamento de aceitação satisfeito. Se não houver card ou ato humano elegível, registrar a espera mantendo a task aberta; não convertê-la em PASS. QA/6.2 é uma obrigação adicional, não substituto desses ensaios.
5. Postqa e strict revalidam todas as tasks aplicáveis. A matriz ainda exige as provas humanas/release nos atos próprios e impede alegação de fluxo integral enquanto qualquer célula obrigatória faltar, inclusive depois de tasks de implementação fechadas. Acompanhamento continua #1130, sem transferência a #1128.

O diagnóstico anterior de `tasks.md pending` e a recusa de encerramento eram corretos para as linhas então sem anotação; estão preservados no [registro anterior](continuation-blockers.md). A presente decisão resolve a dependência temporal conforme Design/checklist, sem marcar os sete checkboxes abertos ou reclassificar evidência histórica. Não foi identificado P0 de produto.

## Verificação desta alteração documental

A função real `_check_tasks` foi chamada sobre este `tasks.md`, sem mudar seu código, com estes resultados:

| Fase | Resultado observado |
| --- | --- |
| precommit | `None`: nenhuma task aplicável pendente |
| postcommit | `tasks.md task 6.1 pending at postcommit` |
| postpin | `tasks.md task 3.4 pending at postpin` |
| postqa | `tasks.md task 3.4 pending at postpin` |
| strict | `tasks.md pending` |

Assim, a primeira barreira que já venceu continua recusando as fases posteriores; não houve liberação geral. Esse é o **subcheck de tasks**, não o checklist completo nem verify-wave. `openspec validate card-1130-codex-cli-fluxo-completo --strict` PASS; links relativos/whitespace dos seis documentos alterados PASS. Contagem permanece 19/26, sete checkboxes abertos. Nenhum código de execução foi modificado e não houve motivo para repetir a regressão runtime já registrada.

Digests preservados: pacote `9f237d884361342c36d115a3f2f2e8032489e2e14a4c0d8c9cdb4aeba008b0a3`; manifesto ativo `3a90add2ddffa07963d28196b495e3ff435356a2d6a980c7e1a33d63dc28e0cb`; `codex_evidence.py` ativo `79fc746a254f64987c7aa3686584921a2df083f446e6376410075042a42d375e`. Sem instalação, trust, evento, Git ou spawn nesta continuação de faseamento.
