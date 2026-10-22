# Configuração do backend

## excluded_symbols.json

Lista de **símbolos excluídos** da otimização em lote e da lista de pares da Binance.

- **Regra automática:** todo par cujo ativo base termina com **UP** ou **DOWN** (ex.: ADAUP/USDT, BNBDOWN/USDT) é sempre ignorado, sem precisar listar aqui.
- **Onde é usado:** oportunidades, endpoint `/api/exchanges/binance/symbols`, batch de otimização.
- **Formato:** use o mesmo da exchange (ex: `BTC/USDT`). No JSON liste apenas outros delistados/não suportados; UP/DOWN são tratados pelo código.
- **Exceção da regra UP/DOWN:** `JUP/USDT` e `SYRUP/USDT` são pares legítimos e não são excluídos (`LEGITIMATE_UP_DOWN_PAIRS` em `app/symbols_config.py`). O catálogo de ativos (#1117) aplica a regra pelo contexto da Binance: sufixo UP/DOWN com spot desligado ou com o ativo sem o sufixo também listado.
