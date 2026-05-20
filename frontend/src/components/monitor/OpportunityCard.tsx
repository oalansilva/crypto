import React from 'react';
import { Download, LineChart, ListChecks, RefreshCw, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../../lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { hasExitedOpportunity, resolveOpportunitySignal } from './signalResolution';
import {
    getStrategyDisplayName,
    isProtectedStrategy,
    type Opportunity,
    type MonitorCardMode,
    type MonitorPreference,
    type MonitorPriceTimeframe,
} from './types';

interface OpportunityCardProps {
    opportunity: Opportunity;
    preference: MonitorPreference;
    isPortfolioDerived: boolean;
    portfolioStatusMessage?: string | null;
    portfolioStatusTone?: 'neutral' | 'success' | 'warning';
    isSavingPreference: boolean;
    isOpeningChart: boolean;
    isAdmin?: boolean;
    onToggleInPortfolio: (symbol: string, nextValue: boolean) => void;
    onToggleCardMode: (symbol: string, nextMode: MonitorCardMode) => void;
    onToggleTimeframe: (symbol: string, nextTimeframe: MonitorPriceTimeframe) => void;
    onOpenChart: (opportunity: Opportunity, mode?: 'chart' | 'trades') => void;
}

const symbolKey = (symbol: string): string => symbol.replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();

const toDisplayValue = (value: unknown, precision = 2): string => {
    if (value === null || value === undefined) {
        return '-';
    }
    if (typeof value === 'number') {
        if (!Number.isFinite(value)) return '-';
        if (Number.isInteger(value) || value > 1e8 || precision === 0) {
            return new Intl.NumberFormat('en-US').format(value);
        }
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: precision,
            maximumFractionDigits: precision,
        }).format(value);
    }
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'string') return value || '-';
    return String(value);
};

const renderKeyValueRows = (values?: Record<string, unknown>): Array<[string, string]> => {
    if (!values || Object.keys(values).length === 0) {
        return [['Sem dados', '-']];
    }

    return Object.entries(values).map(([label, value]) => [label, toDisplayValue(value)]);
};

const protectedRows = (): Array<[string, string]> => [['Protegido', 'Oculto']];

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
    opportunity,
    preference,
    isPortfolioDerived,
    portfolioStatusMessage,
    portfolioStatusTone = 'neutral',
    isSavingPreference,
    isOpeningChart,
    isAdmin = false,
    onToggleInPortfolio,
    onToggleCardMode,
    onToggleTimeframe,
    onOpenChart,
}) => {
    const {
        symbol,
        name,
        template_name,
        timeframe,
        is_holding,
        distance_to_next_status,
        last_price,
    } = opportunity;

    const strategyProtected = isProtectedStrategy(opportunity);
    const strategyDisplayName = getStrategyDisplayName(opportunity);
    const showTechnicalDetails = isAdmin || !strategyProtected;
    const effectiveTimeframe: MonitorPriceTimeframe = '1d';
    const distance = distance_to_next_status;
    const distanceStr = distance !== null && distance !== undefined ? `${distance.toFixed(2)}%` : '-';

    const [isEditingNotes, setIsEditingNotes] = React.useState(false);
    const [notesValue, setNotesValue] = React.useState(opportunity.notes || '');
    const [isSavingNotes, setIsSavingNotes] = React.useState(false);

    React.useEffect(() => {
        setNotesValue(opportunity.notes || '');
    }, [opportunity.notes]);

    const resolvedSignal = React.useMemo(
        () => resolveOpportunitySignal(opportunity, { selectedTimeframe: effectiveTimeframe }),
        [effectiveTimeframe, opportunity],
    );
    const statusMessage = resolvedSignal.statusMessage;
    const exitClassName = resolvedSignal.section === 'exit'
        ? ''
        : 'hold-msg';
    const batchReference = typeof opportunity.notes === 'string'
        ? opportunity.notes.match(/\(([^)]+)\)/)?.[1] ?? '-'
        : '-';
    const batchInfo = opportunity.timestamp ? new Date(opportunity.timestamp).toLocaleString('en-US') : '-';
    const symbolTestKey = symbolKey(symbol);
    const showEntryStopRows = resolvedSignal.section !== 'exit' && !hasExitedOpportunity(opportunity);
    const portfolioStatusClass = portfolioStatusTone === 'success'
        ? 'text-emerald-300'
        : portfolioStatusTone === 'warning'
            ? 'text-amber-300'
            : 'text-slate-300';

    const parameterRows = strategyProtected
        ? protectedRows()
        : renderKeyValueRows(opportunity.parameters as Record<string, unknown> | undefined);
    const indicatorRows = strategyProtected
        ? protectedRows()
        : renderKeyValueRows(opportunity.indicator_values as Record<string, unknown> | undefined);

    const priceString = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
    }).format(last_price);

    const saveNotes = async () => {
        try {
            setIsSavingNotes(true);
            const response = await authFetch(`${API_BASE_URL}/favorites/${opportunity.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: notesValue }),
            });
            if (!response.ok) {
                throw new Error('Erro ao salvar notas');
            }
            setIsEditingNotes(false);
        } catch (error) {
            console.error('Error saving notes:', error);
            alert('Erro ao salvar notas. Tente novamente.');
        } finally {
            setIsSavingNotes(false);
        }
    };

    const exportSummary = async () => {
        const payload = {
            symbol,
            template_name: strategyProtected ? strategyDisplayName : template_name,
            timeframe,
            last_price,
            distance_to_next_status,
            is_holding,
            status: resolvedSignal.visual.badgeText,
            message: statusMessage,
            is_strategy_protected: strategyProtected,
            ...(strategyProtected ? {} : {
                parameters: opportunity.parameters ?? {},
                indicator_values: opportunity.indicator_values ?? {},
            }),
            notes: notesValue,
        };

        if (navigator?.clipboard?.writeText) {
            try {
                await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
                return;
            } catch {
                // fallback below
            }
        }
        window.prompt('Resumo da oportunidade:', JSON.stringify(payload));
    };

    const confirmManagement = () => {
        if (isPortfolioDerived) {
            return;
        }
        onToggleInPortfolio(symbol, true);
    };
    const nextMode: MonitorCardMode = preference.card_mode === 'price' ? 'strategy' : 'price';
    const timeframeOptions: MonitorPriceTimeframe[] = ['1d'];

    return (
        <div
            data-testid={`monitor-card-${symbolTestKey}`}
            data-portfolio-derived={isPortfolioDerived ? 'true' : 'false'}
            onClick={(event) => {
                const target = event.target as HTMLElement;
                if (target.closest('button, a, input, textarea, select')) {
                    return;
                }
                onOpenChart(opportunity, 'chart');
            }}
        >
            <div className="detail-control-strip">
                <div className="detail-pair-summary">
                    <span className="detail-symbol">{symbol}</span>
                    <span className={`status-pill ${resolvedSignal.section}`}>{resolvedSignal.visual.badgeText}</span>
                    <span title="Timeframe da estratégia" className="detail-timeframe">{timeframe || '-'}</span>
                    <span title="Timeframe do gráfico de preço" className="detail-timeframe">Gráfico {effectiveTimeframe}</span>
                </div>
                {showTechnicalDetails ? (
                    <div className="detail-controls">
                        <button
                            type="button"
                            className="btn ghost"
                            data-testid={`portfolio-toggle-${symbolTestKey}`}
                            aria-pressed={preference.in_portfolio}
                            disabled={isPortfolioDerived || isSavingPreference}
                            onClick={() => onToggleInPortfolio(symbol, !preference.in_portfolio)}
                        >
                            {preference.in_portfolio ? 'No portfólio' : 'Fora do portfólio'}
                        </button>
                        <button
                            type="button"
                            className="btn ghost"
                            data-testid={`mode-toggle-${symbolTestKey}`}
                            onClick={() => onToggleCardMode(symbol, nextMode)}
                            disabled={isSavingPreference}
                        >
                            <span data-testid={`mode-label-${symbolTestKey}`}>
                                {preference.card_mode === 'price' ? 'Preço' : 'Estratégia'}
                            </span>
                        </button>
                        <div className="timeframe-toggle-group" aria-label={`Timeframe ${symbol}`}>
                            {timeframeOptions.map((option) => {
                                const active = effectiveTimeframe === option;
                                return (
                                    <button
                                        key={option}
                                        type="button"
                                        className={`btn ghost ${active ? 'active' : ''}`}
                                        data-testid={`timeframe-toggle-${symbolTestKey}-${option}`}
                                        aria-pressed={active}
                                        disabled={isSavingPreference}
                                        onClick={() => onToggleTimeframe(symbol, option)}
                                    >
                                        {option}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ) : null}
            </div>
            <div className="detail">
                <div>
                    <h5 className="h5-exit">
                        <span className="swatch" />
                        Sinal · {resolvedSignal.visual.badgeText}
                    </h5>
                    <div className={`exit-msg ${exitClassName}`}>
                        <span className="label">Mensagem</span>
                        <span>{statusMessage}</span>
                    </div>
                    <div className="candle-meta">
                        <span>
                            estratégia <b>{strategyDisplayName || name || symbol}</b>
                        </span>
                        {opportunity.strategy_description ? (
                            <span className="strategy-description">
                                descrição <b>{opportunity.strategy_description}</b>
                            </span>
                        ) : null}
                        <span>
                            tf <b>{effectiveTimeframe}</b>
                        </span>
                        <span>
                            candle <b>{opportunity.indicator_values_candle_time || '-'}</b>
                        </span>
                        {resolvedSignal.freshnessReason ? (
                            <span>
                                alerta <b>{resolvedSignal.freshnessReason}</b>
                            </span>
                        ) : null}
                    </div>
                    {isPortfolioDerived && portfolioStatusMessage ? (
                        <p className={`monitor-status-card-note ${portfolioStatusClass}`} data-testid={`portfolio-sync-status-${symbolTestKey}`}>
                            {portfolioStatusMessage}
                        </p>
                    ) : null}
                    {isOpeningChart ? (
                        <p className="monitor-status-card-note text-slate-300 text-[11px] mt-2">Abrindo gráfico...</p>
                    ) : null}
                </div>

                {showTechnicalDetails ? (
                    <div>
                        <h5 className="h5-params">
                            <span className="swatch" />
                            Parâmetros
                        </h5>
                        <dl className="kv">
                            {parameterRows.map(([label, value]) => (
                                <React.Fragment key={`param-${label}`}>
                                    <dt>{label}</dt>
                                    <dd>{value}</dd>
                                </React.Fragment>
                            ))}
                        </dl>
                        <div style={{ height: '14px' }} />
                        <h5 className="h5-indicators">
                            <span className="swatch" />
                            Indicadores
                        </h5>
                        <dl className="kv">
                            {indicatorRows.map(([label, value]) => (
                                <React.Fragment key={`indicator-${label}`}>
                                    <dt>{label}</dt>
                                    <dd>{value}</dd>
                                </React.Fragment>
                            ))}
                        </dl>
                    </div>
                ) : null}

                <div>
                    <h5 className="h5-notes">
                        <span className="swatch" />
                        Notas operacionais
                    </h5>
                    {isEditingNotes ? (
                        <div className="notes-edit-block">
                            <textarea
                                className="note-textarea"
                                value={notesValue}
                                onChange={(event) => setNotesValue(event.target.value)}
                                placeholder="Adicionar nota"
                                rows={3}
                            />
                            <div className="detail-edit-actions">
                                <button
                                    type="button"
                                    className="btn ghost"
                                    onClick={() => {
                                        setNotesValue(opportunity.notes || '');
                                        setIsEditingNotes(false);
                                    }}
                                    disabled={isSavingNotes}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="button"
                                    className="btn"
                                    onClick={saveNotes}
                                    disabled={isSavingNotes}
                                >
                                    {isSavingNotes ? 'Salvando...' : 'Salvar'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="notes-block">
                            <span>{notesValue || <span className="empty">Sem notas para esta posição.</span>}</span>
                            <button type="button" className="notes-edit" onClick={() => setIsEditingNotes(true)} disabled={isSavingPreference}>
                                Editar
                            </button>
                        </div>
                    )}

                    <div style={{ height: '14px' }} />
                    <h5 className="h5-notes">
                        <span className="swatch" />
                        {showEntryStopRows ? 'Compra / Stop' : 'Execução'}
                    </h5>
                    <dl className="kv">
                        {showEntryStopRows ? (
                            <React.Fragment>
                                <dt>compra</dt>
                                <dd>
                                    {opportunity.entry_price !== null && opportunity.entry_price !== undefined
                                        ? `$${toDisplayValue(opportunity.entry_price, 8)}`
                                        : '-'}
                                </dd>
                                <dt>stop</dt>
                                <dd>
                                    {opportunity.stop_price !== null && opportunity.stop_price !== undefined
                                        ? `$${toDisplayValue(opportunity.stop_price, 8)}`
                                        : '-'}
                                </dd>
                            </React.Fragment>
                        ) : null}
                        <dt>preço atual</dt>
                        <dd>{priceString}</dd>
                        <dt>distância stop</dt>
                        <dd>
                            {opportunity.distance_to_stop_pct !== null && opportunity.distance_to_stop_pct !== undefined
                                ? `${toDisplayValue(opportunity.distance_to_stop_pct, 2)}%`
                                : '-'}
                        </dd>
                        <dt>distância objetivo</dt>
                        <dd>{distanceStr}</dd>
                    </dl>
                </div>
            </div>

            <div className="detail-foot">
                <div className="hint">Lote {batchInfo} · ref {batchReference}</div>
                <div className="actions">
                    {showTechnicalDetails ? (
                        <>
                        <button type="button" className="btn ghost" onClick={exportSummary}>
                            <Download className="h-3.5 w-3.5" />
                            Exportar
                        </button>
                        <button
                            type="button"
                            className="btn"
                            onClick={() => onToggleCardMode(symbol, nextMode)}
                            title={`Alternar para modo ${nextMode}`}
                        >
                            <RefreshCw className="h-3.5 w-3.5" />
                            Reavaliar
                        </button>
                        <button
                            type="button"
                            className="btn primary"
                            onClick={confirmManagement}
                            disabled={isSavingPreference}
                        >
                            <ShieldCheck className="h-3.5 w-3.5" />
                            Confirmar gestão
                        </button>
                        </>
                    ) : null}
                    <button type="button" className="btn" onClick={() => onOpenChart(opportunity, 'chart')}>
                        <LineChart className="h-3.5 w-3.5" />
                        Abrir Gráfico
                    </button>
                    <button type="button" className="btn primary" onClick={() => onOpenChart(opportunity, 'trades')}>
                        <ListChecks className="h-3.5 w-3.5" />
                        Ver Trades
                    </button>
                </div>
            </div>

        </div>
    );
};
