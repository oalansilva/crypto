const PARAMETER_LABELS: Record<string, string> = {
    direction: 'Direção',
    ema_short: 'EMA curta',
    ema_long: 'EMA longa',
    sma_medium: 'SMA média',
    sma_long: 'SMA longa',
    stop_loss: 'Stop de perda',
    take_profit: 'Take profit',
    data_source: 'Fonte de dados',
};

const PARAMETER_VALUE_LABELS: Record<string, Record<string, string>> = {
    direction: {
        long: 'Compra',
        short: 'Venda',
    },
    data_source: {
        ccxt: 'CCXT',
        binance: 'Binance',
        stooq: 'Stooq',
        yahoo: 'Yahoo',
    },
};

export function formatStrategyParameterLabel(key: string) {
    return PARAMETER_LABELS[key] || key.replace(/_/g, ' ');
}

export function formatStrategyParameterValue(key: string, value: unknown) {
    if (value === null || value === undefined || value === '') {
        return '-';
    }

    const normalizedValue = String(value).trim().toLowerCase();
    const valueLabels = PARAMETER_VALUE_LABELS[key];
    if (valueLabels?.[normalizedValue]) {
        return valueLabels[normalizedValue];
    }

    if (typeof value === 'number' && (key.includes('stop_loss') || key.includes('take_profit') || key.includes('pct'))) {
        const percentage = Math.abs(value) <= 1 ? value * 100 : value;
        return `${percentage.toFixed(2)}%`;
    }

    return String(value);
}
