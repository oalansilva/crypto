# Regras Operacionais do Projeto

1. Sempre usar OpenSpec para qualquer alteração de código, independente de tamanho ou complexidade.
   - Toda mudança de código deve ter a trilha de `openspec/changes/<change>/` (proposta, escopo, critérios e rastreabilidade) antes da implementação, e evidência de validação antes do fechamento.

2. Sempre utilizar subagentes para acelerar o trabalho sempre que houver tarefa de desenvolvimento, investigação, validação ou revisão técnica.
   - Planejar e orquestrar os subagentes de forma padrão para dividir tarefas e reduzir tempo de ciclo, sem trocar o papel do agente principal.

3. Após validação e evidência, o agente tem autonomia para executar o fluxo de merge e repetição de tentativas conforme regras do repositório, sem solicitar nova autorização para cada etapa.
