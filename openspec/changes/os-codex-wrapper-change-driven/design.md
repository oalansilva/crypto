## Overview

Vamos tornar o wrapper `scripts/openspec_codex_task.sh` **change-driven**.

O wrapper deve:
1) exigir `change_id`
2) validar o change (`openspec validate <change_id>`)
3) obter instruções de apply do OpenSpec (`openspec instructions apply --change <change_id> --json`)
4) validar que existem tasks trackeáveis
5) alimentar o Codex com:
   - path do change
   - conteúdo de `tasks.md`
   - instrução enriquecida retornada pelo OpenSpec
   - guardrails de escopo + testes

## Parsing do JSON

`openspec instructions apply --json` pode imprimir linhas de status antes do JSON.
O wrapper deve extrair o primeiro objeto JSON da saída (a partir do primeiro `{`).

Campos relevantes:
- `tasks`: lista de tasks parseadas (pode vir vazia)
- `instruction`: texto para o agent aplicar as tasks
- `contextFiles`: caminhos para proposal/specs/design/tasks

## Fail-fast

O wrapper deve falhar com exit code != 0 quando:
- change não existir em `openspec/changes/<change_id>`
- `tasks.md` não existir
- `tasks` vier vazio (estado `blocked`)

Mensagem deve sugerir criar tarefas e/ou rodar os comandos:
- `openspec instructions tasks --change <id>`
- editar `tasks.md`

## Prompt para o Codex

O prompt deve conter:
- Instruções fixas (escopo, sem refactor, rodar pytest)
- `CHANGE_ID`
- `APPLY_INSTRUCTION`
- as tasks (lista) e/ou o conteúdo de `tasks.md`

## Compatibilidade

Manter flags atuais (ex.: `--model`, `--confirm`).

## Segurança

Sem executar `openspec archive` automaticamente.
