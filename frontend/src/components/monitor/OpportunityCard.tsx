import React from 'react';
import { CircleDollarSign, Download, LineChart, ListChecks, RefreshCw, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../../lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { normalizeStrategyTransparency } from '@/lib/strategyTransparency';
import { StrategyTransparencyPanel } from '../trades/StrategyTransparencyPanel';
import { hasExitedOpportunity, resolveOpportunitySignal, type ResolvedMonitorSignal } from './signalResolution';
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
    resolvedSignal?: ResolvedMonitorSignal;
    isSavingPreference: boolean;
    isOpeningChart: boolean;
    canOpenTrade: boolean;
    tradeUnavailableReason?: string | null;
    isAdmin?: boolean;
    onToggleInPortfolio: (symbol: string, nextValue: boolean) => void;
    onToggleCardMode: (symbol: string, nextMode: MonitorCardMode) => void;
    onToggleTimeframe: (symbol: string, nextTimeframe: MonitorPriceTimeframe) => void;
    onOpenChart: (opportunity: Opportunity, mode?: 'chart' | 'trades') => void;
    onOpenTrade: (opportunity: Opportunity) => void;
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

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
    opportunity,
    preference,
    isPortfolioDerived,
    portfolioStatusMessage,
    portfolioStatusTone = 'neutral',
    resolvedSignal: resolvedSignalOverride,
    isSavingPreference,
    isOpeningChart,
    canOpenTrade,
    tradeUnavailableReason,
    isAdmin = false,
    onToggleInPortfolio,
    onToggleCardMode,
    onToggleTimeframe,
    onOpenChart,
    onOpenTrade,
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

    const strategyTransparency = React.useMemo(
        () => normalizeStrategyTransparency(opportunity.strategy_transparency),
        [opportunity.strategy_transparency],
    );
    const strategyProtected = isProtectedStrategy(opportunity);
    const strategyDisplayName = getStrategyDisplayName(opportunity);
    const isShort = String(
        opportunity.direction ?? opportunity.parameters?.direction ?? strategyTransparency?.direction ?? 'long',
    ).trim().toLowerCase() === 'short';
    const showFunctionalDetails = isAdmin || !strategyProtected || Boolean(opportunity.strategy_transparency);
    const showManagementControls = isAdmin || !strategyProtected;
    const effectiveTimeframe: MonitorPriceTimeframe = '1d';
    const UNAVAILABLE = 'indisponível — dado não confiável';
    const TIMEFRAME_TO_MS: Record<string, number> = {
        '15m': 15 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    };
    const isRiskStale = React.useMemo(() => {
        const ref = opportunity.indicator_values_candle_time;
        if (!ref) return false;
        const ms = Date.parse(ref);
        if (Number.isNaN(ms)) return false;
        const tf = String(opportunity.timeframe || '1d').trim().toLowerCase();
        const maxAge = (TIMEFRAME_TO_MS[tf] ?? TIMEFRAME_TO_MS['1d']) * 3;
        return Date.now() - ms > maxAge;
    }, [opportunity.indicator_values_candle_time, opportunity.timeframe]);
    const hasRiskValue = (value: unknown): boolean => value !== null && value !== undefined && !isRiskStale;
    const formatUsd = (value: number): string => new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
    }).format(value);
    const formatPct = (value: number): string => `${toDisplayValue(value, 2)}%`;
    const distanceStrUnavailable = !hasRiskValue(distance_to_next_status) ? UNAVAILABLE : formatPct(distance_to_next_status as number);
    const distanceStopStr = !hasRiskValue(opportunity.distance_to_stop_pct) ? UNAVAILABLE : formatPct(opportunity.distance_to_stop_pct as number);
    const stopStr = !hasRiskValue(opportunity.stop_price) ? UNAVAILABLE : formatUsd(opportunity.stop_price as number);
    const entryStr = !hasRiskValue(opportunity.entry_price) ? UNAVAILABLE : formatUsd(opportunity.entry_price as number);
    const alvoPrice: number | null = React.useMemo(() => {
        if (!hasRiskValue(distance_to_next_status) || last_price === null || last_price === undefined || isRiskStale) return null;
        const dist = distance_to_next_status as number;
        if (!Number.isFinite(dist) || !Number.isFinite(last_price)) return null;
        return isShort ? last_price * (1 - dist / 100) : last_price * (1 + dist / 100);
    }, [distance_to_next_status, last_price, isShort, isRiskStale]);
    const alvoStr = alvoPrice === null ? UNAVAILABLE : formatUsd(alvoPrice);

    const [isEditingNotes, setIsEditingNotes] = React.useState(false);
    const [notesValue, setNotesValue] = React.useState(opportunity.notes || '');
    const [isSavingNotes, setIsSavingNotes] = React.useState(false);

    React.useEffect(() => {
        setNotesValue(opportunity.notes || '');
    }, [opportunity.notes]);

    const computedResolvedSignal = React.useMemo(
        () => resolveOpportunitySignal(opportunity, { selectedTimeframe: effectiveTimeframe }),
        [effectiveTimeframe, opportunity],
    );
    const resolvedSignal = resolvedSignalOverride ?? computedResolvedSignal;
    const statusMessage = resolvedSignal.statusMessage;
    const latestTradeExplanation = React.useMemo(() => {
        const history = [...(opportunity.signal_history || [])].sort(
            (left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp),
        );
        const explanation = history[0]?.explanation;
        if (!explanation || !['available', 'partial'].includes(explanation.status)) return null;
        return explanation.summary?.trim() || null;
    }, [opportunity.signal_history]);
    const exitClassName = resolvedSignal.section === 'exit'
        ? ''
        : 'hold-msg';
    const batchReference = typeof opportunity.notes === 'string'
        ? opportunity.notes.match(/\(([^)]+)\)/)?.[1] ?? '-'
        : '-';
    const batchInfo = opportunity.timestamp ? new Date(opportunity.timestamp).toLocaleString('en-US') : '-';
    const symbolTestKey = symbolKey(symbol);
    const showEntryStopRows = resolvedSignal.section !== 'exit' && !hasExitedOpportunity(opportunity);
    const entryStopHeading = showEntryStopRows ? (isShort ? 'Venda/Short / Stop' : 'Compra / Stop') : 'Risco residual';
    const hasSignalHistory = (opportunity.signal_history?.length ?? 0) > 0;
    const lastExitItem = React.useMemo(() => {
        if (!hasSignalHistory) return null;
        const sorted = [...(opportunity.signal_history || [])].sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp));
        return sorted.find((i) => i.type === 'exit') ?? sorted[0] ?? null;
    }, [opportunity.signal_history, hasSignalHistory]);
    const residualText = !hasSignalHistory
        ? 'posição encerrada segundo a estratégia — sem risco residual mapeado'
        : lastExitItem?.price !== null && lastExitItem?.price !== undefined
            ? `último EXIT em ${formatUsd(lastExitItem.price as number)} · exposição residual ${hasRiskValue(opportunity.distance_to_stop_pct) ? formatPct(opportunity.distance_to_stop_pct as number) : UNAVAILABLE} até o stop histórico — não operável.`
            : 'risco residual a partir do histórico — não operável.';
    const showScenario = showEntryStopRows && hasRiskValue(opportunity.stop_price);
    const scenarioStopText = hasRiskValue(opportunity.stop_price) ? formatUsd(opportunity.stop_price as number) : '';
    const portfolioStatusClass = portfolioStatusTone === 'success'
        ? 'text-emerald-300'
        : portfolioStatusTone === 'warning'
            ? 'text-amber-300'
            : 'text-slate-300';

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
            template_name: strategyTransparency?.display_name || (strategyProtected ? strategyDisplayName : template_name),
            timeframe,
            last_price,
            distance_to_next_status,
            is_holding,
            status: resolvedSignal.visual.badgeText,
            message: statusMessage,
            is_strategy_protected: strategyProtected && !strategyTransparency,
            parameters: strategyTransparency?.effective_parameters ?? (strategyProtected ? {} : opportunity.parameters ?? {}),
            indicator_values: strategyProtected ? {} : opportunity.indicator_values ?? {},
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
                    <span
                        className={`status-pill ${resolvedSignal.section}`}
                        data-testid={`monitor-card-signal-${symbolTestKey}`}
                    >
                        {resolvedSignal.visual.badgeText}
                    </span>
                    <span title="Timeframe da estratégia" className="detail-timeframe">{timeframe || '-'}</span>
                    <span title="Timeframe do gráfico de preço" className="detail-timeframe">Gráfico {effectiveTimeframe}</span>
                </div>
                {showManagementControls ? (
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
                    <div className="mt-2">
                        <StrategyTransparencyPanel
                            id={`monitor-strategy-rules-${symbolTestKey}`}
                            strategyTransparency={strategyTransparency}
                            direction={isShort ? 'short' : 'long'}
                            timeframe={timeframe}
                            compact
                            fallbackName={strategyDisplayName || name || symbol}
                        />
                    </div>
                    {latestTradeExplanation ? (
                        <div
                            className="mt-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] px-3 py-2 text-sm leading-6 text-[#eaecef]"
                            data-testid={`monitor-trade-explanation-summary-${symbolTestKey}`}
                        >
                            <span className="block text-[10px] font-semibold uppercase text-[#929aa5]">O que aconteceu agora</span>
                            {latestTradeExplanation}
                        </div>
                    ) : null}
                    <div className="candle-meta" data-testid={`monitor-detail-strategy-identity-${symbolTestKey}`}>
                        <strong className="block text-sm font-semibold text-[#eaecef]" data-testid="monitor-detail-strategy-title">
                            {strategyDisplayName || name || symbol}
                        </strong>
                        {opportunity.strategy_description ? (
                            <span className="strategy-description block text-sm leading-6 text-[#b7bdc6]" data-testid="monitor-detail-strategy-description">
                                {opportunity.strategy_description}
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
                        {entryStopHeading}
                    </h5>
                    {showEntryStopRows ? (
                        <>
                            <dl className="kv" data-testid={`monitor-risk-block-${symbolTestKey}`} data-risk-kv={symbolTestKey}>
                                <dt>distância até saída</dt>
                                <dd className={!hasRiskValue(distance_to_next_status) ? 'risk-unavailable' : undefined} title={!hasRiskValue(distance_to_next_status) ? 'dado não confiável ≠ erro de rede' : undefined}>{distanceStrUnavailable}</dd>
                                <dt>distância até stop</dt>
                                <dd className={!hasRiskValue(opportunity.distance_to_stop_pct) ? 'risk-unavailable' : undefined} title={!hasRiskValue(opportunity.distance_to_stop_pct) ? 'dado não confiável ≠ erro de rede' : undefined}>{distanceStopStr}</dd>
                                <dt>stop</dt>
                                <dd className={!hasRiskValue(opportunity.stop_price) ? 'risk-unavailable' : undefined} title={!hasRiskValue(opportunity.stop_price) ? 'dado não confiável ≠ erro de rede' : undefined}>{stopStr}</dd>
                                <dt>alvo</dt>
                                <dd className={alvoPrice === null ? 'risk-unavailable' : undefined} title={alvoPrice === null ? 'dado não confiável ≠ erro de rede' : undefined}>{alvoStr}</dd>
                                <dt>entrada</dt>
                                <dd className={!hasRiskValue(opportunity.entry_price) ? 'risk-unavailable' : undefined} title={!hasRiskValue(opportunity.entry_price) ? 'dado não confiável ≠ erro de rede' : undefined}>{entryStr}</dd>
                                <dt>preço atual</dt>
                                <dd>{priceString}</dd>
                            </dl>
                            {showScenario ? (
                                <p className="scenario-risk" data-scenario={symbolTestKey} aria-live="polite">Se o preço cruzar {scenarioStopText}, a leitura de posição deixa de valer segundo a estratégia (stop).</p>
                            ) : null}
                        </>
                    ) : (
                        <>
                            <dl className="kv" data-testid={`monitor-risk-block-${symbolTestKey}`} data-risk-kv={symbolTestKey}>
                                <dt>preço atual</dt>
                                <dd>{priceString}</dd>
                            </dl>
                            <div className="residual-block" data-residual={symbolTestKey} data-testid={hasSignalHistory ? undefined : 'monitor-risk-fallback'}>
                                <span className="label">Risco residual</span>
                                <span>{residualText}</span>
                            </div>
                        </>
                    )}
                </div>
            </div>

            <div className="detail-foot">
                <div className="hint">Lote {batchInfo} · ref {batchReference}</div>
                <div className="actions">
                    {showFunctionalDetails ? (
                        <>
                        <button type="button" className="btn ghost" onClick={exportSummary}>
                            <Download className="h-3.5 w-3.5" />
                            Exportar
                        </button>
                        {showManagementControls ? (
                            <>
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
                    {canOpenTrade ? (
                        <button
                            type="button"
                            className="btn spot-trade-trigger"
                            data-testid={`open-spot-trade-${symbolTestKey}`}
                            onClick={() => onOpenTrade(opportunity)}
                        >
                            <CircleDollarSign className="h-3.5 w-3.5" />
                            Operar
                        </button>
                    ) : tradeUnavailableReason ? (
                        <button
                            type="button"
                            className="btn spot-trade-unavailable"
                            title={tradeUnavailableReason}
                            aria-label={tradeUnavailableReason}
                            disabled
                        >
                            <CircleDollarSign className="h-3.5 w-3.5" />
                            Operar indisponível
                        </button>
                    ) : null}
                </div>
            </div>

        </div>
    );
};
