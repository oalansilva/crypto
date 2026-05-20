import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel'

export function MonitorPage() {
  return (
    <div className="app-page monitor-page">
      <ScreenHelpPanel title="Como usar o Monitor">
        Acompanhe Compra, Venda e contexto das estrategias priorizadas. Use Abrir Grafico para leitura visual e Ver Trades para revisar historico, sempre como apoio a decisao.
      </ScreenHelpPanel>
      <MonitorDisclaimer />
      <MonitorStatusTab />
    </div>
  )
}
