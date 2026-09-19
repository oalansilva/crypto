UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 967: Descoberta reconstitui sozinha a varredura ativa

## Context

Card [#967](https://github.com/oalansilva/crypto/issues/967). Briefing = issue grelhado. DoD completo (`## Problema`, `## História`, `## Entra` / `## Não entra`). Q1=A gravada. Sem reentrevista. AskUser / grill-card recusados: as Qs já estão no body.

O operador autenticado em `/combo/discovery` (PROD 2026-09-17, badge PROD, `https://criptofarol.com.br/combo/discovery?_sm_nck=1`) vê banner vermelho «Não foi possível verificar a varredura ativa» / «O sweep continua protegido no servidor.», Montar activo com rascunho vazio (0 templates, 0 símbolos), Preflight «0 combinações», Acompanhar em «Acompanhando #—». A varredura **continua no servidor**. Sair / deslogar / logar reconstitui o Acompanhar da mesma run.

Hoje `restoreSession` pede `GET /combos/discovery/sweeps/active` na montagem. Se o GET falha (rede/5xx/timeout) ou `hydrateFromSweep` recusa o payload, `recoveryStatus=error` mostra o banner vermelho e deixa o Montar/rascunho; `activeSweep` fica vazio, daí «#—». O sweep não é cancelado. «Tentar novamente» chama o mesmo `restoreSession`. Logout/login remonta a página e a segunda pergunta reconstitui.

Isto não é F5/#664 (o restore já existe; o furo é a falha com sessão ainda autenticada). Não é o ecrã «Sessão expirada». Não é #954 (Acompanhar stale depois de a run fechar).

**Audience:** operador da Descoberta em produção, sessão autenticada, com varredura viva no servidor.
**Outcome:** a tela reconstitui sozinha o Acompanhar dessa run (número verdadeiro e progresso), sem clique e sem deslogar.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance; sem reescrever DESIGN.md / PRODUCT.md. Shape inferido do issue (Qs fechadas); probe AskUser omitido por briefing grelhado + MUST NOT do spawn.
**Scope:** modo Acompanhar reconstituído + residual do retry. Montar só landmarks + bloqueio de Iniciar outra. Sem ecrã novo de modos.

Regiões clonadas (só estas): shell AppNav autenticado + heading + 3 modos + Montar (Preflight / Rascunho de varredura / «Descoberta de estratégias swing») + chrome Acompanhar + grelha de parciais + header/grelha Decidir (Histórico de outra run, sem delta deste card). Delta só no caminho feliz: Acompanhar visível com `#c91f3a07…` e progresso `12 de 24`; banner vermelho ausente; Iniciar outra bloqueado.

## Goals / Non-Goals

**Goals:**

- Com varredura em curso no servidor e sessão autenticada, a tela reconstitui **sozinha** o Acompanhar dessa run: número verdadeiro (não «#—») e progresso.
- Sem banner vermelho de falha de verificação no caminho feliz. Sem clique. Sem logout.
- «Tentar novamente» só visível se a reconstituição automática falhar de novo.
- Essa falha de tela não cancela nem duplica a run. Iniciar outra continua bloqueado até o operador ver o Acompanhar.

**Non-Goals:**

- Restaurar após F5 (#664, já Pronto).
- Clique em «Tentar novamente» como caminho feliz (Q1=A).
- Acompanhar que mente «em curso» depois de a run já ter fechado (#954).
- Defaults do rascunho (#952).
- Ecrã «Sessão expirada».
- Acelerar worker, Deep/WF, promoção/favorito.
- Combo `/combo/select`, Favoritos, Monitor.
- Inventar ecrã novo de modos além de Montar / Acompanhar / Decidir.

## Decisions

### 1. A reconstituição automática é o caminho feliz (Q1=A)

Quando a verificação do sweep activo falharia com a sessão **ainda autenticada** (não 401 «Sessão expirada», não 403), a UI SHALL repetir sozinha essa verificação até hidratar o Acompanhar da run viva: `sweep_id` verdadeiro no separador, chip EM CURSO, contador `N de M` e barra de progresso. O operador não clica nem desloga.

Enquanto a automática corre, o estado visível MAY permanecer o loading já existente («Verificando varredura ativa…») — **não** o banner vermelho. O vermelho + «Tentar novamente» só depois de a automática esgotar.

Rejeitado: deixar o banner vermelho no caminho feliz. Rejeitado: exigir clique em «Tentar novamente» (Q1≠B). Rejeitado: logout/login como conserto. Rejeitado: F5 como conserto (#664 fora).

### 2. Sweep conhecido hidrata o Acompanhar mesmo se o snapshot do rascunho atrasar

Se o GET activo devolver um sweep não-terminal, a UI SHALL ligar `activeSweep`, abrir o modo Acompanhar e mostrar progresso a partir dos contadores do payload (`processed`/`total`/estado). Recusar `hydrateFromSweep` (snapshot/axes em falta) SHALL NOT estacionar em Montar vazio + «#—» quando o `sweep_id` já é conhecido. O rascunho congelado pode hidratar no ciclo seguinte.

Rejeitado: `recoveryStatus=error` só porque o snapshot não veio no mesmo tick. Rejeitado: cancelar ou criar outra run para «desbloquear» a tela.

### 3. «Tentar novamente» é residual; Iniciar outra continua bloqueado

O botão «Tentar novamente» só entra se a reconstituição automática falhar de novo (teto de tentativas = P3 Apply). Não redesenha modos. Não é o caminho feliz.

Enquanto a run viva não estiver no Acompanhar, Iniciar outra SHALL permanecer bloqueado. A falha de tela SHALL NOT cancelar nem duplicar o sweep no servidor. O desbloqueio de iniciar outra é ver o Acompanhar (e só então cancelar / montar de novo, se quiser).

401 continua no ecrã «Sessão expirada» (fora). 403 continua no painel de permissão (fora).

### 4. Endpoint e worker não mudam

O GET `/combos/discovery/sweeps/active` já existe (#664). Sem endpoint novo. Sem acelerar worker. Sem outbox/websocket como produto.

## Risks / Trade-offs

- [Risco] Retry agressivo martela o GET activo → Mitigação: backoff + teto (P3 Apply); loading já bloqueia Iniciar.
- [Risco] 401 intermitente classificado como retry autenticado → Mitigação: 401 continua «Sessão expirada»; só retry com sessão autenticada.
- [Risco] Operador achar que o vermelho + retry é o conserto → Mitigação: proto canónico = caminho feliz; residual só em `retry.html`.
- [Risco] Snapshot ausente deixa o Montar vazio se o operador mudar de aba cedo → Mitigação: Acompanhar já mostra número e progresso; snapshot hidrata no ciclo seguinte (decisão 2).

## Migration Plan

Sem schema. Deploy = frontend da Descoberta. Rollback = reverter o retry automático de `restoreSession`; o servidor já protegia a run. Sem job de dados.

## Open Questions

Nenhuma. Q1=A gravada. Mecanismo (repetir a verificação sozinha até hidratar o Acompanhar; retry clique só no residual) fechado neste design.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/index.html` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Caminho feliz: sessão autenticada + sweep vivo no servidor → Acompanhar visível com número verdadeiro (não «#—») e progresso; banner «Não foi possível verificar a varredura ativa» ausente; sem clique; sem logout.
- «Tentar novamente» só se a reconstituição automática falhar de novo.
- A falha de tela não cancela nem duplica a run. Iniciar outra continua bloqueado até o operador ver o Acompanhar.
- Isto não é o ecrã «Sessão expirada» nem o restore só por F5 (#664). Não é #954 nem #952.

**P3 aceito (Apply):** intervalo/backoff e teto das tentativas automáticas; se o GET falhou ou só o `hydrateFromSweep`; se o loading «Verificando…» permanece entre tentativas; testes do retry automático (hidrata Acompanhar sem clique) e do residual (banner + retry só após teto). Sem endpoint novo. Sem websocket.

## Recorte

- **Audience:** operador autenticado da Descoberta com varredura viva no servidor.
- **Outcome:** Acompanhar reconstitui-se sozinho; logout deixa de ser o conserto.
- **Direction:** clone da rota viva `/combo/discovery` + delta do Acompanhar reconstituído; Operate; sem new-work.
- **Scope:** reconstituição automática do Acompanhar + residual do retry. Montar só landmark + bloqueio de Iniciar.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/
- Path: `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/index.html`
- Digest: `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` (42186 bytes).
- Base: clone da página viva HEAD `/combo/discovery`. Arranque a partir do proto irmão `card-954-discovery-acompanhar-stale` (chrome + grelha HEAD); landmarks e modos alinhados ao vivo. Sem painel ANTES/DEPOIS no index. T5 mede só este `index.html`.
- Landmarks (catálogo HEAD, substring): «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Clone vs delta: COPIED = shell AppNav, heading, 3 modos, selector de Histórico, rascunho, Preflight, chrome Acompanhar, casca das duas grelhas. DELTA = Acompanhar reconstituído (`#c91f3a07b6e24d8a9f51c2e8470b3d16`, `12 de 24`, EM CURSO); banner vermelho ausente; Iniciar outra bloqueado. Representante da reconstituição PROD 2026-09-17 (o print não capturou o `sweep_id` porque a tela mostrou o placeholder vazio).
- Residual (não canónico): `retry.html` na mesma pasta — banner vermelho + «Tentar novamente» + Montar vazio + «Acompanhando #—», só depois de a automática esgotar. Extra URL da mesma rota, não outra chave de catálogo.
- Estados navegáveis no index: default Acompanhar reconstituído; Montar (rascunho congelado + Iniciar bloqueado, landmarks); Decidir = Histórico de outra run (sem delta).

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/
- Path: `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/index.html`
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://, não curl).
- Ações: default Acompanhar reconstituído → Montar (landmarks + Iniciar bloqueado) → Acompanhar (número + progresso).
- Asserts (mesmo critério nos dois viewports): landmarks «Descoberta de estratégias swing» / Preflight / Rascunho de varredura; Acompanhar visível com número verdadeiro (não «#—») e progresso; banner «Não foi possível verificar a varredura ativa» ausente; 0 console/pageerror.
- Pares `COPIED:start`/`COPIED:end`: 11/11; soma UTF-8 das regiões copiadas 14367 (> 0). T5 mede só este index.html.
- Gate de browser do autor (Playwright Chromium, HTTPS, xvfb): desktop 1440×900 e mobile 390×844 — landmarks presentes; Acompanhar `#c91f3a07` visível; progresso `12 de 24`; banner «Não foi possível verificar a varredura ativa» ausente; 0 console/pageerror. Disco == HTTPS (`9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997`, 42186 bytes).
- Sem emitir PASS oficial de T5 (pai após A/B).

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Sem P0/P1 novos de produto. Sem segundo rework. P3 aceitos no Apply.

**Design Agent verdict: PASS**

- **P0:** nenhum
- **P1:** nenhum
- **P3 (aceites Apply):** Montar condensado vs vivo; grelha mock / Ação a clipar no desktop; overflow 390 no Acompanhar; banner info «Varredura ativa recuperada do servidor» (clone `reconnected`, não o vermelho); histórico aberto por omissão; `DELTA:end` em falta no 2.º bloco; intervalo/backoff/`hydrateFromSweep`/testes. Residual: `retry.html` irmão nunca canónico.

Q1=A não reaberta. Contrato visível intacto: reconstituição sozinha do Acompanhar (número verdadeiro e progresso); banner vermelho ausente no caminho feliz; clique só se a automática falhar de novo.

Snapshots: `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa-assessment-A.md` · `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa-assessment-B.md` · T7 `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa.md`

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
