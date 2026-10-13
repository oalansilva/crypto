## Context

O #1086 produziu Design e crítica, mas não comprovou o runtime dos filhos. `codex_proxy.py` recebe os valores observados por argumentos; `model_proxy.py` compara pares; `codex_review.py` verifica a onda com duas capturas, filhos distintos, sandbox e diff exato. Falta a coleta e a verificação antecipada da sua disponibilidade. Este Design complementa esses contratos com a capacidade `codex-runtime-evidence`, sem mudar a FSM ou permissões humanas.

UI impact: none
live_route: N/A — sem tela ou rota de produto; processo local Codex.
surface: none

Ausência justificada: alteração do processo local Codex e de mensagens de terminal/handoff, sem tela, rota ou componente de produto. Prototype: N/A; nenhum HTML gerado ou copiado. Impeccable: N/A porque não existe superfície visual; crítica de Design e aprovação humana continuam obrigatórias.

A leitura local em 2026-10-13 encontrou uma fonte candidata concreta: `~/.codex/state_5.sqlite` relaciona thread e `rollout_path`; no rollout deste autor, `session_meta` identifica `originator=codex_exec`, `cli_version=0.162.1`, cwd e filiação; `turn_context` identifica turno, modelo, esforço e sandbox. O índice é somente um localizador: seus campos de modelo não substituem eventos de turno. Essa constatação não demonstra coleta automática completa nem qualifica CLI, IDE ou outro host como suportado. Não há novo banco de workflow: o SQLite pertence ao runtime e será lido sem mutação.

## Goals / Non-Goals

**Goals:** recusar cedo quando a fonte necessária não é utilizável; coletar automaticamente a observação e o resultado do filho correto; aceitar conclusão com payload correspondente à captura de nascimento; preservar trabalho e orientar recuperação quando a coleta falhar; demonstrar suporte por host/versão com prova real.

**Non-Goals:** alterar #1086; trocar ou retunar modelos; inferir observação a partir da seleção, do catálogo ou do relato do filho; fallback para outro cliente; alterar gates humanos, trust de hooks, sandbox ou diff exato; expandir os demais adapters ou alegar modo Auto.

## Decisions

### 1. Um coletor Codex com contrato explícito de proveniência

Adicionar um módulo de evidência no adapter `scripts/process-fsm/`, consumido pelo preflight, pelo proxy e pelos verificadores existentes. O primeiro driver será para rollout local, condicionado à prova real da integração. Outras superfícies do mesmo runtime, como eventos app-server, só entram mediante driver e prova equivalentes; não são fallback implícito.

O envelope versionado contém: card/worktree, papel/faixa, identificador da tentativa e digest da captura imutável; parent thread, child thread e turno; identidade do nascimento; host, originator e versão observados; requested separado de observed; status terminal e presença/digest do payload; resultado da validação; razão estruturada; referência de origem, tipos/identificadores dos eventos e digest dos bytes efetivamente usados. Sandbox e digest do diff permanecem obrigatórios onde o contrato de review exige.

O registro de nascimento liga a captura à chamada nativa e ao child id retornado pelo host. O retorno dessa chamada, a filiação em `session_meta` e os eventos do turno precisam concordar. Prompt contendo um attempt id é pista de correlação, nunca prova suficiente isolada. Não selecionar rollout por mtime, nome semelhante, último filho ou apenas cwd. Campos ausentes permanecem `unavailable`, sem copiar requested. Não aceitar flags `--observed-*` manuais como caminho de sucesso de uma execução nova que exige coleta; compatibilidade de leitura histórica não promove registros antigos a evidência nova.

Alternativa descartada: pedir que o operador ou filho preencha o par. Isso reproduz o problema e não prova origem. Um catálogo comprova capacidade de seleção, não execução.

### 2. Preflight antes de qualquer trabalho delegado e da transição dependente

A orquestração Codex executa preflight antes de cada nascimento e antes da mutação de Status para etapa que depende dele. A integração em `process_event` cobre as transições pertinentes do cliente Codex sem criar arestas, estados ou dispensas; contexto de cliente ausente/ambíguo não autoriza inferir compatibilidade. O caminho de delegação documentado exige o mesmo preflight mesmo quando o card já está na coluna. Hooks, quando confiados e cobertos, reutilizam a checagem; ausência de hook nunca equivale a cobertura automática.

O preflight resolve identidade real da sessão/host, versão e schema conhecidos, acesso somente leitura à fonte, eventos obrigatórios legíveis, capacidade de ligar filhos e turnos, captura válida e destino de evidência gravável. Em Code Review, confere também disponibilidade da observação de sandbox do turno pai dedicado read-only. Registro de capacidade fica vinculado a sessão, host/versão e contrato do coletor, sendo revalidado ao mudar qualquer um deles; não basta um cache global de PASS.

Resultado visível: `ready` ou `blocked`, com causa, etapa/card, host/versão, campo/fonte indisponível e recuperação. Em recusa, nenhum filho de trabalho nasce e nenhuma transição é feita; artefatos existentes permanecem. A checagem indica capacidade disponível, não garante que um futuro filho concluirá. Permissão revogada ou trace perdido depois são tratados pela coleta final.

Um host ainda sem prova fica `unverified`, recusado para trabalho de etapa. Sua qualificação usa ensaio explícito sem trabalho de produto e sem transição do card, dentro das permissões existentes; isso evita circularidade entre a primeira prova real e a exigência de suporte. Não exige que Alan preencha metadados observados.

### 3. Coleta final vinculada a nascimento e turno

Após o retorno do host, o pai gravável coleta os eventos do child id daquela tentativa. `session_meta` verifica identidade, filiação, cwd, originator e versão; `turn_context` fornece modelo/esforço e política ativa do turno. Evento terminal como `task_complete`, associado ao mesmo turno, deve concordar com `completed` e conteúdo retornado pelo host. Texto final isolado e evento de outro turno não comprovam conclusão.

O coletor aguarda somente uma janela limitada e documentada para flush do runtime. Evento parcial, ambiguidade, erro de leitura ou timeout produz recusa específica, não espera infinita. A implementação decide o limite operacional e o informa no diagnóstico. Para turnos adicionais/resume, cada turno de trabalho aceito deve ter observação válida contra a captura original; um turno antigo não valida o novo, e um último turno válido não apaga divergência anterior. Uma nova seleção local só afeta novos nascimentos.

O envelope preserva referência/digest de uma extração mínima verificável dos eventos necessários, sem prompt nem transcript completo, em armazenamento local de evidência protegido. O digest é calculado sobre essa extração estável, não sobre o arquivo append-only inteiro. O proxy recebe o envelope validado e registra idempotentemente por tentativa/filho/turno; repetição de coleta não cria uma terceira entrada na onda. Fontes conflitantes não escolhem silenciosamente a que passa.

### 4. Integração mantém todos os gates existentes

Sucesso continua exigindo seleção capturada válida, observação igual, host/versão conhecidos, conclusão e payload. O coletor adiciona proveniência verificável; não substitui critérios de conteúdo, crítica, QA ou revisão. Gate consumidor revalida integridade e vínculo da evidência em vez de confiar só em `successful=true` escrito no JSON.

Code Review continua com dois papéis e filhos distintos, mesma onda, mesmo SHA-256 e captura por nascimento. O pai materializa o diff antes; a sessão que faz os spawns é comprovadamente read-only. A coleta/persistência de proxies ocorre no pai gravável após ambos retornarem; filhos e sessão da onda não recebem escrita para produzir evidência. `verify-wave` e checklist permanecem obrigatórios. Os demais adapters não recebem nova obrigação neste card.

### 5. Recuperação preserva o trabalho

Se a coleta falhar após trabalho produzido, manter Status e artefatos; registrar tentativa recusada com causa e quais evidências faltam. Quando apenas houve atraso ou acesso temporário e a origem íntegra reaparece, recoletar a mesma tentativa idempotentemente, sem trocar sua captura. Se não for possível demonstrar identidade, origem ou par correto, recusar reutilizar a tentativa como prova: novo nascimento com seleção corrente, após preflight, reutiliza os artefatos como insumo e refaz a validação necessária. Não retunar nem resumir agente divergente, não marcar o trabalho anterior como sucesso e não apagar artefatos úteis.

## Risks / Trade-offs

- Schema interno do rollout pode variar → driver versionado e recusa de campos/schema desconhecidos; matriz de capacidade por host/versão, com link para prova real.
- Preflight passa mas runtime perde evidência depois → recusa final explícita, coleta limitada e recuperação preservando trabalho.
- Trace contém material sensível → leitura restrita à identidade alvo, extração mínima, permissões locais e publicação somente de resumo sanitizado.
- Arquivo local não é atestado criptográfico do servidor → declarar limite cooperativo; hash detecta alteração do artefato, não transforma texto adulterado em prova independente.
- Compatibilidade com proxies existentes → versionar envelope e testar consumo; nunca tratar legado sem proveniência como coleta automática comprovada.

## Migration Plan

Depois da aprovação humana e T8, implementar coletor/preflight e integrar caminhos Codex existentes. Executar testes de recusa e ensaio real de qualificação no host alvo antes de marcá-lo suportado. Atualizar runbook e matriz com versão, fonte, campos comprovados, limitações e recuperação; manter hosts não ensaiados como `unverified`/indisponíveis. Rollback do mecanismo preserva capturas, evidências e artefatos, e mantém a recusa quando o gate não pode provar runtime; não há migração de Status ou trust automático.

## Open Questions

Nenhuma decisão de produto pendente. A prova end-to-end e o comportamento exato de flush/terminal da integração serão resolvidos no Apply antes de qualquer alegação de suporte. Localizar campos nesta sessão é evidência exploratória, não substitui esse aceite.

## Accepted Apply Details

- P3 — detalhe de Apply; disposition: aceito. Nome do módulo, códigos de erro, limite de espera, layout privado da extração e plumbing de CLI são definidos e ensaiados no Apply, respeitando o contrato acima.

## Design Critique

- P0–P2: nenhum achado; disposition: sem bloqueio.
- P3 — token `live_route`: disposition: resolvido no único rework; `N/A` com justificativa reconhecida pelo parser.
- P3 — detalhes de Apply: disposition: aceitos; resolver conforme Accepted Apply Details, sem reabrir como P0/P1.
- verdict: PASS de conteúdo; uma autoria, uma crítica sem tela e um rework. Snapshot: `.impeccable/critique/1095-card-1095-codex-evidencia-design-critic.md`.
