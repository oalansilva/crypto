# Correção operacional I4 antes do preflight de etapa — 17/10/2026

Alan autorizou esta correção estreita para resolver a circularidade entre digest alterado e preflight de capacidades. A revisão documental da opção 2 não foi implementada; Design/spec/tasks permanecem como estavam no início desta correção.

## Procedência e estado

O Guard recusou uma escrita nativa em scripts/process-fsm/process_event.py no nucleus fora do binding atual, com target_outside_binding. Nenhuma alteração foi aplicada ali e nenhum meio alternativo foi usado para contornar a recusa. O pai autorizou preparar/testar o candidato inativo dentro do worktree vinculado.

Pacote: `.cursor/tmp/card-1098-i4-preflight-fix/`, com README, manifest.json, i4-preflight-order.patch, before/ e files/. A procedência é candidata local; sincronização canônica com o nucleus está pendente. Os dois arquivos ativos do consumidor e seu manifesto não foram alterados. O retorno desta continuação deve ser coletado antes da integração.

## Comportamento candidato

Em Codex, iniciar_apply e pedir_review deixam o motor existente avaliar digest/I4 antes do preflight da etapa. Identidade de cliente, registro de hooks/trust, Status e vínculo card/change continuam nos checks existentes. Branch card-* e bound_card são conferidos antes da compilação T17. Só o resultado I4 autorizado pelo motor é compilado pela rota Guard já existente; não há actor configurável, nova aresta ou nova autorização humana.

Digest medido diferente permite somente invalidar a aprovação e retornar Design via I4/T17 existente. Não inicia Apply/review nem altera approval sidecar. Digest inalterado continua sujeito ao preflight de capacidade ausente. Os demais eventos Codex conservam o ponto original do preflight; Claude conserva sua ordem.

## Validação

- 23 testes novos: digest medido de arquivos de fixture, as duas entradas I4, dry-run, digest inalterado, estado incorreto, card/change/branch/bound divergentes, cliente conflitante, hooks/trust e actor do motor.
- 337 testes combinados PASS: process_event, account_registration, codex_evidence, Guard, FSM e novos casos, carregando o módulo candidato por harness local. Os movimentos são FakeMover e não houve transição real.
- Quatro avisos conhecidos de configuração pytest: asyncio_mode, timeout, timeout_func_only e timeout_method.
- git apply --check sobre o patch contra o consumidor atual: PASS, sem aplicar o patch.
- Primeiro ensaio detectou newline literal em uma fixture de sidecar; corrigida a fixture, digest inalterado e a regressão completa passaram. Nenhum sidecar real foi modificado.

## Hashes SHA-256

| Arquivo | Antes | Candidato |
| --- | --- | --- |
| process_event.py | 3096b00c72657e86de87d642486ace49fe4f5ed9bcf2e22d145f97b255b042fa | c45c3f8dd338fb6c07724d84bfb075988b9b14a22a0f4c8434f64cce0a9795e9 |
| test_process_event.py | bdb112ffb89a2570ef48c1ff24f5db852694e9c6014d05b596d1f25909794c84 | 9ba47f53c2a699a43eb183ca679abcb31fe95cc6ce9779891ddaf1813c197f7f |

Patch SHA-256: a802efc347162fa759a0d94ddcebda85c83582ae68b43b8eb3cc9a21c8624b8a. Manifesto ativo permaneceu em 9612ee6517ebe1d74113ab4236f97ab7bb85f237591bf4499e67a7cecaecc7c0. Gerador adapter_manifest.py do consumidor preservado em 3a189275bca1af555ddfa295392b52c94fcd6102adbfc272cb4b93b7c83bd05c.

## Integração pendente

Após a coleta, o pai confere hashes before e integra somente os dois payloads. Write e check do manifesto devem usar o **gerador do consumidor**, com pin-base v1.1.22, na mesma operação após a cópia; suas exclusões *_fixtures.py e route-landmarks.yaml são preservadas. Não copiar manifesto/gerador do nucleus. Nova confiança pertence exclusivamente a Alan.

Esta correção não executou write/check de manifesto, trust, commit, push ou process_event real. O resultado vivo do dry-run canônico após integração não é antecipado. A revisão do novo digest do Design, os gates humanos e as demais provas de capacidade permanecem obrigatórios.
