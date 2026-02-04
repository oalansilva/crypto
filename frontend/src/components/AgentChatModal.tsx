import React, { useEffect, useMemo, useRef, useState } from 'react';
import { X, Send, Bot, User, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '@/lib/apiBase';

export interface AgentChatFavorite {
  id: number;
  name: string;
  symbol: string;
  timeframe: string;
  strategy_name: string;
}

type ThinkingLevel = 'off' | 'minimal' | 'low' | 'medium' | 'high';

type ChatMsg = {
  role: 'user' | 'agent';
  text: string;
  ts: number;
};

export const AgentChatModal: React.FC<{
  open: boolean;
  onClose: () => void;
  favorite: AgentChatFavorite | null;
}> = ({ open, onClose, favorite }) => {
  const [conversationId, setConversationId] = useState<string>('');
  const [thinking, setThinking] = useState<ThinkingLevel>('low');
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement | null>(null);

  const title = useMemo(() => {
    if (!favorite) return 'Agente';
    return `Agente • ${favorite.symbol} ${favorite.timeframe} • ${favorite.strategy_name}`;
  }, [favorite]);

  useEffect(() => {
    if (!open) return;
    if (!favorite) return;

    // default stable conversation per favorite
    setConversationId((prev) => prev || `fav-${favorite.id}`);
    setMessages([]);
    setInput('');
    setError(null);
    setBusy(false);
  }, [open, favorite?.id]);

  useEffect(() => {
    if (!open) return;
    // keep scrolled to bottom
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, open]);

  if (!open || !favorite) return null;

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;

    setError(null);
    setBusy(true);
    setInput('');
    const ts = Date.now();
    setMessages((m) => [...m, { role: 'user', text, ts }]);

    try {
      const res = await fetch(`${API_BASE_URL}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          favorite_id: favorite.id,
          message: text,
          conversation_id: conversationId || `fav-${favorite.id}`,
          thinking,
        }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const detail = (data && (data.detail || data.error)) ? String(data.detail || data.error) : `HTTP ${res.status}`;
        throw new Error(detail);
      }

      const reply = String(data.reply || '').trim();
      setConversationId(String(data.conversation_id || conversationId || `fav-${favorite.id}`));
      setMessages((m) => [...m, { role: 'agent', text: reply || '(sem resposta)', ts: Date.now() }]);
    } catch (e: any) {
      setError(e?.message || 'Falha ao chamar o agente');
    } finally {
      setBusy(false);
    }
  };

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-6 bg-black/90">
      <div className="bg-black border-2 border-white/10 w-full max-w-4xl h-[80vh] flex flex-col shadow-2xl relative rounded-xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
          <div>
            <div className="text-white font-bold">{title}</div>
            <div className="text-xs text-gray-400 truncate max-w-[70vw]">{favorite.name}</div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 text-gray-300" title="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-3 border-b border-white/10 bg-black flex items-center gap-3">
          <label className="text-xs text-gray-400">Thinking</label>
          <select
            value={thinking}
            onChange={(e) => setThinking(e.target.value as ThinkingLevel)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-gray-200 outline-none hover:bg-white/10"
          >
            <option className="bg-gray-900" value="off">off</option>
            <option className="bg-gray-900" value="minimal">minimal</option>
            <option className="bg-gray-900" value="low">low</option>
            <option className="bg-gray-900" value="medium">medium</option>
            <option className="bg-gray-900" value="high">high</option>
          </select>

          <div className="ml-auto text-xs text-gray-500">
            conversation_id: <span className="text-gray-300 font-mono">{conversationId || `fav-${favorite.id}`}</span>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-3">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-sm">
              Pergunte coisas como: “Resuma em 3 bullets”, “Por que essa estratégia funciona em bull?”, “Quais próximos testes?”
            </div>
          ) : null}

          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-2 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'agent' && (
                <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-purple-300" />
                </div>
              )}

              <div className={`max-w-[75%] rounded-xl px-4 py-3 text-sm border ${m.role === 'user'
                ? 'bg-blue-600/20 border-blue-500/30 text-gray-100'
                : 'bg-white/5 border-white/10 text-gray-100'
                }`}>
                <div className="whitespace-pre-wrap leading-relaxed">{m.text}</div>
                <div className="mt-1 text-[10px] text-gray-500">{new Date(m.ts).toLocaleString()}</div>
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                  <User className="w-4 h-4 text-blue-300" />
                </div>
              )}
            </div>
          ))}

          {busy && (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Pensando…
            </div>
          )}

          {error && (
            <div className="text-sm text-red-400 border border-red-500/30 bg-red-500/10 rounded-lg p-3">
              Erro: {error}
              {String(error).includes('disabled') || String(error).includes('403') ? (
                <div className="mt-1 text-xs text-gray-400">Dica: habilite no backend com <span className="font-mono">AGENT_CHAT_ENABLED=1</span>.</div>
              ) : null}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-white/10 bg-black">
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Digite sua pergunta…"
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm text-white outline-none placeholder-gray-600 focus:border-blue-500"
              disabled={busy}
            />
            <button
              onClick={send}
              disabled={busy || input.trim().length === 0}
              className="px-4 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-500 hover:to-purple-500 transition-all flex items-center gap-2"
              title="Send"
            >
              <Send className="w-4 h-4" />
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
