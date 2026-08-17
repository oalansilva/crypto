# Design: card-518-kaizen-release-gate

## Problema

O fechamento atual detecta evidência incompleta tarde demais e permite avançar apesar de sinais objetivos de closeout incompleto. Na release de 2026-08-14, a doc canônica entrou com placeholder e foi corrigida repetidamente, a evidência final de deploy mudou duas vezes, o pacote mudou durante o fechamento, a auditoria kaizen ocorreu somente depois de `Pronto`, um spawn sem mensagens/parts não gerou erro e o `post` passou sem `RELEASE_BRANCHES`. O resultado foi fragmentação em PRs, alinhamento adicional do DAG, ausência temporária de evidência e 17 branches remanescentes.

O usuário afetado é quem fecha e audita releases. O dano não é visual: é perda de atomicidade, rastreabilidade e confiança no gate final.

## UI impact

**`UI impact: none`** — a solução atua em `scripts/release-guard`, documentação operacional, delta specs e handoff de subagents. Nenhuma tela, rota, componente, estilo, copy de produto ou interação visual é criada ou alterada.

## Hipótese

Se a documentação incompleta for rejeitada antes do único PR documental e se o `post` exigir evidência kaizen, lista explícita de branches já removidas e `main` local sincronizada, então o fechamento passa a ser fail-closed e repetível. Se um spawn vazio for classificado como erro explícito, a ausência de auditoria não poderá mais ser confundida com sucesso.

## Resultado esperado

- A próxima release usa no máximo um PR de documentação e não necessita PR corretivo apenas para alinhar o DAG.
- A doc canônica da data não entra no PR documental com placeholders e só é preparada depois da evidência final de deploy estar disponível.
- O `post` falha antes de `Pronto` quando não encontra uma entrada kaizen da data canônica.
- O `post` falha quando `RELEASE_BRANCHES` está ausente, vazio, inválido ou quando qualquer branch listada ainda existe localmente ou em `origin`.
- O `post` falha quando `main` local difere de `origin/main`; o closeout sincroniza `main` explicitamente antes de repetir o gate.
- Um resultado Task com zero messages ou zero parts aparece como erro no handoff e não satisfaz a etapa delegada.

## Escopo e não escopo

### Em escopo

- Gates `pre`/`post` do `scripts/release-guard`.
- Data de release determinística para correlacionar doc e kaizen-log.
- Ordem canônica do closeout em `AGENTS.md`.
- Regra de observabilidade de spawn em `AGENTS.md` e histórico em `docs/kaizen-log.md`.
- Testes shell herméticos com repositório Git temporário e `gh` fake; nenhuma chamada de rede.

### Fora de escopo

- Mover cards, publicar release, executar deploy, limpar branches reais ou sincronizar refs nesta etapa de Design.
- Fazer o guard editar arquivos, trocar branch, executar `git pull` ou apagar refs automaticamente.
- Validar semanticamente a veracidade de cada frase da doc; o gate combina estrutura sem placeholder, evidência `PROD_DEPLOY_EVIDENCE` e ordem operacional.
- Alterar a Task tool/plugin do opencode; a visibilidade do spawn vazio é um contrato de processo e handoff neste card.
- Qualquer mudança de UI ou código de produto.

## Decisões

### D1 — Data canônica explícita, com default UTC

O guard resolve uma única `release_date` por execução a partir de `RELEASE_DATE`; quando a variável não estiver definida, usa `date -u +%F`. O valor MUST corresponder a `YYYY-MM-DD` e a uma data de calendário válida. Valor inválido é blocker em `pre`/`post` e warning em `audit`.

Essa decisão evita depender do nome de um branch, da ordem de `ls` ou da data local da máquina. O override mantém fechamentos retroativos ou que atravessam meia-noite reproduzíveis. Todos os checks da change usam o mesmo valor resolvido.

### D2 — `pre` valida somente a doc canônica da release em fechamento

A doc canônica é `docs/release-${release_date}.md`. O `pre` não exige que ela exista no PR de código inicial, pois a evidência final de deploy ainda não existe. Quando a doc existir — caso do PR documental pós-deploy — o `pre` exige:

1. arquivo versionado;
2. `PROD_DEPLOY_EVIDENCE` não vazio;
3. zero match da expressão de placeholders já adotada pelo projeto: `TBD|TODO|lorem|<!--|FIXME|<[A-Z_]+>`.

O primeiro match é suficiente para bloquear, mas a saída lista até cinco ocorrências com arquivo e linha. O `post` repete a validação da doc canônica e mantém a detecção de docs divergentes da mesma data. `audit` pode reportar dívida histórica como warning, sem fazer uma doc antiga bloquear outra release.

Racional: a sequência deixa o PR de código independente da evidência ainda inexistente e transforma o PR documental, feito após deploy, no único ponto de entrada da evidência final.

### D3 — Ordem canônica produz um único PR documental

O fluxo documentado passa a ser:

1. merge manual do PR da release;
2. deploy em PROD e captura da evidência final;
3. execução de `/kaizen release` ainda com os cards em `Homologado`;
4. atualização conjunta de `docs/release-${release_date}.md` e `docs/kaizen-log.md` em um único commit/PR documental de `develop` para `main`;
5. merge do PR documental e `git switch main && git pull --ff-only origin main` no passo final local;
6. deleção local e remota das branches declaradas do pacote;
7. `RELEASE_DATE=... RELEASE_CARDS=... RELEASE_BRANCHES=... PROD_DEPLOY_EVIDENCE=... scripts/release-guard post`;
8. somente após PASS, promoção dos cards para `Pronto`.

A integração normal do PR documental torna o commit de `develop` ancestral de `main` com tree equivalente; não se cria PR separado apenas para alinhamento de DAG.

### D4 — Evidência kaizen é presença canônica, versionada e anterior a `Pronto`

Em `post`, `docs/kaizen-log.md` MUST estar versionado e conter um heading de nível 2 iniciado pela `release_date` e identificado como auditoria de release pelo marcador canônico `Kaizen release` ou `/kaizen release`. A convenção preferida é:

```markdown
## YYYY-MM-DD — Kaizen release (<nome/pacote>, `/kaizen release`)
```

Busca por data isolada não basta, pois poderia aceitar uma triagem de card do mesmo dia. Arquivo ausente, não versionado ou heading correspondente ausente gera blocker. A limpeza da worktree já existente no guard garante que uma entrada ainda não commitada também não resulte em PASS.

O gate comprova que a auditoria e seu registro existem; qualidade e completude dos achados continuam sendo responsabilidade do contrato do Kaizen.

### D5 — `RELEASE_BRANCHES` obrigatório e não-vazio no `post`

O `post` normaliza a lista separada por vírgulas (trim e deduplicação) e rejeita token vazio, nome que não passe `git check-ref-format --branch` ou que não comece com `change-`, `card-` ou `release-`. Definir a variável como string vazia ou apenas separadores não satisfaz o gate.

Depois do `git fetch --prune origin` já executado pelo guard, cada nome MUST estar ausente em `refs/heads/<name>` e `refs/remotes/origin/<name>`. Presença em qualquer lado é blocker. A lista registra as branches originais do pacote mesmo depois da deleção, para permitir prova negativa determinística.

Essa verificação ocorre antes de `Pronto`, substituindo a semântica anterior de “delete after Pronto”. Branches fora do pacote continuam no inventário geral e seguem sua classificação própria.

### D6 — `main` local é sincronizada pelo operador e verificada pelo gate

O guard permanece sem mutações destrutivas ou mudanças de branch. Em `post`, se `refs/heads/main` não existir ou diferir de `origin/main`, o resultado é blocker, não warning. O passo canônico executa `git switch main && git pull --ff-only origin main` antes do `post`; `--ff-only` impede merge local acidental.

Decisão rejeitada: `git branch -f main origin/main` dentro do guard. Isso poderia alterar uma branch em uso por outra worktree e mistura auditoria com correção.

### D7 — Spawn vazio é falha explícita de handoff

Após qualquer delegação via Task tool, o orquestrador MUST verificar que o resultado contém ao menos uma mensagem e ao menos uma part utilizável. `0 messages`, `0 parts`, sessão ausente ou erro de criação são falha explícita: a etapa permanece incompleta, o handoff registra `ERROR: subagent spawn failed/empty` com o identificador disponível e impacto, e não há fallback silencioso nem alegação de que a auditoria ocorreu.

Neste card a regra é documental (`AGENTS.md` + registro no kaizen-log), porque o `release-guard` não controla o runtime da Task tool. Automação no plugin/runtime, se desejada, exige change própria.

## Riscos e mitigação

- **Virada de dia ou release retroativa** — usar `RELEASE_DATE` explícita; default UTC apenas para o caso comum. Testar override e formato inválido.
- **Falso positivo em docs históricas** — `pre`/`post` estritos miram a doc da data resolvida; `audit` pode continuar mostrando dívida antiga como warning.
- **Entrada kaizen superficial criada só para passar** — o regex exige marcador de auditoria, não apenas a data; revisão do conteúdo permanece humana/processual.
- **`RELEASE_BRANCHES` omite branch do pacote** — a lista explícita é conciliada no handoff com os cards/branches do pacote; o inventário geral continua detectando branches não classificadas. O guard não consegue inferir com perfeição todo branch histórico.
- **Branch remota parece ausente por refs stale** — o check usa o `git fetch --prune origin` do início da mesma execução; falha de fetch já é blocker no modo estrito.
- **Sync de `main` sobrescreve trabalho local** — somente `git pull --ff-only`; worktree suja já bloqueia. O guard nunca força a ref.
- **Mudança de processo sem enforcement da Task tool** — risco residual aceito e explícito; este card exige erro no handoff, mas não instrumenta o runtime. Recorrência deve gerar change de automação.
- **Aumento de fricção no closeout** — mitigado por uma ordem única e comando final com quatro envs explícitos; a fricção é intencional para impedir sucesso parcial.

## Estratégia de validação

Criar um teste shell hermético em repositório temporário, com bare origin e `PATH` contendo `gh` fake. O fake fornece snapshots mínimos válidos e registra contagem de chamadas; nenhum GitHub real é consultado. Uma data fixa entra por `RELEASE_DATE`.

Casos mínimos:

1. `pre` bloqueia placeholder na doc da data e lista arquivo/linha.
2. `pre` bloqueia doc canônica sem `PROD_DEPLOY_EVIDENCE`; doc limpa com evidência passa a seção.
3. `post` bloqueia kaizen-log sem heading de release da data; uma entrada de triagem da mesma data não vale; heading canônico vale.
4. `post` bloqueia `RELEASE_BRANCHES` unset, vazio, com token vazio ou nome inválido.
5. `post` bloqueia branch listada presente somente localmente e somente remotamente; passa a seção quando ambas as refs estão ausentes após prune.
6. `post` bloqueia `main` local stale; após fast-forward local, o blocker desaparece.
7. `pre` preserva orçamento remoto de zero chamadas `gh project item-list`/`gh pr list`.
8. Um check documental focado confirma que o contrato de handoff para spawn vazio está presente em `AGENTS.md`; a evidência funcional do critério é um handoff explícito ao ocorrer o próximo caso real/simulado de Task vazia.

## Impeccable Brief

**N/A** — `UI impact: none`; não há superfície frontend para shape, prototype ou direção visual.

## Impeccable Critique

**N/A** — `UI impact: none`; Assessment A/B de interface não se aplica. A crítica independente relevante é operacional e está em `Design Critique`.

## Impeccable Audit

**N/A** — acessibilidade, responsividade, theming e performance visual não se aplicam a script/documentação de processo.

## Impeccable Trace

**N/A** — nenhum pipeline visual, critic de pixels ou browser gate é necessário porque não existe UI afetada.

## Prototype

**N/A** — a change não cria nem altera superfície visual; um protótipo HTML seria artificial e não validaria os gates de shell/processo.

## Prototype Validation

**N/A** — sem protótipo e sem interações de UI. A validação adequada é shell determinístico com Git temporário e `gh` fake, descrita em `Estratégia de validação`.

## Design Critique

### Escopo e produto

- **PASS** — a proposta ataca diretamente os quatro modos de falha observados: doc tardia/incompleta, kaizen após `Pronto`, cleanup sem lista e spawn vazio silencioso.
- **Correção aplicada no design** — a expressão “doc antes da release” seria incompatível com evidência final de deploy. O desenho separa o PR de código do único PR documental pós-deploy e aplica o `pre` quando a doc canônica existir.
- **Correção aplicada no design** — “data do dia” era ambígua em virada de data; `RELEASE_DATE` + default UTC cria uma chave reproduzível compartilhada por doc e kaizen-log.

### Regressão e operação

- **PASS** — o guard continua read-only quanto a refs/arquivos e fail-closed em `post`; não apaga branch nem atualiza `main` automaticamente.
- **Correção aplicada no design** — a regra antiga dizia deletar branches depois de `Pronto`, mas o novo gate precisa prová-las ausentes antes de `Pronto`. A ordem foi explicitamente invertida para evitar contradição.
- **Pendência não bloqueante** — o guard prova presença, não qualidade semântica, da entrada kaizen e da evidência escrita. Revisão humana e o contrato do Kaizen continuam necessários.

### Segurança e confiabilidade

- **PASS** — nomes de branches são validados antes de interpolação em refs; a lista vazia não passa por vacuidade; fetch falho não autoriza prova remota.
- **PASS** — `git pull --ff-only` evita merge local implícito e o guard não usa força.
- **Pendência não bloqueante** — a Task tool não é instrumentada nesta change; a regra de erro explícito é processual. O critério é satisfeito no handoff, com automação futura separada se houver recorrência.

### UI, acessibilidade e responsividade

- **N/A confirmado** — nenhum arquivo/superfície frontend está no escopo e nenhuma alteração visual ficou sem classificação.

### Achados por severidade

- P0 abertos: 0.
- P1 abertos: 0.
- P2/aceitos: 2 — qualidade semântica do texto kaizen continua humana; observabilidade de spawn é processual, não instrumentada. Ambos estão explicitamente delimitados e não impedem os critérios deste card.

### Referências avaliadas

- `scripts/release-guard`: inventário/cleanup de branches, drift de `main`, deploy evidence e seção de release docs.
- `docs/kaizen-log.md`: template e entrada de 2026-08-14, incluindo a evidência do spawn vazio.
- `docs/release-2026-08-14.md`: formato da doc canônica e seção final de deploy.
- `openspec/specs/release-worktree-hygiene/spec.md` e `openspec/specs/kaizen-continuous-improvement/spec.md`.
- Prototype: N/A, justificado acima.

**Design Agent verdict: PASS** — decisões, limites, riscos, cenários de teste e ordem operacional estão definidos sem achado bloqueante. O card ainda deve seguir `Design -> Aprovação de Design -> Pronto para Dev`; este veredito não é aprovação humana e não libera implementação.
