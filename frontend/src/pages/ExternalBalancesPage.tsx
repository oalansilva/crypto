import React, { useEffect, useMemo, useState } from 'react'
import { API_BASE_URL } from '@/lib/apiBase'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { RefreshCw, Wallet } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/use-toast'

type BalanceRow = {
  asset: string
  free: number
  locked: number
  total: number
}

export default function ExternalBalancesPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [balances, setBalances] = useState<BalanceRow[]>([])
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/external/binance/spot/balances`)
      const payload = await res.json()
      if (!res.ok) {
        throw new Error(String(payload?.detail || 'Falha ao carregar saldos externos'))
      }
      const rows = (payload?.balances || []) as BalanceRow[]
      setBalances(rows)
      setLastUpdated(new Date())
    } catch (e) {
      toast({
        title: 'Erro',
        description: e instanceof Error ? e.message : 'Falha ao carregar saldos.',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const sorted = useMemo(() => {
    return [...balances].sort((a, b) => {
      const ta = Number(a.total || 0)
      const tb = Number(b.total || 0)
      if (tb !== ta) return tb - ta
      return String(a.asset || '').localeCompare(String(b.asset || ''))
    })
  }, [balances])

  return (
    <main className="container mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Wallet className="w-5 h-5" /> External Balances
          </h1>
          <p className="text-sm text-gray-400">Binance Spot — read-only</p>
          {lastUpdated && (
            <p className="text-xs text-gray-500 mt-1">Last updated: {lastUpdated.toLocaleTimeString()}</p>
          )}
        </div>
        <Button
          variant="secondary"
          onClick={() => void load()}
          disabled={loading}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Card className="border border-white/10 glass">
        <CardHeader>
          <div className="text-sm text-gray-300">Balances (sorted by total desc)</div>
        </CardHeader>
        <CardContent>
          {sorted.length === 0 && !loading ? (
            <div className="text-gray-400 text-sm py-8">No balances found (or all totals are 0).</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-white/10">
                    <th className="py-2 pr-4">Asset</th>
                    <th className="py-2 pr-4">Free</th>
                    <th className="py-2 pr-4">Locked</th>
                    <th className="py-2 pr-4">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((row) => {
                    const locked = Number(row.locked || 0)
                    const lockedHighlight = locked > 0
                    return (
                      <tr key={row.asset} className="border-b border-white/5">
                        <td className="py-2 pr-4 font-medium text-gray-200">{row.asset}</td>
                        <td className="py-2 pr-4 text-gray-300">{row.free}</td>
                        <td className={`py-2 pr-4 ${lockedHighlight ? 'text-amber-300 font-semibold' : 'text-gray-300'}`}>
                          {row.locked}
                        </td>
                        <td className="py-2 pr-4 text-gray-200">{row.total}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
