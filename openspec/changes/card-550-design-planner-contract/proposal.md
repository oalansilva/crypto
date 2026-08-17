## Why

O contrato atual do `design-planner` não garante a autoria que o gate de Design exige. O agente recebe `proposal.md` como entrada e apresenta apenas `design.md` como saída, embora as regras do projeto atribuam a ele a autoria de `proposal.md`, `specs/**`, `design.md` e `tasks.md`. Como consequência, a sessão principal pode acabar redigindo artefatos ao executar o fluxo acelerado, tornando a evidência de autoria ambígua.

Também há divergências entre configuração e execução. O frontmatter declara `reasoningEffort: high`, mas o runtime observado registrou a variante padrão; no OpenCode, a seleção precisa ocorrer por `variant`. Além disso, critics protegidos apenas por `permission.edit: deny` ainda podem dispor de caminhos de mutação ou efeito externo, como shell, Git/GitHub, rede e nova delegação. Essa proteção não demonstra isolamento read-only real nem independência entre avaliações.

O card #555 depende de um contrato permanente e verificável antes de migrar o fluxo amplo. Sem esta base, continuar a migração permitiria autoria pela sessão errada, execução com variante divergente ou críticas com capacidades incompatíveis com o papel read-only.

## What Changes

- Tornar o `design-planner` o autor obrigatório dos quatro grupos de artefatos do gate: `proposal.md`, `specs/**`, `design.md` e `tasks.md`, além do protótipo quando a classificação de UI o exigir.
- Fixar a execução designada em `model: openai/gpt-5.6-sol` e `variant: high`; configuração declarada e evidência observada no runtime devem coincidir.
- Restringir a sessão principal à orquestração: criar somente o scaffold da change, obter instructions, templates e contexto, delegar a autoria em estágios compatíveis com as dependências dos artefatos e, ao final, validar, publicar e mover o status permitido pelo fluxo. A sessão principal não redige nem completa os artefatos delegados.
- Definir uma allowlist de escrita para o author limitada aos artefatos da change e, quando aplicável, ao diretório canônico do protótipo. Qualquer escrita fora desses caminhos deve ser negada.
- Executar cada critic em contexto separado e efetivamente read-only, sem capacidade de editar, executar comandos mutantes, operar Git/GitHub, usar rede ou delegar novos agentes. O isolamento deve ser comprovado por capacidades observadas e testes negativos, não apenas por instrução textual.
- Registrar evidência runtime correlacionável para cada estágio: identidade e sessão do author, task, modelo, variante, capability ativa e patches produzidos. A evidência deve permitir distinguir autoria do planner de aplicação ou validação pela sessão principal.
- Exigir sessão nova para validar o contrato e impedir reaproveitamento de sessões/spawns iniciados antes da configuração vigente.
- Tratar indisponibilidade, spawn vazio, evidência ausente, divergência de modelo/variante/capability, patch fora da allowlist ou tentativa de mutação por critic como falha fechada: `BLOCKED`, sem fallback silencioso nem avanço de gate.
- Adicionar testes de permissão, isolamento e autoria que cubram o caminho positivo e as negações críticas, incluindo atribuição dos patches e rejeição de capacidades proibidas.
- Manter fora deste card a migração ampla do #555 e quaisquer gates de implementação relacionados a apply/verify.

## Capabilities

### New Capabilities

- `design-planner-routing`: contrato de roteamento, autoria staged, capacidades allowlisted, isolamento read-only dos critics e evidência runtime fail-closed para o gate de Design executado pelo `design-planner` designado.

### Modified Capabilities

Nenhuma.

## Impact

- **Configuração e contrato do OpenCode:** o agent e o orquestrador precisarão representar `variant: high`, fronteiras explícitas de capacidade e autoria por estágio sem permitir que a sessão principal assuma o conteúdo.
- **Evidência operacional:** logs/metadados do runtime e patches passam a fazer parte do critério de validade do gate, com correlação suficiente para auditoria de author, sessão e task.
- **Testes:** serão necessários testes positivos de autoria nos quatro grupos de artefatos e testes negativos para escrita fora da allowlist, mutação/delegação/rede por critics, sessão antiga, spawn vazio e divergências de execução.
- **Compatibilidade:** fluxos que hoje dependem da sessão principal para redigir artefatos ou de `reasoningEffort` sem variante explícita deverão falhar até aderirem ao novo contrato. A migração dos consumidores permanece no #555.
- **Riscos:** uma allowlist incompleta pode bloquear artefatos legítimos; uma allowlist ampla pode reabrir mutações indevidas; evidência não correlacionada pode atribuir autoria incorretamente; e sessões preexistentes podem mascarar a configuração nova. Os testes de capacidades, autoria, patches e fresh session devem cobrir esses casos.
- **Dependência/bloqueio:** o #555 permanece bloqueado até este contrato estar implementado, validado em sessão nova e com evidência runtime completa. Qualquer falha fechada descrita acima mantém o fluxo em `BLOCKED`.
- **UI impact:** none — esta change altera contrato de agentes, roteamento, permissões e evidência, sem criar ou modificar superfície visual do produto.
- **Prototype:** N/A — não existe interface a prototipar neste escopo.
- **Gate humano:** obrigatório. Mesmo com UI impact none, o card deve passar por `Design -> Aprovação de Design` e somente Alan pode promovê-lo para `Pronto para Dev`; este proposal não concede aprovação nem autoriza implementação.
