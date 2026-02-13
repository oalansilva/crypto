import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { API_BASE_URL } from '@/lib/apiBase';
import RunChatView, { type TraceEvent } from '@/components/lab/RunChatView';
import LogPanel from '@/components/lab/LogPanel';
import { useLogSSE } from '@/hooks/useLogSSE';

// TraceEvent type moved to RunChatView

type RunStatus = {
  run_id: string;
  status: string;
  step?: string | null;
  phase?: string | null;
  created_at_ms: number;
  updated_at_ms: number;
  trace: { viewer_url: string; api_url: string; enabled?: boolean; provider?: string; thread_id?: string; trace_id?: string; trace_url?: string | null };
  trace_events?: TraceEvent[];
  backtest_job?: any;
  backtest?: any;
  budget?: any;
  outputs?: any;
  upstream_contract?: any;
  upstream?: {
    messages?: Array<{ role?: string; text?: string; ts_ms?: number }>;
    pending_question?: string;
    strategy_draft?: any;
    ready_for_user_review?: boolean;
    user_approved?: boolean;
    user_feedback?: string;
  };
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
  const [sendingUpstream, setSendingUpstream] = useState(false);
  const [upstreamInput, setUpstreamInput] = useState('');
  const [tab, setTab] = useState<'chat' | 'debug'>('chat');
  const [draftFeedback, setDraftFeedback] = useState('');
  const [sendingDraftFeedback, setSendingDraftFeedback] = useState(false);
  const [approvingDraft, setApprovingDraft] = useState(false);
  const [logsOpen, setLogsOpen] = useState(false);
  const [logStep, setLogStep] = useState('');

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

  const sendUpstreamMessage = async () => {
    if (!id) return;
    const text = upstreamInput.trim();
    if (!text) return;

    setSendingUpstream(true);
    try {
      const res = await fetch(`${API_BASE_URL}/lab/runs/${encodeURIComponent(id)}/upstream/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(String(j?.detail || `HTTP ${res.status}`));
      setUpstreamInput('');
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'Falha ao enviar mensagem upstream');
    } finally {
      setSendingUpstream(false);
    }
  };

  const sendDraftFeedback = async () => {
    if (!id) return;
    const text = draftFeedback.trim();
    if (!text) return;

    setSendingDraftFeedback(true);
    try {
      const res = await fetch(`${API_BASE_URL}/lab/runs/${encodeURIComponent(id)}/upstream/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(String(j?.detail || `HTTP ${res.status}`));
      setDraftFeedback('');
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'Falha ao enviar feedback');
    } finally {
      setSendingDraftFeedback(false);
    }
  };

  const approveDraftAndRun = async () => {
    if (!id) return;
    setApprovingDraft(true);
    try {
      const res = await fetch(`${API_BASE_URL}/lab/runs/${encodeURIComponent(id)}/upstream/approve`, { method: 'POST' });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(String(j?.detail || `HTTP ${res.status}`));
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'Falha ao aprovar e iniciar');
    } finally {
      setApprovingDraft(false);
    }
  };

  const selection = data?.outputs?.selection;
  const gateApproved = selection?.approved === true;
  const upstreamApproved = data?.upstream_contract?.approved === true;
  const upstreamMessages = Array.isArray(data?.upstream?.messages) ? data?.upstream?.messages : [];
  const upstreamPendingQuestion = String(data?.upstream?.pending_question || '');
  const inUpstreamPhase = (data?.phase || 'upstream') === 'upstream';
  const readyForReview = Boolean((data?.upstream as any)?.ready_for_user_review);
  const strategyDraft = (data?.upstream as any)?.strategy_draft;

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
  const comboOptimization = data?.backtest?.combo_optimization;
  const comboStatus = String(comboOptimization?.status || '').toLowerCase();
  const comboTemplateName = String(comboOptimization?.template_name || '');
  const comboAppliedAt = typeof comboOptimization?.applied_at_ms === 'number'
    ? new Date(comboOptimization.applied_at_ms).toISOString()
    : '-';
  const comboBestParameters = comboOptimization?.best_parameters || {};
  const comboBestMetrics = comboOptimization?.best_metrics || {};
  const comboLimitsSnapshot = comboOptimization?.limits_snapshot || {};
  const comboStages = comboOptimization?.stages || [];
  const comboError = String(comboOptimization?.error || '');
  const backtestIsPostCombo = comboStatus === 'completed';
  const canOpenLogs = String(data?.status || '').toLowerCase() === 'running' && Boolean(data?.step);

  useEffect(() => {
    if (!logsOpen) return;
    if (String(data?.status || '').toLowerCase() !== 'running') return;
    const currentStep = String(data?.step || '').trim();
    if (!currentStep) return;
    if (currentStep !== logStep) setLogStep(currentStep);
  }, [logsOpen, data?.status, data?.step, logStep]);

  const {
    logs: liveLogs,
    connectionState: logConnectionState,
    isConnected: logsConnected,
    error: logError,
    reconnect: reconnectLogs,
  } = useLogSSE({
    runId: id,
    step: logStep || (data?.step ? String(data.step) : ''),
    enabled: logsOpen && Boolean(id),
  });

  const logConnectionLabel = (() => {
    if (logConnectionState === 'connected') return 'conectado';
    if (logConnectionState === 'connecting') return 'conectando';
    if (logConnectionState === 'error') return 'erro';
    return 'fechado';
  })();

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
                <div className="text-xs text-gray-400">phase: <span className="font-mono text-gray-200">{data?.phase || '-'}</span></div>
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

              <div className="mt-3 flex flex-wrap items-center gap-2">
                {canOpenLogs ? (
                  <button
                    type="button"
                    onClick={() => {
                      const currentStep = String(data?.step || '').trim();
                      if (!logsOpen && currentStep) setLogStep(currentStep);
                      setLogsOpen((prev) => !prev);
                    }}
                    className="px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-xs text-gray-200"
                  >
                    {logsOpen ? 'Ocultar Logs' : 'Ver Logs'}
                  </button>
                ) : null}
                {logsOpen ? (
                  <div className={`text-[11px] px-2 py-1 rounded-full border ${
                    logConnectionState === 'connected'
                      ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
                      : logConnectionState === 'error'
                        ? 'border-red-500/40 bg-red-500/10 text-red-200'
                        : 'border-yellow-500/40 bg-yellow-500/10 text-yellow-200'
                  }`}>
                    logs: {logConnectionLabel}
                  </div>
                ) : null}
              </div>

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

        {logsOpen ? (
          <div className="mt-4">
            <LogPanel
              logs={liveLogs}
              isLoading={logConnectionState === 'connecting' && liveLogs.length === 0}
              isConnected={logsConnected}
              error={logError?.message || null}
              onRetry={reconnectLogs}
              onClose={() => setLogsOpen(false)}
            />
          </div>
        ) : null}

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
          <details open={inUpstreamPhase}>
            <summary className="cursor-pointer flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">Upstream (chat)</div>
                <div className="text-xs text-gray-500">Humano ↔ Trader</div>
              </div>
              <div className={`text-xs px-2 py-1 rounded-full border ${upstreamApproved ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-yellow-500/40 bg-yellow-500/10 text-yellow-200'}`}>
                {upstreamApproved ? 'aprovado' : 'aguardando input'}
              </div>
            </summary>

            <div className="mt-4 space-y-3">
              {upstreamMessages.length ? (
                <div className="space-y-2">
                  {upstreamMessages.map((msg, idx) => {
                    const role = String(msg?.role || '').toLowerCase();
                    const text = String(msg?.text || '');
                    const isTrader = role === 'trader' || role === 'validator';
                    const ts = Number(msg?.ts_ms || 0);
                    return (
                      <div
                        key={`${ts}-${idx}`}
                        className={`rounded-xl border p-3 ${isTrader ? 'border-purple-500/20 bg-purple-500/10' : 'border-blue-500/20 bg-blue-500/10'}`}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-xs font-mono text-gray-200">{isTrader ? 'Trader' : 'Humano'}</div>
                          <div className="text-[10px] text-gray-500 font-mono">
                            {ts ? new Date(ts).toISOString() : '-'}
                          </div>
                        </div>
                        <div className="mt-1 text-sm text-gray-100 whitespace-pre-wrap">{text}</div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-sm text-gray-400">Sem mensagens no upstream ainda.</div>
              )}

              {inUpstreamPhase && !upstreamApproved ? (
                <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-3">
                  <div className="text-xs text-yellow-100/80">Pergunta atual do Trader</div>
                  <div className="mt-1 text-sm text-yellow-100">{upstreamPendingQuestion || 'Envie uma mensagem para continuar.'}</div>
                </div>
              ) : null}

              {inUpstreamPhase && !upstreamApproved ? (
                <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <textarea
                    value={upstreamInput}
                    onChange={(e) => setUpstreamInput(e.target.value)}
                    rows={3}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
                    placeholder="Responda ao Trader..."
                  />
                  <div className="mt-3 flex justify-end">
                    <button
                      onClick={sendUpstreamMessage}
                      disabled={sendingUpstream || !upstreamInput.trim()}
                      className="px-4 py-2 rounded-lg bg-white text-black text-sm font-semibold disabled:opacity-50"
                    >
                      {sendingUpstream ? 'Enviando…' : 'Enviar'}
                    </button>
                  </div>
                </div>
              ) : null}

              {inUpstreamPhase && upstreamApproved && !readyForReview ? (
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3">
                  <div className="text-sm text-emerald-200 font-semibold">Contrato upstream aprovado</div>
                  <div className="mt-1 text-xs text-emerald-100/90">
                    inputs: <span className="font-mono">{JSON.stringify(data?.upstream_contract?.inputs || {}, null, 0)}</span>
                  </div>
                  <div className="mt-2 text-xs text-emerald-100/80">
                    Aguardando o Trader gerar a proposta da estratégia…
                  </div>
                </div>
              ) : null}

              {inUpstreamPhase && upstreamApproved && readyForReview ? (
                <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold">Proposta do Trader</div>
                      <div className="text-xs text-gray-500">Revise e aprove antes de iniciar a execução</div>
                    </div>
                    <div className="text-[10px] text-gray-500 font-mono">draft v{String(strategyDraft?.version ?? 1)}</div>
                  </div>

                  <div className="mt-3">
                    <div className="text-xs text-gray-400">one-liner</div>
                    <div className="text-sm text-gray-100 whitespace-pre-wrap">{String(strategyDraft?.one_liner || '') || '-'}</div>
                  </div>

                  <div className="mt-3">
                    <div className="text-xs text-gray-400">rationale</div>
                    <div className="text-sm text-gray-100 whitespace-pre-wrap">{String(strategyDraft?.rationale || '') || '-'}</div>
                  </div>

                  <div className="mt-3">
                    <div className="text-xs text-gray-400">indicators</div>
                    <pre className="mt-1 text-[11px] text-gray-200 whitespace-pre-wrap font-mono">{JSON.stringify(strategyDraft?.indicators || [], null, 2)}</pre>
                  </div>

                  <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                      <div className="text-xs text-gray-400">entry</div>
                      <div className="mt-1 text-sm text-gray-100 whitespace-pre-wrap">{String(strategyDraft?.entry_idea || '') || '-'}</div>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                      <div className="text-xs text-gray-400">exit</div>
                      <div className="mt-1 text-sm text-gray-100 whitespace-pre-wrap">{String(strategyDraft?.exit_idea || '') || '-'}</div>
                    </div>
                  </div>

                  <div className="mt-3 rounded-xl border border-white/10 bg-black/20 p-3">
                    <div className="text-xs text-gray-400">risk plan</div>
                    <div className="mt-1 text-sm text-gray-100 whitespace-pre-wrap">{String(strategyDraft?.risk_plan || '') || '-'}</div>
                  </div>

                  <details className="mt-3">
                    <summary className="cursor-pointer text-xs text-gray-300 hover:text-white">ver JSON completo</summary>
                    <pre className="mt-2 text-[11px] text-gray-200 whitespace-pre-wrap font-mono">{JSON.stringify(strategyDraft || {}, null, 2)}</pre>
                  </details>

                  <div className="mt-4 flex flex-col gap-3">
                    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                      <div className="text-xs text-gray-400">Quero ajustar</div>
                      <textarea
                        value={draftFeedback}
                        onChange={(e) => setDraftFeedback(e.target.value)}
                        rows={3}
                        className="mt-2 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
                        placeholder="Ex.: quero RSI + filtro de tendência, e reduzir número de operações"
                      />
                      <div className="mt-2 flex justify-end">
                        <button
                          onClick={sendDraftFeedback}
                          disabled={sendingDraftFeedback || !draftFeedback.trim()}
                          className="px-4 py-2 rounded-lg bg-white text-black text-sm font-semibold disabled:opacity-50"
                        >
                          {sendingDraftFeedback ? 'Enviando…' : 'Enviar feedback'}
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={approveDraftAndRun}
                      disabled={approvingDraft}
                      className="px-4 py-2 rounded-lg bg-emerald-500 text-black text-sm font-bold disabled:opacity-50"
                    >
                      {approvingDraft ? 'Iniciando…' : 'Aprovar e iniciar execução'}
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          </details>
        </div>

        {data?.backtest ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div>
                <div className="text-sm font-semibold">Backtest</div>
                <div className="text-xs text-gray-500">
                  {backtestIsPostCombo
                    ? 'Resultado final pós-Combo para validação do Trader • CP6: walk-forward 70/30 (IS vs Holdout)'
                    : 'CP6: walk-forward 70/30 (IS vs Holdout)'}
                </div>
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

        {comboOptimization ? (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">Combo Optimization</div>
                <div className="text-xs text-gray-500">Parâmetros aplicados automaticamente antes do backtest final.</div>
              </div>
              <div className={`text-xs px-2 py-1 rounded-full border ${
                comboStatus === 'completed'
                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
                  : comboStatus === 'failed'
                    ? 'border-red-500/40 bg-red-500/10 text-red-200'
                    : 'border-yellow-500/40 bg-yellow-500/10 text-yellow-200'
              }`}>
                status: {comboStatus || '-'}
              </div>
            </div>

            <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                <div className="text-gray-500">template</div>
                <div className="mt-1 text-gray-100 font-mono break-all">{comboTemplateName || '-'}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                <div className="text-gray-500">applied_at</div>
                <div className="mt-1 text-gray-100 font-mono">{comboAppliedAt}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                <div className="text-gray-500">final context</div>
                <div className="mt-1 text-gray-100">
                  {comboStatus === 'completed'
                    ? 'Backtest final pós-Combo (sem etapa manual de aprovação de parâmetros).'
                    : 'Etapa Combo não concluída; revisar estado abaixo.'}
                </div>
              </div>
            </div>

            {comboStatus === 'failed' ? (
              <div className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                Falha na otimização do Combo: {comboError || 'erro não informado'}
              </div>
            ) : null}

            <details className="mt-3">
              <summary className="cursor-pointer text-sm text-gray-300 hover:text-white">ver detalhes (parâmetros, métricas, limites)</summary>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <div className="text-xs text-gray-400 mb-2">Best parameters aplicados</div>
                  {Object.keys(comboBestParameters).length ? (
                    <div className="space-y-1">
                      {Object.entries(comboBestParameters).map(([key, value]) => (
                        <div key={key} className="flex items-start justify-between gap-3 text-xs">
                          <span className="text-gray-400 font-mono">{key}</span>
                          <span className="text-gray-100 font-mono break-all">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-500">Sem parâmetros aplicados.</div>
                  )}
                </div>
                <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <div className="text-xs text-gray-400 mb-2">Best metrics</div>
                  <pre className="text-[11px] text-gray-200 whitespace-pre-wrap font-mono">
                    {JSON.stringify(comboBestMetrics, null, 2)}
                  </pre>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <div className="text-xs text-gray-400 mb-2">Limits snapshot</div>
                  <pre className="text-[11px] text-gray-200 whitespace-pre-wrap font-mono">
                    {JSON.stringify(comboLimitsSnapshot, null, 2)}
                  </pre>
                </div>
                <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                  <div className="text-xs text-gray-400 mb-2">Stages</div>
                  <pre className="text-[11px] text-gray-200 whitespace-pre-wrap font-mono">
                    {JSON.stringify(comboStages, null, 2)}
                  </pre>
                </div>
              </div>
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
