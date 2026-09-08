## Why

Quem monta uma varredura em Descoberta escolhe a seleção e clica **Iniciar**. Hoje, depois de cancelar ou terminar uma run, esse clique devolve **Falha ao iniciar** em vez de começar a seleção da tela — o caminho feliz passa a depender de **Novo rascunho**, que deveria ser atalho, não obrigação.

## What Changes

- **Iniciar** começa a varredura da seleção que está no rascunho naquele momento (templates, símbolos, timeframes, direções e período). Sem segundo botão, sem recarregar a página.
- Depois de **Cancelar** ou do fim da run, o rascunho fica editável e **Iniciar** vale para a seleção da tela — mesmo que a seleção seja **igual** à da run que acabou: começa uma varredura **nova**, nunca reabre a run morta.
- Com uma varredura **em execução**, **Iniciar** de outra seleção fica bloqueado com aviso para cancelar antes; não cria segunda em paralelo nem substitui a que está a correr.
- Clique repetido na mesma seleção enquanto a varredura dela está a ser criada ou a correr não gera duplicata: a tela mostra a que já existe.
- Recarregar a página não prende o operador à run anterior: **Iniciar** continua começando a seleção da tela.
- A mensagem de falha, se ainda existir, é em linguagem de operação (o que fazer), nunca JSON técnico.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-sweep`: o requisito de criação por rascunho passa a tratar o clique **Iniciar** após run terminal como começo novo da seleção da tela (nova varredura mesmo com seleção igual); **Iniciar** de outra seleção com varredura em execução é recusado com orientação para cancelar; repetição na mesma seleção em criação/execução retorna a existente sem duplicar; falha de início fala linguagem de operação.

## Impact

- Frontend: `frontend/src/pages/DiscoveryPage.tsx` (estados do botão **Iniciar**, bloqueio com execução, mensagens, fluxo pós-cancelar/terminar e após reload). Sem mudar preflight, limite de combinações, leaderboard, promoção ou descarte.
- Backend: criação de varredura em `backend/**` (tratamento do começo novo pós-terminal e da recusa orientada com execução). Mecanismo exato fica para o Design.
- Spec canónica `openspec/specs/discovery-sweep/spec.md` (senão o Apply reintroduz o 409 do caminho feliz).
- Rota `/combo/discovery` já existente; sem redesign além do clique **Iniciar** / fim de run; sem mexer no identificador interno do rascunho.
- Fora: select-all de templates/símbolos (#831); telas Combo, Monitor, Favoritos.
