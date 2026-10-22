import { authFetch } from './authFetch'
import { API_BASE_URL } from './apiBase'
import type {
  AssetClass,
  CatalogAsset,
  ClassFilter,
  CountsMap,
  FreshnessMap,
} from './assetSelection'

export interface CatalogPage {
  items: CatalogAsset[]
  q: string
  class: ClassFilter
  page: number
  page_size: number
  pages: number
  total: number
  eligible_total: number
  marked_total: number
  counts: CountsMap
  freshness: FreshnessMap
}

export interface ResolvedFilter {
  asset_ids: string[]
  items: Array<{ asset_id: string; symbol: string; asset_class: AssetClass; name: string }>
  eligible_total: number
  marked_total: number
  total: number
}

export class CatalogRequestError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function readJson<T>(res: Response, fallback: string): Promise<T> {
  if (!res.ok) {
    let message = fallback
    try {
      const data = await res.json()
      const detail = data?.detail
      if (typeof detail === 'string') message = detail
    } catch {
      /* corpo vazio */
    }
    throw new CatalogRequestError(message, res.status)
  }
  return (await res.json()) as T
}

export async function fetchCatalogPage(
  params: { q: string; filter: ClassFilter; page: number; pageSize: number },
  signal?: AbortSignal,
): Promise<CatalogPage> {
  const search = new URLSearchParams({
    q: params.q,
    class: params.filter,
    page: String(params.page),
    page_size: String(params.pageSize),
  })
  const res = await authFetch(`${API_BASE_URL}/assets/catalog?${search.toString()}`, { signal })
  return readJson<CatalogPage>(res, 'Não foi possível carregar o catálogo de ativos.')
}

export async function resolveCatalogFilter(
  params: { q: string; filter: ClassFilter },
  signal?: AbortSignal,
): Promise<ResolvedFilter> {
  const res = await authFetch(`${API_BASE_URL}/assets/catalog/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q: params.q, class: params.filter }),
    signal,
  })
  return readJson<ResolvedFilter>(res, 'Não foi possível listar os ativos do filtro.')
}

export async function lookupCatalogAssets(
  symbols: string[],
): Promise<{ items: CatalogAsset[]; freshness: FreshnessMap }> {
  const res = await authFetch(`${API_BASE_URL}/assets/catalog/lookup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols }),
  })
  return readJson(res, 'Não foi possível consultar o catálogo de ativos.')
}

export async function refreshCatalog(group?: 'crypto' | 'equity'): Promise<{ freshness: FreshnessMap }> {
  const res = await authFetch(`${API_BASE_URL}/assets/catalog/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(group ? { group } : {}),
  })
  return readJson(res, 'Não foi possível atualizar o catálogo agora.')
}
