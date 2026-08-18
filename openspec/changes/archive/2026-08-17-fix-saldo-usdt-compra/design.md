# Design — fix-saldo-usdt-compra (card #463)

## Problema

Usuário com saldo USDT visível na Carteira não consegue comprar ativo Spot no Monitor: o modal exibe **"Saldo livre em USDT insuficiente"** mesmo com **100,65 USDT** aparentemente disponíveis (evidência do relato e análise visual das screenshots).

## Usuário afetado

Usuário do beta fechado com saldo USDT em **Simple Earn (rendimento)** na Binance, que aparece somado ao saldo "livre" da Carteira do Cripto Farol, mas **não é elegível para compra Spot direta** (não é `free` do Spot).

## Causa raiz (evidenciada)

1. **Carteira soma Simple Earn ao saldo exibido:** `fetch_spot_balances_snapshot` (`backend/app/services/binance_spot.py:260-268`) adiciona posições de Simple Earn (LDUSDT/`simple-earn`) ao campo `free`/`total` exibido ao usuário. O relato mostra `FREE = TOTAL = 100.65270319` — consistente com saldo somado de Earn.
2. **Compra valida apenas `free` do Spot:** `_balance_map` (`backend/app/services/binance_market_orders.py:72-83`) usa somente `free` de `/api/v3/account`; `build_market_order_plan` rejeita com "Saldo livre em USDT insuficiente" quando `requested_quote > quote_balance` (`:226-227`).
3. **Modal de entrada não mostra o saldo real:** na etapa `entry`, o modal exibe "Saldo livre — Confirmado pela Binance na próxima etapa" **sem valor** (`SpotMarketTradePanel.tsx:550-553`), então o usuário só descobre o problema no erro do preview.
4. Consequência de produto: o usuário **vê** um saldo que o sistema **não pode operar**, com erro genérico e sem dica de causa.

## Hipóteses secundárias (não dominantes, cobertas por mensagem)

- Conta/chave divergente (Carteira e compra usam a mesma credencial do usuário — `get_user_exchange_credential` — portanto improvável).
- Taxa não reservada no limite exato (`saldo == valor`) — não se aplica ao caso (saldo 10x maior).

## Decisão de produto

O saldo em Simple Earn **não** será operável por compra direta (exigiria redeem/resgate, fora do escopo). A correção torna a divergência **transparente e não bloqueante**:

1. **Modal de compra mostra o saldo real livre (Spot) antes de validar** — campo "Saldo livre" passa a exibir o valor efetivo com estados explícitos (`carregando…`, valor, `indisponível`), em vez do texto vazio atual.
2. **Erro de saldo insuficiente vira mensagem acionável:** quando o `free` Spot for insuficiente, o backend retorna o saldo livre real e, se houver USDT em Simple Earn, a dica de que o saldo está em rendimento (Simple Earn) e não é elegível para compra direta.
3. **Carteira separa/explicita Simple Earn:** a linha USDT indica quando parte do saldo está em Simple Earn (`inclui X em Simple Earn`), para o usuário entender que aquele montante não é livre Spot.

## Escopo

| Camada | Arquivo | Mudança |
| --- | --- | --- |
| Backend | `binance_market_orders.py` | Erro de saldo insuficiente inclui saldo livre real; quando houver LD* do quote, anexa dica de Simple Earn (payload estruturado ou mensagem sanitizada). |
| Backend | `binance_spot.py` | Snapshot expõe montante de Simple Earn por ativo (`earn_amount` na linha) sem somar ao `free` operável — sem quebrar contrato existente (`free` permanece Spot free + locked breakdown). |
| Frontend | `SpotMarketTradePanel.tsx` | Etapa `entry`: busca saldo livre real do quote (endpoint de balances) e exibe no campo "Saldo livre" com estados loading/erro; mensagem de erro do preview usa o payload enriquecido. |
| Frontend | Carteira (linhas de balanço) | Nota `inclui X em Simple Earn` na linha do ativo quando aplicável. |
| Testes | backend + Playwright visual | Unit: divergência Earn vs free no erro de saldo; modal exibe saldo real; nota Earn na Carteira. |

## Decisões técnicas

- **Fonte de saldo do modal:** endpoint existente `GET /external/binance/spot/balances` (mesma fonte da Carteira, credenciais do usuário) — sem novo endpoint para o modal; o backend passa a não misturar Earn no `free` usado para operação.
- **Compatibilidade de contrato:** `fetch_spot_balances_snapshot` mantém `free`/`locked`/`total` e adiciona campo opcional `earn_amount` (0 quando não houver Earn). Frontend usa `free` (Spot livre real) para operação e `earn_amount` para a nota.
- **Segurança:** nenhum segredo/identificador exposto; erro continua sanitizado (`_safe_rejection_message`).
- **UI impact: affected** — delta restrito ao modal de compra (campo Saldo livre com valor/estados) e à linha de balanço da Carteira (nota Earn). Sem mudança de layout/shell/tokens; segue `DESIGN.md` e o protótipo do card #385 como base de fidelidade.

## Prototype

- **URL navegável:** `https://dev.criptofarol.com.br/prototypes/card-463-saldo-usdt-compra/`
- **Caminho versionado:** `frontend/public/prototypes/card-463-saldo-usdt-compra/index.html`
- **Base do sistema atual:** modal `SpotMarketTradePanel` (estrutura/tokens do protótipo card-385 + `index.css` atual) e tela Carteira (`ExternalBalancesPage`).
- **Delta representado:**
  1. Modal etapa `entry`: "Saldo livre" com valor real (USDT Spot free) e estado de carregamento.
  2. Erro de preview enriquecido: "Saldo livre em USDT insuficiente (X USDT disponíveis). Seu saldo restante está em Simple Earn (rendimento) e não é elegível para compra direta."
  3. Carteira: linha USDT com nota "inclui X em Simple Earn".
- **Fluxos/estados:** carregando → valor; valor insuficiente + Earn → mensagem acionável; linha Carteira com e sem Earn.

## Impeccable Brief

- **Problema:** usuário vê saldo e não consegue comprar, com erro genérico e campo de saldo vazio no modal.
- **Usuário:** beta fechado com USDT em Simple Earn.
- **Resultado:** compra falha apenas quando o Spot free é realmente insuficiente; mensagem explica o saldo real e a causa (Earn); modal mostra saldo livre desde a entrada.
- **Direção:** transparência de saldo sem redesenho — mesmo modal, mesmo shell, valores e estados explícitos.
- **Escopo:** modal de compra + nota na Carteira. Sem novas telas, sem alteração de fluxo de confirmação.
- **Estados:** loading (saldo), valor (saldo), erro insuficiente com Earn, linha Carteira com/sem Earn.
- **Interação:** abrir modal → ver saldo real; clicar Continuar → preview; falha de saldo → mensagem acionável.
- **Restrições:** `DESIGN.md`; fidelidade ao sistema atual; a11y (teclado/foco existentes do modal); responsivo desktop/mobile; sem quebra de contrato da API.

## Design Critique

Análise crítica da solução antes da validação em navegador:

- **Produto:** correta e mínima — trata a causa raiz (divergência de fonte de saldo) e a UX de erro (campo vazio + mensagem genérica). Não expande escopo para "resgatar Earn" (fora do card).
- **UX:** mostrar o saldo livre real na entrada elimina o momento de confusão; mensagem de erro com causa e valor dá agência ao usuário.
- **Acessibilidade:** mantém foco/teclado/aria do modal atual; nota da Carteira como texto de apoio (não apenas cor).
- **Responsividade:** delta não altera layout; modal já é responsivo (panel width min(460px,100%)).
- **Estados:** cobertos loading/valor/erro; ausência de saldo nunca é tratada como zero sem estado explícito (requisito do spec).
- **Riscos aceitos:** usuário com saldo 100% em Earn ainda não conseguirá comprar — agora com explicação clara (decisão de produto documentada); taxa não reservada em limite exato permanece como erro Binance -2010 (fora do caso reportado, mensagem sanitizada já existente).

## Prototype Validation

- **URL servida:** `https://dev.criptofarol.com.br/prototypes/card-463-saldo-usdt-compra/`
- **Arquivo:** `frontend/public/prototypes/card-463-saldo-usdt-compra/index.html`
- **Digest (SHA-256):** `f7b66abdc95a7d852fd386e494fb04c2951f654c619dcf3080c1119c77e17ab7`
- **Ferramenta:** Playwright (projeto `functional`), teste `frontend/tests/e2e/card-463-prototype-gate.spec.ts` — **2 passed**.
- **Viewports:** desktop 1440×900 e mobile 390×844.
- **Asserts executados e resultados (todos verdes):**
  - `[data-testid="quote-balance"]` = `100,65 USDT` no estado padrão (entry); = `carregando…` no cenário loading; = `indisponível` no cenário unavailable.
  - Cenário `insufficient`: mensagem contém `Simple Earn` e `0,65 USDT disponíveis`.
  - Cenário `wallet`: linha USDT visível com badge `inclui 100,00 em Simple Earn`; navegação `Monitor` (sidebar) volta à tela inicial.
  - Mobile: `open-trade-mobile` abre o modal; `usdt-mobile-row` visível; **sem overflow horizontal** (`scrollWidth == clientWidth`) em modal e Carteira.
  - Nenhum `console.error` nem `pageerror` em nenhum viewport.
- **Erros de console/página:** nenhum com impacto no fluxo.

## Impeccable Brief

- **Problema:** usuário vê saldo e não consegue comprar, com erro genérico e campo de saldo vazio no modal.
- **Usuário:** beta fechado com USDT em Simple Earn.
- **Resultado:** compra falha apenas quando o Spot free é realmente insuficiente; mensagem explica o saldo real e a causa (Earn); modal mostra saldo livre desde a entrada.
- **Direção:** transparência de saldo sem redesenho — mesmo modal, mesmo shell, valores e estados explícitos.
- **Escopo:** modal de compra + nota na Carteira. Sem novas telas, sem alteração de fluxo de confirmação.
- **Estados:** loading (saldo), valor (saldo), indisponível (falha de consulta), erro insuficiente com Earn, linha Carteira com/sem Earn.
- **Interação:** abrir modal → ver saldo real; clicar Continuar → preview; falha de saldo → mensagem acionável.
- **Restrições:** `DESIGN.md`; fidelidade ao sistema atual; a11y (teclado/foco existentes do modal); responsivo desktop/mobile; sem quebra de contrato da API.

## Impeccable Critique

### Assessment A (produto/UX/a11y/responsividade/estados — critic read-only)

Veredito inicial: **BLOCKED** com 4 P1; após correções, **PASS**.

- **F2 P1 (Carteira inventada):** protótipo inicial desenhava a Carteira com linguagem visual do Monitor; corrigido clonando a superfície real (`ExternalBalancesPage`: fundo `#07111a`, painel `#101c2a`, bordas `white/10`, 8 colunas, badges DUST-style). Nota `inclui X em Simple Earn` agora é badge no asset, como o badge DUST real. **Resolvido.**
- **F4 P1 (cópia conflitante):** frase "Confirmado pela Binance na próxima etapa" (placeholder do produto) mantida ao lado do valor; removida e substituída por "Consultado agora na Binance". **Resolvido.**
- **P1-1 P1 (cenário entry idêntico ao erro):** input pré-preenchido com 10 e saldo 0,65 sempre disparava erro; cenário entry agora usa saldo 100,65 com input vazio (fluxo feliz) e o erro fica restrito ao cenário `insufficient`. **Resolvido.**
- **P3-1 P2 (estado indisponível ausente):** adicionado cenário `unavailable` com mensagem de falha de consulta. **Resolvido.**
- **F3/A2 P2 (contraste do erro):** `--sell` alterado de `#f6465d` (3.5:1 sobre branco) para `#d64555` (≈4.6:1, AA). **Resolvido.**
- **A1 P2 (tabs sem teclado):** roving tabindex + setas ←/→/Home/End replicados do produto real. **Resolvido.**
- **A4 P2 (quick-amounts sem nome acessível):** `aria-label` adicionado. **Resolvido.**
- **U2 P2 (loading não anunciado):** `role="status"` + `aria-live="polite"` no strip de saldo. **Resolvido.**
- **R1 P1 (nota clippada no mobile):** tabela Carteira com `overflow-x: auto` + variante mobile de cards (como a página real). **Resolvido.**
- **R2 P2 (monitor sem variante mobile):** `mobile-list` replicado da base card-385. **Resolvido.**
- **P4-1 P3 (precisão):** aceito — modal usa 2 casas (`formatUsdt`) e Carteira 8 casas, espelhando o produto real; sem ação.

### Assessment B (detector + navegador — critic read-only)

Veredito inicial: **BLOCKED** (1 assert de a11y); após correções, **PASS**.

- 52/52 asserts de fluxo passaram na primeira rodada (desktop/mobile): foco inicial no fechar, Esc fecha, foco retorna ao trigger, trap de Tab, `app.inert`, `role=dialog`/`aria-modal`/`aria-labelledby`, `aria-live` no erro, `aria-selected` nas tabs, sem overflow.
- Contraste do erro `#f6465d` = 3.53:1 (falhou AA) → corrigido para `#d64555`. **Resolvido.**
- Detector: 1 warning `flat-type-hierarchy` (12px/12.5px/13px) → tipografia unificada (removido 12.5px). Detector final: **[]**.

## Impeccable Audit

- **Acessibilidade:** foco preso no modal, roving tabindex nas tabs, `aria-live` no erro e no saldo, labels acessíveis nos quick amounts, contraste AA no erro, `role=status` no carregamento. OK.
- **Performance:** protótipo estático sem dependências externas; sem impacto.
- **Responsividade:** desktop 1440×900 e mobile 390×844 validados em navegador; sem overflow horizontal; Carteira com scroll horizontal em largura reduzida e cards mobile (padrão real).
- **Theming:** tokens do DESIGN.md preservados (`--canvas/--surface/--primary #fcd535`); Carteira clonada com tokens próprios da página real.
- **Integridade:** nenhum erro de console/página; nenhum recurso quebrado; todas as interações de cenário executam sem dead-end (navegação Monitor↔Carteira funcionando).

## Impeccable Trace

- **Pipeline:** `context.mjs --target frontend/public/prototypes/card-463-saldo-usdt-compra/index.html` → `detect.mjs` (pós-correção: `[]`) → browser gate Playwright (2 passed).
- **Comandos:** `npx playwright test card-463-prototype-gate --project=functional` (desktop + mobile); `node .agents/skills/impeccable/scripts/detect.mjs --json <protótipo>`.
- **Digest do alvo:** `f7b66abdc95a7d852fd386e494fb04c2951f654c619dcf3080c1119c77e17ab7` (versão validada = versão servida na URL DEV, conferida via curl).
- **Sessão principal:** opencode (deepseek-v4-flash) — ownership do design.md, correções direcionadas, síntese dos dois assessments e gate final.
- **Assessment A e B:** subagents read-only herdando o modelo/versão da sessão principal (sem troca de LLM); contextos independentes, resultados não compartilhados antes da síntese; A avaliou fidelidade/produto/UX/a11y/responsividade/estados; B executou detector + navegador real com asserts.
- **Findings do detector:** 1 warning `flat-type-hierarchy` na primeira rodada; 0 após a correção de tipografia.
- **Vínculo com Prototype Validation:** browser gate reexecutado após as correções pós-crítica; versão final validada é a mesma registrada no digest e servida na URL.

## Design Agent verdict

- **PASS** — zero P0/P1 abertos, achados P2/P3 corrigidos ou aceitos com justificativa, browser gate verde (desktop + mobile), detector limpo, nenhum erro de console/página, evidência de igualdade de modelo nos dois assessments e protótipo validado idêntico ao servido (digest conferido).
