## Problema

O fechamento de #509 ficou tecnicamente correto no código publicado, mas incompleto como closeout verificável. Há três fatos a reconciliar: (1) as tasks 5.1–5.4 e o archive foram regularizados depois da auditoria; (2) a redução GraphQL de aproximadamente 4.900 para 204 pontos está registrada, mas precisa permanecer vinculada ao comando/run; e (3) uma falha de snapshot não pode ser transformada em evidência de que a branch está “em andamento” e, por isso, preservada.

O usuário operacional afetado é quem executa o closeout e precisa decidir, sem falso positivo, se cards podem avançar e se refs antigas podem ser removidas.

**UI impact: none.** A change é restrita a scripts/testes operacionais, OpenSpec, evidência e refs Git; nenhuma superfície visual é criada ou alterada.

## Hipótese

Se a indisponibilidade do board for representada explicitamente como estado desconhecido, coberta por asserts negativos contra `preserved`, e se a limpeza for dirigida por um manifest nominal com prova de equivalência por branch, então o closeout deixará de aceitar tanto o fail-open remoto quanto deleções baseadas em inferência incompleta.

## Resultado esperado

- A evidência histórica de #509 fica reconciliada e rastreável.
- `post` bloqueia quando o board não é autoritativo; `audit` diagnostica a mesma causa; nenhum modo chama o estado desconhecido de preservação válida.
- Uma execução real consome no máximo aproximadamente 500 pontos GraphQL, com medição antes/depois e contexto suficiente para auditoria.
- Todas as 17 branches históricas são enumeradas e provadas ausentes local/remotamente ou ficam classificadas com autorização explícita.
- O fechamento termina com validação OpenSpec global verde e audit sem warnings das branches do pacote.

## Escopo e não escopo

### Em escopo

- Verificação do archive, tasks e sync da change #509.
- Teste focado com fake `gh`, incluindo asserts positivos e negativos da saída.
- Medição única do delta GraphQL.
- Recuperação do manifest e limpeza segura das refs da release 2026-08-14.
- Handoff com comandos, hashes, resultados e autorizações.

### Fora de escopo

- Nova política de release, retry/polling do GitHub ou cache persistente.
- Mudança de status de card, aprovação humana, release/deploy ou restart.
- Deleção de branches de cards atuais fora do manifest da release.
- Alteração planejada de código do guard. Falha dos asserts é blocker de implementação e exige reconciliação explícita do escopo, não relaxamento do critério.
- Qualquer alteração de UI/UX.

## Decisões

### D1 — Provar `BOARD_STATE=failed` pela fronteira pública do processo

O teste não exportará `BOARD_STATE` diretamente, pois o script inicializa esse global. O fake `gh` retornará snapshot de Project ausente, inválido, incompleto ou com exit code não zero, fazendo `ensure_board_snapshot` definir `BOARD_STATE=failed` pelo caminho real.

O fixture criará ao menos uma branch reconhecível, por exemplo `change-100-a`, e fornecerá snapshot de PRs válido. A matriz mínima será:

| Modo | Assert positivo | Assert negativo |
| --- | --- | --- |
| `post` | `returncode != 0`; `BLOCKER: board snapshot failed or invalid`; causa original visível | ausência de `preserved (card in flight; not deleted)` e de qualquer classificação `preserved` para `change-100-a` |
| `audit` | `returncode == 0`; `WARN: board snapshot failed or invalid`; estado remoto desconhecido explícito | ausência de `preserved (card in flight; not deleted)` e de qualquer classificação `preserved` para `change-100-a` |

O retorno não zero do `post` é a prova de bloqueio; o guard não move cards. A saída deve continuar útil para diagnóstico, mas jamais converter `unknown` em estado de negócio conhecido. Reaproveitar os testes existentes de falha global não basta sem os asserts negativos ligados a uma branch.

### D2 — Não mascarar divergência entre requisito e implementação

A leitura estática mostra blocker/warning global em `snapshot_issue`, mas também mostra que `card_is_terminal` retorna falso para `unknown` e que o inventário pode cair no rótulo `preserved (card in flight; not deleted)`. O teste de D1 decide o estado real. Se falhar, o card permanece bloqueado para closeout; não se altera o assert nem se aceita o blocker global como substituto da semântica de inventário.

### D3 — Medir GraphQL uma única vez, em janela controlada

Registrar, no mesmo handoff:

1. UTC, commit do guard, modo, variáveis relevantes e identidade do run.
2. `graphql.remaining`, `limit` e `reset` imediatamente antes.
3. Uma única execução real do guard, sem repetição para “melhorar” o número.
4. Os mesmos campos imediatamente depois.
5. `delta = remaining_antes - remaining_depois`, resultado do guard e contagens observáveis de `item-list`, `pr list` e páginas de idade.

Executar em janela sem outra automação conhecida usando a mesma credencial. Caso haja consumo concorrente, classificar a medição como inconclusiva em vez de atribuir todo o delta ao guard. A referência histórica de 204 pontos e o baseline de aproximadamente 4.900 ficam citados, mas a aceitação requer delta observado de no máximo aproximadamente 500 em uma execução identificada.

### D4 — Manifest nominal antes de qualquer deleção

O número “17” não é um manifest. Recuperar da saída original do guard/handoff da release os 17 nomes exatos e persistir a tabela abaixo no handoff: `branch`, `card`, `local SHA`, `remote SHA`, `worktree`, `patches exclusivos`, `árvore equivalente`, `autorização`, `ação`, `prova pós-ação`.

O snapshot read-only deste Design já mostra que as três branches “not merged” citadas e as branches óbvias dos cards da release não aparecem nas refs atuais, mas isso não prova a lista histórica inteira. Branches atuais 469/502/503/504/516/517/518 não podem ser incluídas por semelhança de prefixo.

### D5 — Critério seguro por branch

Após atualizar/prunar refs remotas, selecionar a ref local ou `origin/<branch>` e registrar o tip antes da ação. Considerar integrada apenas quando pelo menos uma prova verificável se sustentar:

- tip ancestral de `origin/develop`; ou
- árvore idêntica à de `origin/develop`; ou
- `git cherry origin/develop <ref>` sem commits `+`; ou
- para os arquivos tocados desde o merge-base, diff material vazio contra `origin/develop`.

Também verificar worktrees antes da remoção. Branch integrada usa deleção segura local; `-D` só é permitido para branch sem integração quando houver comparação de árvore/patch, ausência de conteúdo que deva ser preservado e autorização explícita de Alan vinculada ao nome e SHA. Esse requisito é obrigatório para `change-470-walk-forward-gate`, `change-482-kaizen-board-issue-rename-note` e `card-480-kaizen-guard-homologacao` se qualquer ref reaparecer após o fetch.

Depois da ação, executar novo prune e provar para cada nome: ausência em `refs/heads/<branch>` e resposta vazia de `git ls-remote --heads origin refs/heads/<branch>`. Não usar apenas `git branch -a` como prova final.

### D6 — Separar evidência já concluída de validação atual

O archive e as tasks 5.1–5.4 podem ser aceitos pela presença versionada dos artefatos e pelo log de 2026-08-14. Já `openspec validate --all`, teste focado e guard audit precisam ser executados novamente no fechamento deste card e registrados como resultados atuais, terminais e não presumidos.

## Riscos e mitigação

- **P1 — Falso `preserved` apesar de blocker global:** os asserts negativos de D1 tornam a contradição observável; falha bloqueia o closeout.
- **P1 — Manifest incompleto causar falsa limpeza:** nenhuma deleção/aceitação começa sem os 17 nomes; a amostragem atual é apenas baseline.
- **P1 — Perda de commit exclusivo em branch “not merged”:** registrar SHA, `git cherry`, árvore e diff; exigir autorização nominal antes de deleção forçada.
- **P2 — Consumo concorrente contaminar a medição:** janela controlada, timestamps e resultado inconclusivo em caso de concorrência.
- **P2 — Ref remota rastreada ficar stale:** fetch/prune antes da análise e `git ls-remote` depois da ação.
- **P2 — Limpeza capturar card em voo:** operar exclusivamente sobre o manifest histórico; bloquear branch com worktree ativa ou fora da autorização.
- **P2 — Evidência histórica ser confundida com validação atual:** separar claramente “verificado no archive/log” de “executado neste card”.

## Prototype

N/A. `UI impact: none`: não existe tela, protótipo, HTML, rota ou interação visual neste escopo.

## Prototype Validation

N/A. Não há superfície visual nem protótipo; browser gate desktop/mobile e asserts Playwright de UI não se aplicam. A validação relevante é CLI/teste focado e está descrita em D1–D6.

## Impeccable Brief

N/A. A change não possui contexto, direção ou estados de interface; é exclusivamente operacional.

## Impeccable Critique

N/A. Assessments A/B de UI não se aplicam porque nenhuma superfície visual é afetada. A crítica operacional independente está em `Design Critique`.

## Impeccable Audit

N/A. Acessibilidade, responsividade, theming, performance de frontend e integridade visual não são afetados.

## Impeccable Trace

N/A. Nenhum `context`, `shape`, protótipo, polish ou browser gate visual foi executado, justificadamente por `UI impact: none`.

## Design Critique

- **Produto/escopo — PASS:** o plano fecha a dívida do #509 sem reabrir política de release, deploy ou UI.
- **Correção operacional — achado P1 tratado no design:** blocker global e classificação por branch são provas diferentes. D1 exige ambos e impede aceitar `unknown` como `preserved`.
- **Segurança de dados Git — PASS com gate explícito:** D4/D5 proíbem deleção por contagem ou nome aproximado e exigem prova por SHA/árvore/patch, worktree e autorização.
- **Auditabilidade — achado P1 tratado no design:** a doc da release não contém os 17 nomes. Recuperar e versionar o manifest é requisito, não pendência opcional.
- **Medição — PASS com ressalva controlada:** D3 evita repetir o guard e reconhece contaminação da cota compartilhada como resultado inconclusivo.
- **Regressão de produto — PASS:** nenhuma superfície visual, comportamento de trading, dado de usuário ou serviço é afetado.
- **Testabilidade — PASS:** a matriz tem retorno, mensagens positivas e ausência de rótulos proibidos; archive, refs e custo têm provas observáveis separadas.
- **Achados abertos no design:** nenhum P0/P1. A implementação ainda precisa demonstrar os critérios; falha do teste ou manifest irrecuperável mantém o card em execução/bloqueado e não reduz o aceite.
- **Referências avaliadas:** archive `2026-08-14-card-509-release-guard-graphql-budget`, `docs/kaizen-log.md` linhas 271–283, `docs/release-2026-08-14.md`, `scripts/release-guard` (snapshots, `branch_merged` e inventário), teste focado existente e fotografia atual de refs/worktrees. Prototype N/A justificado.

Design Agent verdict: PASS
