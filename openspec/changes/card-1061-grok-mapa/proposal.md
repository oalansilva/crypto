## Why

No Grok Build, o filho de juízo ou de execução não nasce: o mapa compartilhado não tinha par do Grok, o spawn lia o slug do Cursor ou um slug inválido, e o host recusava.

## Problema

No Grok Build, o filho de juízo ou de execução não nasce. O host só aceita os modelos `grok-4.5`, `grok-4.6`, `grok-4.7` e `grok-4.7-build-fast`. O mapa compartilhado não tinha par do Grok, então o spawn lia o slug do Cursor ou um slug inválido e era recusado.

## História

Como operador no Grok, quero que juízo e execução usem modelos que esse host aceita, para a grelha e o resto do fluxo poderem criar filhos sem herdar o picker e sem alterar os pares do Cursor e do Codex.

## Entra

- No mapa compartilhado da develop do GitHub, o par do Grok fica: juízo Grok 4.7 (`grok-4.7`); execução Grok 4.6 (`grok-4.6`). O pai no Grok lê esse par, não o par do Cursor. Não omite o modelo e não herda o picker. Aceite de Alan: «Juízo 4.7, execução 4.6».
- O Cursor permanece juízo Grok 4.6 (`cursor-grok-4.6-high`) e execução Composer 2.5 (`composer-2.5`).
- O Codex permanece juízo GPT-6 Sol (`gpt-6-sol`, esforço high) e execução GPT-6 Luna (`gpt-6-luna`, esforço max).
- Modelo que o host não aceita, ou par do Grok em falta, continua falha visível. Sem herdar o picker e sem troca silenciosa.
- A mudança entra na `develop` atual do GitHub. O commit local `b2cac2d5` está numa `develop` divergente (45 commits do GitHub que ele não tem, e 1 commit local que o GitHub não tem); não enviar esse commit com push forçado.
- Os dois revisores no Grok nascem no Grok 4.6 e deixam de ficar de fora neste card. A frase que ainda os recusa deixa de valer. Aceite de Alan, texto livre: «revisores soa execucao» — revisores são execução.
- No Grok, fechar release usa o Grok 4.6 e não fica de fora deste card. Aceite de Alan, texto livre: «fechar releze e execucao» — fechar release é execução.
- Filho de execução retomado noutro modelo que não o Grok 4.6, inclusive o modelo rápido, não conta: falha e nasce de novo no Grok 4.6. Facto da lei já vigente (a retomada fica no modelo de execução; o fast do Cursor já falha assim), aplicado ao par que Alan fechou. Não é decisão nova.

## Não entra

- Trocar os pares do Cursor ou do Codex.
- Publicar o commit atrasado direto no remoto.
- Mover este card para Todo. Isso continua com Alan.

## What Changes

- O mapa compartilhado `.cursor/model-map.yaml` ganha o par do Grok: `juizo.grok` = Grok 4.7 (`grok-4.7`); `execucao.grok` = Grok 4.6 (`grok-4.6`). O pai no Grok lê esse par, passa `model` no `spawn_subagent` e não herda o picker.
- Os pares de topo do Cursor e os sub-blocos `codex` permanecem. OpenCode e dsh continuam inherit.
- Slug que o host Grok não aceita, ou par `grok` em falta, continua falha visível. Sem troca silenciosa para o slug do Cursor, do Codex, ou para outro modelo que o host aceite.
- A frase que recusa revisores no Grok deixa de valer. `diff-reviewer` e `code-reviewer` no Grok nascem em `grok-4.6` (execução).
- No Grok, fechar release (T16 e `fecho-lote`) usa `grok-4.6` e entra neste card.
- Filho de execução no Grok retomado noutro modelo que não `grok-4.6`, inclusive `grok-4.7-build-fast`, falha e nasce de novo em `grok-4.6`.
- A mudança aplica-se nesta branch, a partir da `develop` atual do GitHub. Não publica `b2cac2d5` por push forçado. Não move este card para Todo.

## Capabilities

### New Capabilities

- (nenhuma) — o par do Grok entra nas specs de harness já existentes. Este card não inventa coluna nem capability.

### Modified Capabilities

- `cursor-harness`: o mapa compartilhado passa a ter `juizo.grok` / `execucao.grok`; o pai no Grok lê esse par e não omite `model`; slug recusado pelo host ou par em falta é falha visível; revisores e fecho de release no Grok usam `execucao.grok`; retomada de execução fora de `grok-4.6` não conta. Os pares do Cursor e do Codex não mudam.
- `covenant-flow`: o runbook deixa de recusar revisores no Grok; no cliente Grok, juízo lê `juizo.grok` e execução lê `execucao.grok`; fechar release no Grok exige o slug de execução do Grok; a frase de inherit dos stubs Grok deixa de valer. OpenCode e dsh continuam inherit.
- `process-harness`: o stub Grok deixa de mapear Task `inherit` para `spawn_subagent` inherit; manda passar `model` do par `grok` e não copiar o runbook. Corpo continua ≤8 linhas.
- `cursor-code-review`: no Grok, os dois revisores nascem em `grok-4.6`. No Cursor, continuam no slug de `execucao` e não passam a usar o slug do Grok.
- `llm-flow-emission`: no Grok, Assessment A/B usam `juizo.grok` e os dois revisores usam `execucao.grok`. No Cursor, as faixas de topo não mudam.
- `impeccable-design-gate`: no Grok, A/B usam `juizo.grok` (não o slug do Cursor e não o picker). Este card é sem-tela; o pipeline Impeccable não corre aqui.
- `kaizen-continuous-improvement`: `/kaizen release` compara `proxy modelo:` do Grok a `juizo.grok` / `execucao.grok`, não ao par do Cursor.

## Impact

- `.cursor/model-map.yaml` (só os sub-blocos `grok`; Cursor e Codex intactos).
- `.cursor/skills/covenant-flow/SKILL.md` (cláusula do cliente Grok; a frase que recusa revisores no Grok sai).
- `scripts/process-fsm/grok_stubs.py` e stubs gerados em `.grok/skills/**/SKILL.md` (uma ponte curta; sem copiar a tabela de papéis).
- Specs delta desta change. Sem rota de produto, sem HTML, sem protótipo, sem aresta nova na FSM, sem crescer `AGENTS.md`, sem dual-write do runbook em `.opencode/` ou `.dsh/`.
- Não publica o commit `b2cac2d5`. Não move o card para Todo.
- Relacionados citados no issue, não reabertos como pacote: #1017, #904, #939.
