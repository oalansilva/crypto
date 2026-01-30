# Configuração do backend

## excluded_symbols.json

Lista de **símbolos excluídos** da otimização em lote e da lista de pares da Binance.

- **Regra automática:** todo par cujo ativo base termina com **UP** ou **DOWN** (ex.: ADAUP/USDT, BNBDOWN/USDT) é sempre ignorado, sem precisar listar aqui.
- **Onde é usado:** oportunidades, endpoint `/api/exchanges/binance/symbols`, batch de otimização.
- **Formato:** use o mesmo da exchange (ex: `BTC/USDT`). No JSON liste apenas outros delistados/não suportados; UP/DOWN são tratados pelo código.
