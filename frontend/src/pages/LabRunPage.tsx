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
  budget?: any;
  outputs?: any;
  needs_user_confirm?: boolean;
};

const LabRunPage: React.FC = () => {
  const { runId } = useParams();
  const id = (runId || '').trim();
  const [data, setData] = useState<RunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [continuing, setContinuing] = useState(false);

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

  const continueRun = async () => {
    if (!id) return;
    setContinuing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/lab/runs/${encodeURIComponent(id)}/continue`, { method: 'POST' });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(String(j?.detail || `HTTP ${res.status}`));
      // polling will refresh
    } catch (e: any) {
      setError(e?.message || 'Falha ao continuar');
    } finally {
      setContinuing(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-xs text-gray-400">Lab run</div>
            <div className="font-mono text-sm text-gray-200">{id}</div>
          </div>
          <div className="flex items-center gap-4">
            <a href="/openspec/07-strategy-lab-langgraph-v2" className="text-sm text-gray-300 hover:text-white underline underline-offset-4">spec v2</a>
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

          {data?.budget ? (
            <div className="text-xs text-gray-400 font-mono whitespace-pre-wrap">
              budget: {JSON.stringify(data.budget)}
            </div>
          ) : null}

          {data?.needs_user_confirm ? (
            <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-3">
              <div className="text-sm text-yellow-200 font-semibold">Limite atingido — confirmar para continuar</div>
              <div className="text-xs text-yellow-200/80 mt-1">Continuar adiciona +3 turns e +15000 tokens.</div>
              <button
                onClick={continueRun}
                disabled={continuing}
                className="mt-3 px-4 py-2 rounded-lg bg-yellow-500 text-black text-sm font-bold disabled:opacity-50"
              >
                {continuing ? 'Continuando…' : 'Continuar'}
              </button>
            </div>
          ) : null}

          <div className="text-xs text-gray-500">Polling a cada 2s</div>

          {data?.trace?.api_url ? (
            <div className="text-xs text-gray-400">
              API: <span className="font-mono">{data.trace.api_url}</span>
            </div>
          ) : null}
        </div>

        {data?.backtest ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="text-sm font-semibold mb-3">Backtest (CP6: walk-forward 70/30)</div>
            <div className="text-xs text-gray-400 font-mono whitespace-pre-wrap">
              {JSON.stringify(
                {
                  symbol: data.backtest.symbol,
                  timeframe: data.backtest.timeframe,
                  template: data.backtest.template,
                  deep_backtest: data.backtest.deep_backtest,
                  candles_all: data.backtest.candles,
                  metrics_all: data.backtest.metrics,
                  in_sample: data.backtest.walk_forward?.in_sample,
                  holdout: data.backtest.walk_forward?.holdout,
                },
                null,
                2
              )}
            </div>
          </div>
        ) : null}

        {data?.outputs ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3">
            <div className="text-sm font-semibold">Personas (CP4)</div>
            {data.outputs.coordinator_summary ? (
              <div>
                <div className="text-xs text-gray-400">Coordinator</div>
                <pre className="text-xs text-gray-200 whitespace-pre-wrap font-mono">{data.outputs.coordinator_summary}</pre>
              </div>
            ) : null}
            {data.outputs.dev_summary ? (
              <div>
                <div className="text-xs text-gray-400">Dev</div>
                <pre className="text-xs text-gray-200 whitespace-pre-wrap font-mono">{data.outputs.dev_summary}</pre>
              </div>
            ) : null}

            {data.outputs.candidate_template_name ? (
              <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                <div className="text-xs text-gray-400">Candidate template (CP8)</div>
                <div className="mt-1 flex items-center gap-3">
                  <div className="text-xs text-gray-200 font-mono break-all">{data.outputs.candidate_template_name}</div>
                  <a
                    className="text-xs text-gray-300 hover:text-white underline underline-offset-4"
                    href={`/combo/edit/${encodeURIComponent(data.outputs.candidate_template_name)}`}
                  >
                    abrir no editor
                  </a>
                </div>
              </div>
            ) : null}
            {data.outputs.validator_verdict ? (
              <div>
                <div className="text-xs text-gray-400">Validator</div>
                <pre className="text-xs text-gray-200 whitespace-pre-wrap font-mono">{data.outputs.validator_verdict}</pre>
              </div>
            ) : null}
            {!data.outputs.coordinator_summary && !data.outputs.dev_summary && !data.outputs.validator_verdict ? (
              <div className="text-sm text-gray-400">Aguardando execução das personas…</div>
            ) : null}
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
