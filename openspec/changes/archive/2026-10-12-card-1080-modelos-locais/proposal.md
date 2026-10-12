## Problema
Alan precisa trocar os modelos e, quando suportados, os esforços dos agentes nos diferentes harnesses sem gerar um card, commit e release a cada escolha operacional, mantendo as regras do processo versionadas e verificáveis.

## História
Como operador dos agentes nos harnesses suportados pelo processo, incluindo Codex e Cursor, quero escolher o modelo e os parâmetros de esforço suportados por cliente e faixa de juízo ou execução numa configuração local da máquina, compartilhada entre os repositórios, para que cada novo agente use minha escolha sem exigir alteração no Git a cada troca.

## Entra
- Separar a seleção operacional de modelos e esforços das regras do processo em todos os harnesses suportados, incluindo Codex, Cursor e Grok: a escolha fica fora do Git, compartilhada pelos repositórios da mesma máquina e distinguida por cliente e faixa de juízo ou execução; papéis, regras e validações continuam versionados.
- Na migração, preservar as escolhas atuais de cada cliente. Para Codex, os valores iniciais desejados são GPT-6 Astra com esforço medium para juízo e GPT-6.1 Sol com esforço high para execução. Esses valores não se aplicam automaticamente aos demais clientes.
- Depois de alterar uma escolha local, o próximo agente do cliente e da faixa correspondentes, em qualquer repositório que use esse processo na mesma máquina, recebe explicitamente o modelo e os parâmetros suportados configurados, sem precisar de card, commit ou release para essa troca operacional.
- Consultar a escolha vigente a cada novo agente; agentes já em andamento mantêm a escolha com que foram iniciados. A troca para um cliente ou faixa não altera as escolhas dos demais.
- Respeitar as capacidades de cada harness: configuração de esforço somente onde houver suporte, sem presumir os mesmos modelos, valores ou capacidades entre clientes. Uma escolha incompatível com o cliente deve falhar de modo visível.
- Quando a configuração necessária estiver ausente ou inválida, a solicitação do agente falha de modo visível, sem substituição silenciosa de modelo ou esforço.
- Registrar separadamente a escolha solicitada e a observada no runtime, incluindo esforço quando aplicável; quando não houver trace, registrar o observado como indisponível (`unavailable`). A configuração local, por si só, não comprova o modelo executado.
- Preservar as restrições versionadas de modelos proibidos e demais regras e validações do processo.
- Fazer a mudança inicial do processo passar por Design, aprovações, implementação, revisão, validações e commit conforme os gates vigentes. A dispensa de card, commit e release aplica-se às futuras trocas operacionais de modelos e esforços suportados, após essa mudança.

## Não entra
- Criar perfis ou exceções de escolha de modelo por projeto.
- Uniformizar modelos ou capacidades de esforço entre clientes, nem trocar suas escolhas atuais além dos valores iniciais Codex já solicitados.
- Criar capacidades de modelo ou esforço que o harness não ofereça.
- Alterar a lista de modelos proibidos ou outras regras do processo alheias à externalização da seleção.
- Trocar o modelo de sessões ou agentes já em execução.
- Comparar qualidade, custo ou desempenho dos modelos, nem garantir disponibilidade do provedor.
- Resolver a ausência de trace do runtime ou inferir o modelo executado a partir do modelo solicitado.
- Alterar a interface do produto, publicar uma release ou antecipar aprovações do fluxo.

## Why

A seleção operacional está acoplada ao Git e aos pins; uma troca local deve valer no próximo spawn em todos os consumidores da máquina.

## What Changes

- **BREAKING**: escolhas saem do mapa versionado para configuração local por máquina, sem fallback.
- Resolver comum com capacidades por harness, captura imutável por spawn/onda, migração explícita e parâmetros suportados.
- Remover pins de modelo dos agentes e substituir herança OpenCode/dsh por seleção explícita verificável.

## Capabilities

### New Capabilities
- `machine-model-selection`: configuração local, migração, capacidades e captura por spawn/onda.

### Modified Capabilities
- `cursor-harness`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `covenant-flow`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `cursor-code-review`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `developer-tooling`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `process-harness`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `llm-flow-emission`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `impeccable-design-gate`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.
- `kaizen-continuous-improvement`: trocar fonte versionada, herança e pins pelo contrato local por cliente/faixa e evidência capturada; preservar demais gates.

## Impact

Resolver/proxies Python, plugins dsh/OpenCode, instruções/hooks Cursor/Codex/Grok, agentes, stubs e instalador/pins. Sem UI, banco, novas arestas FSM ou publicação de release.
