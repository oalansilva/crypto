## 1. Design e aprovação

- [x] 1.1 Produzir protótipo fiel ao Monitor para `Operar`, compra por USDT, venda 100%, confirmação e estados críticos; concluir design-critic, Impeccable e browser gate desktop/mobile.
- [x] 1.2 Publicar os artefatos OpenSpec e o protótipo no card #385, mover para Aprovação de Design e obter o arraste humano de Alan para Pronto para Dev.

## 2. Persistência e contrato backend

- [x] 2.1 Adicionar model PostgreSQL `monitor_spot_order_requests` com unicidade idempotente, estados, resumo sanitizado e timestamps.
- [x] 2.2 Criar migration Alembic reversível para a tabela e seus índices/constraints.
- [x] 2.3 Definir schemas FastAPI de preview, submit, consulta de estado e respostas sanitizadas.

## 3. Integração Binance Spot

- [x] 3.1 Implementar adaptador assinado para `exchangeInfo`, conta/saldos, `POST /api/v3/order` e consulta por `origClientOrderId`, reutilizando padrões seguros existentes.
- [x] 3.2 Implementar validação atual de símbolo, saldo, `MARKET_LOT_SIZE`/`LOT_SIZE`, `MIN_NOTIONAL`/`NOTIONAL` e arredondamento para baixo.
- [x] 3.3 Implementar `BUY MARKET` por `quoteOrderQty` em USDT e `SELL MARKET` do máximo válido de 100% do saldo `free`.
- [x] 3.4 Implementar idempotência, transições persistidas, reconciliação de timeout/resultado desconhecido e bloqueio de resubmissão econômica.
- [x] 3.5 Expor rotas autenticadas de preview, submit/status e garantir uso exclusivo da credencial Binance do usuário.

## 4. Experiência do Monitor

- [x] 4.1 Adicionar o acionador `Operar` ao Monitor sem alterar a hierarquia das ações existentes.
- [x] 4.2 Implementar painel transacional responsivo com escolha Comprar/Vender 100%, valor de compra em USDT e preview do servidor.
- [x] 4.3 Implementar confirmação explícita, foco/teclado/touch e estados sem credencial, inválido, loading, submitting, reconciling, filled, partial e rejected.
- [x] 4.4 Reconciliar saldos/posição no Monitor após resultado terminal e impedir cliques/retries duplicados.
- [x] 4.5 Atualizar copy de Credenciais Binance em Meu Perfil para compra, venda e stop com Spot Trading, IP whitelist e sem withdraw.

## 5. Testes e segurança

- [x] 5.1 Adicionar testes unitários do adaptador/filtros/arredondamento para compra USDT e venda integral.
- [x] 5.2 Adicionar testes de service/rota para autenticação, credencial por usuário, idempotência, timeout desconhecido, reconciliação, parcial e sanitização.
- [x] 5.3 Adicionar testes da migration/model PostgreSQL sem uso de SQLite operacional.
- [x] 5.4 Adicionar Playwright funcional e visual desktop/mobile cobrindo preview, confirmações, cancelamento, bloqueios e resultado sem enviar ordem real.
- [x] 5.5 Executar scan de segurança do diff e confirmar ausência de secrets, signed URLs e payloads privados em respostas/logs/UI.

## 6. Verificação e fechamento técnico

- [x] 6.1 Executar testes focados backend/frontend, build, lint aplicável e validação da change.
- [x] 6.2 Executar `/opsx:verify`, `openspec validate --all` e corrigir qualquer falha relevante ou higiene global bloqueante.
- [x] 6.3 Mover para Code Review, executar review Codex independente do diff exato e corrigir/classificar achados antes do commit.
- [x] 6.4 Commitar/pushar o SHA revisado, mover para QA, abrir PR para `develop` e aguardar `qa-gate` e Playwright visual terminais verdes.
- [x] 6.5 Integrar em `develop`, executar `./restart`, validar a URL/runtime e registrar Done técnico no card sem arquivar a change.
