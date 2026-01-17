// src/lib/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface BacktestRunCreate {
    mode: 'run' | 'compare' | 'optimize';
    exchange: string;
    symbol: string;
    timeframe: string | string[];  // Can be single or multiple for optimization
    timeframes?: string[]; // Deprecated, kept for backward compatibility
    full_period?: boolean;
    since?: string | null;
    until?: string | null;
    strategies: (string | Record<string, any>)[];
    params?: Record<string, any> | null;
    cash?: number;
    fee?: number;
    slippage?: number;
    stop_pct?: number | { min: number, max: number, step: number } | null;
    take_pct?: number | { min: number, max: number, step: number } | null;
    fill_mode?: string;
}

export interface BacktestRunResponse {
    run_id: string;
    status: string;
    message: string;
}

export interface BacktestStatusResponse {
    run_id: string;
    status: 'PENDING' | 'RUNNING' | 'DONE' | 'FAILED';
    created_at: string;
    error_message?: string;
    progress?: number;
    current_step?: string;
}

export interface PresetResponse {
    id: string;
    name: string;
    description: string;
    config: BacktestRunCreate;
}

export interface BacktestRunListItem {
    id: string;
    created_at: string;
    status: string;
    mode: string;
    symbol: string;
    timeframe: string;
    strategies: (string | Record<string, any>)[];
    message?: string;
    progress?: number;
}

// API Functions
export const backtestApi = {
    // Health check
    health: () => api.get('/health'),

    // Get presets
    getPresets: () => api.get<PresetResponse[]>('/presets'),

    // Create backtest run


    // Create comparison backtest
    createCompare: (data: BacktestRunCreate) =>
        api.post<BacktestRunResponse>('/backtest/compare', data),

    // Create optimization backtest
    createOptimize: (data: BacktestRunCreate) =>
        api.post<BacktestRunResponse>('/backtest/optimize', data),

    getBinanceSymbols: () =>
        api.get<{ symbols: string[], count: number }>('/exchanges/binance/symbols'),

    // Get status
    getStatus: (runId: string) =>
        api.get<BacktestStatusResponse>(`/backtest/status/${runId}`),

    // Get result
    getResult: (runId: string) =>
        api.get(`/backtest/result/${runId}`),

    // List runs
    listRuns: (limit = 50, offset = 0) =>
        api.get<BacktestRunListItem[]>(`/backtest/runs?limit=${limit}&offset=${offset}`),

    // Delete run
    deleteRun: (runId: string) =>
        api.delete(`/backtest/runs/${runId}`),

    // Pause/Resume
    pause: (runId: string) => api.post<{ status: string; message: string }>(`/backtest/pause/${runId}`),
    resume: (runId: string) => api.post<{ status: string; message: string }>(`/backtest/resume/${runId}`),
    listJobs: () => api.get<any[]>('/backtest/jobs'),
};
