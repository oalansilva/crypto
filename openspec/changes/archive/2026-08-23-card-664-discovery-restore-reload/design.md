## Context

Card [#664](https://github.com/oalansilva/crypto/issues/664) corrige a perda aparente de uma varredura após reload da tela de Descoberta. A tela atual mantém `activeSweep` e `viewSweep` apenas em estado React; `GET /combos/discovery/sweeps/history` já lista runs não terminais, mas o carregamento inicial não promove nenhuma delas a sweep ativo nem reidrata o snapshot do rascunho. Além disso, `DiscoveryService.command("resume")` altera `paused` para `running` sem garantir um novo intent na outbox depois que o intent anterior foi confirmado.

**Status do gate**

- Card: `#664`
- Change: `card-664-discovery-restore-reload`
- Status observado: `Design`
- **UI impact: affected** — a tela autenticada existente de Descoberta ganha recuperação explícita de sessão e estados de reconexão.
- Aprovação humana: pendente. Este documento não aprova nem libera implementação.

O usuário é o administrador do beta fechado que inicia uma análise potencialmente longa, pode fechar/recarregar a página e precisa saber se o servidor continua executando, pausou, falhou ou terminou. O servidor é a fonte de verdade; `sessionStorage` pode conservar apenas preferências efêmeras do rascunho, nunca o lifecycle ou os contadores.

## Goals / Non-Goals

**Goals**

- Reconstituir o sweep não terminal mais recente do ator autenticado ao abrir `/combo/discovery`, sem ocultar outros sweeps não terminais.
- Mostrar o mesmo `sweep_id`, snapshot, estado e contadores do `GET /sweeps/{sweep_id}`; restaurar o leaderboard dessa run por padrão.
- Reidratar o configurador a partir do snapshot persistido e mantê-lo congelado enquanto o sweep recuperado não for terminal.
- Manter sweeps terminais no histórico e manter a seleção histórica separada do bloco de lifecycle ativo.
- Fazer `resume` e a reconciliação do dispatcher recuperarem um wake-up durável quando há combinações pendentes e nenhum orquestrador entregue.
- Tornar loading, erro de recuperação, corrida com terminal e pausa visualmente claros e acessíveis em desktop e mobile.

**Non-Goals**

- Não recalcular preflight, alterar a seleção congelada ou criar uma nova combinação durante a recuperação.
- Não substituir a identidade visual/shell da tela de Combo nem alterar promoção, descarte (#663), Short ou worker PROD (#566).
- Não persistir posição de scroll, foco ou filtros como requisito de negócio; o retorno ao processo significa recuperar o sweep, snapshot, progresso e leaderboard, com filtros iniciando no padrão.
- Não fazer o navegador publicar diretamente em Celery nem usar `localStorage` como banco de estado.

## Impeccable Brief

- **Job/audiência:** administrador executa uma varredura swing longa e retorna à tela depois de um reload; modo `Operate`.
- **Problema:** o painel desaparece e a tela parece editável mesmo quando existe trabalho no servidor; `resume` pode deixar sete combinações pending sem worker acordado.
- **Resultado:** ao voltar, o administrador vê imediatamente o sweep real, a fase atual e uma ação segura para continuar; o rascunho não pode iniciar uma segunda run por engano.
- **Direção:** extensão da superfície existente de Combo, densa e sóbria; canvas escuro, hairlines, superfícies planas, Inter/IBM Plex Sans e amarelo apenas para CTA/foco. O delta é um estado de reconexão e recuperação no painel já existente, sem layout paralelo.
- **Escopo:** desktop `1440×1000` e mobile `390×844`; estados recovered-running, recovered-paused, restoring, no-active, terminal-race e recovery-error.
- **Restrições:** admin-only, sem promessa financeira, targets de interação ≥44 px, foco visível, live region sem ruído e nenhuma edição de `DESIGN.md`.

## Decisions

### D1. A recuperação será server-first e terá um endpoint explícito

Adicionar `GET /api/combos/discovery/sweeps/active`, protegido por `get_current_admin`, que retorna `{"sweeps": [<SweepDetail>...]}` contendo todos os sweeps não terminais do ator autenticado, ordenados por `created_at DESC, sweep_id DESC`. A lista vazia (`{"sweeps": []}`) é a resposta para nenhum ativo; não há `204` nem `null`. O endpoint não aceita `actor` no corpo ou query e não consulta runs de outro principal.

`SweepDetail` é o contrato `{sweep_id, state, total, succeeded, failed, skipped, processed, terminal_reason, terminal_code, draft_key, snapshot, started_at, completed_at, created_at, updated_at}`. `snapshot` é o snapshot imutável completo já usado pelo preflight (`axes`, `raw_total`, `exclusions`, `valid_total`, `limits`, `expires_at`, `snapshot_token`, `snapshot_hash`, `period_type`); `draft_key` é a chave UUID de idempotência gerada no cliente e ecoada pelo servidor, não um segredo e não reemitida no reload. O endpoint ativo já retorna detalhes completos, portanto a UI não precisa fazer uma segunda inferência por `history`.

O frontend escolhe o primeiro como `activeSweep` visual, mas mantém os demais no histórico para que nenhuma execução seja escondida. O endpoint explícito evita que o frontend tenha de inferir “ativo” a partir de uma lista histórica e torna a regra de seleção verificável no backend. `GET /sweeps/{sweep_id}`, o leaderboard e os três comandos de lifecycle devem filtrar pelo ator autenticado e responder `404` para recurso de outro ator, sem vazar sua existência.

O endpoint de histórico usa a mesma cláusula de ownership e a ordenação `created_at DESC, sweep_id DESC`; não existe merge client-side entre atores nem desempate dependente da ordem de chegada. O retorno de active/history contém `SweepDetail` completo, evitando uma janela em que o card mostra um ID sem snapshot/counters.

**Alternativas consideradas**

- Impor no PostgreSQL um único sweep não terminal por ator: simplifica a tela, mas quebra execuções legítimas existentes e exige migração de dados; rejeitado para este card.
- Usar apenas `history` e escolher o primeiro item no React: menor alteração, mas duplica a regra de ativo, cria uma janela de corrida e não fornece um contrato claro para a recuperação.
- Guardar o sweep inteiro no navegador: falha quando outra aba/processo avança a run e pode exibir contadores falsos; rejeitado.

### D2. O carregamento inicial terá uma fase de recuperação bloqueante

Na montagem da página, `loadActiveSweep` e `loadHistory` rodam em paralelo. Enquanto a recuperação está `loading`, o configurador mostra um estado curto “Verificando varredura ativa…” e o CTA de início fica desabilitado; o preflight automático não executa. Isso impede que um reload inicie outra run antes de a resposta do servidor chegar. O estado `viewSelectionOrigin` distingue `auto` de `user`.

Se existir sweep não terminal:

1. `activeSweep` recebe o primeiro payload detalhado da lista.
2. `viewSweep` passa a apontar para ele somente quando `viewSelectionOrigin=auto`; uma seleção histórica feita pelo usuário nunca é substituída pelo polling.
3. O snapshot persistido hidrata `preflight`, `selectedTemplates`, `selectedSymbols`, `timeframes`, `directions`, `period` e `committedSelection`; `draftFrozen=true`.
4. O leaderboard é carregado com a métrica padrão Calmar, sem filtros e na página 1.
5. O painel informa `Reconectado ao sweep ativo` em uma live region curta e o polling de 2s continua enquanto o estado não for terminal.

Se não houver ativo, a tela libera o rascunho normal e conserva o comportamento atual de selecionar a run histórica mais recente para o leaderboard. A corrida terminal não depende de um segundo GET para “descobrir” o ativo: `GET .../sweeps/active` já omite terminais. Se um `GET /{id}` paralelo, um poll ou uma resposta atrasada mostrar estado terminal para o sweep que a UI tentava restaurar, esse sweep **não** é hidratado como `activeSweep`; entra no histórico no mesmo `sweep_id` e o leaderboard dessa run é exibido.

**Alternativas consideradas**

- Renderizar o formulário editável imediatamente e corrigir depois: permite start duplicado e contradiz o snapshot; rejeitado.
- Restaurar apenas o painel, sem o rascunho: deixa a seleção visualmente editável e não cumpre o “voltar onde eu estava”; rejeitado.

### D3. O snapshot persistido é a fonte da reidratação do rascunho

O `snapshot` do sweep já contém `axes`, `start_date`, `end_date`, `period_type`, `valid_total`, `exclusions`, hash e token. O frontend não reconstrói total nem chama preflight para um sweep ativo. A seleção reidratada é manual, com os IDs presentes no snapshot; o catálogo atual apenas resolve labels e descrições quando disponível.

O payload detalhado expõe `draft_key`, eco da `idempotency_key` gerada no cliente e confirmada pelo servidor, como identificador não secreto de retry. O cliente vincula essa chave ao `sweep_id` recuperado; não usa uma chave de `sessionStorage` sem confirmação do servidor e o servidor não reemite uma chave nova no reload. A chave continua disponível para repetir com segurança uma criação cuja resposta tenha sido perdida. Enquanto o rascunho recuperado permanece congelado, o CTA de start fica desabilitado. **Novo rascunho** (ação explícita) gera uma chave nova, descongela o configurador e habilita o start para uma segunda run; o painel do sweep anterior continua visível. Reload, retry e preflight automático nunca disparam essa permissão.

Se o catálogo auxiliar falhar, o snapshot ainda é exibido por seus IDs e a recuperação não é convertida em um novo preflight. Se o snapshot estiver ausente ou inválido, a tela mostra erro de recuperação e mantém o CTA de start bloqueado até uma nova tentativa.

### D4. O ativo e o histórico continuam sendo seleções diferentes

`activeSweep` controla exclusivamente lifecycle, congelamento, pausa/retomada/cancelamento e progresso. `viewSweep` controla o leaderboard. Ao retornar de reload, o ativo é o primeiro item de `GET .../active` (`created_at DESC, sweep_id DESC`) e também a seleção inicial do leaderboard. Selecionar uma run **terminal** no histórico não remove nem altera o painel de lifecycle. Selecionar outra run **não terminal** no histórico promove essa run a `activeSweep` visual (pause/resume/cancel passam a apontar para ela); as demais continuam na lista. Um reload volta a promover o mais recente do servidor. O texto da seção explicita quando o leaderboard está “separado do sweep em foco”.

Quando o sweep ativo termina, o polling para, o detalhe terminal permanece visível no bloco para anunciar a conclusão nesta sessão, e o histórico é atualizado. Em um novo reload, não haverá ativo não terminal; o histórico seleciona o mesmo `sweep_id` agora terminal (não uma run anterior diferente) e o leaderboard dessa run permanece consultável.

### D5. Wake-up é uma invariável durável, não uma responsabilidade do navegador

Criar no serviço um caminho idempotente de `ensure_sweep_wakeup`/`rotate_sweep_wakeup`, protegido por lock da linha `DiscoverySweep`. A estratégia escolhida é criar uma nova geração monotônica após um intent `acked`; intents antigos não são reabertos, preservando sua auditoria:

- só atua para sweep `running` com combinação `pending` reclamável;
- se existe intent `delivered` para o sweep, não cria outro;
- se existe intent `pending`, conserva o intent;
- se o último intent está `acked`, cria a próxima geração com estado `pending`;
- se não existe intent, cria um intent `pending` com geração monotonicamente maior;
- commit do intent precede a publicação; falha do broker mantém o intent `pending`;
- `DiscoveryOutbox` ganha unicidade `(sweep_id, generation)` e chamada repetida sob lock produz no máximo um wake-up reclamável.

`resume` deve executar a garantia como parte do mesmo fluxo de lifecycle: depois de `paused → running`, o wake-up é garantido e despachado. Se o banco já confirmou a transição e o broker estiver indisponível, a resposta mantém `state=running`, `wake_up_state=pending` e `dispatch_status=deferred`; o dispatcher continua responsável pela publicação. O dispatcher periódico também deve reparar sweeps `running` com pendências, sem intent `pending`/`delivered`, para cobrir crash, reload e ACK anterior. Se o start inicial cair depois do commit do sweep `pending`, o dispatcher promove esse sweep a `running` sob o mesmo lock antes de publicar/permitir claim. O orquestrador, ao terminar um lote e encontrar mais pendências, deve inserir a próxima geração `pending` e só então confirmar a entrega atual; não pode depender de `apply_async` isolado.

Pausa continua sendo barreira de início: uma wake-up já entregue pode acordar, mas o worker revalida o estado e não inicia combinação enquanto `paused`. `cancelling` prevalece e nunca é reaberto por reparo automático.

**Alternativas consideradas**

- No `resume`, publicar Celery diretamente sem outbox: perde o trabalho se o broker/publicação falhar; rejeitado.
- Fazer o `GET active` alterar a fila: mistura leitura com mutação e cria efeitos difíceis de repetir; a reparação fica no dispatcher e no comando `resume`.
- Criar um job por combinação: contradiz a topologia existente e aumenta a superfície de duplicação; rejeitado.

### D6. O contrato visual privilegia recuperação explícita e baixa surpresa

Quando há sweep ativo, o bloco de progresso é movido para imediatamente abaixo do banner de recuperação, antes do configurador, para que a pergunta “o que está acontecendo?” seja respondida acima da dobra. O restante da hierarquia e do shell permanece o mesmo; sem sweep ativo, o configurador conserva sua posição normal. O delta visual é:

- durante recuperação: status de verificação inline, sem spinner solto no conteúdo e CTA de start desabilitado;
- recuperado: sublinha `Reconectado ao servidor · snapshot ...`, chip de estado real e contadores do servidor;
- paused: ponto e ação amarelos, copy explicando que pendências aguardam Retomar;
- erro: aviso inline com `Tentar novamente`, sem esconder histórico nem habilitar start inseguro;
- terminal: estado neutro/conclusivo; controles de lifecycle disabled, leaderboard permanece consultável.

No mobile, o painel mantém uma coluna, ações em largura equivalente e o contador permanece junto do heading. Nenhuma mensagem de “recarregue para retomar” fica como caminho primário depois desta mudança.

### D7. Acessibilidade e estados observáveis são parte do design

O estado de recuperação usa `role=status`/`aria-live=polite` apenas para mudanças de estado, não para cada poll. O reload anuncia a recuperação sem roubar foco; o heading do progresso recebe foco após uma transição terminal ou uma recuperação acionada explicitamente por retry. O progresso mantém `role=progressbar`, `aria-valuenow`, `aria-valuemax` e a igualdade dos contadores em texto. A implementação escolhe single-flight com um request em voo por sweep e uma revisão monotônica de resposta; `updated_at` do servidor é o desempate defensivo.

Todos os controles preservam nome de ação (`Retomar`, `Pausar`, `Cancelar`, `Tentar novamente`), foco visível azul, contraste dos estados e target mínimo de 44 px. O erro de recuperação não usa toast como única evidência.

## Fluxo de dados

```text
mount /combo/discovery
  ├─ GET /sweeps/active ──┐
  └─ GET /sweeps/history ─┤
                           ├─ active não terminal → detalhe/snapshot → freeze + leaderboard ativo
                           ├─ active ausente       → rascunho editável + histórico mais recente
                           └─ corrida terminal     → histórico + leaderboard terminal

POST /sweeps/{id}/resume
  └─ lock sweep → paused→running → ensure wake-up pending → commit → dispatcher/Celery

dispatcher poll
  └─ reparar running + pending sem intent → outbox pending → orchestrator
```

## Contratos de API e dados

- `GET /api/combos/discovery/sweeps/active`: `200 {"sweeps": [<SweepDetail>...] }`; lista vazia `{"sweeps": []}`; escopo pelo principal autenticado; ordenação `created_at DESC, sweep_id DESC`.
- `GET /api/combos/discovery/sweeps/history`: retorna somente sweeps do ator autenticado e ordena por `created_at DESC, sweep_id DESC`; a UI deduplica por `sweep_id` ao combinar active/history.
- `GET /api/combos/discovery/sweeps/{id}`: inclui `draft_key` ecoada (cliente) e `updated_at`; rejeita sweep de outro ator com `404`.
- `POST /api/combos/discovery/sweeps/{id}/resume`: responde `200` depois que a transição e o intent durável estão commitados; se a publicação no broker falhar, o corpo ainda é `200` com `state=running`, `wake_up_state=pending`, `dispatch_status=deferred`.
- Outbox: unicidade por `(sweep_id, generation)`; no máximo uma intent `pending` ou `delivered` por sweep em cada ponto de wake-up; um sweep **`running`** com combinações reclamáveis nunca permanece apenas com intent `acked`. `paused` + pending + `acked` é válido até o `resume`.

## Riscos / Trade-offs

| Risco | Mitigação |
| --- | --- |
| Duas abas restauram o mesmo sweep | Seleção por ator no servidor, lock da linha pai e payload idempotente; a segunda aba apenas observa. |
| Reload ocorre no instante da transição terminal | Reconsultar detalhe; tratar terminal como histórico, nunca como ativo falso. |
| Catálogo mudou desde o snapshot | Labels são auxiliares; IDs/snapshot persistidos permanecem a fonte; não executar preflight automático. |
| Dispatcher cria wake-up enquanto outro está sendo ACKado | Lock de `DiscoverySweep` + rotação transacional do intent; teste de corrida. |
| Backend ativo responde erro | Bloquear novo start durante `loading/error`, oferecer retry e manter histórico como leitura auxiliar. |
| Mensagens de polling poluem leitor de tela | `aria-live` somente em recuperação/terminal; contadores atualizados no próprio progressbar. |
| Múltiplos sweeps não terminais ficam fora da tela | Endpoint retorna todos; o mais recente ocupa o bloco ativo e os demais seguem no histórico como runs não terminais. |
| Comandos concorrentes violam cancelamento | Lock da linha pai, transição monotônica e comandos do frontend single-flight. |
| Resposta antiga do polling reverte terminal | Request single-flight/revisão monotônica descarta payload atrasado. |

## Migration Plan

1. Implementar o endpoint de ativo e os testes de autorização/ordenação usando PostgreSQL de teste.
2. Implementar wake-up idempotente, rotação de outbox e reparo periódico; cobrir resume, ACK anterior, crash e pausa.
3. Implementar a hidratação do frontend sem alterar o contrato de start/preflight.
4. Adicionar protótipo versionado e testes Playwright para recovered-running, paused, loading, error, terminal e mobile.
5. Validar em DEV; observar uma run pequena, recarregar, pausar, retomar e confirmar que `processed` avança até terminal.

Rollback: desativar a recuperação visual e o reparo de wake-up preservando as tabelas existentes; não apagar sweeps, combinações, resultados ou intents. A migração não exige alteração destrutiva de dados.

## Open Questions

Nenhuma bloqueante para o design. A escolha é criar uma nova geração monotônica após `acked`, com unicidade `(sweep_id, generation)`; essa decisão deve ser coberta por teste de corrida, crash e redelivery.

## Prototype

- **URL:** `http://127.0.0.1:4181/prototypes/card-664-discovery-restore-reload/` no gate local; publicação DEV `https://dev.criptofarol.com.br/prototypes/card-664-discovery-restore-reload/`.
- **Caminho versionado:** `frontend/public/prototypes/card-664-discovery-restore-reload/index.html`.
- **Base:** protótipo card-469 e shell autenticado de Combo (`AppNav` + `/combo/discovery`); somente o delta de restauração pós-reload foi introduzido.
- **Viewports:** desktop `1440×1000` e mobile `390×844`.
- **Versão:** rodada final do design; digest SHA-256 `8a7e4ab2ec652cd0a55595816fcffd07d27621f4f662c30a8aab4d99c1e2e211`.
- **Estados representados:** recovered-running, paused, deferred, loading, pending, cancelling, erro, no-active, failed, partial_failure, terminal, corrida terminal e histórico com segundo ativo.
- **Interações:** `Simular F5`, `Pausar`/`Retomar`, `Tentar novamente`, histórico (incluindo promover lifecycle do segundo ativo), cancelamento em pending, `Novo rascunho` (segunda run explícita) e start bloqueado no reload.

## Impeccable Critique

### Assessments independentes

- **Assessment A, rodada inicial:** `BLOCKED` (shell/ordem, loading, histórico inerte, contrato aberto).
- **Assessment B, rodada inicial:** `BLOCKED` (corrida, múltiplos ativos, polling obsoleto).
- **Recrítica A (pós-correção de P1):** `PASS`. Zero P0/P1 de artefato.
- **Recrítica B (pós-correção de P1, isolada):** primeiro `BLOCKED` (lifecycle só no mais recente); após D4 + `applyLifecycleFocus`, `PASS`. Zero P0/P1 de artefato.
- **Correções direcionadas desta rodada:** mesmo `sweep_id` no reload terminal; `draft_key` cliente+eco; cancel pending; resume `deferred`; targets 44px; GET active como lista; `acked` só em `running`; corrida via poll/`GET /{id}`; Novo rascunho habilita segunda run; seleção não-terminal promove lifecycle.

| Finding | Disposição |
| --- | --- |
| Protótipo separado da aplicação real | Aceito como contrato visual estático versionado; shell/tokens alinhados; delta = recuperação. |
| Implementação backend/frontend ainda não aplicada | Aceito: `Status=Design` bloqueia código de produto; `tasks.md` cobre o apply. |
| Toolbar de fixture inerte no produto | Aceito: affordance exclusiva do protótipo, rotulada `Protótipo`. |
| Catálogo integral não materializado | Aceito: IDs do snapshot; produção pagina. |

### Crítica final do autor

- Produto/UX: o retorno responde primeiro “qual sweep está vivo?”, bloqueia start no reload e permite segunda run só com Novo rascunho.
- Contrato: lista `sweeps`, `draft_key` ecoada, ownership 404, wake-up monotônico, `deferred`, foco de lifecycle em não-terminais extras.
- Acessibilidade: recovery anunciada uma vez; retry/terminal restauram foco; controles de produto ≥44 px no gate.
- P0/P1 de design aberto: **zero**.

## Impeccable Audit

| Dimensão | Resultado | Evidência |
| --- | ---: | --- |
| Acessibilidade | 4/4 | Playwright: recovery/error/retry, foco no heading, cancel pending, 0 `button`/`select` visíveis < 44 px. |
| Performance | 4/4 | Protótipo autocontido, sem catálogo integral. |
| Responsividade | 4/4 | `1440×1000` e `390×844`; `scrollWidth == innerWidth` no mobile. |
| Theming | 4/4 | Shell/tokens; detector `[]`; wake-up usa info, não verde de PnL. |
| Integridade | 4/4 | Playwright `2 passed`; console/page errors `0`. |
| **Total** | **20/20** | Detector `[]`; P0/P1 de artefato zerados nas recríticas A e B. |

### Detector final

- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-664-discovery-restore-reload/index.html`
- Resultado: `[]`.

## Impeccable Trace

1. **Context:** `PRODUCT.md` / `DESIGN.md` da Discovery; `DESIGN.md` não reescrito.
2. **Shape:** Operate; server-first; ativo/histórico; snapshot congelado no reload; progresso acima do configurador com ativo.
3. **Prototype:** `frontend/public/prototypes/card-664-discovery-restore-reload/index.html`.
4. **Critique:** A/B iniciais BLOCKED; recrítica A PASS; recrítica B PASS após foco de lifecycle.
5. **Audit:** detector `[]`.
6. **Targeted fixes:** P1 de reload terminal, 44px, pending cancel, deferred, lista active, acked/`running`, corrida, segunda run, promover não-terminal.
7. **Polish:** digest `8a7e4ab2ec652cd0a55595816fcffd07d27621f4f662c30a8aab4d99c1e2e211`.
8. **Browser gate:** Playwright `1.58.2`, `http://127.0.0.1:4181/prototypes/card-664-discovery-restore-reload/`, screenshots `/tmp/card-664-discovery-design-desktop-final-v3.png` e `/tmp/card-664-discovery-design-mobile-final-v3.png`.

## Prototype Validation

- URL servida: `http://127.0.0.1:4181/prototypes/card-664-discovery-restore-reload/`.
- Viewports: desktop `1440×1000` e mobile `390×844`.
- Fluxos: running 21/28; pause/resume com processed persistido 22/28; loading/erro/retry; pending cancel; deferred; Novo rascunho (chave nova + start); histórico previous/other-active (lifecycle PAUSED em `#a8c12e4b`); completed reload no mesmo `sweep_id`; fixture `race`.
- Assertions: `2 passed` em `frontend/tests/e2e/card-664-prototype.spec.ts`.
- Resultado visual: shell DEV/conta/Configurações; progresso acima do rascunho; mobile sem overflow.

## Design Critique

Fontes: `proposal.md`, `design.md`, `specs/discovery-sweep/spec.md`, `tasks.md`, protótipo, Playwright, `DiscoveryPage.tsx`, `AppNav.tsx`, `DESIGN.md`.

Critics A e B (`inherit`, isolados) em PASS no artefato. Sem autorização para `backend/` ou `frontend/src/` antes de `Pronto para Dev`.

**Design Agent verdict: PASS** — handoff somente `Design` → `Aprovação de Design`; aprovação humana continua com Alan.
