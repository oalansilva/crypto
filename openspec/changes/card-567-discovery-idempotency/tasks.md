## 1. Backend

- [x] 1.1 Canonicalizar templates/símbolos/timeframes/direções no `payload_hash`
- [x] 1.2 Não usar `snapshot_hash` como `idempotency_key`
- [x] 1.3 Teste de integração: payload equivalente (ordem diferente) = retry, não 409

## 2. Frontend

- [x] 2.1 Gerar UUID por rascunho e enviar como `idempotency_key` no start
- [x] 2.2 “Novo rascunho” gera chave nova (não reutiliza a do sweep anterior)
- [x] 2.3 Comparar a rota entregue com o protótipo aprovado e registrar no handoff

## 3. Specs e e2e

- [x] 3.1 Sincronizar `discovery-sweep` no apply com o comportamento canônico
- [x] 3.2 e2e funcional start/retry/novo rascunho
- [x] 3.3 QA visual Discovery desktop/mobile (atualizar baseline só se o chip da chave entrar no produto)
