## MODIFIED Requirements

### Requirement: Resultado do lote vira favorito em qualquer classe
O melhor resultado de cada ativo com sucesso SHALL ser gravado como favorito, em qualquer classe, **sem estrela** (`tier` nulo; decisão 4 de Alan, 27/10/2026), com a nota "gerado em lote (<id8>)" e `notify_telegram = true` (o alerta só vale depois que o dono der a estrela), sem sobrescrever favorito existente com a mesma configuração. O favorito fica em Favoritos, fora do Monitor e sem alerta, até ganhar estrela. O favorito MUST guardar:
- `asset` (símbolo, id, classe, nome, moeda);
- a configuração (fonte, sessão, ajuste);
- `execution` (precisão pedida e efetiva, trecho sem intradiário, janela pedida e coberta);
- `conventions`;
- `data_provenance`, com o `snapshot_id`.

#### Scenario: Lote grava NVDA
- **WHEN** NVDA termina com sucesso no lote 7f3c2a91
- **THEN** um favorito de NVDA MUST ser gravado com a nota "gerado em lote (7f3c2a91)", sem estrela, classe Ação, moeda USD, configuração Binance Ações, precisão diária e janela efetiva
- **AND** ele MUST NOT aparecer no Monitor nem gerar alerta até o dono dar a estrela

#### Scenario: Lote grava cripto
- **WHEN** BTC/USDT termina com sucesso no mesmo lote
- **THEN** o favorito de BTC/USDT MUST também ser gravado sem estrela
