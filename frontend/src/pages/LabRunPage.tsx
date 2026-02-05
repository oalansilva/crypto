import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { API_BASE_URL } from '@/lib/apiBase';

type TraceEvent = {
  ts_ms: number;
  type: string;
  data?: any;
};

type RunStatus = {
  run_id: string;
  status: string;
  step?: string | null;
  created_at_ms: number;
  updated_at_ms: number;
  trace: { viewer_url: string; api_url: string };
  trace_events?: TraceEvent[];
  backtest?: any;
};

const LabRunPage: React.FC = () => {
  const { runId } = useParams();
  const id = (runId || '').trim();
  const [data, setData] = useState<RunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let alive = true;

    const tick = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/lab/runs/${encodeURIComponent(id)}`);
        const j = (await res.json().catch(() => null)) as any;
        if (!res.ok) throw new Error(String(j?.detail || `HTTP ${res.status}`));
        if (!alive) return;
        setData(j as RunStatus);
        setError(null);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.message || 'Falha ao carregar');
      }
    };

    tick();
    const t = setInterval(tick, 2000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [id]);

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-xs text-gray-400">Lab run</div>
            <div className="font-mono text-sm text-gray-200">{id}</div>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/lab" className="text-sm text-gray-300 hover:text-white underline underline-offset-4">novo run</Link>
            <a href="/favorites" className="text-sm text-gray-300 hover:text-white underline underline-offset-4">favorites</a>
          </div>
        </div>

        {error ? (
          <div className="text-sm text-red-400 border border-red-500/30 bg-red-500/10 rounded-lg p-3">Erro: {error}</div>
        ) : null}

        <div className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3">
          <div className="text-sm">
            <span className="text-gray-400">status:</span> <span className="font-semibold">{data?.status || '…'}</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-400">step:</span> <span className="font-mono">{data?.step || '-'}</span>
          </div>
          <div className="text-xs text-gray-500">Polling a cada 2s</div>

          {data?.trace?.api_url ? (
            <div className="text-xs text-gray-400">
              API: <span className="font-mono">{data.trace.api_url}</span>
            </div>
          ) : null}
        </div>

        {data?.backtest ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="text-sm font-semibold mb-3">Backtest (CP3)</div>
            <div className="text-xs text-gray-400 font-mono whitespace-pre-wrap">
              {JSON.stringify(
                {
                  symbol: data.backtest.symbol,
                  timeframe: data.backtest.timeframe,
                  template: data.backtest.template,
                  deep_backtest: data.backtest.deep_backtest,
                  candles: data.backtest.candles,
                  metrics: data.backtest.metrics,
                },
                null,
                2
              )}
            </div>
          </div>
        ) : null}

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-semibold">Trace (CP2)</div>
            <div className="text-xs text-gray-500">
              {data?.trace_events?.length ? `${data.trace_events.length} eventos` : 'sem eventos'}
            </div>
          </div>

          {data?.trace_events?.length ? (
            <div className="space-y-3">
              {data.trace_events.slice().reverse().map((ev, idx) => (
                <div key={`${ev.ts_ms}-${idx}`} className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-xs text-gray-300 font-mono">{ev.type}</div>
                    <div className="text-[10px] text-gray-500 font-mono">{new Date(ev.ts_ms).toISOString()}</div>
                  </div>
                  {ev.data ? (
                    <pre className="mt-2 text-xs text-gray-200 whitespace-pre-wrap font-mono">
                      {JSON.stringify(ev.data, null, 2)}
                    </pre>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-400">Nenhum evento de trace ainda.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LabRunPage;
