## 1. Mapeamento change → card

- [x] 1.1 Refatorar `scripts/release-guard` para enumerar todas as changes ativas antes de avaliar artifacts/tasks.
- [x] 1.2 Preservar extração autoritativa de id para nomes `card-<id>-*`/`issue-<id>-*` e registrar `mapping=name`.
- [x] 1.3 Implementar fallback local por título usando `BOARD_JSON`, `CANONICAL_CARDS`, repositório `oalansilva/crypto`, slug e `proposal.md`, sem chamada `gh` por change.
- [x] 1.4 Tornar normalização, score, limiar e desempate explícitos/determinísticos; não extrair card de referências numéricas soltas nos artifacts.
- [x] 1.5 Tratar título/status ausente, item duplicado e associação ambígua como diagnóstico em `audit` e fail-closed em `post` quando a prova do pacote ficar incompleta.

## 2. Regra de terminalidade e modos

- [x] 2.1 Classificar cada change apenas para mensagem como `complete` (artifacts esperados + zero task aberta) ou `in-progress`; não usar essa classificação para descartá-la.
- [x] 2.2 Reportar toda change ativa mapeada a card `Pronto`/`Cancelado`, incluindo `change`, `card`, `status`, `progress`, `mapping` e pertencimento ao pacote.
- [x] 2.3 Manter `audit` como warning e fazer `post` bloquear com qualquer change ativa de card terminal, garantindo blocker para cards de `RELEASE_CARDS`.
- [x] 2.4 Atualizar a mensagem de sucesso para “nenhuma change ativa mapeada a card terminal”, removendo a condição enganosa de artifacts/tasks completos.
- [x] 2.5 Preservar `pre` sem esse check e preservar um único snapshot de board/PR por execução.

## 3. Testes determinísticos com gh falso

- [x] 3.1 Estender `_board`/fixtures em `backend/tests/integration/test_release_guard.py` com `content.title` e helpers para criar changes completas e in-progress.
- [x] 3.2 Cobrir em `audit` os seis slugs sem id da release: `walk-forward-gate`→#470, `kaizen-homologacao-evidence-comment`→#480, `kaizen-stuck-cards-age-alert`→#481, `kaizen-board-issue-rename-note`→#482, `hide-quant-test-templates`→#489 e `design-planner-grok-4-6`→#491.
- [x] 3.3 Cobrir `card-509-release-guard-graphql-budget` ativo com task pendente e card #509 terminal, provando warning apesar de `progress=in-progress`.
- [x] 3.4 Cobrir `post` retornando falha para change completa e in-progress de card do pacote, por mapeamento de nome e de título.
- [x] 3.5 Cobrir card não terminal, título sem score mínimo, empate, título/status ausente ou item duplicado, validando ausência de associação arbitrária e fail-closed estrito.
- [x] 3.6 Cobrir archive/removal do fixture: depois de retirar a change da árvore ativa, a seção não emite warning/blocker terminal.
- [x] 3.7 Assegurar que múltiplos fallbacks continuam gerando exatamente uma chamada `gh project item-list` e uma `gh pr list` no run.

## 4. Validação da implementação

- [x] 4.1 Rodar os testes focados de `backend/tests/integration/test_release_guard.py` e corrigir qualquer regressão.
- [x] 4.2 Rodar `scripts/release-guard audit` com `RELEASE_CARDS=470,480,481,482,489,491,509` e registrar os sete casos esperados ou sua situação já arquivada.
- [x] 4.3 Validar a delta spec/change com a CLI OpenSpec aplicável e registrar a evidência no handoff.
- [x] 4.4 Confirmar no diff que nenhum frontend, API, migration, banco ou serviço foi alterado.

## 5. Limpeza das changes terminais — somente com autorização

- [ ] 5.1 Obter autorização explícita de Alan para o bulk archive; não executar a limpeza apenas com a aprovação técnica do design.
- [ ] 5.2 Usar a skill `/opsx:bulk-archive` e a CLI indicada para verificar card terminal, status OpenSpec e instruções de sync de cada change: `kaizen-dedupe-card-comments` (#456), `kaizen-guard-branch-inventory` (#457), `kaizen-bulk-archive-terminal-changes` (#458), `fix-saldo-usdt-compra` (#463), `walk-forward-gate` (#470), `kaizen-homologacao-evidence-comment` (#480), `kaizen-stuck-cards-age-alert` (#481), `kaizen-board-issue-rename-note` (#482), `hide-quant-test-templates` (#489) e `design-planner-grok-4-6` (#491).
- [ ] 5.3 Arquivar as dez changes elegíveis em `openspec/changes/archive/YYYY-MM-DD-<change>/`, sincronizando specs quando aplicável e registrando qualquer exceção `--skip-specs` com justificativa.
- [ ] 5.4 Confirmar que `card-509-release-guard-graphql-budget` permanece somente no archive e não tem cópia ativa duplicada.
- [ ] 5.5 Reexecutar `release-guard audit` e comprovar ausência de warnings de changes terminais para os cards limpos; validar OpenSpec global conforme o gate de fechamento aplicável.

## 6. Handoff e gates

- [ ] 6.1 Republicar proposal/design/spec/tasks no card sem criar novo Gist/comentário quando já houver publicação anterior.
- [ ] 6.2 Registrar `UI impact: none`, `Design Agent verdict`, evidência de aprovação humana e os resultados dos testes/guard no handoff.
- [ ] 6.3 Não iniciar `/opsx:apply`, editar o script/testes ou arquivar changes antes de o card #517 chegar a `Pronto para Dev` com aprovação de Alan.
