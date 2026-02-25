import React, { useMemo, useState } from 'react';

export type TraceEvent = {
  ts_ms: number;
  type: string;
  data?: unknown;
};

type UpstreamSummary = {
  approved: boolean;
  missing: string[];
  question: string;
};

type ChatItem =
  | { kind: 'phase_marker'; phase: 'upstream' | 'execution'; ts_ms: number }
  | { kind: 'agent_message'; persona: string; text: string; ts_ms: number; tokens?: number; duration_ms?: number }
  | { kind: 'key_event'; label: string; ts_ms: number; details?: unknown }
  | { kind: 'debug_event'; ts_ms: number; type: string; data?: unknown };

const asObj = (v: unknown): Record<string, unknown> | null => {
  if (v && typeof v === 'object' && !Array.isArray(v)) return v as Record<string, unknown>;
  return null;
};

const getStr = (o: Record<string, unknown> | null, k: string): string => {
  const v = o?.[k];
  return typeof v === 'string' ? v : '';
};

const getNum = (o: Record<string, unknown> | null, k: string): number | undefined => {
  const v = o?.[k];
  return typeof v === 'number' ? v : undefined;
};

const getArrStr = (o: Record<string, unknown> | null, k: string): string[] => {
  const v = o?.[k];
  if (!Array.isArray(v)) return [];
  return v.filter((x) => typeof x === 'string') as string[];
};

const normalizePersona = (p: string) => {
  const s = String(p || '').trim();
  if (!s) return 'agent';
  if (s === 'validator') return 'trader';
  return s;
};

const personaUiLabel = (p: string) => {
  return p;
};

const bubbleClassForPersona = (who: string) => {
  if (who === 'dev_senior') return 'bg-blue-500/10 border-blue-500/20';
  if (who === 'trader') return 'bg-purple-500/10 border-purple-500/20';
  if (who === 'coordinator') return 'bg-emerald-500/10 border-emerald-500/20';
  return 'bg-black/30 border-white/10';
};

const fmtTs = (ts: number) => {
  try {
    return new Date(ts).toISOString();
  } catch {
    return String(ts);
  }
};

export const RunChatView: React.FC<{ traceEvents?: TraceEvent[] }> = ({ traceEvents }) => {
  const events = (traceEvents || []).slice().sort((a, b) => a.ts_ms - b.ts_ms);

  const personas = ['coordinator', 'dev_senior', 'trader', 'system'] as const;
  type Persona = (typeof personas)[number];

  const [selected, setSelected] = useState<Set<Persona>>(new Set(personas));
  const [showTechnical, setShowTechnical] = useState(false);

  const upstreamSummary: UpstreamSummary | null = useMemo(() => {
    const ev = events.find((e) => e.type === 'upstream_done');
    if (!ev) return null;
    const d = asObj(ev.data);
    return {
      approved: Boolean(d?.approved),
      missing: getArrStr(d, 'missing'),
      question: getStr(d, 'question'),
    };
  }, [traceEvents]);

  const items: ChatItem[] = useMemo(() => {
    const out: ChatItem[] = [];
    if (!events.length) return out;

    const technicalTypes = new Set([
      'persona_started',
      'iteration_started',
      'iteration_done',
      'seed_chosen',
      'param_tuned',
      'node_started',
      'node_done',
    ]);

    const keyTypes = new Set(['backtest_done', 'final_decision', 'upstream_done']);

    let sawUpstream = false;
    let sawExecution = false;
    let upstreamDoneIdx = -1;

    for (let i = 0; i < events.length; i++) {
      if (events[i].type === 'upstream_done') {
        upstreamDoneIdx = i;
        break;
      }
    }

    for (let i = 0; i < events.length; i++) {
      const ev = events[i];

      if (!sawUpstream && (ev.type === 'upstream_started' || ev.type === 'upstream_done')) {
        out.push({ kind: 'phase_marker', phase: 'upstream', ts_ms: ev.ts_ms });
        sawUpstream = true;
      }

      const d = asObj(ev.data);

      const isPersonaDone = ev.type === 'persona_done' && Boolean(getStr(d, 'persona'));
      const isPersonaStarted = ev.type === 'persona_started' && Boolean(getStr(d, 'persona'));

      // Heuristic: execution begins when we see the first persona event after upstream_done (or if there is no upstream).
      if (!sawExecution) {
        const upstreamDoneSeen = upstreamDoneIdx >= 0 ? i > upstreamDoneIdx : true;
        if (upstreamDoneSeen && (isPersonaStarted || isPersonaDone)) {
          out.push({ kind: 'phase_marker', phase: 'execution', ts_ms: ev.ts_ms });
          sawExecution = true;
        }
      }

      if (isPersonaDone) {
        const persona = normalizePersona(getStr(d, 'persona'));
        const text = getStr(d, 'text');
        const tokens = getNum(d, 'tokens');
        const duration_ms = getNum(d, 'duration_ms');
        out.push({ kind: 'agent_message', persona, text, ts_ms: ev.ts_ms, tokens, duration_ms });
        continue;
      }

      if (keyTypes.has(ev.type)) {
        let label = ev.type;
        if (ev.type === 'backtest_done') label = 'backtest_done';
        if (ev.type === 'final_decision') label = 'final_decision';
        if (ev.type === 'upstream_done') label = 'upstream_done';
        out.push({ kind: 'key_event', label, ts_ms: ev.ts_ms, details: ev.data });
        continue;
      }

      if (technicalTypes.has(ev.type) || showTechnical) {
        out.push({ kind: 'debug_event', ts_ms: ev.ts_ms, type: ev.type, data: ev.data });
      }
    }

    return out;
  }, [traceEvents, showTechnical]);

  const visibleItems = useMemo(() => {
    const allowed = selected;
    return items.filter((it) => {
      if (it.kind === 'agent_message') {
        if (it.persona === 'coordinator' && !allowed.has('coordinator')) return false;
        if (it.persona === 'dev_senior' && !allowed.has('dev_senior')) return false;
        if (it.persona === 'trader' && !allowed.has('trader')) return false;
        // other personas treated as system
        if (!['coordinator', 'dev_senior', 'trader'].includes(it.persona) && !allowed.has('system')) return false;
      }
      if (it.kind === 'key_event' || it.kind === 'debug_event') {
        // key/debug are “system-ish”
        if (!allowed.has('system')) return false;
        if (it.kind === 'debug_event' && !showTechnical) return false;
      }
      return true;
    });
  }, [items, selected, showTechnical]);

  const togglePersona = (p: Persona) => {
    setSelected((prev) => {
      const n = new Set(prev);
      if (n.has(p)) n.delete(p);
      else n.add(p);
      return n;
    });
  };

  if (!events.length) {
    return <div className="text-sm text-gray-400">Sem conversa disponível (trace vazio).</div>;
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
        <div className="text-xs text-gray-400">
          mensagens: <span className="font-mono text-gray-200">{items.filter((i) => i.kind === 'agent_message').length}</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {personas.map((p) => (
            <button
              key={p}
              onClick={() => togglePersona(p)}
              className={`px-2 py-1 rounded-full border text-[11px] font-mono ${selected.has(p) ? 'border-white/20 bg-white/10 text-white' : 'border-white/10 bg-black/20 text-gray-500'}`}
            >
              {personaUiLabel(p)}
            </button>
          ))}

          <button
            onClick={() => setShowTechnical((v) => !v)}
            className={`ml-2 px-2 py-1 rounded-full border text-[11px] ${showTechnical ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-200' : 'border-white/10 bg-black/20 text-gray-400'}`}
          >
            {showTechnical ? 'Ocultar eventos técnicos' : 'Mostrar eventos técnicos'}
          </button>
        </div>
      </div>

      {upstreamSummary ? (
        <div className="mb-4 rounded-2xl border border-white/10 bg-black/30 p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="text-xs text-gray-400 font-semibold">Upstream</div>
            <div className={`text-xs px-2 py-1 rounded-full border ${upstreamSummary.approved ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-red-500/40 bg-red-500/10 text-red-200'}`}>
              {upstreamSummary.approved ? 'aprovado' : 'bloqueado'}
            </div>
          </div>

          {!upstreamSummary.approved ? (
            <div className="mt-3">
              {upstreamSummary.question ? (
                <div className="text-sm text-gray-200 whitespace-pre-wrap">{upstreamSummary.question}</div>
              ) : null}
              {upstreamSummary.missing.length ? (
                <div className="mt-2 text-xs text-gray-400">
                  faltando: <span className="font-mono text-gray-200">{upstreamSummary.missing.join(', ')}</span>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="space-y-3">
        {visibleItems.map((it, idx) => {
          if (it.kind === 'phase_marker') {
            return (
              <div key={`${it.kind}-${it.ts_ms}-${idx}`} className="text-center">
                <span className="inline-block px-3 py-1 rounded-full text-[11px] font-semibold border border-white/10 bg-white/5 text-gray-300">
                  {it.phase === 'upstream' ? 'Upstream' : 'Execução'}
                </span>
              </div>
            );
          }

          if (it.kind === 'agent_message') {
            const who = it.persona;
            const bubbleClass = bubbleClassForPersona(who);
            return (
              <div key={`${it.kind}-${it.ts_ms}-${idx}`} className={`rounded-2xl border p-4 ${bubbleClass}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="text-xs text-gray-300 font-mono">{personaUiLabel(who)}</div>
                  <div className="text-[10px] text-gray-500 font-mono">{fmtTs(it.ts_ms)}</div>
                </div>
                {(it.tokens != null || it.duration_ms != null) ? (
                  <div className="mt-1 text-[10px] text-gray-500 font-mono">
                    {it.duration_ms != null ? `dur: ${it.duration_ms}ms` : ''}{it.duration_ms != null && it.tokens != null ? ' • ' : ''}{it.tokens != null ? `tokens: ${it.tokens}` : ''}
                  </div>
                ) : null}
                <pre className="mt-2 text-xs text-gray-100 whitespace-pre-wrap font-mono">{it.text || ''}</pre>
              </div>
            );
          }

          if (it.kind === 'key_event') {
            return (
              <div key={`${it.kind}-${it.ts_ms}-${idx}`} className="rounded-2xl border border-white/10 bg-black/30 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="text-xs text-gray-300 font-mono">{it.label}</div>
                  <div className="text-[10px] text-gray-500 font-mono">{fmtTs(it.ts_ms)}</div>
                </div>
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs text-gray-400 hover:text-white">detalhes</summary>
                  <pre className="mt-2 text-[11px] text-gray-300 whitespace-pre-wrap font-mono">{JSON.stringify(it.details || {}, null, 2)}</pre>
                </details>
              </div>
            );
          }

          // debug_event
          return (
            <div key={`${it.kind}-${it.ts_ms}-${idx}`} className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="text-[11px] text-gray-400 font-mono">{it.type}</div>
                <div className="text-[10px] text-gray-600 font-mono">{fmtTs(it.ts_ms)}</div>
              </div>
              <details className="mt-1">
                <summary className="cursor-pointer text-[11px] text-gray-500 hover:text-white">data</summary>
                <pre className="mt-2 text-[11px] text-gray-300 whitespace-pre-wrap font-mono">{JSON.stringify(it.data || {}, null, 2)}</pre>
              </details>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RunChatView;
