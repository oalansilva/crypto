## Why

O fluxo já tem quatro clientes, mas o Codex CLI e a IDE local ainda não consomem o mesmo contrato versionado. O card #1042 fixa o quinto adapter e um mapa de modelos compartilhado sem criar uma segunda FSM.

## Problema

Alan, ao alternar entre Cursor e Codex CLI ou IDE local, enfrenta diferenças nas regras de fluxo, nas proteções de escrita e na escolha de modelos, com risco de ações fora da etapa correta.

## História

Como Alan, quero usar o Codex CLI e a IDE local com a mesma FSM, as skills canônicas e um mapa de modelos compartilhado com o Cursor, para que os clientes sigam o mesmo processo e cada filho use o modelo e esforço definidos para sua faixa; `juizo.codex = gpt-6-sol` com esforço `high` e `execucao.codex = gpt-6-luna` com esforço `max`.

## Entra

- Uma sessão nova no Codex CLI e outra na IDE local encontram as skills do repositório, mostram a orientação correspondente ao Status do card e permitem as operações de especificação já previstas no fluxo.
- Nas duas superfícies Codex, tentativas de escrita de produto em `develop` ou `Todo` são negadas tanto por comandos quanto por edição de arquivos. Em Design, os artefatos dessa etapa são permitidos; escrita de produto só é permitida no worktree vinculado depois de T8.
- A condição que aciona a orientação Impeccable produz o mesmo resultado no Codex e nos clientes existentes.
- Cada solicitação de filho das faixas `juizo` e `execucao` no Codex usa, respectivamente, `gpt-6-sol` com esforço `high` e `gpt-6-luna` com esforço `max`. Alterar o modelo ou esforço no mapa compartilhado afeta o próximo spawn da faixa correspondente; os valores Cursor vigentes continuam aplicados ao Cursor. Modelo ou esforço ausente ou indisponível gera falha visível, sem troca silenciosa.
- Design, Apply, reviews e QA usam filhos isolados. Os dois reviewers recebem o diff exato, fazem somente leitura e entregam pareceres separados.
- O Status do card avança apenas pelos eventos da FSM, com as aprovações humanas preservadas. Um card piloto percorre Design, aprovação, dois reviews, QA e Done técnico sem pular etapas.
- O instalador do pin reproduz o adapter no Cripto. Specs e testes cobrem o novo cliente, e os testes dos quatro clientes existentes continuam verdes. Depois do ensaio, a descrição do board deixa de afirmar que o Codex está inativo.

## Não entra

- Codex Cloud nesta fase.
- Alterar T0–T18, os gates humanos ou as regras de release.
- Duplicar a FSM ou suas regras em `.codex/`, manter um segundo mapa de modelos ou alterar código de produto em `backend/` ou `frontend/src/`.
- Reivindicar modo Auto para Codex.
## What Changes

- Adicionar adapter Codex local, carregado pelo CLI e pela IDE local, que usa a FSM, o Guard, a orientação Moore e as skills canônicas do repositório.
- Expandir o mapa versionado atual com modelo e esforço Codex; no pin, preservar os valores Cursor e `forbid` lidos do destino vigente, com recusa visível ou merge explícito em conflito, sem overwrite silencioso.
- Definir ensaios de escrita negada, isolamento de filhos, par de reviews e card piloto; incluir o adapter no instalador do pin e na documentação de estado do board após evidência.

## Capabilities

### New Capabilities

- `codex-harness`: descoberta local, hooks, Guard, filhos, modelos e prova de fluxo nas duas superfícies Codex.

### Modified Capabilities

- `process-harness`: núcleo passa a ter quinto adapter instalado sem duplicar a lei ou alterar a FSM.
- `covenant-flow`: o instalador do pin passa a reproduzir o quinto adapter no consumidor.
- `cursor-harness`: mapa antes Cursor-only passa a ser compartilhado, preservando os valores Cursor vigentes.
- `impeccable-design-gate`: disparo do detector no Codex converge com a condição existente.
- `llm-flow-emission`: isolamento, diff exato e proxies passam a abranger os filhos Codex.

## Impact

Pacote do produto `oalansilva/covenant-flow`, pin instalado no Cripto, configuração local Codex e testes de `scripts/process-fsm/`. Nenhuma API ou tela do produto muda. Os hooks documentados cobrem ferramentas locais específicas, com exceções; a extensão real da proteção será medida por ensaio de deny no CLI e na IDE.
