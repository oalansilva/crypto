## 1. Guard pre — evidência de deploy PROD

- [x] 1.1 Adicionar check no modo `pre`: evidência de deploy PROD (commit publicado no source PROD + services reiniciados + URL pública validada) antes de liberar `Pronto`; ausência = blocker em modo estrito
- [x] 1.2 Documentar formato da evidência (variável/arquivo/parâmetro) no output de usage e no AGENTS.md

## 2. Guard post — inventário de refs e worktrees órfãs

- [x] 2.1 Adicionar inventário de refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*` no modo `post`, com exigência de classificação (integrar/preservar/limpar com autorização)
- [x] 2.2 Adicionar inventário de worktrees `preserve/*` com sinalização de WIP não commitado (`git status --porcelain`)
- [x] 2.3 Garantir que itens do inventário são blockers em modo estrito com instrução de classificação

## 3. Docs

- [x] 3.1 Atualizar AGENTS.md/skill alan-workflow-ambientes conforme novo comportamento do guard

## 4. Validação

- [x] 4.1 Rodar `scripts/release-guard audit` e modos `pre`/`post` em cenários com e sem evidência/refs órfãs
- [x] 4.2 Rodar validação OpenSpec da change
