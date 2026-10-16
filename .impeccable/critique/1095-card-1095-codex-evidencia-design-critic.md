# Snapshot de crítica — #1095

Data: 2026-10-13. Papel: design-critic; faixa: juizo. Rodada sem tela: um autor, este crítico e no máximo um rework ordinário. Snapshot independente de conteúdo; não certifica execução runtime, publicação, T5 ou aprovação humana.

## Contexto e validações

- Card: oalansilva/crypto#1095, «Codex: coletar evidência de execução e detectar indisponibilidade antes de iniciar etapas».
- Status consultado por `gh issue view 1095 --repo oalansilva/crypto --json number,projectItems`: `Design`, projeto `MVP Cripto - Beta Fechado`.
- Branch consultada: `card-1095-codex-evidencia`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1095-codex-evidencia`.
- Fontes lidas: AGENTS.md, skills canônicas covenant-flow e design-critic, briefing REST `/tmp/issue-1095.json`, captura de seleção e os quatro artefatos da change `openspec/changes/card-1095-codex-evidencia`.
- Artefatos: `proposal.md`, `design.md`, `tasks.md`, `specs/codex-runtime-evidence/spec.md`.
- Verificação programática: Problema, História, Entra e Não entra do briefing aparecem literalmente e em conjunto na proposta (`briefing_copied_verbatim=True`).
- Não houve implementação, mudança de estado, commit, push, publicação, alteração de hooks/trust nem nascimento de outro agente. Este crítico grava somente este snapshot.

## Resultado emitível

- P0: nenhum achado.
- P1: nenhum achado.
- P2: nenhum achado.
- P3 — token documental: `live_route: none` não é reconhecido pelo parser local; disposition: corrigir no rework já previsto para `live_route: N/A processo local Codex, sem rota de produto`, mantendo `UI impact: none` e `surface: none`. Não exige nova rodada de crítica.
- P3 — detalhe de Apply: nome do módulo, códigos de erro, limite de espera, layout privado da extração e plumbing de CLI; disposition: aceito conforme a seção Accepted Apply Details, resolver no Apply sem reabrir como P0/P1.
- verdict: PASS de conteúdo; normalização documental no rework previsto. Avanço continua condicionado aos gates existentes e à evidência runtime coletada pelo pai.

## Análise de contrato

O usuário afetado é o operador que hoje descobre a indisponibilidade da comprovação depois de receber trabalho útil. A proposta preserva essa história; o desenho responde com recusa antes de nascimento e transição dependente, e com recuperação quando uma fonte inicialmente disponível falha durante o trabalho. Não transforma um preflight positivo em promessa de conclusão.

| Dimensão | Evidência nos artefatos | Avaliação |
| --- | --- | --- |
| Preflight antecipado | Decisão 2, requisito Evidence availability e tasks 2.1–2.2; verifica sessão, host/versão, schema, fonte, identidade, captura e destino | Cobre nascimento e transição, inclusive card já na coluna; recusa preserva Status e artefatos |
| Coleta automática | Decisões 1 e 3, requisito Observations automatically collected, tasks 1.2 e 2.3 | Fonte de runtime exigida; índice é localizador; nenhuma aprovação por flags manuais |
| Proveniência | Registro de nascimento, retorno nativo, filiação e eventos devem concordar; extração mínima com referência e digest | Rejeita último arquivo, cwd ou timestamp como prova suficiente; explicita limite cooperativo |
| Identidade e temporalidade | Captura imutável, parent/child e turnos; requisito Evidence belongs; task 3.4 | Outro filho, outro turno ou seleção posterior não validam tentativa atual; turno final válido não apaga divergência anterior |
| Requested versus observed | Separação explícita, campos ausentes unavailable, binário local não prova versão do host | Não infere observado da configuração ou relato do filho |
| Conclusão e payload | Evento terminal do turno concorda com completed e conteúdo devolvido pelo host | Texto final isolado não basta; falta de payload continua recusa |
| Recuperação | Decisão 5, requisito Collection failure, task 2.4 | Recoleta íntegra idempotente; origem irrecuperável exige novo nascimento sem apagar trabalho |
| Gates preservados | Decisão 4 e requisito Existing gates | Dois reviewers distintos, onda read-only, mesmo diff, sandbox observado, checklist, crítica e aprovação humana mantidos |
| Escopo | Não entra da proposta e Goals/Non-Goals | Sem Donchian/#1086, outros adapters, fallback de cliente, retuning, trust automático ou modo Auto |
| Prova real | Migration Plan, requisito Support claims, tasks 4.1–4.3 | Suporte exige ensaio nativo completo e recusas; fixtures não promovem outro host/versão |

A fonte local descrita em design.md é explicitamente candidata. Esta crítica não inspecionou os rollouts citados nem converte sua descoberta em comprovação independente de suporte. A prova end-to-end permanece entrega de Apply. A qualificação sem trabalho de produto e sem transição evita que o host precise estar previamente qualificado para realizar seu primeiro ensaio, mantendo as permissões existentes.

O envelope e seus consumidores revalidam vínculo e integridade em vez de confiar em um booleano de sucesso. O desenho também reconhece que digest de arquivo local não é atestado do servidor. Essa distinção é adequada ao contrato cooperativo solicitado.

## Estados e usabilidade operacional

Não existe tela de produto, protótipo, rota, layout ou fluxo visual para avaliar. Personas adicionais e tabela Nielsen de interface seriam artificiais. A avaliação de uso concentrou-se no operador do briefing:

- Antes do trabalho: ready/blocked contém etapa/card, host/versão, causa, fonte/campo e recuperação; ambiente não comprovado permanece unverified.
- Depois de falha transitória: trabalho e Status ficam preservados; recoleta da mesma tentativa usa captura original e não duplica a onda.
- Depois de divergência/origem irrecuperável: recusa visível e novo nascimento; artefatos anteriores podem ser insumo, sem se tornarem prova de execução.
- Ao declarar suporte: matriz por host/versão distingue exploração, teste simulado e prova real reproduzível sanitizada.

## Rubrica de tokens

Parser inspecionado: `scripts/process-fsm/design_clone_gate.py`, funções `parse_ui_impact`, `parse_live_route`, `parse_surface` e `evaluate_clone_gate`.

Execução real via Python 3 contra design.md:

```text
ui = none
live = (None, '')
surface = none
clone_gate = True
```

A regex aceita rota iniciada em `/`, `landing` ou `N/A`, não `none`. O gate de clone atual retorna True pela condição `ui == none` sem superfície existente; portanto não há alegação de bloqueio desse gate nesta versão. A exigência de tokens parseáveis da skill continua justificando a normalização documental. Ensaio da linha proposta retornou `('N/A', 'processo local Codex, sem rota de produto')`. Não emprestar rota do catálogo nem produzir protótipo para sanar o token.

## Cobertura de testes prevista

Tasks 3.3–3.5 cobrem fonte ausente, host/schema desconhecido, cliente ambíguo, perda de permissão, truncamento/timeout, divergências de modelo/esforço, identidades e capturas erradas, seleção posterior, continuação divergente, terminal sem payload, fontes conflitantes, adulteração de digest, flags manuais, duplicidade e regressões de sandbox/diff/onda e outros adapters. Tasks 4.1–4.4 adicionam prova positiva nativa, recusas reais, documentação e suíte pertinente. Nenhuma task foi executada ou marcada feita por esta crítica; testes de implementação não cabem nesta etapa.

## Metadata de seleção e observação

Origem de requested: `/tmp/1095-design-critic-selection.json`.

```yaml
role: design-critic
band: juizo
client_requested: codex
attempt_id: fbcb053d-b115-4cea-85df-58ec21d7e4b1
capture_sha256: 2810321abead70c13624ae6f103c51082b08bc5d4110b81d5ac0ebe0c9178670
requested:
  label: GPT-6 Astra
  model: gpt-6-astra
  reasoning_effort: medium
observed:
  model: unavailable
  reasoning_effort: unavailable
  host: unavailable
  version: unavailable
  child_id: unavailable
  turn_id: unavailable
  runtime_terminal_status: unavailable
```

Os campos observados não foram coletados por este crítico. O pai coletará o runtime após o retorno e deve vincular a evidência verificável ao nascimento/turno; configuração solicitada e este snapshot não os substituem. `completed` será confirmado pelo host no retorno com payload, sem declaração antecipada de equivalência requested/observed.

proxy modelo: design-critic → GPT-6 Astra (gpt-6-astra)

HTML gerado/copiado: N/A. Spawns executados por este crítico: 0. O veredicto de conteúdo não elimina falha de gate por metadata indisponível.
