# Decision Log

## 2026-08-25 - JWT_SECRET fail-closed sem default do repositório (card #684)

**Decisão:** o runtime que assina/valida JWT recusa subir se `JWT_SECRET` estiver ausente, vazio, igual a `dev-secret-change-in-production` ou com comprimento menor que 32. Um único `resolve_jwt_secret()` no import (auth, middleware, prova OOS). Pytest usa secret explícito. Rotação operacional no `.env` (DEV no Done, PROD no release); o valor não vai para git, `Environment=`, chat ou evidência.

**Motivo:** o fallback versionado permitia forjar HS256 `access`/`refresh` para qualquer `sub`.

**Onde:** `backend/app/jwt_secret.py`, auth/middleware/OOS, `backend/.env.example`, spec `jwt-secret-fail-closed`. Card #684.

## 2026-08-23 - Cortar emissão LLM no fluxo sem perder gates (card #673)

**Decisão:** Design/Apply/Review **avaliam** com a rubrica Impeccable completa e **publicam** só o veredito (bullets P0–P3 + disposition + verdict). Relatório longo fica em `.impeccable/critique/` (git-tracked, link no card); apply/review não leem o snapshot. Um chat por coluna (`#id Design|Apply|Review|Release`). Vale nos dois clientes (Cursor e Grok). Avaliação intacta: dual critic, browser gate, zero P0/P1; snapshot vazio ⇒ `BLOCKED`.

**Motivo:** o custo era dominado por output (prosa Impeccable no chat e no `design.md`) e por cache × turnos em chat longo, sem ganho de qualidade no retorno.

**Onde:** `.agents/skills/design-critic`, skill Impeccable (token-sheet), `alan-workflow`, apply skill, reviewers, stubs Grok, specs `llm-flow-emission` / `impeccable-design-gate` / `cursor-harness`. Card #673.

## 2026-08-23 - Discovery restaura varredura ativa após reload (card #664)

**Decisão:** ao abrir Descoberta, se existir sweep não terminal do ator (`pending`/`running`/`paused`/`cancelling`), a tela reconstitui o bloco Sweep ativo, progresso, leaderboard da run e rascunho congelado. `Retomar` (e reload com sweep `running` incompleto) volta a despachar o orquestrador via wake-up durável da outbox. Sweep terminal não reaparece como ativo.

**Motivo:** o painel vivia só na sessão React; F5 apagava o progresso e Retomar não reabria o outbox.

**Onde:** `DiscoveryPage`, `GET /combos/discovery/sweeps/active`, outbox/wake-up, spec `discovery-sweep`. Card #664. Migration `20260823_0001`.

## 2026-08-23 - Discovery permite excluir resultado da varredura (card #663)

**Decisão:** no leaderboard de uma varredura concluída, cada linha tem promover (quando elegível, com motivo se bloqueado) e excluir/descartar com confirmação. Após confirmar, o resultado some do ranking daquela varredura e não pode ser promovido. Default: descarte permanente do candidato (não apaga favorito já promovido).

**Motivo:** pedido de Alan — promoção muitas vezes bloqueada e sem ação para descartar descoberta indesejada.

**Onde:** Discovery leaderboard + detalhe, specs `discovery-discard`, `discovery-leaderboard`, `discovery-promotion`. Card #663.

## 2026-08-23 - Em Refinamento grelha a história no issue (card #667)

**Decisão:** em `Em Refinamento` o agente afia a história no **body do GitHub** via skill `grill-card` (primitivo vendorado `grilling`). Artefato = issue, não `CONTEXT.md`/`docs/adr/`. T1 continua só Alan. OpenSpec em Design sintetiza o issue grelhado; não reentrevista e não usa `grill-with-docs`/`to-spec` como porta. Sem coluna nova.

**Motivo:** Design herdava card vago; a entrevista no chat morria entre colunas.

**Onde:** `.cursor/skills/grill-card/`, `.cursor/skills/grilling/`, `alan-workflow`, `context_file` Em Refinamento/Todo/Design, spec `grill-card`. Card #667.

## 2026-08-23 - Núcleo único, adapters Cursor e Grok (card #668)

**Decisão:** a lei do processo mora no núcleo (`process-fsm.yaml` + `scripts/process-fsm/` + skills canônicas + stub `AGENTS.md`). Cursor e Grok Build são adapters (hooks, JSON deny dual `{permission, decision}`, paging por arquivo no Grok). Sem dual-write de colunas/I1–I9. Grok permanece cooperativo até o ensaio deny humano PASS no mesmo worktree.

**Motivo:** o runtime compilado só existia como pele Cursor; abrir o repo no Grok era fail-open e a lei divergia.

**Onde:** `scripts/process-fsm/guard.py`, `.grok/hooks/`, `.grok/rules/00-harness.md`, specs `process-harness`, `cursor-harness`, `process-fsm-guard`, `process-fsm-paging`. Card #668.

## 2026-08-23 - post exige materialização Kaizen (card #661)

**Decisão:** `release-guard post` exige, na entrada canônica de `/kaizen release`, tabela `### Cards kaizen criados…` com 1–3 issues novas, ou `(não criado) … coberto por #N` com `#N` ainda em fluxo (não Pronto/Cancelado), ou o marcador `Sem achados acionáveis` sem linhas de dados. A skill `kaizen` continua read-only; o orquestrador materializa.

**Motivo:** nos lotes de 2026-08-21 o log passou, o `post` PASS, e zero cards novos nasceram.

**Onde:** `scripts/release-guard`, `scripts/kaizen_materialization_check.py`, spec `kaizen-continuous-improvement`. Card #661.

## 2026-08-21 - sessionStart pagina só o frame Moore (card #613)

**Decisão:** o hook `sessionStart` injeta no máximo ~20 linhas com `(q, bound_card, q_git)`, `enabled_events` e o stub `context_file[q]` (ou unbound: Write produto deny, sem playbook de release). `harness.mdc` fica em 8–15 linhas; `AGENTS.md` é stub e aponta `docs/crypto-overlay.md` on-demand. Prioridade da skill: δ e Guard > overlay > skill > wording. Pedido explícito de release continua carregando o overlay (T16 / `release-guard`), mesmo com sessão unbound.

**Motivo:** o Auto afogava no overlay sempre-on. Paging sozinho não segura Write; o lote 1 (#609–#611) já compilou a tabela e o Guard.

**Onde:** `scripts/process-fsm/paging.py`, `.cursor/hooks/process-fsm-session-start.sh`, `.cursor/hooks.json`, `.cursor/rules/harness.mdc`, `AGENTS.md`, skill `alan-workflow`. Specs `process-fsm-paging` e `cursor-harness`. Card #613. Epic #608.

## 2026-08-20 - process_event e a unica via Agent para Status (card #612)

**Decisão:** a CLI `scripts/process-fsm/process_event.py` valida δ e só então move o Status do Project 1. Actor da função/CLI é sempre Agent. T1/T7/T15/T16 rejeitam; Alan arrasta no UI. T8 não libera Write (I3). Digest mudado em aplicar/pedir_review vira I4/T17 para Design. T14 live rejeita (`checks_green` unset). T16 é stub: `fechar_release` rejeita e aponta `alan-workflow-ambientes` / `release-guard`. O Guard deny `item-edit` de Status e write do sidecar de digest; sem `PROCESS_FSM_MOVE`.

**Motivo:** o Agent ainda movia coluna com `item-edit` solto e o chat virava T7. O lote 1 do dia (#610/#611) cobriu resolver e Guard Write, não o SMAG de evento.

**Onde:** `scripts/process-fsm/process_event.py`, `guard.py`, `fsm.py`, `.cursor/hooks/process-fsm-guard.sh`. Specs `process-fsm-event`, `process-fsm-guard`, `process-fsm`, `cursor-harness`. Card #612. Epic #608.

## 2026-08-20 - Discovery sempre Deep Backtest 15m + walk-forward 70/30 (card #605)

**Decisão:** toda combinação do Discovery chama `run_optimization` com `deep_backtest=true` e `split_train_ratio=0.7`. Ranking, coverage e elegibilidade 30/90 usam a janela in-sample. Holdout (`oos_metrics` / `oos_verdict`) persiste no JSON `metrics` e não substitui a elegibilidade Discovery. Zero trades IS permanece N/A. Isto substitui, no Discovery, o path legado sem split descrito em 2026-08-19 (#599); Combo/outros callers sem split continuam no helper #599.

**Motivo:** pedido de Alan para o Discovery usar as mesmas opções da tela Combo (Deep 15m + validação 70/30), sem reabrir o #599.

**Onde:** `backend/app/tasks/discovery_tasks.py`, specs `discovery-sweep` e `discovery-leaderboard`. Card #605.

## 2026-08-20 - Guard Write compila a EFSM + resolver (cards #610 e #611)

**Decisão:** o resolver classifica `(q, bound_card, q_git)` pelo worktree do **path**. O Guard Cursor (`preToolUse` + `beforeShellExecution`) compila `.cursor/process-fsm.yaml` + resolver; Write de produto na `develop`/`main` ou fora de I1 é deny. Fail-closed assimétrico: produto deny se `q` ilegível; Design em `card-<id>-*` allow. Impeccable permanece. Residual P2: comando Shell cujo argv não mostra o path de produto (script wrapper).

**Motivo:** a sessão `b6a71170` escreveu `backend/` com `q_git=develop`. Prompt não basta para o Auto.

**Onde:** `scripts/process-fsm/resolve.py`, `scripts/process-fsm/guard.py`, `.cursor/hooks.json`. Specs `process-fsm-resolver`, `process-fsm-guard`, `cursor-harness`. Cards #610 e #611. Epic #608.

## 2026-08-19 - Identidade pública da estratégia é um bloco título+descrição em Combo, Descoberta, Favoritos e Monitor (card #549)

**Decisão:** o título e a descrição públicos da estratégia passam a ser a mesma hierarquia em Combo (select/resultado/edit), Descoberta, Favoritos e Monitor. Admin edita o par global em `/combo/edit/{template}` (inclusive template `is_readonly`); Combo resultado permanece leitura. Persistência: coluna `combo_templates.display_name` + descrição existente; resolvedor banco > mapa > fallback.

**Motivo:** as superfícies mostravam Title-Case do `template_id` ou linhas redundantes, e o Combo select não deixava editar identidade de templates oficiais.

**Onde:** `backend/app/services/strategy_descriptions.py`, Combo edit/select, Discovery/Favorites/Monitor. Spec `strategy-template-descriptions`. Card #549.

## 2026-08-19 - Discovery persiste Calmar/CAGR/B&H no path sem walk-forward (card #599)

**Decisão:** no path legado do optimizer sem `split_train_ratio`, o Discovery calcula e persiste as métricas de ranking (CAGR, Calmar, B&H, Δ B&H) a partir do backtest final. Zero trades ou valores não finitos permanecem `N/A` (null), nunca `0.0`. RSI scalping em 1d com zero sinais deixa de aparecer como ranking zerado.

**Motivo:** o leaderboard mostrava N/A ou zeros artificiais em combinações com trades, e RSI scalping 1d saía com métricas 0.

**Onde:** `backend/app/services/combo_optimizer.py`, spec `discovery-leaderboard`. Card #599.

## 2026-08-19 - Tabela EFSM das 12 colunas versionada em process-fsm.yaml (card #609)

**Decisão:** a EFSM do processo (T0–T17a/b, I1–I9) fica compilável em `.cursor/process-fsm.yaml` com validador e fixtures em `scripts/process-fsm/`. `write_produto` não entra em `illegal_events` (gated por I1). Este card não liga hook Cursor; filhos #610/#611 seguem.

**Onde:** `.cursor/process-fsm.yaml`, `scripts/process-fsm/`, spec `process-fsm`. Card #609. Epic #608.

## 2026-08-17 - Segundo pacote no mesmo dia não herda evidência do lote anterior (card #580)

**Decisão:** `release-guard pre` classifica PR de código vs documental pelo diff de arquivos (`origin/main...HEAD` em `release-*`, senão `origin/main...origin/develop`) contra allowlist de closeout. Existência de `docs/release-YYYY-MM-DD.md` não exige mais `PROD_DEPLOY_EVIDENCE` por si só. Um segundo pacote no mesmo dia atualiza a mesma doc após o deploy; o `post` exige que o SHA da evidência seja ancestral de `origin/main` cujo delta restante ⊆ allowlist, com abreviação ≥7 na doc.

**Motivo:** no lote 2 de 2026-08-17 o `pre` do PR de código #578 só passou reusando `91f5620e` do lote 1.

**Onde:** `scripts/release-guard`, `AGENTS.md`, `openspec/specs/release-worktree-hygiene/spec.md`. Card #580.

## 2026-08-17 - Skills de processo versionadas no GitHub (card #585)

**Decisão:** `alan-workflow`, `alan-workflow-ambientes` e `github-project-board` passam a ser arquivos reais em `.cursor/skills/` no GitHub `oalansilva/crypto`. Hermes e `~/.codex/skills/` ficam em freeze (sem dual-write). Opção B (symlink absoluto, card #584 Cancelado) está revogada.

**Mapa Cursor:** harness alwaysApply curto (preflight de coluna, Gist, OpenSpec ≥ card); runbook na skill; `AGENTS.md` overlay cripto; `rules.md` lei humana. Cópia crypto-scoped (12 colunas). Sem `agents/openai.yaml`.

**Onde:** `.cursor/skills/`, `.cursor/rules/harness.mdc`, `AGENTS.md`, `rules.md`, `openspec/specs/cursor-harness/spec.md`. Card #585.

## 2026-08-17 - Code Review com reviewers locais inherit/readonly (Bugbot opcional)

**Decisão:** o gate `Status=Code Review` passa a usar dois `Task` `generalPurpose` read-only com `model: inherit`: `.cursor/agents/diff-reviewer.md` (bugs no diff) e `.cursor/agents/code-reviewer.md` (processo/OpenSpec/Design). Pré-commit: uncommitted vs HEAD. Fechamento: `origin/develop...HEAD` ainda na branch do card, antes de QA. `/review-bugbot` e `/review-security` só se Alan pedir. Bugbot no dashboard permanece Off de propósito (custo). Autofix não commita na branch existente. Agent Review automático pós-commit permanece desligado. Regras versionadas: `.cursor/BUGBOT.md`.

**Motivo:** Alan recusou ligar o produto Bugbot por custo. O `Task` genérico anterior não versionava o prompt nem comparava com `develop`. Reviewers locais usam o modelo já pago da sessão, aceitam base `develop` explícita, e não geram fatura usage-based.

**Revogação:** a decisão do mesmo dia que tornava `/review-bugbot` obrigatório deixa de valer. O arquivo `.cursor/BUGBOT.md` permanece como contrato lido pelo reviewer local.

**Onde:** `AGENTS.md`, `rules.md`, `docs/backlog-operating-model.md`, `.cursor/BUGBOT.md`, `.cursor/agents/diff-reviewer.md`, `.cursor/agents/code-reviewer.md`. Card #569.

## 2026-08-17 - Code Review nativo com /review-bugbot vs develop

**Decisão:** o gate `Status=Code Review` passa a usar `/review-bugbot` como revisor padrão. Pré-commit: `Diff: uncommitted changes` (sem `Base Branch`). Fechamento: `Diff: branch changes` + `Base Branch: develop`. `/review-security` só nos globs de auth/credencial/trading/wallet/API. Revisor de processo é Task `generalPurpose` read-only com `.cursor/agents/code-reviewer.md`. Autofix não commita na branch existente. Agent Review automático pós-commit permanece desligado. Rules `.mdc` não valem para Bugbot; o contrato visível é `.cursor/BUGBOT.md`.

**Motivo:** o review genérico (`Task` `generalPurpose`) e a regra “bugbot só se Alan pedir” deixavam o revisor nativo do Cursor fora do caminho feliz. A skill oficial não aceita `uncommitted` + `Base Branch`.

**Onde:** `AGENTS.md`, `rules.md`, `docs/backlog-operating-model.md`, `.cursor/BUGBOT.md`, `.cursor/agents/code-reviewer.md`. Card #569.

## 2026-08-17 - Cursor Agent como harness único (cutover OpenCode)

**Decisão:** o Cursor Agent passa a ser o único harness operacional do Cripto Farol. OpenCode sai do contrato ativo. O modelo é o selecionado no chat (hoje Grok 4.6) para Design, código, review e visão. O gate Design fica em regras + skill + Task de crítica isolada + hook Impeccable; sem lease/packet/`design_artifact_write`/attestation OpenCode 1.18.18.

**Motivo:** Alan invertou o destino do #561 (OpenCode único / Sol/Pro/Qwen). O guard multi-artifact já tinha travado o #555/#559. Dual-harness gera docs mentirosas.

**Revogação:** a regra de 2026-08-14 que exigia `design-planner` + GPT 5.6 Sol como autor do Design deixa de ser obrigatória. Mitigação: crítica em Task + aprovação humana em `Pronto para Dev`. Se a qualidade de spec cair, o ajuste futuro é “Sol só no Design”, não reconstruir o guard.

**Onde:** `AGENTS.md`, `rules.md`, `.agents/skills/design-critic/SKILL.md`, `.cursor/`, `docs/backlog-operating-model.md`. Card #562 substitui #561 (Cancelado).

## 2026-08-14 - design-planner obrigatório como autor dos artefatos do gate Design

**Decisão:** o `design-planner` (`openai/gpt-5.6-sol`, effort `high`) deixa de ser opcional/experimental e passa a ser **obrigatório como autor** dos artefatos do gate Design em todo card: `proposal.md`, `design.md` (com Design Critique e veredito), `specs/**` e `tasks.md`, com `UI impact: affected` ou `none`. A sessão principal (Go/flash) consolida, valida OpenSpec, publica e move `Design -> Aprovação de Design`; a crítica independente pode ser feita por segundo spawn do `design-planner` (read-only). Crítica sem artefatos redigidos pelo `design-planner` não completa o gate.

**Motivo:** o card #509 expôs que os artefatos foram redigidos pela sessão principal (deepseek-v4-flash) e o `design-planner` atuou apenas como crítico. Alan aprovou em 2026-08-14 que a redação do gate Design seja sempre executada pelo frontier (`gpt-5.6-sol`), mantendo a consolidação/board na sessão principal.

**Regra atualizada:** `AGENTS.md` (Roteamento de LLM), `rules.md` (regra 9). O card #509 foi refeito com essa regra (artefatos redigidos e republicados pelo `design-planner`).

## 2026-08-13 - Exceção de roteamento design-planner (grok 4.6) no gate Design

**Decisão:** criar o subagent `design-planner` (`.opencode/agent/design-planner.md`) com `model: opencode/grok-4.6` fixo (provider Zen) e `reasoningEffort: high` para executar o contrato `design-critic` no `Status=Design` — segunda exceção explícita à herança de modelo, ao lado do `vision`. Critics A/B do Impeccable herdam o modelo da sessão de design designada; sem igualdade observável, `BLOCKED`.

**Motivo:** o gate Design (specs, crítica, protótipo) é judgment-heavy e acontece uma vez por card; grok 4.6 existe no Zen e não no Go. Evidência de custo (2026-08-13): sessão de exploração rodando `opencode/grok-4.6` como **sessão principal** gastou ~$3,03–$3,30 (590k input, 8,5M cache_read) — orquestração no frontier não é viável. Regra resultante: **grok nunca roda como sessão principal**; o planner recebe packet compacto e roda como spawn isolado (sem teto de custo por card).

**Regra atualizada:** `AGENTS.md` (Roteamento de LLM, Impeccable, subagents), `rules.md` (regras 4 e 9), `.agents/skills/design-critic/SKILL.md` (igualdade A/B = sessão de design designada), `.opencode/agent/kaizen.md` (routing-drift: vision + design-planner). Go (volume) e Zen (frontier pontual) coexistem; fallback `opencode-go/grok-4.5` (effort high) só com autorização de Alan.

**Rework 2026-08-13 (mesmo dia):** Alan trocou o modelo do `design-planner` de `opencode/grok-4.6` (Zen) para **`openai/gpt-5.6-sol` (OpenAI via OAuth, effort `high`)** — GPT Sol High. Ajustes: agent frontmatter, OpenSpec (proposal/design/specs), AGENTS.md, rules.md, design-critic SKILL.md. **Sem controle de custo por card** (decisão de Alan); mantém-se apenas o isolamento do spawn (frontier nunca como sessão principal). Zen permanece conectado, mas deixa de ser o provider do gate Design. Card #491 mantém `Status=Done` (regra de não regressão).

## 2026-08-10 - Coluna Em Refinamento como primeira coluna e entrada obrigatoria de todo card novo

**Decisao:** adicionar a coluna `Em Refinamento` como primeira coluna do board Project 1 (opcao do campo `Status` na posicao 0, antes de `Todo`) e como entrada obrigatoria de todo card novo. Em `Em Refinamento`, Alan escolhe, prioriza (campo `Prioridade`) ou cancela o card antes de ele ir para `Todo`. Cards kaizen tambem nascem em `Em Refinamento` (nao mais em `Todo`).

**Motivo:** Alan pediu uma coluna de triagem/priorizacao antes do backlog; cards novos entram nela e so seguem para `Todo` apos refinamento humano.

**Regra atualizada:** `AGENTS.md`, `rules.md`, `docs/backlog-operating-model.md` e `.opencode/commands/kaizen.md` passam a refletir o fluxo `Em Refinamento -> Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`, com `Cancelado` terminal e acionavel inclusive a partir de `Em Refinamento`. Os 4 cards que estavam em `Todo` (Backup de ambiente, #456, #457, #458) foram movidos para `Em Refinamento` para triagem de Alan.

**Nota operacional:** a API GraphQL (`updateProjectV2Field`) recria as opcoes do campo single-select com IDs novos ao atualizar `singleSelectOptions`, invalidando os valores de Status existentes; a reconstrucao do board foi feita a partir de snapshot anterior e validada contra o estado original (162 Pronto, 13 Cancelado, 4 Em Refinamento, 2 Em desenvolvimento). A definicao de opcao padrao do campo `Status` nao e exposta pela API; o default foi configurado manualmente na UI do board (Settings do campo Status) e **confirmado por Alan**: `Em Refinamento` como `Default`, descricao "Entrada obrigatoria de todo card novo: Alan escolhe, prioriza ou cancela antes de ir para Todo" — cards novos entram automaticamente em `Em Refinamento`.

## 2026-08-08 - Pronto exige deploy em PROD (source + services + URL pública)

**Decisao:** o fechamento de release passou a exigir deploy em PROD antes de mover cards para `Pronto`. Merge em `main` sozinho nao e evidencia de `Pronto`. Passos obrigatorios em `/srv/apps/prod/criptofarol/source`: `git fetch origin && git reset --hard origin/main`, `alembic upgrade head`, build frontend com `VITE_APP_ENV=production`, restart dos services PROD afetados e validacao do endpoint publico `https://criptofarol.com.br`.

**Motivo:** na release 2026-08-08 os cards foram movidos para `Pronto` apos o merge em `main`, mas o runtime PROD continuou no commit da release anterior (`cd0a3401`), com dist antigo e migration pendente — a regra local definia `Pronto = main` sem o passo de runtime, e a skill `alan-workflow-ambientes` (mapa DEV/PROD e deploy) nao foi carregada durante o fechamento. O deploy foi corrigido depois (commit `d237b078`, migration `20260803_0001`, bundle novo, services reiniciados, endpoint validado).

**Regra atualizada:** `AGENTS.md` e `rules.md` do cripto passam a exigir `alan-workflow-ambientes` em qualquer pedido de release/publicacao/lote/deploy e o passo de deploy PROD antes de `Pronto`.

## 2026-08-03 - Impeccable obrigatório no Design do Codex

**Decisao:** integrar o Impeccable em escopo project-local somente no Codex. Cards com `UI impact: affected` passam a registrar `Impeccable Brief`, crítica dual-agent, audit, trace, correções direcionadas, polish e nova validação em navegador real antes de `Design Agent verdict: PASS`. Cards `UI impact: none` registram Impeccable como `N/A`, sem reduzir o gate humano de Design.

**Modelo:** Assessment A e Assessment B são critics read-only independentes e devem herdar exatamente o mesmo LLM/modelo e versão da sessão principal do Codex. Sem evidência observável de igualdade, o veredito é `BLOCKED`; não há fallback. Cursor permanece no contrato base `design-critic` e não recebe este provider.

**Versionamento:** pacote CLI npm `impeccable@3.5.0`; payload instalado da skill declara `4.0.4`; `gitHead` npm `9a949fb543d44cfb406f61bcab99d95d7f12cf1d`. Arquivos versionados: `.agents/skills/impeccable/`, `.codex/hooks.json`, `PRODUCT.md` e o bloco oficial de ignore do `.impeccable`.

**Fontes e proteção:** `PRODUCT.md` foi derivado de `docs/project-hub.md`, `docs/mvp-scope.md` e `docs/brand-system.md`. `DESIGN.md` continua a autoridade visual e não foi alterado pelo setup. A mudança não reabre nem reutiliza os cards cancelados `362` e `369`.

**Rollback:** remover `.codex/hooks.json`, `.agents/skills/impeccable/`, `PRODUCT.md` e o bloco de ignore, preservando `design-critic`, `DESIGN.md`, protótipos e os gates existentes. Não há alteração de API, banco, runtime de produção ou status de card.

## 2026-08-01 - Browser gate obrigatório para protótipos

**Decisao:** nenhum protótipo com UI pode receber `Design Agent verdict: PASS` apenas por build, HTTP 200, `curl` ou inspeção do código. A versão final servida deve ser aberta em navegador real, validada em desktop/mobile e ter estado padrão, interações e critérios críticos comprovados por asserts observáveis.

**Remoções:** o estado final precisa provar que o elemento removido não existe ou não está visível. O incidente do #353 mostrou que `hidden=true` podia ser neutralizado por CSS (`display:flex`), algo que HTTP 200 não detecta.

**Evidência:** registrar URL, viewports, ações/asserts e resultado em `design.md` (`## Prototype Validation`). Alteração posterior em HTML/CSS/JS ou rebuild/restart invalida a evidência. Sem navegador ou com falha, o card permanece em `Design` com veredito `BLOCKED`.

**Onde:** `rules.md`, `AGENTS.md`, `.agents/skills/design-critic`, `alan-workflow`.

## 2026-08-01 - Protótipo baseado no sistema atual (quando a tela já existir)

**Decisao:** em Design, se a tela/rota/shell já existir no produto, o protótipo deve partir da UI atual e redesenhar só o delta do card, para Alan validar a diferença. Proibido mock paralelo/genérico. Tela ainda inexistente pode ser desenhada do zero, alinhada a `DESIGN.md` e ao shell autenticado.

**Onde:** `rules.md`, `AGENTS.md`, `.agents/skills/design-critic` (+ adaptadores), `alan-workflow`.

## 2026-08-01 - Design gate obrigatório sem bypass

**Decisao:** todo card do Project 1/Cripto deve passar por `Design -> Aprovação de Design -> Pronto para Dev` antes de qualquer implementação. Não existe bypass `Todo -> Pronto para Dev`.

**Escopo:** vale para UI e não-UI, remoções, bugs, docs com card e pedidos de chat como `implemente` / `pode codar`. `UI impact: none` só reduz o peso da evidência (Prototype pode ser N/A explícito); não pula colunas.

**Aprovação:** apenas Alan autenticado move `Aprovação de Design -> Pronto para Dev`. OpenSpec `design.md` não substitui a coluna Kanban `Design`.

**Relação com decisões anteriores:** esta decisão altera a regra de bypass registrada em 2026-07-31 e alinha `rules.md`, `AGENTS.md`, `design-critic`, `alan-workflow` e `github-project-board`.

## 2026-07-31 - Gate humano de design antes do desenvolvimento

**Decisao:** substituir `In Progress` por `Em desenvolvimento` e adotar o fluxo `Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto` no Project 1, Kanban interno e instruções de Codex/Cursor.

**Aprovação:** para cards com impacto de UI, o Designer/Critic Agent produz ou refatora o protótipo, executa crítica de produto, UX, acessibilidade, responsividade e estados e move apenas `Design -> Aprovação de Design` quando a evidência estiver completa. Alan aprova a versão revisada arrastando `Aprovação de Design -> Pronto para Dev`; nenhum agente pode executar ou simular essa transição.

**Bypass (revogado em 2026-08-01):** a permissão antiga de `Todo -> Pronto para Dev` com `UI impact: none` foi removida. Todo card passa por Design.

**Agentes:** o contrato canônico do Designer/Critic Agent fica em `.agents/skills/design-critic/SKILL.md`, com adaptadores finos para Codex e Cursor. OpenSpec usa a mesma ordem operacional por `/opsx:*` e pelos aliases Cursor `/opsx-*`.

**Relação com decisões anteriores:** esta decisão substitui o vocabulário e a sequência operacional definidos em 2026-07-12, preservando `QA` como gate automatizado, `Done` como checkpoint técnico, `Homologado` como aprovação funcional de Alan e `Pronto` como publicação final.

## 2026-07-12 - Gate QA automatizado entre Code Review e Done

**Decisao:** adotar o fluxo `Todo -> In Progress -> Code Review -> QA -> Done -> Homologado -> Pronto` no Project 1 e na operação técnica. `QA` é um gate automatizado, não substitui a homologação funcional do Alan.

**Regra:** depois do Code Review limpo, o SHA revisado entra em QA. `Done` exige `qa-gate` verde, Playwright visual executado ou dispensado explicitamente por Alan, integração em `develop`, `./restart` e validação do runtime. Falha de código retorna a `In Progress -> Code Review -> QA`; falha de infraestrutura permanece em QA para rerun documentado.

**QA visual:** todo card executa regressão Playwright por padrão, inclusive sem mudança de frontend. Dispensa exige label `qa-visual-skip` e comentário de Alan iniciado por `QA visual dispensado por Alan.` com motivo.

**Motivo:** separar revisão humana de validação automatizada e impedir que uma entrega tecnicamente revisada avance sem prova visual, de testes e de runtime.

**Relação com decisão anterior:** esta decisão substitui apenas a sequência operacional descrita em 2026-05-08 para cards da Clara; preserva `Done` como checkpoint técnico, `Homologado` como aprovação de Alan e `Pronto` como publicação final.

## 2026-04-28 - Stack de acompanhamento do projeto

**Decisao:** usar GitHub Projects + Issues como fonte operacional de execucao e `crypto_backlog_po.xlsx` no SharePoint como visao executiva/produto.

**Motivo:** nao manter dois backlogs ativos. GitHub e melhor para issue, PR, commit, teste, status e rastreabilidade tecnica; a planilha e melhor para roadmap macro, decisao de produto, validacao comercial e evidencia executiva consolidada.

**Alternativas avaliadas:**

- Trello: simples, mas fraco para rastrear PR/commit/teste.
- Linear: excelente, mas adiciona ferramenta e limite no plano gratuito.
- Notion: bom para documentacao, mas pode virar base paralela e gerar dispersao.
- ClickUp: completo, mas pesado demais para a fase atual.
- Taiga/OpenProject/Kanboard self-hosted: gratuitos, mas adicionam manutencao.

**Regra:** Telegram nao e fonte da verdade. Chat serve para alinhamento rapido; item em execucao vive no GitHub Project; a planilha recebe resumo/evidencia apenas quando isso mudar produto, roadmap, beta ou negocio.

## 2026-04-28 - Criterio de conclusao

**Decisao:** item concluido precisa de evidencia.

**Evidencias aceitas:** PR, commit, resultado de teste, print, log, feedback real de usuario, link de arquivo ou decisao registrada.

**Motivo:** evitar status inventado e separar intencao de efeito confirmado.

## 2026-05-07 - Hub unico de consulta rapida do projeto

**Decisao:** manter `docs/project-hub.md` como documento central de consulta rapida do projeto, sem substituir o GitHub Project como fonte operacional.

**Motivo:** Alan pediu um local unico para consultar definicoes, status atual e organizacao do produto/projeto sem depender apenas dos cards.

**Regra:** cards continuam sendo execucao; o hub consolida objetivo, estado atual, bloqueios, decisoes e links para os documentos detalhados.

## 2026-05-08 - Nome e dominio do produto

**Decisao:** usar **Cripto Farol** como nome do produto e `criptofarol.com.br` como dominio principal.

**Motivo:** decisao explicita de Alan apos rodadas de naming. O nome comunica orientacao e apoio a decisao sem prometer lucro.

**Evidencia:** whois retornou sem match para `criptofarol.com.br` e `criptofarol.com` no momento da checagem. Busca web rapida encontrou ruido para a expressao `Cripto Farol` ligado a curso/reclamacao; isso fica registrado como ponto de atencao, nao bloqueio.

**Proximo passo:** Alan registrar o dominio no card `#154`; depois atualizar DNS, landing, copy e identidade visual.

## 2026-05-08 - Definicoes homologadas para beta fechado

**Decisao:** consolidar como base do produto as definicoes homologadas por Alan nos cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159`.

**Definicoes consolidadas:**

- Direcao visual: clareza, criterio e vigilancia tranquila.
- Ambiente: VPS atual, frontend como entrada, backend interno e cadastro publico desabilitado.
- Divulgacao: rede quente e abordagem direta antes de canal amplo.
- Feedback: roteiro estruturado via Telegram.
- Metricas: 10 a 20 interessados, 3 a 5 testers ativos, 3 feedbacks completos e 2 sinais de valor.
- Validacao: checklist com tarefas reais no Monitor.
- Captacao: formulario simples com triagem manual.
- Landing: headline "Enxergue melhor antes de decidir em cripto" e CTA "Entrar na lista do beta fechado".

**Regra:** essas definicoes devem sobreviver aos cards e orientar landing, onboarding, comunicacao e validacao.

## 2026-05-08 - Fluxo de revisao dos cards da Clara

**Decisao:** quando Clara concluir um entregavel, deve mover o card para `Status=Done` e `Fluxo=Validate`, nunca para `Pronto`.

**Motivo:** Alan corrigiu o fluxo para que `Done` seja o estado usado para revisao/homologacao dele.

**Regra:** se ainda falta execucao real, manter em `In Progress`; se o entregavel esta produzido e precisa de revisao de Alan, mover para `Done / Validate`.

## 2026-05-09 - Release documental dos cards homologados

**Decisao:** quando Alan pedir uma release de cards no nome da Clara ou do Alan, os cards `Homologado` e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos no pacote devem ter suas decisões e entregáveis consolidados na documentação local e no Google Drive antes de serem movidos para `Pronto`.

**Cards incluídos nesta release documental:** `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159`.

**Documentos revisados:** `docs/project-hub.md`, `docs/mvp-scope.md`, `docs/beta-validation.md`, `docs/backlog-operating-model.md` e `docs/decision-log.md`.

**Evidencia:** PR `#175` mergeado em `main` com merge commit `9ecbf88`; Google Docs/Drive sincronizados; `openspec validate --all` passou; CI do PR passou.

**Resultado:** cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159` movidos de `Homologado / Validate` para `Pronto / Done`.

**Regra:** release documental concluída com evidência permite avançar os cards da Clara ou do Alan incluídos de `Homologado` para `Pronto`. Cards de `Codex` ficam fora deste fluxo e seguem o fluxo técnico próprio do Codex.

## 2026-05-09 - Identidade visual minima do beta

**Decisao:** fechar a identidade minima do Cripto Farol com wordmark, simbolo isolado, paleta, tipografia e criterio de uso suficientes para landing, captacao e tela inicial do beta.

**Arquivos entregues:** `docs/brand-system.md`, `frontend/public/brand/cripto-farol-mark.svg` e `frontend/public/brand/cripto-farol-wordmark.svg`.

**Regra:** a identidade do beta deve comunicar clareza, criterio e vigilancia tranquila, sem estetica de guru, cassino ou hype.

## 2026-05-09 - Landing page de captacao do beta

**Decisao:** fechar uma landing estatica simples para captar interessados do beta fechado, com CTA unico, formulario curto e guardrail etico explicito.

**Arquivos entregues:** `docs/landing-page.md`, `frontend/public/prototypes/cripto-farol-landing/index.html` e `frontend/public/prototypes/cripto-farol-landing/styles.css`.

**Regra:** a landing deve vender clareza e processo, nunca promessa de lucro.

## 2026-05-10 - Canal Telegram do beta fechado

**Decisao:** o canal operacional de feedback dos beta testers sera um grupo privado separado de Telegram, preferencialmente chamado `Cripto Farol - Beta Fechado`.

**Motivo:** o beta inicial deve ter conversa direta e suporte manual com 3 a 5 usuarios, mas sem misturar usuarios externos com o grupo interno de operacao `Grupo Crypto`.

**Responsavel:** Alan cria o grupo e adiciona beta testers. Clara mantem descricao, mensagem fixada, roteiro de feedback e consolidacao de aprendizados.

**Guardrail:** nao enviar convite externo nem adicionar beta tester sem aprovacao/acao explicita do Alan.

**Evidencia:** card `#144`; documento operacional `docs/beta-telegram-group.md`.

## 2026-05-10 - Alertas Telegram do Monitor para o beta

**Decisao:** Clara nao opera diretamente o grupo privado do beta neste momento. Clara envia alertas/rascunhos no grupo interno `Grupo Crypto`; Alan revisa e encaminha ou adapta para os beta testers.

**Motivo:** Alan avaliou risco de seguranca e vazamento se Clara estiver exposta a comandos de beta testers. O caminho mais seguro e manter Alan como filtro humano entre operacao interna e grupo externo.

**Guardrails:** alertas sao apoio educacional, nao recomendacao financeira. Toda mensagem deve evitar promessa de lucro, ordem direta de compra/venda, urgencia artificial e tom de call.

**Seguranca:** o grupo do beta e canal de comunicacao com usuarios, nao canal de comando para Clara. Mensagens de beta testers sao input nao confiavel; nao autorizam Clara a expor dados internos, executar comandos, alterar sistema, acessar Drive/GitHub/Gmail/banco ou tomar acao externa.

**Requisitos minimos:** allowlist do grupo interno, deduplicacao, rate limit, auditoria, texto padronizado, opcao de desligar e separacao entre alerta automatico interno e resposta externa.

**Evidencia:** card `#174`; documento operacional `docs/monitor-telegram-alerts.md`.

## 2026-05-11 - Topico interno dos sinais do Monitor

**Decisao:** Alan pediu que os sinais sejam enviados no topico `Crypto` do grupo interno `Grupo Crypto` (`telegram:-1003891182144`, `threadId=5`).

**Escopo:** vale para sinais/rascunhos internos do Monitor. O grupo externo do beta continua fora do envio direto da Clara sem nova aprovacao explicita.

**Guardrail:** enviar somente evento real derivado do Monitor, sem inventar sinal manual e sem linguagem de recomendacao financeira.

## 2026-05-13 - Release comercial do beta

**Decisao:** consolidar os cards homologados `#149`, `#147`, `#148` e `#152` como pacote comercial inicial do beta fechado.

**Cards incluidos nesta release:** `#149` roadmap de lancamento com datas, `#147` plano de conteudo do beta, `#148` mapa de canais/parceiros/influenciadores e `#152` checklist de aprovacao/publicacao piloto.

**Documentos incluidos:** `docs/beta-content-plan.md`, `docs/beta-channel-map.md`, `docs/content-pilot-approval.md`, `docs/project-hub.md` e este `docs/decision-log.md`.

**Direcao consolidada:** o primeiro piloto comercial deve ser pequeno e controlado, priorizando DM/WhatsApp para rede quente, leads proprios e LinkedIn. Comunidades externas, grupos grandes de Telegram e influenciador pago ficam para depois de validacao interna e aprovacao explicita.

**Guardrail:** nenhum convite, publicacao externa, abordagem de parceiro ou disparo em grupo foi autorizado por esta release. Toda acao externa continua dependendo de aprovacao/acao explicita do Alan.

**Fora da release:** `#197` lista inicial de contatos segue em execucao sob responsabilidade do Alan para envio manual via WhatsApp.

## 2026-05-18 - Release tecnica/documental com todos os responsaveis

**Decisao:** ao subir uma release, considerar todos os cards `Homologado` incluídos no pacote, independente do responsavel.

**Cards incluídos nesta release:** `#217`, `#216`, `#213`, `#208`, `#75` e `#77`.

**Fluxo consolidado:** cards de `Codex` exigem commits/branches, PR, testes e merge em `main`; cards de `Clara` ou `Alan` exigem revisao documental local em `docs/` e sincronizacao com Google Drive quando aplicável.

**Documentos revisados:** `docs/project-hub.md`, `docs/backlog-operating-model.md`, `docs/decision-log.md` e `docs/release-2026-05-18.md`.

**Guardrail:** documento de produto/processo atualiza Markdown local e Drive sem divergencia; execucao/status atualiza GitHub Project e Issue/PR quando houver codigo.

## 2026-05-20 - Higiene de WIP e output em release

**Decisao:** WIP salvo em branch de backup deve ser revisado e integrado por branch normal; artefatos gerados em `output/` nao entram em `develop` nem `main`.

**Motivo:** a release de 2026-05-20 encontrou alteracoes uteis misturadas com evidencias locais do Playwright em `output/playwright`. O backup preservou tudo para nao perder trabalho, mas o lixo apareceu porque o repo ainda nao ignorava `output/` e porque o WIP estava solto na worktree antes do fechamento.

**Regra:** antes de release, todo `git status --short` precisa classificar arquivos como codigo, documentacao, evidencia operacional ou descarte. Evidencia operacional gerada localmente fica fora do Git, salvo quando existir decisao explicita de versionar.

**Evidencia:** issue `#231`, branch `change-231-integrar-wip-flow-cleanup` e backup original `backup/develop-wip-20260520-022324`.
