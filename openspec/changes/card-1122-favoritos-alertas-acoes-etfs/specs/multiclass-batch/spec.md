## MODIFIED Requirements

### Requirement: Resultado do lote vira favorito em qualquer classe
O melhor resultado de cada ativo com sucesso SHALL ser gravado como favorito, em qualquer classe, com 1 estrela (`tier = 3`), a nota "gerado em lote (<id8>)" e `notify_telegram = false`, sem sobrescrever favorito existente com a mesma configuração. O favorito MUST guardar:
- `asset` (símbolo, id, classe, nome, moeda);
- a configuração (fonte, sessão, ajuste);
- `execution` (precisão pedida e efetiva, trecho sem intradiário, janela pedida e coberta);
- `conventions`;
- `data_provenance`, com o `snapshot_id`.

#### Scenario: Lote grava NVDA
- **WHEN** NVDA termina com sucesso no lote 7f3c2a91
- **THEN** um favorito de NVDA MUST ser gravado com a nota "gerado em lote (7f3c2a91)", 1 estrela, classe Ação, moeda USD, configuração Binance Ações, precisão diária e janela efetiva
- **AND** ele MUST nascer sem "Alertar"
