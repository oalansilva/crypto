# P0 — spawn nativo do Codex CLI não passa pelo `PreToolUse`

Este registro cobre somente Codex CLI. A validação da IDE local está adiada e permanece pendente; não há alegação sobre essa superfície. `proposal.md`, `design.md` e specs aprovados não foram alterados.

## Ensaio real

- Host: `codex-cli 0.156.1`, sessão TUI interativa em clone descartável `/tmp/card-1042-cli.atr1zt/repo`.
- Estado: o hook de projeto já estava confiado; a definição de hook não foi modificada nem foi usado bypass de trust/sandbox.
- O `.codex/hooks.json` instalado na cópia inclui matcher `Bash|exec_command|apply_patch|Edit|Write|Agent` para `PreToolUse`.
- Um wrapper temporário de `python3` observou o stdin do hook sem alterá-lo: registrava payload do Agent somente se a rota chegasse; para outras ferramentas registrava apenas nome da ferramenta/evento/chaves. Em seguida encaminhava stdin sem mudança para o adapter original.
- Foi solicitado exatamente um filho local com `model=gpt-6-luna` e `reasoning_effort=high`, um par deliberadamente divergente do mapa vigente `execucao.codex=gpt-6-luna/max`. O filho real iniciou, completou e devolveu o marcador inocuo `CHILD_PROBE_OK`.

Resultado correlacionado: o JSONL da sessão contém uma chamada real `function_call` `collaboration.spawn_agent`, com o modelo/esforço acima, e registra a conclusão da chamada colaborativa. A captura do wrapper contém **duas** entradas `PreToolUse`, ambas `tool_name=Bash`, e **zero** entradas `Agent`/`spawn_agent`. Portanto, a chamada real não foi interceptada pelo hook, apesar do matcher incluir `Agent`; o deny sintético do adapter não prova enforcement no caminho nativo.

Depois do probe, um `pwd` em Bash encontrou falha de namespace do sandbox (`bwrap: ... RTM_NEWADDR`). A solicitação para executar fora do sandbox foi recusada; não houve bypass. Essa falha não altera o resultado independente do spawn observado.

## Evidência local e integridade

Os arquivos brutos permanecem nos caminhos abaixo. Os digests permitem identificar exatamente os artefatos examinados, sem copiar prompt/transcript para este registro.

| Artefato | Caminho | SHA-256 |
| --- | --- | --- |
| Definição de hooks do clone ensaiado | `/tmp/card-1042-cli.atr1zt/repo/.codex/hooks.json` | `69df18690f540e11cf990d803541b6bb26d13bc67dba202ffc1e580394f9b83d` |
| Adapter executado no clone | `/tmp/card-1042-cli.atr1zt/repo/scripts/process-fsm/codex_adapter.py` | `68c98e7f4f3a45edc598fe69d78bee35e798f461c2b29dfac7c1aa6385d1062d` |
| Wrapper temporário de captura | `/tmp/card1042-hookprobe.JthP0d/python3` | `e870ee2b65fd593d025b01163d4708c92c048878b4fa1d357816156af9a163d0` |
| Trace minimizado do hook (`Bash` somente) | `/tmp/card1042-hookprobe.JthP0d/tui-events.jsonl` | `643ba25076f4ea6055092b1d25091b1801be17286f2efdd205cb4e3a0be40997` |
| Sessão do Codex CLI (conteúdo não reproduzido) | `/home/ubuntu/.codex/sessions/2026/09/25/rollout-2026-09-25T08-36-17-01a0d7b5-4b3e-7262-a394-ae47f9d7d76c.jsonl` | `ec0508110ee61424d64354940dd96267bf533e1a14e2488ec901c05c49c4fc43` |

O adapter invocado diretamente havia negado a mesma combinação sintética `Agent` com `gpt-6-luna/high`; esse teste cobre o código do adapter, não a chamada real do CLI. A captura acima separa explicitamente os dois resultados.

## Alternativa oficial avaliada

A documentação oficial do Codex descreve `agents.enabled=false` como forma de desabilitar ferramentas multi-agent e permite overrides de modelo/esforço numa execução do CLI por `--model` e `--config`. Isso sugere uma arquitetura distinta: desativar spawn nativo e lançar processos `codex exec` por um wrapper que relê o mapa compartilhado, aplica os overrides, verifica chamadas diretas via o Guard e transporta/registre o payload de retorno.

Essa alternativa não foi implementada nem ensaiada. Ela muda a rota de filhos/thread/retorno do spawn colaborativo nativo para subprocessos Bash e requer um wrapper/contrato de orquestração que o Design aprovado não especifica. Não é uma correção local do matcher nem evidência de que a rota nativa satisfaça o mapa. Como a mudança seria arquitetural, o Apply para no P0 até reaprovação do Design; nenhuma segunda tabela/mapa foi criada.

Referências oficiais consultadas: [Hooks](https://learn.chatgpt.com/docs/hooks) (matcher de `Agent` também cobre `spawn_agent`, com ressalva de que rotas especializadas podem sair do caminho padrão) e [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) (opção `agents.enabled=false`, precedência de configuração e coordenação/retorno nativos).
