## 1. Regra de path-check

- [x] 1.1 Documentar no AGENTS.md/fluxo de QA visual: antes de delegar arquivos ao vision, confirmar existência (`ls`/glob); path inexistente bloqueia a delegação
- [x] 1.2 Documentar caminho canônico de artefatos visuais (`/tmp/opencode/<slug>/`) usado na delegação

## 2. Falha de leitura do subagent

- [x] 2.1 Documentar regra: em falha de leitura (`File not found`), gerar/recriar o artefato no caminho esperado antes de respawnar (máx. 1 re-delegação com path verificado)

## 3. Validação de URLs

- [x] 3.1 Documentar regra: webfetch só em URLs confirmadas/existentes no fluxo de QA visual; sem fetch em URLs inventadas
- [x] 3.2 Registrar proibição de respawn por arquivo inexistente

## 4. Validação

- [x] 4.1 Validar o fluxo em um cenário de QA visual com path existente e inexistente (foco)
- [x] 4.2 Rodar validação OpenSpec da change
