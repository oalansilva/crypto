import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { API_BASE_URL } from '@/lib/apiBase';
import RunChatView, { type TraceEvent } from '@/components/lab/RunChatView';

// TraceEvent type moved to RunChatView

type RunStatus = {
  run_id: string;
  status: string;
  step?: string | null;
  created_at_ms: number;
  updated_at_ms: number;
  trace: { viewer_url: string; api_url: string; enabled?: boolean; provider?: string; thread_id?: string; trace_id?: string; trace_url?: string | null };
  trace_events?: TraceEvent[];
  backtest_job?: any;
  backtest?: any;
  budget?: any;
  outputs?: any;
  needs_user_confirm?: boolean;
};

const fmtPct = (v: any) => {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-';
  const n = Number(v);
  return `${(n * 100).toFixed(2)}%`;
};

const fmtNum = (v: any, digits = 2) => {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-';
  return Number(v).toFixed(digits);
};

const MetricCard: React.FC<{ title: string; subtitle?: string; metrics?: any }> = ({ title, subtitle, metrics }) => {
  const m = metrics || {};
  return (
    <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">{title}</div>
          {subtitle ? <div className="text-[11px] text-gray-500 mt-0.5">{subtitle}</div> : null}
        </div>
        <div className="text-xs text-gray-400">trades: <span className="font-mono text-gray-200">{m.total_trades ?? '-'}</span></div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <div>
          <div className="text-[10px] text-gray-500">return</div>
          <div className="text-sm font-mono">{m.total_return_pct != null ? `${fmtNum(m.total_return_pct)}%` : (m.total_return != null ? fmtPct(m.total_return) : '-')}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500">max DD</div>
          <div className="text-sm font-mono">
            {m.max_drawdown_pct != null ? `${fmtNum(m.max_drawdown_pct)}%` : (m.max_drawdown != null ? `${fmtNum(m.max_drawdown)}${m.max_drawdown > 1.5 ? '%' : ''}` : '-')}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500">sharpe</div>
          <div className="text-sm font-mono">{m.sharpe_ratio != null ? fmtNum(m.sharpe_ratio) : '-'}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500">profit factor</div>
          <div className="text-sm font-mono">{m.profit_factor != null ? fmtNum(m.profit_factor) : '-'}</div>
        </div>
      </div>
    </div>
  );
};

const LabRunPage: React.FC = () => {
  const { runId } = useParams();
  const id = (runId || '').trim();
  const [data, setData] = useState<RunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [continuing, setContinuing] = useState(false);
  const [tab, setTab] = useState<'chat' | 'debug'>('chat');

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

  const selection = data?.outputs?.selection;
  const gateApproved = selection?.approved === true;

  const wf = useMemo(() => {
    const bt = data?.backtest;
    const w = bt?.walk_forward;
    return {
      all: bt?.metrics,
      inSample: w?.in_sample?.metrics,
      holdout: w?.holdout?.metrics,
      inSampleRange: w?.in_sample ? `${w.in_sample.since} → ${w.in_sample.until}` : undefined,
      holdoutRange: w?.holdout ? `${w.holdout.since} → ${w.holdout.until}` : undefined,
    };
  }, [data?.backtest]);

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-5xl mx-auto">
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

        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <div className="text-xs text-gray-400">Status</div>
              <div className="mt-1 flex items-center gap-3">
                <div className="text-sm font-semibold">{data?.status || '…'}</div>
                <div className="text-xs text-gray-400">step: <span className="font-mono text-gray-200">{data?.step || '-'}</span></div>
                {selection ? (
                  <div className={`text-xs px-2 py-1 rounded-full border ${gateApproved ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-red-500/40 bg-red-500/10 text-red-200'}`}>
                    gate: {gateApproved ? 'approved' : 'blocked'}
                  </div>
                ) : null}
              </div>

              {data?.backtest ? (
                <div className="mt-2 text-xs text-gray-400">
                  {data.backtest.symbol} • {data.backtest.timeframe} • template <span className="font-mono text-gray-200">{data.backtest.template}</span>
                </div>
              ) : null}

              <div className="mt-2 text-[10px] text-gray-500">Polling a cada 2s</div>

              {data?.needs_user_confirm ? (
                <div className="mt-4 rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-3">
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
            </div>

            <div className="text-xs text-gray-400 space-y-2">
              {data?.backtest_job?.job_id ? (
                <div>
                  <div>
                    Job: <span className="font-mono text-gray-200">{data.backtest_job.job_id}</span>
                    {data.backtest_job.status ? (
                      <span className="ml-2">status: <span className="font-mono text-gray-200">{data.backtest_job.status}</span></span>
                    ) : null}
                  </div>
                  {data.backtest_job.progress ? (
                    <div className="mt-1">
                      step: <span className="font-mono text-gray-200">{data.backtest_job.progress.step}</span> ({data.backtest_job.progress.pct}%)
                      <div className="mt-1 h-2 w-full bg-white/10 rounded-full overflow-hidden">
                        <div className="h-2 bg-white/40" style={{ width: `${Math.min(100, Math.max(0, Number(data.backtest_job.progress.pct) || 0))}%` }} />
                      </div>
                    </div>
                  ) : null}
                  <a
                    className="inline-block mt-2 text-gray-300 hover:text-white underline underline-offset-4"
                    href={`${API_BASE_URL}/lab/jobs/${encodeURIComponent(data.backtest_job.job_id)}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    ver JSON do job
                  </a>
                </div>
              ) : null}

              {data?.budget ? (
                <details className="mt-2">
                  <summary className="cursor-pointer text-gray-300 hover:text-white">budget</summary>
                  <pre className="mt-2 text-[11px] text-gray-300 font-mono whitespace-pre-wrap">{JSON.stringify(data.budget, null, 2)}</pre>
                </details>
              ) : null}

              {data?.trace?.trace_url ? (
                <a
                  className="inline-block text-sm text-gray-300 hover:text-white underline underline-offset-4"
                  href={String(data.trace.trace_url)}
                  target="_blank"
                  rel="noreferrer"
                >
                  Abrir no Studio
                </a>
              ) : null}

              {data?.trace?.api_url ? (
                <div className="text-[11px] text-gray-500">
                  API: <span className="font-mono">{data.trace.api_url}</span>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        {data?.backtest ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div>
                <div className="text-sm font-semibold">Backtest</div>
                <div className="text-xs text-gray-500">CP6: walk-forward 70/30 (IS vs Holdout)</div>
              </div>
              <div className="text-xs text-gray-400">candles: <span className="font-mono text-gray-200">{data.backtest.candles ?? '-'}</span></div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard title="ALL" metrics={wf.all} />
              <MetricCard title="IN-SAMPLE" subtitle={wf.inSampleRange} metrics={wf.inSample} />
              <MetricCard title="HOLDOUT" subtitle={wf.holdoutRange} metrics={wf.holdout} />
            </div>

            <details className="mt-4">
              <summary className="cursor-pointer text-sm text-gray-300 hover:text-white">ver JSON completo</summary>
              <pre className="mt-3 text-xs text-gray-300 font-mono whitespace-pre-wrap">
                {JSON.stringify(data.backtest, null, 2)}
              </pre>
            </details>
          </div>
        ) : null}

        {data?.outputs ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div className="text-sm font-semibold">Decisão (personas + gate)</div>
              {selection ? (
                <div className={`text-xs px-2 py-1 rounded-full border ${gateApproved ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-red-500/40 bg-red-500/10 text-red-200'}`}>
                  {gateApproved ? 'APROVADO (gate)' : 'REJEITADO (gate)'}
                </div>
              ) : null}
            </div>

            {data.outputs.candidate_template_name ? (
              <div className="rounded-xl border border-white/10 bg-black/30 p-3 mb-3">
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

            {selection ? (
              <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                <div className="text-xs text-gray-400">Selection gate (CP10) — motivos</div>
                {selection.approved ? (
                  <div className="text-sm text-emerald-200">Passou no gate.</div>
                ) : (
                  <ul className="mt-2 list-disc pl-5 text-sm text-gray-200 space-y-1">
                    {(selection.reasons || []).map((r: string) => (
                      <li key={r} className="font-mono text-xs">{r}</li>
                    ))}
                  </ul>
                )}
              </div>
            ) : null}

            {!data.outputs.coordinator_summary && !data.outputs.dev_summary && !data.outputs.validator_verdict ? (
              <div className="text-sm text-gray-400">Aguardando execução das personas…</div>
            ) : null}
          </div>
        ) : null}

        {/* Conversa / Trace */}
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <div className="text-sm font-semibold">Conversa</div>
              <div className="text-xs text-gray-500">Upstream/Execução em formato de chat</div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setTab('chat')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${tab === 'chat' ? 'border-white/20 bg-white/10 text-white' : 'border-white/10 bg-black/20 text-gray-400'}`}
              >
                Chat (simplificado)
              </button>
              <button
                onClick={() => setTab('debug')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${tab === 'debug' ? 'border-white/20 bg-white/10 text-white' : 'border-white/10 bg-black/20 text-gray-400'}`}
              >
                Eventos (debug)
              </button>
            </div>
          </div>

          {tab === 'chat' ? (
            <RunChatView traceEvents={(data?.trace_events || []) as TraceEvent[]} />
          ) : (
            <div>
              <div className="text-xs text-gray-400 mb-3">
                {data?.trace_events?.length ? `${data.trace_events.length} eventos` : 'sem eventos'}
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
          )}
        </div>
      </div>
    </div>
  );
};

export default LabRunPage;
