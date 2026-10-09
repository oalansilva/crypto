## 1. Configuração e migração

- [x] 1.1 Fechar matriz verificável de schemas/capacidades para Cursor, Codex, Grok, OpenCode e dsh; registrar versões reais, rotas atuais não secretas e incompatibilidades sem inventar esforço ou sucesso.
- [x] 1.2 Implementar schema local, política versionada e resolver CLI/API único, caminho independente do repo, validação de faixa/papel, proibições e erros visíveis sem fallback.
- [x] 1.3 Implementar plano/migração explícita e escrita atômica; preservar arquivo existente e escolhas Cursor/Grok; inicializar Codex conforme Alan; materializar OpenCode/dsh somente com rota efetiva conhecida.

## 2. Integração dos cinco harnesses

- [x] 2.1 Integrar Cursor nos dois caminhos Task e Grok no spawn_subagent, passando somente parâmetros suportados; documentar esforço Grok demonstrado e recusar configuração incompatível.
- [x] 2.2 Integrar Codex resolver/adapter/proxy/review, substituindo leitura Git e PIN_PAIRS por captura local e validação exata da faixa.
- [x] 2.3 Integrar dsh seleção explícita suportada, descriptor e guards por agent.ctx; eliminar substituição high nos filhos geridos e preservar root/filhos antigos, grill deny e error handling.
- [x] 2.4 Integrar OpenCode ao caminho nativo de filho preservando semântica task e seleção provider/model/variant; ensaiar versão real e manter recusa/cobertura pendente se capacidade faltar.

## 3. Captura e contratos

- [x] 3.1 Implementar captura imutável por spawn, releitura por nascimento, coerência por faixa na onda e erro selection_changed sem retunar agentes existentes.
- [x] 3.2 Atualizar proxies, verify-wave, resume/destape, release_closeout e auditoria para comparar captura aplicável, mantendo requested/observed separados e unavailable sem trace.
- [x] 3.3 Atualizar runbook, paging, agents, stubs e skills; remover pins operacionais e herança, preservando papéis, gates e limite dos stubs. Inventariar referências normativas restantes nas specs sem deixar mapas/pins antigos operativos.
- [x] 3.4 Atualizar instalador/pin e seus testes para não exigir mapa legado nem escrever escolhas locais; mover apenas regras/proibições para política versionada e documentar diagnóstico/rollback.

## 4. Verificação

- [x] 4.1 Testar dois repositórios e dois worktrees sob HOME temporário compartilhado: editar cada cliente/faixa, verificar próximo spawn e preservação das demais escolhas/filhos vivos.
- [x] 4.2 Testar YAML duplicado, arquivo/cliente/faixa ausentes, schema/campos inválidos, modelo proibido, esforço incompatível, provider recusado e capacidade indisponível; provar ausência de fallback e ausência de escrita pelo pin.
- [x] 4.3 Testar edição entre dois reviewers, edição alheia à faixa, proxy após edição, resume e comparação do pai release; preservar gates de sandbox/diff/status e metadata verdadeira.
- [x] 4.4 Executar ensaios de passagem explícita de cada adapter e registrar matriz de cobertura real; mock não substitui runtime observado. Onde faltar trace, manter unavailable e gate correspondente pendente.
- [x] 4.5 Rodar checks focados do harness, validação OpenSpec e diff check; apresentar evidências e limitações para revisão/QA sem publicar release ou antecipar aprovação.

## Evidência de Apply

Consumer implementado; nucleus integrado no worktree autorizado do mesmo #1080, sem overlay crypto nem alterações main/source/branches1042. Task3.4: 126 testes focados nucleus passaram, incluindo seis installer reais e resolver/hook funcional no destino pinado. Preflight hooks/roles/bridges/mecanismos preservado; nenhuma leitura/escrita de escolhas locais. Trust review é ação do operador, não efeito do pin.

Migração aplicada pelo pai create_only; validate passou nos dez pares, source_sha256 6167e38fd93f8f00577de4adab6f73ab0c0f6942d72f610e85e989d78eabe9c4. Nenhum existente sobrescrito.

Histórico de Apply, antes da QA: Grok tentativa nativa encontrou Not signed in. Cursor probe Plan não criou filho, sem aprovação/bypass. dsh habilitação nativa ainda precisava ensaio positivo. OpenCode1.18.32 capacidade task equivalente indisponível/residual explícito. Probe Codex/Review seria conduzido pelo pai. Esses resultados históricos permanecem em `evidence/apply-resume-checks.json`; não representam a matriz final. Mock não conta como runtime.

Fechamento 4.4 em QA (2026-10-09): Cursor e Codex têm nascimento nativo, modelo observado e retorno PASS. Grok passou após login: captura pede `grok-4.6`, metadata própria do filho registra `current_model_id=grok-4.6`, usage nativo registra backend `grok-4.6-build` (identificadores distintos preservados), retorno completed/exit0 com payload `LOCAL_SELECTION_PROBE_OK`. dsh é `waived_by_user`, nunca PASS: Alan dispensou explicitamente o ensaio nesta sessão ([registro da instrução](https://github.com/oalansilva/crypto/issues/1080#issuecomment-6071728818)); observado continua unavailable, preservando a recusa anterior de saldo insuficiente antes do spawn. Adapter/testes dsh continuam entregues. OpenCode permanece residual explícito de cobertura positiva pela capacidade insuficiente de task na versão instalada, com recusa segura prevista no Design; não há nascimento positivo atestado. Task concluída no escopo de QA autorizado, sem relaxar specs ou converter recusa/dispensa em sucesso. Matriz e evidências duráveis: `evidence/qa-closeout.json`; verificação: `evidence/verification-report.md`.

Histórico: P0 nucleus inicialmente registrado foi resolvido nesta retomada autorizada. O Design#1080 inclui installer no mesmo card, sem gate extra por repo. Nenhum review/commit/publicação neste Apply.

Verificação da retomada de Apply (histórica): nucleus622 passed/0 skipped; hooks Node3 passed; consumer84 passed/6 installer skipped (os seis passaram realmente no nucleus). OpenSpec strict válido, diff check ambos limpo, task gate precommit None. Evidência `evidence/apply-resume-checks.json`. Naquele momento: 15/16, apenas4.4 after-qa, sem P0. Após a QA acima: 16/16 tasks concluídas, com dispensa dsh e residual OpenCode explicitamente preservados; checklist postqa e demais gates devem usar a evidência final de verificação.
