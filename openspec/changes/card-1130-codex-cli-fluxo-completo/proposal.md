## Why

O terminal Codex precisa conduzir o Covenant Flow inteiro com provas reais e recuperação operacional, sem depender de resíduos privados do worktree de implementação. #1130 concentra as pendências CLI de #1098/#1128; o bloqueio de #1117 é a primeira reprodução, não o limite da entrega.

## Problema

Alan precisa executar todo o Covenant Flow pelo terminal, mas a entrega do #1098 deixou etapas CLI sem comprovação completa e o refinamento do #1117 continua bloqueado antes do nascimento do agente. A separação de escopo para o #1128 incluiu etapas de terminal que Alan não pretendia excluir.

## História

Como operador, quero conduzir todo o fluxo Covenant Flow pelo terminal Codex, da criação e refinamento do card até o fechamento e a release autorizada, para trabalhar sem bloqueios de preparação não resolvidos, sem trocar de interface e sem configurar permissões manualmente a cada revisão.

## Entra

- Entregar o fluxo completo pelo terminal: criação e refinamento, priorização humana, Design e crítica, aprovação humana, Apply, dois reviewers independentes, QA, integração em develop, homologação ou não homologação e fechamento de release quando explicitamente autorizado.
- Demonstrar as etapas e suas passagens reais, incluindo retomadas em sessões novas, retornos para correção previstos no processo e preservação do trabalho após falha ou interrupção. Uma etapa implementada ou testada somente com fixtures não conta como funcionamento integral comprovado.
- Fazer o fluxo funcionar em sessões novas abertas em /source e nos worktrees corretos, resolvendo o vínculo necessário sem depender silenciosamente de arquivos privados presentes apenas no worktree de implementação ou de uma sessão anterior.
- Resolver preparo e reutilização válida das evidências, distinguindo qualificação por superfície de comprovação exigida no chat atual. Conduzir a preparação no fluxo autorizado e informar precisamente os atos reservados ao operador. Não encerrar a entrega com uma orientação genérica para realizar ensaios manualmente.
- No refinamento, conduzir perguntas e respostas no mesmo chat e atualizar o card correto. Usar o bloqueio do #1117 como caso inicial de reprodução e validação autorizada, respeitando seu estado no momento do ensaio.
- Preservar agentes nativos, seleção local de modelo/esforço, contexto isolado conforme o contrato vigente, identidade, estado, conclusão com payload e vínculo ao card/worktree/etapa. O pai orquestra sem substituir os filhos nas etapas delegadas.
- No Review, manter o principal gravável e iniciar automaticamente o coordenador somente leitura e os dois reviewers nativos, com mesmo diff e SHA verificados, leitura integral, deny/readback e pareceres completos. Exigir verify-wave e checklist aprovados antes do commit, sem alternância manual de permissões.
- Preservar gates humanos e eventos válidos da FSM, incluindo priorização, aprovação de Design e homologação/não homologação. Silêncio não é aprovação; demonstração não autoriza pular etapas.
- Demonstrar caminhos positivos e recusas pertinentes por evidência inválida, vínculo incorreto, etapa não autorizada e permissões incompatíveis, sem copiar receipts como prova de outro contexto nem afrouxar gates.
- Publicar matriz do fluxo inteiro pelo terminal com evidências reais, limitações e instruções reproduzíveis. Corrigir falhas encontradas e não declarar o fluxo integral entregue enquanto houver etapa de terminal bloqueada ou sem comprovação exigida.
- Reconciliar os registros do #1098 e #1128 com a orientação explícita de Alan: somente App/IDE ficaram fora. Coordenar pendências CLI neste card para evitar duplicação, preservando histórico e sem promover ensaios pendentes a concluídos.

## Não entra

- Qualificar App/IDE; essas superfícies continuam fora deste card.
- Alterar gates humanos, trocar modelos silenciosamente, executar etapas delegadas no pai como fallback, registrar confiança automaticamente ou declarar modo Auto.
- Ampliar suporte a outros clientes.
- Executar release ou alteração em produção sem pedido explícito próprio. O suporte ao fechamento pelo terminal faz parte da entrega; este card não concede autorização antecipada para publicar.

## What Changes

- Orquestração terminal completa com descoberta e revalidação de qualificação, preparação diagnóstica autorizada, vínculo nativo e recuperação sem perda de trabalho.
- Review automático em coordenador exec read-only e dois filhos nativos, mantendo o principal gravável.
- Matriz viva por etapa e rota, com estados de comprovação separados e fechamento posterior condicionado aos gates humanos e pedido de release.
- Distribuição nucleus → consumidor com manifests e confiança humana separada, mais reconciliação rastreável dos cards relacionados.

## Capabilities

### New Capabilities

- `codex-terminal-flow`: contrato operacional integral do terminal, rotas TUI/exec, recuperação, matriz viva e comprovação progressiva até release autorizada.

### Modified Capabilities

- `codex-runtime-evidence`: descoberta/revalidação por superfície e schema independente do worktree, mantendo contexto, identidade e autorização específicos de cada execução.

## Impact

Scripts `scripts/process-fsm/codex_evidence.py`, `codex_context.py`, `codex_review_session.py`, `codex_review.py`, proxies e testes; documentação Codex e skill canônica `covenant-flow`; distribuição no nucleus e manifests do consumidor. `process_event`, Guard, seleção local, checklist e release guards conservam suas decisões e gates. Não muda produto Cripto, banco, UI, FSM nem outros clientes. Evidências privadas continuam fora do Git e publicações recebem somente resumos sanitizados.
