import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel'

export function MonitorPage() {
  return (
    <div className="app-page monitor-page">
      <ScreenHelpPanel title="Como usar o Monitor">
        Acompanhe as estrategias que voce selecionou em Favoritos. Use Compra, Venda, contexto, Abrir Grafico e Ver Trades sempre como apoio a decisao.
      </ScreenHelpPanel>
      <MonitorDisclaimer />
      <MonitorStatusTab />
    </div>
  )
}
