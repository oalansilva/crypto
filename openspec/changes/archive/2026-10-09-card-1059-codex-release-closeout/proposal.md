## Why

A motivação de produto é a seção `## Problema` abaixo, copiada literalmente do issue #1059. Este arquivo não reescreve essa história.

## Problema

Na release de 26/09/2026, concluída em 27/09, o Codex interrompeu repetidamente um fechamento já solicitado por Alan. Houve perguntas redundantes, interpretação excessivamente restritiva da autorização, diagnóstico incompleto e defeitos nos helpers. Alan precisou reiterar que o agente deveria registrar comentários e concluir a release.

Card filho de #1042, solicitado por Alan após a auditoria do histórico completo disponível. O objetivo é corrigir a paridade operacional do fechamento entre Codex e Cursor, preservando a FSM e os gates humanos.

## História

Como Alan, quero que uma release explicitamente solicitada prossiga até o fechamento com autonomia nas tarefas operacionais já autorizadas, perguntando apenas sobre decisões realmente ausentes, para não precisar repetir instruções nem transportar manualmente o contexto entre sessões e modelos.

## Entra

- Autonomia operacional, deduplicação e persistência das decisões/perguntas no Codex.
- Contrato canônico de release compartilhado entre clientes, com adaptações mínimas por ferramenta.
- Preflight completo, manifesto retomável e identidade do contexto de validação/T16.
- Diagnósticos acionáveis, evidências completas e idempotentes e verificação antecipada de integração.
- Coordenação com #1022, sem duplicar silenciosamente a implementação do defeito de archive.
- Testes de regressão e ensaio comparável nos dois clientes.

### Critérios observáveis

- [ ] Um pedido explícito de release leva o agente pelas tarefas operacionais normais de fechamento até a conclusão ou um bloqueio real explicado, sem reconfirmar ações já autorizadas ou dados disponíveis. A decisão humana de homologar e os demais gates permanecem obrigatórios.
- [ ] Homologação humana comprovada gera o comentário canônico pelo agente sem nova aprovação. O registro da evidência não é confundido com a própria decisão de homologar nem com a aprovação de Design.
- [ ] Antes de perguntar por responsáveis ou classificação, o agente reconcilia as fontes disponíveis e registra a origem de cada valor. Uma decisão humana explícita e inequivocamente atribuída ao card prevalece sobre inferências; resposta sem distribuição clara entre cards ou fontes incompatíveis continua sendo lacuna, nunca decisão atribuída a Alan.
- [ ] As lacunas reais conhecidas do pacote aparecem em uma consulta consolidada, com o valor faltante identificado por card. Respostas já dadas não são perguntadas novamente após retomada ou compactação. Silêncio ou ausência de resposta não resolve decisão pendente; tarefas independentes já autorizadas podem continuar.
- [ ] As perguntas são aceitas pela ferramenta disponível no cliente; nenhuma das seis falhas de formato relatadas se repete. Se a ferramenta não estiver disponível, as mesmas escolhas são apresentadas em texto, sem perder alternativas ou tratar a recomendação como aceita.
- [ ] A retomada preserva pacote, decisões, origem dos valores, evidências e etapas concluídas, revalida o que puder ter mudado e continua da primeira etapa incompleta. Não exige que Alan transporte manualmente esse contexto nem volta a buscar credenciais já disponíveis; segredos não são copiados para o registro da release.
- [ ] Para changes concluídas, sync e archive seguem o fechamento solicitado sem menu genérico de reconfirmação. Conflito sem resolução, descarte ou exceção que exija decisão humana é apresentado como tal. O caminho legítimo para archive é coordenado com #1022, sem implementação duplicada e sem liberar produto ou pacote/card não resolvido.
- [ ] As verificações possíveis antes da publicação identificam pendências de comentários, campos, documentação, archive, duplicação, integração, contexto de trabalho e disponibilidade do modelo. Verificações que dependem do deploy continuam ocorrendo na etapa correspondente; preflight não é anunciado como execução de uma etapa ainda não iniciada.
- [ ] Uma negativa informa a operação e o contexto realmente avaliados, a causa e a ação corretiva cabível. Uma operação negada não é apresentada como prova de que outra também é proibida; T16 não exige repetir uma verificação apenas para descobrir a causa já conhecida do bloqueio.
- [ ] Preflight, post e T16 identificam o pacote e o contexto de validação. Evidência produzida em outro contexto ou invalidada por mudanças não autoriza o fechamento; a divergência é explicada e a validação pertinente é refeita no contexto correto.
- [ ] Antes de T16, todas as changes concluídas do pacote têm as pós-condições de sync e archive verificadas, inclusive enquanto os cards ainda estão Homologado. Duplicação ativa/arquivada impede aceitar o fechamento com evidência inconsistente.
- [ ] T16 publica comentários com os dados reais do pacote e das branches, sem placeholders. Evidência existente incompleta é atualizada de forma idempotente; repetir a operação não cria comentários duplicados nem exige correção manual posterior.
- [ ] Runtime, modelo e esforço são verificados por turno a partir de evidência disponível. Divergência ou indisponibilidade é informada sem troca silenciosa nem alteração do mapa; quando a ferramenta suporta encaminhamento, a sessão adequada recebe o contexto preservado. Quando não suporta, o bloqueio e o handoff necessário ficam explícitos, sem alegar encaminhamento realizado.
- [ ] A integração é verificada antes da CI do PR e a documentação final é agrupada conforme o fechamento vigente. A proposta de checks proporcionais para alterações estritamente documentais explicita a cobertura e a regressão necessárias, preservando as proteções exigidas.
- [ ] O replay do cenário desta release, com #1042 fora do pacote, duplicação de #1017 e alterações locais alheias, preserva esse trabalho e não promove conteúdo não homologado. As regressões cobrem continuidade, retomada, decisões ambíguas, contexto divergente e evidência incompleta.
- [ ] Um ensaio comparável em Cursor e Codex apresenta a mesma decisão operacional: zero perguntas evitáveis, consulta consolidada quando faltar decisão real e continuidade até conclusão ou bloqueio externo explicado. Diferenças de ferramenta não criam novos gates humanos; as regras compartilhadas e as adaptações necessárias ficam coerentes.

## Não entra

- Pular Design, aprovação humana, QA, homologação ou T16; mover cards por fora da FSM.
- Homologar em nome de Alan, interpretar silêncio como aprovação, descartar trabalho alheio ou ignorar deny.
- Implementar diretamente neste registro, modificar produto ou reabrir a release concluída.
- Reivindicar modo Auto ou trocar modelo silenciosamente.
- Publicar transcripts privados, conteúdo de sessões ou credenciais; usar apenas IDs e evidência agregada.

## What Changes

- Contrato canônico de fechamento de release compartilhado entre Cursor e Codex: autonomia nas tarefas operacionais já autorizadas, pergunta só quando falta decisão real, manifesto retomável e o mesmo contexto em preflight, post e T16.
- Diagnóstico da operação realmente avaliada, evidência de Pronto completa e idempotente, e verificação de sync/archive das changes concluídas do pacote antes de T16, enquanto os cards ainda estão Homologado.
- Adaptação mínima por ferramenta para perguntas e para o par de modelo/esforço já definido no mapa; sem mapa novo, sem modo Auto e sem fallback silencioso.
- Coordenação com #1022: este card consome o caminho oficial de archive e não implementa de novo o defeito do guard.
- Testes de regressão do cenário auditado e ensaio comparável nos dois clientes. Nenhuma tela, rota ou código de produto.

## Capabilities

### New Capabilities

- `release-closeout-autonomy`: autonomia operacional, perguntas, manifesto, diagnóstico, evidência, preflight, contexto de T16 e ensaio comparável do fechamento.

### Modified Capabilities

- `covenant-flow`: a seção Release do runbook deixa de tratar o menu genérico de archive como confirmação obrigatória, deixa de chamar de T18 o pré-requisito de modelo do pai e alinha a ordem de limpeza de branches ao gate já existente, sem crescer `AGENTS.md` nem criar evento de FSM.

## Impact

Runbook `covenant-flow`, frases de release do overlay que contradizem esse contrato, `scripts/release-guard`, a mensagem de `fechar_release` e o comentário de T16, o helper de evidência de card e testes do harness. Sem código de produto, sem aresta nova na FSM, sem alteração do mapa de modelos e sem segunda implementação do archive de #1022.
