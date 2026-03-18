import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from '@/lib/apiBase';

type GetResp = { id: string; markdown: string };
type ChangeResp = { change_id: string; artifact: string; markdown: string };

const OpenSpecDetailPage: React.FC = () => {
  const params = useParams<{ '*': string; id: string }>();
  // With route "/openspec/*" React Router puts the remainder in params["*"]
  const rawId = (params['*'] || params.id || '') as string;
  const specId = (rawId || '').trim();

  const isChangeArtifact = specId.startsWith('changes/');
  const changePath = isChangeArtifact ? specId.slice('changes/'.length) : '';
  const [changeId, changeArtifact] = isChangeArtifact ? changePath.split('/', 2) : ['', ''];

  type Resp = GetResp | ChangeResp;

  const { data, isLoading, error } = useQuery<Resp>({
    queryKey: ['openspec', 'get', isChangeArtifact ? 'change' : 'spec', specId],
    queryFn: async () => {
      if (isChangeArtifact) {
        const res = await fetch(`${API_BASE_URL}/openspec/changes/${encodeURIComponent(changeId)}/${encodeURIComponent(changeArtifact)}`);
        if (!res.ok) {
          const body = await res.text().catch(() => '');
          throw new Error(`Failed to load change artifact (${res.status}): ${body.slice(0, 200)}`);
        }
        return (await res.json()) as ChangeResp;
      }

      const res = await fetch(`${API_BASE_URL}/openspec/specs/${encodeURIComponent(specId)}`);
      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(`Failed to load spec (${res.status}): ${body.slice(0, 200)}`);
      }
      return (await res.json()) as GetResp;
    },
    enabled: Boolean(specId) && (!isChangeArtifact || (Boolean(changeId) && Boolean(changeArtifact))),
    refetchOnWindowFocus: false,
  });

  return (
    <div className="min-h-screen bg-black text-slate-900 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-xs text-slate-400">{isChangeArtifact ? 'Change' : 'Spec'}</div>
            <h1 className="text-xl font-bold font-mono">{specId}</h1>
          </div>
          <Link
            to="/openspec"
            className="text-sm text-slate-500 hover:text-slate-900 underline underline-offset-4"
          >
            voltar
          </Link>
        </div>

        {isLoading ? (
          <div className="text-slate-400">Carregando…</div>
        ) : error ? (
          <div className="text-red-400">Erro: {error instanceof Error ? error.message : 'falha ao carregar'}</div>
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <pre className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700 font-mono">
              {data?.markdown || ''}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenSpecDetailPage;
