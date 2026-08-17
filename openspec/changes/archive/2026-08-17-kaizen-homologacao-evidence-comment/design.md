## Contexto

- Card: `#480`
- Change: `kaizen-homologacao-evidence-comment`
- Status observado no packet: `Design`
- **UI impact: none** — a mudança é restrita a scripts e documentação operacional (`release-guard`, helper de comentários, `AGENTS.md` e log Kaizen), sem frontend, tela, interação visual, runtime de API ou banco de dados.

## Problema

O fluxo permite que um card seja homologado por Alan via chat ou arraste no board sem executar o helper que publica a evidência canônica `Homologado por Alan na develop.`. Na release de 2026-08-11, isso ocorreu em 5 de 5 cards e repetiu um achado anterior de auditoria.

Hoje há duas lacunas complementares:

1. a transição operacional não garante a publicação do comentário; e
2. o closeout não detecta sua ausência para os cards do pacote.

Assim, o status pode estar correto, mas a trilha auditável exigida pelo processo fica incompleta.

## Hipótese

Se o helper permitir uma recuperação retroativa segura e verificável, e o `release-guard` conferir a presença do marcador canônico nos cards explicitamente informados em `RELEASE_CARDS`, então omissões serão corrigíveis sem duplicação e não voltarão a passar silenciosamente pelo closeout de uma release.

## Resultado esperado

- `release-guard audit`, quando executado com `RELEASE_CARDS`, lista como warning cada card elegível sem a evidência canônica.
- `release-guard post`, quando executado com `RELEASE_CARDS`, trata a mesma ausência ou a impossibilidade de verificá-la como blocker.
- Cards em `Homologado` ou `Pronto` são cobertos, permitindo validar tanto antes quanto depois da promoção final.
- O helper oferece preview por `--dry-run` e mantém dedupe por transição, inclusive para comentários legados sem referência reconhecível de commit.
- Os cards 456, 457, 458, 463 e 464 podem receber a evidência retroativa uma única vez, após dry-run e confirmação de que Alan de fato os homologou.
- Nenhum comportamento de frontend, API, banco de dados ou runtime do produto muda.

## Decisões de design

### 1. Escopo do guard por pacote explícito

A validação de comentário será executada somente em `post` e `audit` e terá `RELEASE_CARDS` como lista autoritativa do pacote. Não será feita uma varredura bloqueante de todo o histórico do board.

- Com `RELEASE_CARDS` definido, cada valor deve ser um número de card válido; entradas inválidas, card não encontrado ou consulta inconclusiva são falhas de verificação.
- Duplicatas na lista devem ser normalizadas para que um card seja consultado e reportado uma única vez.
- Para cards selecionados, o check se aplica quando o status observado for `Homologado` ou `Pronto`.
- `audit` usa severidade de warning e permanece diagnóstico.
- `post` usa severidade blocker e falha fechado quando a evidência está ausente ou não pode ser consultada.
- `pre` não executa o check, pois a homologação pode ainda não estar consolidada para o pacote de publicação.
- Sem `RELEASE_CARDS`, o guard registra warning de que a verificação do pacote foi pulada, preservando retrocompatibilidade; não infere quais cards pertencem à release.

Essa decisão acompanha o padrão já usado pela validação dos campos `Responsável`, `Prioridade` e `Tipo`, mantendo o closeout determinístico e evitando dívida legada fora do pacote como falso bloqueio.

### 2. Critério canônico de presença

Um card satisfaz a evidência quando ao menos um comentário contém, por comparação fixa e sem distinção de maiúsculas/minúsculas, o marcador:

`Homologado por Alan na develop.`

O guard deve consultar todos os comentários disponíveis do card, com paginação quando a API usada a exigir. Falha de autenticação, API, paginação ou JSON não pode ser interpretada como “comentário ausente” nem como sucesso: deve ser reportada como verificação indisponível, respeitando a severidade do modo.

O guard apenas verifica; ele não publica comentários nem altera status.

### 3. Recuperação retroativa pelo helper existente

O caminho de reparo continua sendo `scripts/post-card-evidence-comment.sh --transition homologado`, sem introduzir um segundo publicador.

- `--dry-run` deve executar validação de argumentos, leitura de comentários e dedupe, mostrar exatamente o corpo pretendido e terminar sem escrita.
- A execução real ocorre somente após um dry-run revisado e evidência prévia de que Alan homologou o card; o script não cria nem presume aprovação humana.
- O contrato atual de `--commit` é preservado para compatibilidade entre transições. Como o template de `homologado` não imprime referência de commit, o marcador da transição é a chave efetiva para comentários ref-less.
- Um comentário existente com o mesmo marcador bloqueia nova postagem, mesmo sem SHA reconhecível. Quando houver referência reconhecível, a normalização de SHA curto/longo continua válida.
- Falha ao listar comentários permanece fail-closed: não postar quando não for possível provar que não existe duplicata.

Para a recuperação de 2026-08-11, os cards 456, 457, 458, 463 e 464 são processados individualmente: primeiro dry-run, depois execução real, e por fim validação pelo guard com o pacote explícito.

### 4. Dedupe por transição, não por release

A unidade de idempotência é `card + transition marker`, e não `card + release`. A homologação representa uma decisão funcional única no fluxo normal; uma reexecução de release ou um reparo posterior não deve gerar uma segunda declaração equivalente.

Se futuramente o processo admitir revogação e nova homologação formal, isso exigirá uma mudança específica de contrato em vez de enfraquecer silenciosamente o dedupe atual.

### 5. Localização e saída operacional

O novo check deve ficar junto à seção de documentos/campos do board do `release-guard`, pois todos validam evidências de closeout vinculadas a `RELEASE_CARDS`. A saída deve:

- identificar o número de cada card sem evidência;
- distinguir ausência de comentário de indisponibilidade da consulta;
- orientar o operador a revisar a homologação humana e usar o helper com `--dry-run` antes da postagem;
- não incluir conteúdo sensível de comentários na saída.

### 6. Mudanças documentais

`AGENTS.md` deve deixar explícito que a promoção para `Homologado` inclui o comentário via helper e que uma homologação registrada em chat/arraste precisa da mesma evidência. `docs/kaizen-log.md` registra a recorrência e o reparo dos cinco cards, sem transformar o log em fonte alternativa de aprovação.

## Escopo e não escopo

### Incluído

- detecção do comentário nos cards do pacote em `post/audit`;
- severidade por modo;
- recuperação retroativa idempotente via helper;
- documentação da obrigação e do achado recorrente.

### Excluído

- automação de transições no board;
- inferência de que Alan homologou um card;
- postagem automática pelo `release-guard`;
- alteração de templates de `Done` ou `Pronto` além do necessário para compatibilidade;
- frontend, protótipo, API, banco de dados, serviços e deploy.

## Riscos e mitigação

| Risco | Severidade | Mitigação/decisão |
|---|---:|---|
| Postagem duplicada durante reparo ou retry | Alta | Leitura prévia fail-closed e dedupe por marcador da transição; dry-run antes da escrita. |
| Comentário afirmar homologação sem decisão real de Alan | Alta | O helper é somente registrador de evidência; uso retroativo exige confirmação humana preexistente e o guard nunca auto-publica. |
| Closeout passar sem conferir cards por `RELEASE_CARDS` ausente | Média | Warning explícito e orientação para exportar o pacote; compatibilidade preservada. A obrigatoriedade operacional de fornecer a variável permanece documentada. |
| Falso negativo por comentários paginados | Alta | Consulta paginada; falha/incompletude vira verificação indisponível, não sucesso. |
| Falso negativo por pequena variação textual | Baixa | Comparação fixa case-insensitive do marcador canônico. Variações não canônicas devem ser reparadas pelo helper, preservando auditabilidade determinística. |
| Card histórico fora do pacote bloquear a release | Média | Verificação bloqueante limitada à lista explícita de `RELEASE_CARDS`. |
| Regressão do `release-guard` para operadores existentes | Média | Check somente em `post/audit`; ausência da variável gera warning, não varredura histórica nem novo blocker global. |
| Entrada malformada em `RELEASE_CARDS` afetar filtros/comandos | Média | Aceitar somente IDs numéricos, normalizar e rejeitar valores inválidos antes de montar consultas. |
| API/GitHub indisponível ser tratado como aprovação | Alta | Fail-closed com `RELEASE_CARDS`: warning em `audit`, blocker em `post`. |

## Prototype

N/A — `UI impact: none`; a mudança não cria nem altera superfície visual, portanto um protótipo navegável não representaria o comportamento de tooling a ser validado.

## Prototype Validation

N/A — não há protótipo ou interação de UI. O gate de navegador desktop/mobile não se aplica a scripts CLI; a validação futura deverá ser técnica e focada em dry-run, dedupe e resultados `audit/post`, fora desta etapa de Design.

## Impeccable Brief

N/A — não existe interface de usuário, direção visual, responsividade ou estado de tela a modelar. O contrato relevante é operacional e está descrito nas decisões do guard e do helper.

## Impeccable Critique

N/A — Assessments visuais A/B não se aplicam porque nenhuma superfície frontend é criada ou alterada. A crítica independente de escopo e riscos operacionais consta em `Design Critique`.

## Impeccable Audit

N/A — acessibilidade visual, performance de frontend, theming e responsividade não são afetados. Os riscos auditáveis são integridade, idempotência e fail-closed do tooling.

## Impeccable Trace

N/A — o pipeline Impeccable (`context -> shape -> prototype -> critique -> audit -> targeted fixes -> polish -> browser gate`) é reservado a `UI impact: affected`. Nenhum `DESIGN.md`, protótipo ou código visual foi criado ou modificado.

## Design Critique

### Referências avaliadas

- `proposal.md` da change;
- comportamento atual de `scripts/release-guard`, especialmente modos, função de severidade e validação condicionada a `RELEASE_CARDS`;
- comportamento atual de `scripts/post-card-evidence-comment.sh`, incluindo transições, marcador canônico, dry-run, dedupe e falha fechada;
- `Prototype: N/A`, justificado por `UI impact: none`.

### Crítica independente read-only

| Dimensão | Achado | Severidade | Disposição |
|---|---|---:|---|
| Produto/processo | Detectar ausência sem oferecer reparo seguro deixaria o closeout bloqueado sem caminho operacional. | Alta | Resolvido no design ao manter um único caminho de reparo via helper, com dry-run e dedupe. |
| Integridade | Postar automaticamente a partir do guard confundiria ausência de registro com ausência de aprovação e poderia atribuir decisão a Alan indevidamente. | Bloqueante | Evitado: guard somente detecta; postagem exige homologação humana preexistente. |
| Escopo | Verificar todo o board criaria blockers por dívida legada não pertencente ao pacote. | Alta | Resolvido com escopo autoritativo por `RELEASE_CARDS`. |
| Confiabilidade | Uma consulta parcial ou falha do GitHub poderia produzir falso PASS. | Bloqueante | Resolvido por paginação e fail-closed quando o pacote está definido. |
| Compatibilidade | Tornar a variável imediatamente obrigatória dentro do script poderia quebrar execuções históricas não preparadas. | Média | Aceito como warning quando ausente; a exigência permanece no procedimento de closeout. |
| Idempotência | O template de homologação não contém SHA, embora a interface requeira `--commit`. | Média | Aceito para compatibilidade: comentário ref-less deduplica pelo marcador; uma mudança de CLI mais ampla fica fora do escopo. |
| Segurança de entrada | IDs interpolados sem validação podem quebrar filtros e tornar o resultado ambíguo. | Média | Resolvido na decisão de aceitar somente números e normalizar duplicatas. |
| UI/UX | Nenhuma superfície visual nova ou alterada foi encontrada no escopo declarado. | Nenhuma | Classificação `UI impact: none` confirmada; Prototype e Impeccable são N/A. |

### Pendências não bloqueantes

- A efetividade do blocker depende de o operador exportar `RELEASE_CARDS`, como já exige o processo de fechamento. Tornar a ausência da variável um blocker global pode ser avaliado separadamente após observar compatibilidade operacional.
- Uma futura necessidade de re-homologação após revogação exigirá versionar o contrato de evidência; não deve ser simulada com comentários duplicados hoje.

Não há achados P0/P1 abertos no escopo de design. As decisões são coerentes com o comportamento atual dos scripts e não deixam alteração visual sem classificação.

**Design Agent verdict: PASS**

## Handoff

- Entrega pronta para a sessão principal consolidar e solicitar `Design -> Aprovação de Design`.
- Nenhuma movimentação de board foi executada por este agente.
- Alan continua sendo o único responsável por aprovar `Aprovação de Design -> Pronto para Dev`.
- Implementação permanece bloqueada até essa aprovação humana.
