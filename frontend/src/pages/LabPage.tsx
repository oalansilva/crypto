import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '@/lib/apiBase';

const LabPage: React.FC = () => {
  const navigate = useNavigate();
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1d');
  const [baseTemplate, setBaseTemplate] = useState('multi_ma_crossover');

  const [symbols, setSymbols] = useState<string[]>([]);
  const [timeframes, setTimeframes] = useState<string[]>([]);
  const [templates, setTemplates] = useState<string[]>([]);
  const [loadingMeta, setLoadingMeta] = useState(false);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      setLoadingMeta(true);
      try {
        const [symRes, tfRes, tplRes] = await Promise.all([
          fetch(`${API_BASE_URL}/exchanges/binance/symbols`),
          fetch(`${API_BASE_URL}/exchanges/binance/timeframes`),
          fetch(`${API_BASE_URL}/combos/templates`),
        ]);
        const symJson = await symRes.json().catch(() => ({} as any));
        const tfJson = await tfRes.json().catch(() => ({} as any));
        const tplJson = await tplRes.json().catch(() => ({} as any));
        if (!alive) return;
        if (symRes.ok) setSymbols(Array.isArray(symJson.symbols) ? symJson.symbols : []);
        if (tfRes.ok) setTimeframes(Array.isArray(tfJson.timeframes) ? tfJson.timeframes : []);
        if (tplRes.ok) {
          const prebuilt = (tplJson?.prebuilt || []).map((t: any) => t?.name).filter(Boolean);
          const examples = (tplJson?.examples || []).map((t: any) => t?.name).filter(Boolean);
          const custom = (tplJson?.custom || []).map((t: any) => t?.name).filter(Boolean);
          const all = Array.from(new Set<string>([...prebuilt, ...examples, ...custom]));
          all.sort();
          setTemplates(all);
        }
      } catch {
        // ignore; user can still type manually
      } finally {
        if (alive) setLoadingMeta(false);
      }
    };
    load();
    return () => {
      alive = false;
    };
  }, []);

  const timeframeOptions = useMemo(() => {
    return timeframes.length ? timeframes : ['15m', '1h', '4h', '1d', '1w'];
  }, [timeframes]);
  const [objective, setObjective] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/lab/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          timeframe,
          base_template: baseTemplate,
          direction: 'long',
          constraints: { max_drawdown: 0.2, min_sharpe: 0.4 },
          objective: objective || null,
          thinking: 'low',
          deep_backtest: true,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(String(data?.detail || `HTTP ${res.status}`));
      }
      const runId = String(data.run_id || '').trim();
      if (!runId) throw new Error('run_id vazio');
      navigate(`/lab/runs/${runId}`);
    } catch (e: any) {
      setError(e?.message || 'Falha ao iniciar run');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Strategy Lab</h1>
            <div className="text-xs text-gray-500 mt-1">
              Spec v2: <a href="/openspec/07-strategy-lab-langgraph-v2" className="underline underline-offset-4 text-gray-300 hover:text-white">openspec/07-strategy-lab-langgraph-v2</a>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <a href="/openspec/07-strategy-lab-langgraph-v2" className="text-sm text-gray-300 hover:text-white underline underline-offset-4">spec v2</a>
            <a href="/favorites" className="text-sm text-gray-300 hover:text-white underline underline-offset-4">voltar</a>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-gray-400">Symbol (Binance)</label>
              <input
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                list="lab-binance-symbols"
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
              />
              <datalist id="lab-binance-symbols">
                {symbols.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>
              <div className="text-[10px] text-gray-500 mt-1">
                {loadingMeta ? 'carregando símbolos…' : symbols.length ? `${symbols.length} símbolos` : 'digite manualmente'}
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-400">Timeframe</label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
              >
                {timeframeOptions.map((tf) => (
                  <option key={tf} value={tf} className="bg-gray-900">
                    {tf}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400">Template base</label>
              {templates.length ? (
                <select
                  value={baseTemplate}
                  onChange={(e) => setBaseTemplate(e.target.value)}
                  className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
                >
                  {templates.map((t) => (
                    <option key={t} value={t} className="bg-gray-900">
                      {t}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  value={baseTemplate}
                  onChange={(e) => setBaseTemplate(e.target.value)}
                  className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
                />
              )}
              <div className="text-[10px] text-gray-500 mt-1">
                {loadingMeta ? 'carregando templates…' : templates.length ? `${templates.length} templates` : 'digite manualmente'}
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-400">Objetivo (opcional)</label>
            <textarea value={objective} onChange={(e) => setObjective(e.target.value)} rows={3} className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none" placeholder="Ex.: melhorar robustez em bear mantendo DD < 20%" />
          </div>

          {error ? (
            <div className="text-sm text-red-400 border border-red-500/30 bg-red-500/10 rounded-lg p-3">Erro: {error}</div>
          ) : null}

          <div className="flex items-center justify-end gap-3">
            <button
              onClick={run}
              disabled={busy}
              className="px-5 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-bold disabled:opacity-50"
            >
              {busy ? 'Rodando…' : 'Run Lab'}
            </button>
          </div>

          <div className="text-xs text-gray-500">
            CP1: apenas cria run_id + polling. Sem LangGraph ainda.
          </div>
        </div>
      </div>
    </div>
  );
};

export default LabPage;
