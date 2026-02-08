import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '@/lib/apiBase';

type ParsedLabInputs = {
  symbol?: string;
  timeframe?: string;
};

const parseLabInputsFromPrompt = (text: string): ParsedLabInputs => {
  const raw = String(text || '');
  const symbolMatch = raw.match(/(?:^|\s)symbol\s*[:=]\s*([A-Za-z0-9._-]+\/[A-Za-z0-9._-]+)/i);
  const timeframeMatch = raw.match(/(?:^|\s)timeframe\s*[:=]\s*([0-9]+[A-Za-z]+)/i);

  return {
    symbol: symbolMatch?.[1]?.trim(),
    timeframe: timeframeMatch?.[1]?.trim(),
  };
};

const LabPage: React.FC = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [fullHistory, setFullHistory] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendQuestion, setBackendQuestion] = useState<string | null>(null);

  const run = async () => {
    setBusy(true);
    setError(null);
    setBackendQuestion(null);

    try {
      const parsed = parseLabInputsFromPrompt(message);
      const res = await fetch(`${API_BASE_URL}/lab/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: parsed.symbol,
          timeframe: parsed.timeframe,
          direction: 'long',
          constraints: { max_drawdown: 0.2, min_sharpe: 0.4 },
          objective: message.trim() || null,
          thinking: 'low',
          deep_backtest: true,
          full_history: fullHistory,
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(String(data?.detail || `HTTP ${res.status}`));
      }

      if (data?.status === 'needs_user_input') {
        setBackendQuestion(String(data?.question || 'Informe symbol e timeframe para iniciar o Lab.'));
        return;
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
          <div>
            <label className="text-xs text-gray-400">Mensagem para o Lab</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={5}
              className="mt-1 w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none"
              placeholder="Ex.: Quero rodar o lab com symbol=BTC/USDT timeframe=1h, foco em robustez e DD < 20%."
            />
            <div className="text-[10px] text-gray-500 mt-1">
              Use formato explícito no chat: <span className="font-mono">symbol=BTC/USDT timeframe=1h</span>
            </div>
          </div>

          <div className="flex items-center justify-between gap-3">
            <label className="text-xs text-gray-400">Período</label>
            <label className="flex items-center gap-2 text-xs text-gray-300">
              <input
                type="checkbox"
                checked={fullHistory}
                onChange={(e) => setFullHistory(e.target.checked)}
              />
              usar full history
            </label>
          </div>
          <div className="text-[10px] text-gray-500 -mt-2">
            Se marcado: since padrão = 2017-01-01 (pode demorar mais em intraday).
          </div>

          {backendQuestion ? (
            <div className="text-sm text-yellow-200 border border-yellow-500/30 bg-yellow-500/10 rounded-lg p-3">
              {backendQuestion}
            </div>
          ) : null}

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
            Inputs obrigatórios (symbol/timeframe) agora entram via chat.
          </div>
        </div>
      </div>
    </div>
  );
};

export default LabPage;
