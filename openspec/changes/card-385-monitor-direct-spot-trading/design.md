## Context

O card #385 transforma o Monitor de uma superfície apenas analítica em um ponto de execução Binance Spot iniciado pelo usuário. O produto já possui credenciais Binance por usuário, leitura de saldos e um serviço assinado escopado para stop-limit protetivo; não possui, porém, um contrato genérico para ordens diretas, idempotência durável nem uma experiência de confirmação para compra/venda imediata.

Decisões confirmadas por Alan no chat em 2026-08-06:

- compra: o usuário informa quantos USDT deseja usar;
- venda: sempre 100% do saldo `free` do ativo;
- execução direta no Monitor, sem abrir a Binance.

`UI impact: affected` — a tela existente do Monitor recebe uma nova ação transacional de alto risco e seus estados. A base visual obrigatória é a rota `/monitor`, o shell autenticado, a tabela/cards atuais e os tokens de `DESIGN.md`; o delta é apenas o acionador `Operar` e a superfície protegida de execução.

## Goals / Non-Goals

**Goals:**

- executar `BUY MARKET` por `quoteOrderQty` em USDT e `SELL MARKET` do máximo válido de 100% do saldo `free`;
- confirmar a intenção com contexto suficiente para reduzir erro sem transformar o Monitor em terminal de trading;
- validar regras atuais da Binance e usar somente credenciais do usuário autenticado;
- impedir duplicidade econômica e reconciliar timeout/resultado desconhecido;
- manter auditoria segura em PostgreSQL e atualizar saldos após um resultado terminal;
- preservar acessibilidade, responsividade e fidelidade ao Monitor atual.

**Non-Goals:**

- Futures, margem, short, alavancagem, saque, transferência ou outra exchange;
- ordem limit, stop, OCO ou automação por sinal;
- editar a lógica das estratégias ou recomendar a operação;
- criar histórico completo de ordens como nova área do produto;
- alterar shell, navegação, tabela, gráfico ou identidade visual fora do delta necessário.

## Decisions

### 1. Um acionador `Operar` preserva a densidade do Monitor

Na tabela desktop e no card mobile, o delta inicial será um botão textual `Operar` junto às ações atuais. Ele abre uma superfície transacional protegida com duas escolhas explícitas: `Comprar` e `Vender 100%`.

O desktop usa painel lateral sobreposto; no mobile, a mesma superfície ocupa a largura e ancora as ações na região inferior. O painel mantém símbolo, preço indicativo e saldo visíveis durante configuração e confirmação.

**Alternativas consideradas:** quatro botões diretamente na linha (`Comprar`, `Vender`, `Abrir Gráfico`, `Ver Trades`) aumentariam carga e risco de toque; esconder o fluxo apenas no gráfico contrariaria o pedido de operar na tela do Monitor.

### 2. A superfície transacional usa modo claro dentro do Monitor escuro

`DESIGN.md` define superfícies transacionais em light mode. O painel usa canvas claro, ink, hairlines e CTA amarelo; verde e vermelho ficam restritos à semântica de compra/venda. O shell, tabela e cards permanecem no tema atual.

**Alternativa considerada:** drawer inteiramente escuro teria maior continuidade visual, porém reduziria a separação entre leitura analítica e envio de ordem real.

### 3. Compra e venda são ordens MARKET com parâmetros econômicos diferentes

- Compra: `POST /api/monitor/spot-market-orders` com `side=BUY`, `quote_amount_usdt` e `idempotency_key`; o serviço envia `quoteOrderQty`.
- Venda: mesmo endpoint com `side=SELL` e sem quantidade fornecida pelo cliente; o backend consulta o saldo atual e calcula a maior `quantity` válida que não exceda 100% do `free`.
- `newOrderRespType=FULL` é solicitado para obter fills suficientes ao resumo imediato quando disponível.

**Alternativas consideradas:** aceitar quantidade base na compra não atende a decisão de Alan; aceitar quantidade na venda permitiria divergir da regra de 100%.

### 4. Preview vem do servidor e a confirmação referencia uma versão curta

Um `POST /api/monitor/spot-market-orders/preview` valida símbolo, status, filtros, preço indicativo e saldos atuais sem criar ordem. Ele retorna um `preview_token` curto, com expiração, lado, valores calculados e avisos. A confirmação envia esse token e a chave idempotente; o backend revalida saldo/filtros imediatamente antes do envio e rejeita mudança material insegura.

**Alternativas consideradas:** calcular preview só no frontend duplicaria regras e criaria confiança em estado obsoleto; enviar a ordem sem preview impediria uma confirmação auditável.

### 5. Idempotência e auditoria usam PostgreSQL

Uma tabela `monitor_spot_order_requests` registra `user_id`, chave idempotente, `client_order_id`, símbolo, lado, valor solicitado, quantidade calculada, estado, resumo sanitizado, timestamps e referência da ordem Binance. Há unicidade por `(user_id, idempotency_key)` e por `client_order_id`.

O `client_order_id` usa prefixo `cftrade_` mais hashes curtos não reversíveis. Repetições devolvem o registro existente. Em timeout, 5xx ou falha de transporte com resultado desconhecido, o registro entra em `reconciling` e o serviço consulta `GET /api/v3/order` por `origClientOrderId` antes de permitir nova tentativa.

**Alternativa considerada:** somente confiar na rejeição de `newClientOrderId` da Binance não oferece histórico local, não cobre respostas terminais já preenchidas e dificulta reabrir o estado após refresh.

### 6. O adaptador Binance reutiliza assinatura e normaliza filtros/erros

O serviço de stop existente fornece padrões de HMAC, timestamp, `recvWindow`, request HTTP e sanitização, mas ordens diretas ficam em um módulo próprio para não misturar proteção pendente com execução imediata. O novo adaptador consulta `exchangeInfo`, conta/saldos e ordem por client id; suporta `MARKET_LOT_SIZE`, fallback defensivo a `LOT_SIZE`, `MIN_NOTIONAL` e `NOTIONAL` com aplicação a market conforme os flags da exchange.

Erros externos são mapeados para códigos internos estáveis e copy segura; chaves, secrets, assinaturas, URLs assinadas e payloads crus nunca saem do backend.

### 7. Estado do frontend é uma máquina pequena e pessimista

Estados: `idle -> previewing -> review -> submitting -> reconciling -> filled|partial|rejected`. Enquanto `submitting` ou `reconciling`, o painel bloqueia nova confirmação do mesmo pedido. Fechar/reabrir consulta o estado pela chave idempotente quando houver pedido não terminal. Resultado terminal dispara refresh dos saldos usados pelo Monitor.

**Alternativa considerada:** atualização otimista foi descartada porque um timeout pode representar ordem executada e nunca deve aparecer como falha simples.

## Risks / Trade-offs

- [Preço de mercado varia entre preview e execução] → copy explícita, preço apenas indicativo e revalidação de saldo/filtros; nunca prometer preço final.
- [Timeout pode esconder execução real] → estado `reconciling`, consulta por `origClientOrderId` e bloqueio de resubmissão.
- [Venda de 100% pode deixar dust] → arredondar apenas para baixo, exibir quantidade efetiva e aviso de possível residual não negociável.
- [Saldo muda em outra aba/exchange] → refresh no preview e imediatamente antes do POST assinado; retornar conflito sanitizado.
- [Permissão TRADE aumenta impacto de credencial comprometida] → credencial por usuário, IP whitelist recomendada, proibição explícita de withdraw e nenhuma exposição de secret.
- [Adicionar PostgreSQL aumenta o escopo] → tabela pequena e append/update controlado, migration Alembic reversível e sem armazenamento de payload sensível.
- [O botão Operar pode ser confundido com recomendação] → manter disclaimer educacional e separar ação de execução do badge/sinal da estratégia.

## Migration Plan

1. Adicionar model e migration Alembic de `monitor_spot_order_requests` com índices/uniqueness.
2. Publicar backend com preview, submit/status e adaptador Binance cobertos por mocks; endpoints permanecem inacessíveis sem autenticação e credencial do usuário.
3. Publicar frontend com acionador e painel atrás do contrato novo; falha do endpoint apenas desabilita operação e preserva o Monitor.
4. Executar testes focados, suíte visual, `openspec validate --all`, review e QA.
5. Integrar em `develop`, executar `./restart` (inclui migration), validar endpoint/URL e manter card em Done técnico para homologação.

Rollback: remover o acionador do frontend e desabilitar as rotas; a tabela pode permanecer sem uso ou ser removida pela downgrade migration quando comprovadamente segura.

## Open Questions

Nenhuma decisão de produto bloqueante permanece. Valores mínimos/máximos e precisões são sempre derivados dos filtros atuais da Binance, não hard-coded.

## Impeccable Brief

- **Job e audiência:** investidor do beta fechado, no Monitor em modo `Operate`, que já decidiu agir e precisa executar sem perder o contexto do ativo.
- **Resultado e prova:** comprar usando um valor explícito em USDT ou vender 100% do saldo livre; antes da ordem, reconhecer par, lado, saldo, valor/quantidade e risco de variação; depois, compreender o resultado.
- **Direção:** preservar integralmente shell/tabela/cards atuais e acrescentar um único acionador `Operar`; abrir painel transacional claro, sequencial e protegido, com uma decisão por etapa.
- **Escopo/antiobjetivos:** sem redesign do Monitor, sem linguagem de urgência, sem automação, sem promessa de preço/lucro e sem esconder que a ordem é real.
- **Estados:** sem credencial, sem permissão, saldo insuficiente, abaixo do mínimo, preview, confirmação, envio, reconciliação, preenchida, parcial e rejeitada.
- **Interação/layout:** painel lateral no desktop e folha de largura total no mobile; foco preso/retornado, Escape/cancelar antes do envio, CTA final inequívoco e indisponível durante estado incerto.
- **Restrições:** React/FastAPI/PostgreSQL, tokens `DESIGN.md`, teclado/touch, 390px e 1440px, copy PT-BR e zero secret/payload técnico na UI.

O brief incorpora as correções explícitas de Alan nesta sessão (compra por USDT e venda integral) e está confirmado por essas decisões diretas.

## Prototype

- URL canônica de revisão: `https://dev.criptofarol.com.br/prototypes/card-385-monitor-direct-spot-trading/`
- Caminho: `frontend/public/prototypes/card-385-monitor-direct-spot-trading/index.html`
- Base: rota `/monitor`, shell autenticado, tabela/cards e modal atuais observados no código e nos baselines Playwright desktop/mobile.
- Escopo: acionador `Operar`, compra por USDT, venda 100%, residual por filtro, vínculo por ativo, confirmação, bloqueio durante submit e estados demonstráveis `no-credentials|reconciling|partial|rejected|filled`, sem chamar API real.
- Versão/digest final do HTML: `cc38a528f4294b3bb5fe7f0ef5642cea9884f905ce5b7a8274211caad52653ad`.

## Impeccable Critique

Os dois assessments iniciais foram executados em isolamento, read-only, sem override de modelo; ambos herdaram por garantia da plataforma o mesmo modelo/versão da sessão principal. Eles avaliaram o digest anterior `c5ffbd6a...d8bd81` e retornaram `BLOCKED`.

- **Assessment A:** bloqueou por risco de ETH abrir BTC, ausência de reconciliação/parcial/rejeição, venda sem residual explícito, padrão de tabs incompleto, token ativo ausente e evidência insuficiente.
- **Assessment B:** confirmou os mesmos riscos e adicionou fechamento durante submit, callback stale, contraste insuficiente no painel claro e falta de vínculo entre screenshots/digest.
- **Correções aplicadas:** fixtures por símbolo; confirmação do par; reconciliação persistida por símbolo e lado; bloqueio de Escape/backdrop/fechar durante submit; proteção contra callback stale; estados navegáveis de preflight/reconciliação/parcial/rejeição; quantidade válida e residual da venda; recovery link para `/profile`; tabs WAI-ARIA, `inert`, foco de heading e retorno; token ativo; texto/CTA com contraste acessível; nova evidência browser no digest final.

Reassessments finais no digest congelado `cc38a528...52653ad`:

- **Assessment A: PASS.** Confirmou reconciliação isolada por símbolo/lado, recovery link no focus trap, foco visível, vínculo do SHA servido e ausência de blocker atual.
- **Assessment B: PASS.** Confirmou detector `[]`, hashes/evidências posteriores ao HTML, URL canônica no mesmo SHA, ciclo de foco do recovery, fluxos desktop/mobile e console `0/0`.

## Impeccable Audit

- Detector determinístico final: `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-385-monitor-direct-spot-trading/index.html` → `[]`.
- Contraste calculado: ink/painel `17.39:1`; ink/CTA amarelo `12.18:1`; body/canvas dark `16.35:1`; muted/canvas dark `4.46:1`; ink/marca de resultado `9.10:1`.
- Acessibilidade básica: labels de formulário presentes; diálogo nomeado e descrito; aplicação em `inert`; foco inicial/preso/retornado; headings focados nas mudanças de etapa; tabs com `aria-controls`, `tabpanel`, roving tabindex e setas/Home/End; submit anunciado e não dispensável; mobile sem overflow horizontal.
- Responsividade: painel lateral a `1440x1000`; bottom sheet `390x844`, largura `390px`, `y=124.47px`, sem overflow.
- Segurança de interação: buy informa USDT; sell não aceita quantidade e confirma `100% solicitado`; residual visível; submit bloqueia dismiss; reconciliação não oferece nova ordem e reaparece ao reabrir.

## Impeccable Trace

- `context`: executado uma vez contra `frontend/src/components/monitor/ChartModal.tsx`, carregando `PRODUCT.md` e `DESIGN.md`.
- `shape`: brief confirmado pelas decisões de Alan — compra em USDT e venda sempre 100% do free.
- `prototype`: HTML navegável construído sobre o shell/tabela/cards do Monitor atual.
- `critique`: assessments A/B isolados no digest inicial, ambos BLOCKED; findings consolidados acima.
- `audit`: detector, contraste, teclado, foco, semântica, segurança de submit, console e responsividade verificados.
- `targeted fixes`: ativo correto, estados críticos, residual, contraste, tabs, inert/foco e idempotência visual corrigidos.
- `polish`: capturas desktop/mobile inspecionadas visualmente; painel claro mantém hierarquia enxuta, CTA amarelo e nenhuma linguagem de urgência.
- `browser gate`: executado no digest final conforme seção abaixo.

## Prototype Validation

- Ferramenta: Playwright CLI, Chromium headless real.
- URL final publicada e validada: `https://dev.criptofarol.com.br/prototypes/card-385-monitor-direct-spot-trading/`.
- Vínculo de versão: o conteúdo servido pela URL final retornou SHA-256 `cc38a528f4294b3bb5fe7f0ef5642cea9884f905ce5b7a8274211caad52653ad`, idêntico ao HTML fonte.
- Viewports: `1440x1000` e `390x844`.
- Desktop asserts: abertura/fechamento; foco inicial e retorno; background `inert`; tabs por teclado; compra `300,00 USDT`; bloqueio de Escape/close no submit; resultado; gatilhos BTC e ETH vinculados ao par/saldo corretos; venda `100% solicitado`; quantidade válida/residual; resultado de venda; reconciliação sem nova ordem, retomada ao reabrir e isolada por símbolo/lado (`BTC incerto -> ETH novo -> BTC incerto`); parcial; rejeitada; preflight sem permissão, recovery link `/profile` e ciclo de foco `recovery -> Tab -> fechar -> Shift+Tab -> recovery`.
- Mobile asserts: gatilho visível; sheet dentro de `390px`; sem overflow; mínimo `10 USDT`; compra por `100 USDT`; venda `100% solicitado`; residual e confirmação visíveis.
- Console: `0 errors`, `0 warnings` após o gate final.
- Evidências vinculadas ao digest final:
  - compra desktop: `8be5ba9ba922b6db09bdc4f5bb40acaa9c22de9d6b184cda6eabe2e96a2c70f8`;
  - venda/confirm desktop: `c8b66c3dc2fba73dd652ef0d3e7f82cf16d8106e48b9654517cd2bc4d2f3a70e`;
  - venda/result desktop: `e0bd2b63c9f7f31b7e7ee9b6cabe07fb5d81924b54024c4317f1da0227bb4599`;
  - reconciliação desktop: `1fc7b5432e193adb7cc0cc9ad4d1776b562d42d20dec39155fb79612bcec9c22`;
  - preflight desktop: `0a52aab175f9cb4674229f01f4be9e290829d1665947c5ab81e831f0ea6f6499`;
  - venda mobile: `91b251dcc75b3b346473c6b7a1a94214dbef0aebe6453c0bd6e13ef1815696a2`.
- Qualquer mudança posterior no HTML ou republicação invalida esta evidência e exige novo gate.

## Design Critique

- Fidelidade: o Monitor atual permanece reconhecível e o delta transacional fica isolado em painel claro.
- Produto/UX: intenção, lado, par, valor, quantidade, residual e risco são apresentados antes do submit; nenhuma operação é automática.
- A11y/responsividade: checklist e browser gate concluídos conforme evidências acima.
- Estados: preflight, validação, confirmação, submit bloqueado, filled, partial, rejected e reconciling são demonstráveis.
- Risco bloqueante atual: nenhum no design; desenvolvimento permanece bloqueado somente pelo gate humano `Aprovação de Design -> Pronto para Dev`.

Design Agent verdict: PASS
