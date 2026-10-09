## Why

O Guard nega `openspec/changes/**` em `release-*` com `q=None`/`bound_card=⊥` (`fail_closed`), e o closeout cai no desvio worktree-do-card + cherry-pick. Este card torna oficial o archive no caminho `release-*` já documentado, com o pacote resolvido e sem aprovação operacional extra.

## Problema

Alan e o agente que fecha uma release já solicitada encontram bloqueio no arquivamento das mudanças concluídas do pacote, precisam contornar o contexto de trabalho e podem interromper o fechamento para pedir confirmações operacionais redundantes.

## História

Como Alan, quero que o agente consiga arquivar as mudanças concluídas e homologadas de uma release solicitada pelo caminho oficial, com o pacote identificado e os limites de escrita preservados, para concluir o fechamento sem desvio improvisado nem repetir autorizações já dadas.

## Entra

- Caminho oficial e documentado para arquivar as mudanças concluídas do pacote durante o fechamento de uma release explicitamente solicitada.
- Identificação dos cards, do estado e da pertinência de cada mudança ao pacote antes de permitir o arquivamento.
- Correção coordenada entre o controle de escrita e o runbook, com regressão do bloqueio já observado e evidência no próximo fechamento aplicável.

### Critérios observáveis

- [ ] Com release solicitada, pacote identificado e mudanças concluídas e homologadas, o agente consegue preparar e registrar o arquivamento pelo caminho oficial sem bloqueio causado apenas pela ausência de um único card vinculado ao contexto da release.
- [ ] O caminho oficial é executável sem intervenção manual de Alan nem nova confirmação para operações já autorizadas. Se exigir contextos de trabalho vinculados aos cards, o agente conduz essa preparação e a incorporação do resultado conforme o contrato definido no Design.
- [ ] Quando não for possível identificar o pacote, resolver o estado dos cards ou comprovar que a mudança pertence ao pacote autorizado, a escrita correspondente continua bloqueada e o motivo é informado. O nome da branch ou uma lista declarada de cards, isoladamente, não libera o arquivamento.
- [ ] A correção fica limitada aos arquivos de mudanças OpenSpec envolvidos no arquivamento autorizado. Escrita de produto, arquivos fora desse escopo e contextos que não sejam de release mantêm as permissões atuais.
- [ ] A regressão reproduz o bloqueio registrado, comprova o arquivamento permitido com contexto válido e comprova a negativa para contexto não resolvido ou mudança fora do pacote, sem relaxar as demais proteções.
- [ ] O contrato documentado identifica um caminho normal de fechamento e sua evidência. A próxima release aplicável consegue registrar o archive sem desvio improvisado, e a verificação Kaizen registra se a recorrência foi encerrada.
- [ ] A integração com #1059 usa esta correção e o mesmo contrato de archive, sem duas implementações concorrentes nem nova aprovação operacional extraída do texto deste issue.

## Não entra

- Ampliar permissões de escrita fora do arquivamento autorizado, ignorar uma negativa do guard ou incluir conteúdo não homologado no pacote.
- Alterar a FSM, substituir decisões humanas de aprovação ou homologação, ou executar uma release por causa deste refinamento.
- Absorver os demais ajustes de continuidade, perguntas, manifesto, evidências e fechamento geral de #1059.

## What Changes

- O Guard deixa de negar, só por `q=None`/`bound_card=⊥`, a escrita de archive OpenSpec em `release-*` quando o pacote, o estado dos cards e a pertinência da mudança estão resolvidos.
- O runbook de publicação (`overlay_doc`) e a skill `covenant-flow` passam a tratar esse archive em `release-*` como caminho normal, sem worktree-do-card + cherry-pick e sem confirmação extra de Alan.
- A regressão cobre o deny observado (`fail_closed` em `release-*` unbound), o allow com contexto válido e o deny para pacote não resolvido ou mudança fora do pacote.
- #1059 consome este contrato; este card não implementa continuidade, manifesto, evidências nem fecho geral.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `process-fsm-guard`: em `q_git=release-*` unbound, escrita de `openspec/changes/**` do archive autorizado deixa de ser `fail_closed` automático; produto, protótipo e contextos que não sejam `release-*` mantêm o deny actual.
- `release-archive-via-release-branch`: o archive OpenSpec do pacote Homologado ocorre na própria `release-*`, sem desvio cherry-pick, com evidência no próximo closeout aplicável.
- `covenant-flow`: o runbook de release nomeia este caminho como oficial, recusa aprovação operacional extra extraída do issue, e aponta #1059 como consumidor do mesmo contrato.

## Impact

`scripts/process-fsm/guard.py` (decisão de escrita, sem estado/evento/hook/`enabled_tools` novos), testes de `scripts/process-fsm/` com Status injectado (sem GitHub), `docs/crypto-overlay.md` (secção de publicação/archive em `release-*`) e a secção Release de `.cursor/skills/covenant-flow/SKILL.md`. Resolver continua a devolver `bound_card=⊥` em `release-*`. Nenhuma API, tela, `backend/**` ou `frontend/src/**`. Este card não executa uma release.
