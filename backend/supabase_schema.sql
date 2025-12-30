-- Crypto Backtester - Supabase Schema
-- MVP sem autenticação (Service Role no backend)

-- Tabela de runs de backtest
CREATE TABLE IF NOT EXISTS backtest_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'DONE', 'FAILED')),
    mode TEXT NOT NULL CHECK (mode IN ('run', 'compare')),
    
    -- Dataset
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    since TIMESTAMPTZ NOT NULL,
    until TIMESTAMPTZ NOT NULL,
    
    -- Estratégias e parâmetros
    strategies JSONB NOT NULL, -- Array de strings: ["sma_cross", "rsi_reversal"]
    params JSONB, -- Dict por estratégia: {"sma_cross": {"fast": 20, "slow": 50}}
    
    -- Configurações de execução
    fee NUMERIC DEFAULT 0.001,
    slippage NUMERIC DEFAULT 0.0005,
    cash NUMERIC DEFAULT 10000,
    stop_pct NUMERIC,
    take_pct NUMERIC,
    fill_mode TEXT DEFAULT 'close' CHECK (fill_mode IN ('close', 'next_open')),
    
    -- Erro (se houver)
    error_message TEXT
);

-- Tabela de resultados
CREATE TABLE IF NOT EXISTS backtest_results (
    run_id UUID PRIMARY KEY REFERENCES backtest_runs(id) ON DELETE CASCADE,
    result_json JSONB NOT NULL, -- Resultado completo: metrics, trades, equity, drawdown, markers
    metrics_summary JSONB, -- Atalho para comparação rápida
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON backtest_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON backtest_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_symbol ON backtest_runs(symbol);

-- Comentários
COMMENT ON TABLE backtest_runs IS 'Histórico de execuções de backtest';
COMMENT ON TABLE backtest_results IS 'Resultados detalhados dos backtests (sem candles completos)';
COMMENT ON COLUMN backtest_runs.strategies IS 'Array de nomes de estratégias executadas';
COMMENT ON COLUMN backtest_results.result_json IS 'Resultado completo: metrics, trades, equity, drawdown, markers (candles não inclusos)';
