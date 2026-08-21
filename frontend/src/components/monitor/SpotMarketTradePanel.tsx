import React, { useCallback, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { AlertTriangle, Check, Ellipsis, LoaderCircle, X } from 'lucide-react';

import { API_BASE_URL } from '@/lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import type { Opportunity } from './types';

type TradeSide = 'BUY' | 'SELL';
type QuoteOrigin = 'USDT' | 'USDC';
type PanelStep = 'entry' | 'previewing' | 'review' | 'submitting' | 'resuming' | 'result';
type OrderState = 'submitting' | 'reconciling' | 'filled' | 'partial' | 'rejected';
type RefreshState = 'idle' | 'pending' | 'success' | 'failed';
type BalanceState = 'loading' | 'value' | 'unavailable';

type Preview = {
    preview_token: string;
    idempotency_key: string;
    expires_at: string;
    symbol: string;
    strategy_symbol?: string;
    side: TradeSide;
    base_asset: string;
    quote_asset: string;
    indicative_price: string;
    quote_balance: string;
    base_balance: string;
    requested_quote_amount: string | null;
    calculated_base_quantity: string | null;
    estimated_base_quantity: string | null;
    estimated_quote_amount: string | null;
    residual_quantity: string;
    warning: string;
};

type OrderResult = {
    idempotency_key: string;
    symbol: string;
    strategy_symbol?: string | null;
    side: TradeSide;
    state: OrderState;
    quote_asset?: string | null;
    requested_quote_amount: string | null;
    calculated_base_quantity: string | null;
    executed_base_quantity: string | null;
    executed_quote_amount: string | null;
    average_price: string | null;
    fees: Array<{ asset: string; amount: string }>;
    binance_status: string | null;
    residual_quantity: string | null;
    error_code: string | null;
    message: string | null;
};

interface SpotMarketTradePanelProps {
    opportunity: Opportunity;
    binanceConfigured: boolean;
    onClose: () => void;
    onTerminal: () => void | Promise<void>;
}

const normalizeSymbol = (symbol: string): string => symbol.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();

const splitSymbol = (symbol: string): { base: string; pair: string } => {
    const normalized = normalizeSymbol(symbol);
    const base = normalized.endsWith('USDT') ? normalized.slice(0, -4) : normalized;
    return { base, pair: `${base}/USDT` };
};

const pendingStorageKey = (symbol: string): string => `monitor-spot-order:${normalizeSymbol(symbol)}`;
const ORIGIN_PREF_KEY = 'monitor-spot-pay-origin';

const readOriginPreference = (): QuoteOrigin => {
    try {
        const stored = sessionStorage.getItem(ORIGIN_PREF_KEY);
        return stored === 'USDC' ? 'USDC' : 'USDT';
    } catch {
        return 'USDT';
    }
};

const numericValue = (value: string | number | null | undefined): number => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
};

const formatQuote = (value: string | number | null | undefined): string => (
    new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 8 })
        .format(numericValue(value))
);

const formatUsdt = formatQuote;

const formatBase = (value: string | number | null | undefined): string => (
    new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 12 })
        .format(numericValue(value))
);

const parseAmount = (raw: string): number => {
    const compact = raw.trim().replace(/\s/g, '');
    const hasComma = compact.includes(',');
    const normalized = hasComma ? compact.replace(/\./g, '').replace(',', '.') : compact;
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : 0;
};

const responseMessage = (payload: unknown, fallback: string): string => {
    if (!payload || typeof payload !== 'object') return fallback;
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object') {
        const message = (detail as { message?: unknown }).message;
        if (typeof message === 'string' && message.trim()) return message;
    }
    return fallback;
};

const responseCode = (payload: unknown): string | null => {
    if (!payload || typeof payload !== 'object') return null;
    const detail = (payload as { detail?: unknown }).detail;
    if (!detail || typeof detail !== 'object') return null;
    const code = (detail as { code?: unknown }).code;
    return typeof code === 'string' ? code : null;
};

const isTerminal = (state: OrderState): boolean => ['filled', 'partial', 'rejected'].includes(state);

export const SpotMarketTradePanel: React.FC<SpotMarketTradePanelProps> = ({
    opportunity,
    binanceConfigured,
    onClose,
    onTerminal,
}) => {
    const { base, pair } = splitSymbol(opportunity.symbol);
    const [side, setSide] = useState<TradeSide>('BUY');
    const [quoteOrigin, setQuoteOrigin] = useState<QuoteOrigin>(() => readOriginPreference());
    const [step, setStep] = useState<PanelStep>('entry');
    const [amount, setAmount] = useState('');
    const [preview, setPreview] = useState<Preview | null>(null);
    const [result, setResult] = useState<OrderResult | null>(null);
    const [acknowledged, setAcknowledged] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [refreshState, setRefreshState] = useState<RefreshState>('idle');
    const [quoteBalanceState, setQuoteBalanceState] = useState<BalanceState>('loading');
    const [quoteBalanceValue, setQuoteBalanceValue] = useState<number | null>(null);
    const panelRef = useRef<HTMLElement>(null);
    const closeRef = useRef<HTMLButtonElement>(null);
    const headingRef = useRef<HTMLHeadingElement>(null);
    const amountRef = useRef<HTMLInputElement>(null);
    const returnFocusRef = useRef<HTMLElement | null>(null);
    const requestGenerationRef = useRef(0);
    const quoteBalanceGenerationRef = useRef(0);
    const quoteOriginRef = useRef(quoteOrigin);
    quoteOriginRef.current = quoteOrigin;
    const submitLockedRef = useRef(false);
    const missingStatusCountRef = useRef(0);
    const pollAttemptsRef = useRef(0);
    const onTerminalRef = useRef(onTerminal);
    const busy = step === 'previewing' || step === 'submitting';
    const refreshingAfterTerminal = refreshState === 'pending';
    const orderQuote = preview?.quote_asset ?? (side === 'BUY' ? quoteOrigin : 'USDT');
    const resultQuote = result?.quote_asset
        ?? preview?.quote_asset
        ?? (result?.side === 'BUY' && result.symbol?.endsWith('USDC') ? 'USDC' : 'USDT');
    const orderPairLabel = preview
        ? `${preview.base_asset}/${preview.quote_asset}`
        : `${base}/${quoteOrigin}`;
    const indicativePriceLabel = preview
        ? `${formatQuote(preview.indicative_price)} ${preview.quote_asset}${
            preview.quote_asset !== 'USDT' ? ` · ordem ${preview.symbol}` : ''
        }`
        : quoteOrigin === 'USDC' && side === 'BUY'
            ? `Ordem ${base}USDC · preço confirmado ao Continuar`
            : `${formatQuote(opportunity.last_price)} USDT`;

    const refreshQuoteBalance = useCallback(async (origin?: QuoteOrigin) => {
        const targetOrigin = origin ?? quoteOriginRef.current;
        const generation = ++quoteBalanceGenerationRef.current;
        setQuoteBalanceState('loading');
        try {
            const response = await authFetch(`${API_BASE_URL}/external/binance/spot/balances?min_usd=0`);
            const payload = await response.json().catch(() => null);
            if (generation !== quoteBalanceGenerationRef.current) return;
            if (!response.ok || !payload || typeof payload !== 'object') {
                setQuoteBalanceState('unavailable');
                return;
            }
            const balances = (payload as { balances?: unknown }).balances;
            if (!Array.isArray(balances)) {
                setQuoteBalanceState('unavailable');
                return;
            }
            if (balances.length === 0) {
                setQuoteBalanceValue(0);
                setQuoteBalanceState('value');
                return;
            }
            const quote = balances.find((row) => String(row?.asset ?? '').trim().toUpperCase() === targetOrigin);
            const free = Number(quote?.free ?? NaN);
            if (!Number.isFinite(free)) {
                setQuoteBalanceState('unavailable');
                return;
            }
            setQuoteBalanceValue(free);
            setQuoteBalanceState('value');
        } catch {
            if (generation !== quoteBalanceGenerationRef.current) return;
            setQuoteBalanceState('unavailable');
        }
    }, []);

    const refreshAfterTerminal = useCallback(async () => {
        setRefreshState('pending');
        try {
            await onTerminalRef.current();
            sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
            setRefreshState('success');
            void refreshQuoteBalance();
        } catch {
            setRefreshState('failed');
        }
    }, [opportunity.symbol, refreshQuoteBalance]);

    const completeTerminal = useCallback(async (terminalResult: OrderResult) => {
        if (terminalResult.state === 'rejected') {
            sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
            setRefreshState('success');
            return;
        }
        await refreshAfterTerminal();
    }, [opportunity.symbol, refreshAfterTerminal]);

    useEffect(() => {
        onTerminalRef.current = onTerminal;
    }, [onTerminal]);

    const safelyClose = useCallback(() => {
        if (!busy && !refreshingAfterTerminal) onClose();
    }, [busy, onClose, refreshingAfterTerminal]);

    const loadStatus = useCallback(async (idempotencyKey: string): Promise<OrderResult | null> => {
        const response = await authFetch(
            `${API_BASE_URL}/monitor/spot-market-orders/${encodeURIComponent(idempotencyKey)}`,
        );
        const payload = await response.json().catch(() => null);
        if (!response.ok) {
            if (response.status === 404) {
                return null;
            }
            throw new Error(responseMessage(payload, 'Não foi possível consultar a operação.'));
        }
        return payload as OrderResult;
    }, []);

    useEffect(() => {
        returnFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
        const previousOverflow = document.body.style.overflow;
        const applicationRoot = document.getElementById('root');
        const applicationWasInert = applicationRoot?.inert ?? false;
        document.body.style.overflow = 'hidden';
        if (applicationRoot) applicationRoot.inert = true;
        window.requestAnimationFrame(() => closeRef.current?.focus());
        if (binanceConfigured) {
            void refreshQuoteBalance();
        } else {
            setQuoteBalanceState('unavailable');
        }
        return () => {
            document.body.style.overflow = previousOverflow;
            if (applicationRoot) applicationRoot.inert = applicationWasInert;
            returnFocusRef.current?.focus();
        };
        // refreshQuoteBalance is stable; do not re-run modal mount when pay-with origin changes.
    }, [binanceConfigured, refreshQuoteBalance]);

    useEffect(() => {
        const key = sessionStorage.getItem(pendingStorageKey(opportunity.symbol));
        if (!key) return;
        let active = true;
        setStep('resuming');
        void loadStatus(key)
            .then((current) => {
                if (!active || !current) {
                    if (active) {
                        sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
                        setStep('entry');
                    }
                    return;
                }
                setSide(current.side);
                setResult(current);
                setStep('result');
                if (isTerminal(current.state)) {
                    void completeTerminal(current);
                }
            })
            .catch((statusError) => {
                if (!active) return;
                setError(statusError instanceof Error ? statusError.message : 'Falha ao retomar a operação.');
                setStep('entry');
            });
        return () => {
            active = false;
        };
    }, [binanceConfigured, completeTerminal, loadStatus, opportunity.symbol]);

    useEffect(() => {
        if (result?.state !== 'reconciling') return;
        let active = true;
        pollAttemptsRef.current = 0;
        const timer = window.setInterval(() => {
            pollAttemptsRef.current += 1;
            if (pollAttemptsRef.current >= 40) {
                window.clearInterval(timer);
                setError(
                    'Não foi possível confirmar o resultado após novas consultas. Feche e abra o painel novamente para consultar; nenhum novo envio será feito automaticamente.',
                );
                return;
            }
            void loadStatus(result.idempotency_key)
                .then((current) => {
                    if (!active) return;
                    if (!current) {
                        missingStatusCountRef.current += 1;
                        if (missingStatusCountRef.current < 3) return;
                        sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
                        setResult(null);
                        setPreview(null);
                        setAcknowledged(false);
                        setError(
                            'A operação não foi localizada após novas consultas. Gere uma nova prévia antes de tentar novamente.',
                        );
                        setStep('entry');
                        return;
                    }
                    missingStatusCountRef.current = 0;
                    setError(null);
                    setResult(current);
                    if (isTerminal(current.state)) {
                        window.clearInterval(timer);
                        void completeTerminal(current);
                    }
                })
                .catch((statusError) => {
                    if (!active) return;
                    if (pollAttemptsRef.current >= 40) {
                        window.clearInterval(timer);
                        setError(
                            'Não foi possível confirmar o resultado após novas consultas. Feche e abra o painel novamente para consultar; nenhum novo envio será feito automaticamente.',
                        );
                        return;
                    }
                    setError(
                        statusError instanceof Error
                            ? statusError.message
                            : 'Não foi possível consultar a operação. Revise a conexão Binance.',
                    );
                });
        }, 2500);
        return () => {
            active = false;
            window.clearInterval(timer);
        };
    }, [completeTerminal, loadStatus, opportunity.symbol, result?.idempotency_key, result?.state]);

    useEffect(() => {
        if (step === 'review' || step === 'result') {
            window.requestAnimationFrame(() => headingRef.current?.focus());
        }
    }, [step]);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                safelyClose();
                return;
            }
            if (event.key !== 'Tab' || !panelRef.current) return;
            const focusable = Array.from(
                panelRef.current.querySelectorAll<HTMLElement>(
                    'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])',
                ),
            );
            if (focusable.length === 0) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [safelyClose]);

    const selectSide = (nextSide: TradeSide) => {
        if (busy) return;
        setSide(nextSide);
        setPreview(null);
        setResult(null);
        setError(null);
        setAcknowledged(false);
        setStep('entry');
    };

    const selectOrigin = (origin: QuoteOrigin) => {
        if (busy || side !== 'BUY') return;
        setQuoteOrigin(origin);
        try {
            sessionStorage.setItem(ORIGIN_PREF_KEY, origin);
        } catch {
            /* ignore */
        }
        setPreview(null);
        setError(null);
        void refreshQuoteBalance(origin);
    };

    const handleOriginKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, current: QuoteOrigin) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const next: QuoteOrigin = event.key === 'End'
            ? 'USDC'
            : event.key === 'Home'
                ? 'USDT'
                : current === 'USDT' ? 'USDC' : 'USDT';
        selectOrigin(next);
        window.requestAnimationFrame(() => {
            panelRef.current?.querySelector<HTMLButtonElement>(`[data-testid="spot-origin-${next.toLowerCase()}"]`)?.focus();
        });
    };

    const handleTabKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const nextSide: TradeSide = event.key === 'Home'
            ? 'BUY'
            : event.key === 'End'
                ? 'SELL'
                : side === 'BUY' ? 'SELL' : 'BUY';
        selectSide(nextSide);
        window.requestAnimationFrame(() => {
            panelRef.current?.querySelector<HTMLButtonElement>(`#spot-${nextSide.toLowerCase()}-tab`)?.focus();
        });
    };

    const requestPreview = async () => {
        if (!binanceConfigured) return;
        const quoteAmount = parseAmount(amount);
        if (side === 'BUY' && quoteAmount <= 0) {
            setError(`Informe quanto deseja usar em ${quoteOrigin}.`);
            amountRef.current?.focus();
            return;
        }
        const generation = ++requestGenerationRef.current;
        setError(null);
        setStep('previewing');
        try {
            const response = await authFetch(`${API_BASE_URL}/monitor/spot-market-orders/preview`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: opportunity.symbol,
                    side,
                    quote_amount_usdt: side === 'BUY' ? quoteAmount : null,
                    quote_asset: side === 'BUY' ? quoteOrigin : 'USDT',
                }),
            });
            const payload = await response.json().catch(() => null);
            if (!response.ok) {
                throw new Error(responseMessage(payload, 'Não foi possível validar a ordem.'));
            }
            if (generation !== requestGenerationRef.current) return;
            setPreview(payload as Preview);
            setAcknowledged(false);
            setStep('review');
        } catch (previewError) {
            if (generation !== requestGenerationRef.current) return;
            setError(previewError instanceof Error ? previewError.message : 'Falha ao validar a ordem.');
            setStep('entry');
        }
    };

    const submitOrder = async () => {
        if (!preview || !acknowledged || submitLockedRef.current) return;
        submitLockedRef.current = true;
        setError(null);
        setStep('submitting');
        sessionStorage.setItem(pendingStorageKey(opportunity.symbol), preview.idempotency_key);
        let definitiveResponseReceived = false;
        try {
            const response = await authFetch(`${API_BASE_URL}/monitor/spot-market-orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    preview_token: preview.preview_token,
                    idempotency_key: preview.idempotency_key,
                }),
            });
            definitiveResponseReceived = response.status !== 408 && response.status < 500;
            const payload = await response.json().catch(() => null);
            if (!response.ok) {
                const code = responseCode(payload);
                if (code === 'PRIOR_ORDER_RECONCILED' || code === 'PREVIEW_EXPIRED' || code === 'INVALID_PREVIEW') {
                    sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
                    setPreview(null);
                    setResult(null);
                    setAcknowledged(false);
                    setAmount('');
                    setError(code === 'PRIOR_ORDER_RECONCILED'
                        ? responseMessage(payload, 'Revise a operação anterior e gere uma nova prévia.')
                        : 'A prévia não é mais válida. Gere uma nova antes de confirmar.');
                    setStep('entry');
                    return;
                }
                throw new Error(responseMessage(payload, 'A ordem não pôde ser enviada.'));
            }
            const orderResult = payload as OrderResult;
            setResult(orderResult);
            setStep('result');
            if (isTerminal(orderResult.state)) {
                await completeTerminal(orderResult);
            }
        } catch (submitError) {
            if (!definitiveResponseReceived) {
                setResult({
                    idempotency_key: preview.idempotency_key,
                    symbol: preview.symbol,
                    side: preview.side,
                    state: 'reconciling',
                    requested_quote_amount: preview.requested_quote_amount,
                    calculated_base_quantity: preview.calculated_base_quantity,
                    executed_base_quantity: null,
                    executed_quote_amount: null,
                    average_price: null,
                    fees: [],
                    binance_status: null,
                    residual_quantity: preview.residual_quantity,
                    error_code: 'ORDER_STATUS_UNKNOWN',
                    message: 'A conexão foi interrompida após o envio.',
                });
                setStep('result');
                return;
            }
            setError(submitError instanceof Error ? submitError.message : 'Falha ao enviar a ordem.');
            setStep('review');
        } finally {
            submitLockedRef.current = false;
        }
    };

    const reset = () => {
        if (busy || refreshingAfterTerminal) return;
        sessionStorage.removeItem(pendingStorageKey(opportunity.symbol));
        setPreview(null);
        setResult(null);
        setError(null);
        setAcknowledged(false);
        setAmount('');
        setRefreshState('idle');
        setStep('entry');
        void refreshQuoteBalance();
    };

    const unknownOutcome = result?.error_code === 'BINANCE_QUERY_FAILED'
        || result?.error_code === 'BINANCE_ORDER_NOT_FOUND'
        || result?.error_code === 'ORDER_STATUS_UNKNOWN';
    const resultTitle = result?.state === 'filled'
        ? `${result.side === 'BUY' ? 'Compra' : 'Venda'} executada`
        : result?.state === 'partial'
            ? 'Execução parcial'
            : result?.state === 'rejected'
                ? (unknownOutcome ? 'Resultado não confirmado' : 'Ordem não executada')
                : 'Verificando execução';
    const resultCopy = result?.state === 'reconciling'
        ? 'A Binance ainda não confirmou o resultado. Não reenvie a ordem; continuaremos consultando a operação existente.'
        : result?.state === 'rejected'
            ? (result.message || 'A Binance rejeitou a ordem. Nenhum novo envio será feito automaticamente.')
            : refreshState === 'success'
                ? 'A Binance confirmou o resultado. Os saldos do Monitor foram atualizados.'
                : refreshState === 'failed'
                    ? 'A Binance confirmou o resultado, mas não foi possível atualizar os saldos. Atualize o Monitor antes de operar novamente.'
                    : 'A Binance confirmou o resultado. Atualizando os saldos do Monitor…';
    const partialRemaining = result?.state === 'partial'
        ? Math.max(0, result.side === 'BUY'
            ? numericValue(result.requested_quote_amount) - numericValue(result.executed_quote_amount)
            : numericValue(result.calculated_base_quantity) - numericValue(result.executed_base_quantity))
        : 0;

    return createPortal((
        <div
            className="spot-trade-backdrop"
            data-testid="spot-trade-dialog"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) safelyClose();
            }}
        >
            <section
                ref={panelRef}
                className="spot-trade-panel"
                role="dialog"
                aria-modal="true"
                aria-labelledby="spot-trade-title"
                aria-describedby="spot-trade-price"
                aria-busy={busy}
            >
                <header className="spot-trade-head">
                    <div>
                        <h2 id="spot-trade-title">Operar {pair}</h2>
                        <p id="spot-trade-price">Preço indicativo: {indicativePriceLabel}</p>
                    </div>
                    <button
                        ref={closeRef}
                        type="button"
                        className="spot-trade-close"
                        aria-label="Fechar operação"
                        onClick={safelyClose}
                        disabled={busy}
                    >
                        <X aria-hidden="true" />
                    </button>
                </header>

                {!binanceConfigured && !result && step !== 'resuming' ? (
                    <div className="spot-trade-preflight">
                        <h3 ref={headingRef} tabIndex={-1}>Operação indisponível</h3>
                        <p>Conecte a Binance com permissão “Spot Trading”. Permissão de saque não é necessária.</p>
                        <a className="spot-trade-button spot-trade-button--primary" href="/profile">Revisar conexão Binance</a>
                    </div>
                ) : step === 'entry' || step === 'previewing' ? (
                    <div>
                        <div className="spot-trade-tabs" role="tablist" aria-label="Tipo de operação">
                            <button
                                type="button"
                                role="tab"
                                id="spot-buy-tab"
                                aria-selected={side === 'BUY'}
                                aria-controls="spot-buy-panel"
                                tabIndex={side === 'BUY' ? 0 : -1}
                                onClick={() => selectSide('BUY')}
                                onKeyDown={handleTabKeyDown}
                            >Comprar</button>
                            <button
                                type="button"
                                role="tab"
                                id="spot-sell-tab"
                                aria-selected={side === 'SELL'}
                                aria-controls="spot-sell-panel"
                                tabIndex={side === 'SELL' ? 0 : -1}
                                onClick={() => selectSide('SELL')}
                                onKeyDown={handleTabKeyDown}
                            >Vender 100%</button>
                        </div>

                        <div
                            id="spot-buy-panel"
                            role="tabpanel"
                            aria-labelledby="spot-buy-tab"
                            hidden={side !== 'BUY'}
                        >
                            <div className="spot-trade-pay-with" data-testid="spot-pay-with">
                                <div className="spot-trade-pay-with-label" id="spot-pay-with-label">Pagar com</div>
                                <div className="spot-trade-origin-group" role="radiogroup" aria-labelledby="spot-pay-with-label">
                                    {(['USDT', 'USDC'] as QuoteOrigin[]).map((origin) => (
                                        <button
                                            key={origin}
                                            type="button"
                                            role="radio"
                                            className="spot-trade-origin"
                                            aria-checked={quoteOrigin === origin}
                                            tabIndex={quoteOrigin === origin ? 0 : -1}
                                            data-testid={`spot-origin-${origin.toLowerCase()}`}
                                            onClick={() => selectOrigin(origin)}
                                            onKeyDown={(event) => handleOriginKeyDown(event, origin)}
                                            disabled={busy}
                                        >
                                            {origin}
                                        </button>
                                    ))}
                                </div>
                                <p className="spot-trade-origin-hint">
                                    {quoteOrigin === 'USDT'
                                        ? `A estratégia continua ${pair}. Ordem Spot em ${base}USDT.`
                                        : `A estratégia continua ${pair}. Ordem Spot em ${base}USDC (origem USDC).`}
                                </p>
                            </div>
                            <div className="spot-trade-balances">
                                <span>Saldo livre em {quoteOrigin}{' '}
                                    {quoteBalanceState === 'loading' ? (
                                        <b className="spot-trade-balance-loading" role="status" aria-live="polite">carregando…</b>
                                    ) : quoteBalanceState === 'value' ? (
                                        <b role="status" aria-live="polite">{formatQuote(quoteBalanceValue)} {quoteOrigin}</b>
                                    ) : (
                                        <b role="status" aria-live="polite">indisponível</b>
                                    )}
                                </span>
                                <span>Consultado agora na Binance</span>
                            </div>
                            <label className="spot-trade-label" htmlFor="spot-buy-amount">
                                <span>Quanto deseja usar?</span><span>{quoteOrigin}</span>
                            </label>
                            <div className="spot-trade-amount">
                                <input
                                    ref={amountRef}
                                    id="spot-buy-amount"
                                    data-testid="spot-buy-amount"
                                    inputMode="decimal"
                                    autoComplete="off"
                                    value={amount}
                                    onChange={(event) => {
                                        setAmount(event.target.value);
                                        setError(null);
                                    }}
                                    placeholder="0,00"
                                    disabled={busy}
                                    aria-describedby="spot-trade-error"
                                />
                                <span>{quoteOrigin}</span>
                            </div>
                            <div className="spot-trade-quick" aria-label="Valores rápidos">
                                {[100, 250, 500].map((quickAmount) => (
                                    <button key={quickAmount} type="button" onClick={() => setAmount(String(quickAmount))}>
                                        {quickAmount}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div
                            id="spot-sell-panel"
                            role="tabpanel"
                            aria-labelledby="spot-sell-tab"
                            className="spot-trade-sell-total"
                            hidden={side !== 'SELL'}
                        >
                            <strong>Venda de 100% do saldo livre</strong>
                            <p>O backend consultará o saldo atual e enviará a maior quantidade válida sem ultrapassar 100%.</p>
                        </div>

                        <div className="spot-trade-warning">
                            <AlertTriangle aria-hidden="true" />
                            <span>Uma ordem MARKET pode executar em preço diferente da estimativa. Você revisará os dados antes do envio.</span>
                        </div>
                        <p id="spot-trade-error" className="spot-trade-error" role="alert">{error}</p>
                        <div className="spot-trade-actions">
                            <button type="button" className="spot-trade-button" onClick={safelyClose} disabled={step === 'previewing'}>Cancelar</button>
                            <button
                                type="button"
                                className="spot-trade-button spot-trade-button--primary"
                                data-testid="spot-continue-order"
                                onClick={() => void requestPreview()}
                                disabled={step === 'previewing'}
                            >
                                {step === 'previewing' ? <><LoaderCircle className="spot-trade-spinner" aria-hidden="true" /> Validando…</> : 'Continuar'}
                            </button>
                        </div>
                    </div>
                ) : step === 'resuming' ? (
                    <div className="spot-trade-preflight">
                        <h3 ref={headingRef} tabIndex={-1}>Verificando operação anterior…</h3>
                        <p>Consultando o resultado pendente na Binance. Nenhum novo envio será feito.</p>
                        <div className="spot-trade-actions">
                            <button
                                type="button"
                                className="spot-trade-button"
                                data-testid="spot-resume-close"
                                onClick={safelyClose}
                            >
                                Fechar
                            </button>
                        </div>
                    </div>
                ) : step === 'review' || step === 'submitting' ? (
                    <div className="spot-trade-review">
                        <h3 ref={headingRef} tabIndex={-1}>Confirme sua ordem</h3>
                        <p>Confira a operação. O envio à Binance acontece somente após sua confirmação.</p>
                        <dl className="spot-trade-summary">
                            <div><dt>Estratégia / sinal</dt><dd>{pair}</dd></div>
                            <div><dt>Par da ordem</dt><dd>{preview?.symbol ?? orderPairLabel}</dd></div>
                            <div><dt>Lado e tipo</dt><dd>{side === 'BUY' ? 'Comprar' : 'Vender'} · MARKET</dd></div>
                            <div>
                                <dt>{side === 'BUY' ? 'Gastar' : 'Quantidade solicitada'}</dt>
                                <dd>{side === 'BUY'
                                    ? `${formatQuote(preview?.requested_quote_amount)} ${orderQuote}`
                                    : `100% · ${formatBase(preview?.base_balance)} ${base}`}</dd>
                            </div>
                            {side === 'BUY' ? (
                                <div>
                                    <dt>Saldo livre (origem)</dt>
                                    <dd>{formatQuote(preview?.quote_balance)} {orderQuote}</dd>
                                </div>
                            ) : null}
                            {side === 'SELL' ? (
                                <div>
                                    <dt>Quantidade válida / possível residual</dt>
                                    <dd>{formatBase(preview?.calculated_base_quantity)} / {formatBase(preview?.residual_quantity)} {base}</dd>
                                </div>
                            ) : null}
                            <div>
                                <dt>Resultado estimado</dt>
                                <dd>{side === 'BUY'
                                    ? `≈ ${formatBase(preview?.estimated_base_quantity)} ${base}`
                                    : `≈ ${formatQuote(preview?.estimated_quote_amount)} USDT`}</dd>
                            </div>
                            <div><dt>Taxas</dt><dd>Definidas na execução</dd></div>
                        </dl>
                        <p className="spot-trade-preview-warning">{preview?.warning}</p>
                        <label className="spot-trade-ack">
                            <input
                                type="checkbox"
                                checked={acknowledged}
                                onChange={(event) => setAcknowledged(event.target.checked)}
                                disabled={step === 'submitting'}
                            />
                            <span>
                                Entendo que a ordem será enviada em <strong>{preview?.symbol ?? orderPairLabel}</strong>
                                {side === 'BUY' ? ` pagando com ${orderQuote}` : ''} a mercado e que o preço final pode variar.
                            </span>
                        </label>
                        <p className="spot-trade-error" role="alert">{error}</p>
                        <div className="spot-trade-actions">
                            <button type="button" className="spot-trade-button" onClick={() => setStep('entry')} disabled={step === 'submitting'}>Voltar</button>
                            <button
                                type="button"
                                className="spot-trade-button spot-trade-button--primary"
                                data-testid="spot-confirm-order"
                                onClick={() => void submitOrder()}
                                disabled={!acknowledged || step === 'submitting'}
                            >
                                {step === 'submitting'
                                    ? <><LoaderCircle className="spot-trade-spinner" aria-hidden="true" /> Enviando uma vez…</>
                                    : side === 'BUY' ? 'Confirmar compra' : 'Confirmar venda total'}
                            </button>
                        </div>
                    </div>
                ) : result ? (
                    <div className={`spot-trade-result spot-trade-result--${result.state}`} aria-live="polite">
                        <div className="spot-trade-result-mark" aria-hidden="true">
                            {result.state === 'filled'
                                ? <Check />
                                : result.state === 'rejected' ? <X /> : <Ellipsis />}
                        </div>
                        <h3 ref={headingRef} tabIndex={-1}>{resultTitle}</h3>
                        <p>{resultCopy}</p>
                        <dl className="spot-trade-summary">
                            <div><dt>Status</dt><dd>{result.state === 'filled' ? 'Executada' : result.state === 'partial' ? 'Parcialmente executada' : result.state === 'rejected' ? 'Rejeitada' : 'Consultando Binance'}</dd></div>
                            {result.state === 'reconciling' ? (
                                <div><dt>Valores executados</dt><dd>Aguardando confirmação</dd></div>
                            ) : (
                                <>
                                    <div><dt>Quantidade executada</dt><dd>{formatBase(result.executed_base_quantity)} {base}</dd></div>
                                    <div><dt>Valor executado</dt><dd>{formatQuote(result.executed_quote_amount)} {result.side === 'BUY' ? resultQuote : 'USDT'}</dd></div>
                                </>
                            )}
                            {result.state === 'partial' ? (
                                <div>
                                    <dt>Restante não executado</dt>
                                    <dd>{result.side === 'BUY' ? `${formatQuote(partialRemaining)} ${resultQuote}` : `${formatBase(partialRemaining)} ${base}`}</dd>
                                </div>
                            ) : null}
                            {numericValue(result.average_price) > 0 ? <div><dt>Preço médio</dt><dd>{formatQuote(result.average_price)} {resultQuote}</dd></div> : null}
                            {result.fees.length > 0 ? (
                                <div><dt>Taxas cobradas</dt><dd>{result.fees.map((fee) => `${formatBase(fee.amount)} ${fee.asset}`).join(' · ')}</dd></div>
                            ) : null}
                            {numericValue(result.residual_quantity) > 0 ? <div><dt>Residual estimado</dt><dd>{formatBase(result.residual_quantity)} {base}</dd></div> : null}
                        </dl>
                        {result.state === 'reconciling' ? (
                            <p className="spot-trade-reconciling"><LoaderCircle className="spot-trade-spinner" aria-hidden="true" /> Consulta automática em andamento. Não envie novamente.</p>
                        ) : null}
                        {error ? <p className="spot-trade-error" role="alert">{error}</p> : null}
                        <div className="spot-trade-actions">
                            <button
                                type="button"
                                className="spot-trade-button"
                                onClick={safelyClose}
                                disabled={refreshingAfterTerminal}
                            >
                                Fechar
                            </button>
                            {result.state !== 'reconciling' ? (
                                <button
                                    type="button"
                                    className="spot-trade-button spot-trade-button--primary"
                                    onClick={refreshState === 'failed' ? () => void refreshAfterTerminal() : reset}
                                    disabled={refreshingAfterTerminal}
                                >
                                    {refreshingAfterTerminal
                                        ? 'Atualizando saldos…'
                                        : refreshState === 'failed' ? 'Tentar atualizar saldos' : 'Nova operação'}
                                </button>
                            ) : null}
                        </div>
                    </div>
                ) : null}
            </section>
        </div>
    ), document.body);
};
