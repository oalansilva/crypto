import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from '@/lib/apiBase';

type SpecItem = {
  id: string;
  path: string;
  title?: string | null;
  status?: string | null;
  updated_at?: string | null;
};

type ListResp = { items: SpecItem[] };

const OpenSpecListPage: React.FC = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['openspec', 'list'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/openspec/specs`);
      if (!res.ok) throw new Error(`Failed to load specs (${res.status})`);
      return (await res.json()) as ListResp;
    },
    refetchOnWindowFocus: false,
  });

  const items = data?.items || [];

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">OpenSpec</h1>
          <a
            href="/favorites"
            className="text-sm text-gray-300 hover:text-white underline underline-offset-4"
          >
            voltar
          </a>
        </div>

        {isLoading ? (
          <div className="text-gray-400">Carregando…</div>
        ) : error ? (
          <div className="text-red-400">Erro: {(error as any)?.message || 'falha ao carregar'}</div>
        ) : items.length === 0 ? (
          <div className="text-gray-400">Nenhum spec encontrado.</div>
        ) : (
          <div className="space-y-3">
            {items.map((it) => (
              <Link
                key={it.id}
                to={`/openspec/${it.id}`}
                className="block rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors p-4"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="font-semibold truncate">
                      {it.title || it.id}
                    </div>
                    <div className="text-xs text-gray-400 font-mono truncate">
                      {it.path}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 text-right whitespace-nowrap">
                    {it.status ? <div className="uppercase">{it.status}</div> : null}
                    {it.updated_at ? <div>{it.updated_at}</div> : null}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenSpecListPage;
