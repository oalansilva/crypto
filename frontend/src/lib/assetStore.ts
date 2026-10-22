import { useEffect, useMemo, useSyncExternalStore } from 'react'
import { lookupCatalogAssets } from './assetCatalogApi'
import {
  normalizeSymbol,
  resolveSelection,
  type CatalogAsset,
  type FreshnessMap,
  type SelectionEntry,
} from './assetSelection'

/**
 * Cache compartilhado do que o catálogo já disse sobre cada símbolo. O seletor e
 * as telas hospedeiras (Preflight, aviso ao otimizar) leem o mesmo cache, então
 * uma seleção antiga (rascunho, snapshot, favorito, `?symbol=`) é reidratada uma
 * vez, com o estado de hoje.
 */

const known = new Map<string, CatalogAsset>()
const looked = new Set<string>()
const inFlight = new Set<string>()
const listeners = new Set<() => void>()
let freshness: FreshnessMap | null = null
let version = 0

function emit() {
  version += 1
  listeners.forEach((listener) => listener())
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

function getVersion() {
  return version
}

export function rememberAssets(
  items: CatalogAsset[],
  options: { fresh?: FreshnessMap | null; overwrite?: boolean } = {},
) {
  const { fresh, overwrite = true } = options
  for (const item of items) {
    const symbol = normalizeSymbol(item.symbol)
    if (!overwrite && known.has(symbol)) {
      looked.add(symbol)
      continue
    }
    known.set(symbol, item)
    looked.add(symbol)
  }
  if (fresh) freshness = fresh
  emit()
}

export function setCatalogFreshness(fresh: FreshnessMap) {
  freshness = fresh
  emit()
}

export function getKnownAssets(): ReadonlyMap<string, CatalogAsset> {
  return known
}

export function getCatalogFreshness(): FreshnessMap | null {
  return freshness
}

/** Consulta o catálogo dos símbolos ainda desconhecidos (uma vez cada). */
export async function ensureAssets(symbols: string[]): Promise<void> {
  const need = [
    ...new Set(symbols.map(normalizeSymbol).filter((s) => s && !looked.has(s) && !inFlight.has(s))),
  ]
  if (!need.length) return
  need.forEach((s) => inFlight.add(s))
  try {
    for (let i = 0; i < need.length; i += 5000) {
      const chunk = need.slice(i, i + 5000)
      const data = await lookupCatalogAssets(chunk)
      for (const item of data.items) known.set(normalizeSymbol(item.symbol), item)
      chunk.forEach((s) => looked.add(s))
      freshness = data.freshness
    }
  } catch {
    // Sem resposta do catálogo a seleção segue neutra (nada é marcado nem recusado
    // por palpite); o servidor decide ao rodar.
    need.forEach((s) => looked.add(s))
  } finally {
    need.forEach((s) => inFlight.delete(s))
    emit()
  }
}

/**
 * Só os negociáveis do catálogo, na ordem pedida. Usado pelo Top 10 do Combo:
 * pares marcados ou fora do catálogo (ex.: MATIC/USDT) nunca entram.
 */
export async function tradableCrypto(symbols: string[]): Promise<string[]> {
  const wanted = symbols.map(normalizeSymbol)
  try {
    const data = await lookupCatalogAssets(wanted)
    rememberAssets(data.items, { fresh: data.freshness })
  } catch {
    return []
  }
  return wanted.filter((symbol) => {
    const asset = known.get(symbol)
    return asset != null && asset.asset_class === 'crypto' && asset.state === 'tradable'
  })
}

/** Para testes e para o "Tentar de novo": esquece o que foi consultado. */
export function resetAssetStore() {
  known.clear()
  looked.clear()
  inFlight.clear()
  freshness = null
  emit()
}

export interface SelectionView {
  entries: SelectionEntry[]
  /** `true` enquanto algum símbolo da seleção ainda não foi consultado. */
  loading: boolean
  freshness: FreshnessMap | null
}

export function useSelectionView(symbols: string[]): SelectionView {
  const current = useSyncExternalStore(subscribe, getVersion, getVersion)
  const key = symbols.join('|')

  useEffect(() => {
    void ensureAssets(symbols)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  return useMemo(() => {
    const normalized = symbols.map(normalizeSymbol)
    const pending = normalized.some((s) => !looked.has(s))
    const entries = resolveSelection(normalized, known, freshness, looked)
    return { entries, loading: pending, freshness }
    // `current` muda a cada atualização do cache.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, current])
}
