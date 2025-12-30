# Proposta: Armazenamento Incremental de Dados (Smart Storage)

## Problema
Atualmente, o `CCXTLoader` utiliza um sistema de cache baseado no hash da requisição (`since`, `until`). Isso significa que se o usuário alterar ligeiramente o período do backtest (ex: adicionar um dia), o sistema baixa **novamente** todo o histórico, desperdiçando banda e tempo.
O usuário solicitou uma solução inteligente que baixe "toda a vida" do ativo uma única vez e, nas execuções seguintes, baixe apenas os dados novos (incremental), servindo o backtest a partir do armazenamento local de forma performática.

## Solução Proposta

Implementar um sistema de **Data Lake Local** utilizando **Parquet**.

### 1. Formato de Armazenamento
Utilizaremos **Apache Parquet** devido à sua alta performance de leitura (colunar), compressão eficiente e integração nativa com Pandas.
Estrutura de diretórios proposta:
```
data/
  storage/
    binance/
      BTC_USDT/
        1h.parquet
        5m.parquet
      ETH_USDT/
        ...
```

### 2. Lógica de Carregamento (`IncrementalDataLoader`)

Ao solicitar dados (`fetch_data(symbol, timeframe, since, until)`):

1. **Verificação Local:**
   - Verifica se existe o arquivo `.parquet` correspondente.
   - Se existir, lê os metadados para obter o `last_timestamp` (último candle salvo).

2. **Atualização Incremental (Delta):**
   - **Caso 1 (Novo):** Arquivo não existe.
     - Baixa dados desde a data de "Inception" (ex: 2017-01-01) até `agora`.
     - Salva em Parquet.
   - **Caso 2 (Atualização):** Arquivo existe.
     - Calcula o delta: `since_for_download = last_timestamp + 1 candle`.
     - Verifica se `since_for_download < agora`.
     - Se sim, baixa apenas os novos candles.
     - Carrega o arquivo antigo, concatena os novos dados, remove duplicatas e reescreve o Parquet.

3. **Serving:**
   - Carrega o DataFrame completo (ou utiliza filtros de leitura do Parquet para otimizar memória se necessário, embora para Backtest geralmente carreguemos tudo em memória RAM de qualquer forma).
   - Filtra o DataFrame para retornar apenas o intervalo `[since, until]` solicitado pelo Backtest.
   - Retorna o DataFrame.

### 3. Vantagens
- **Performance:** Leitura de Parquet é ordens de magnitude mais rápida que CSV.
- **Eficiência:** Nunca baixa o mesmo candle duas vezes.
- **Robustez:** Garante que o usuário sempre tenha a base histórica mais completa possível localmente.

### 4. Mudanças Técnicas
- **Novo Loader:** Criar `src/data/incremental_loader.py`.
- **Dependências:** Adicionar `pyarrow` ou `fastparquet` (já incluído no Pandas geralmente, mas verificar).
- **Integração:** Atualizar `BacktestService` para utilizar o novo Loader.

## Plano de Implementação

1. Criar novo Loader (`IncrementalLoader`).
2. Migrar `BacktestService` para usar o novo Loader.
3. Adicionar botão/rotina de "Forçar Atualização Completa" (opcional, para corrigir buracos).
