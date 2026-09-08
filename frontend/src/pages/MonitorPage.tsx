import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel'

export function MonitorPage() {
  return (
    <div className="app-page monitor-page">
      <ScreenHelpPanel title="Como usar o Monitor">
        Acompanhe as estrategias que voce selecionou em Favoritos. Use Em posição, Saída / cobertura, contexto, Abrir Grafico e Ver Trades sempre como apoio a decisao.
      </ScreenHelpPanel>
      <MonitorDisclaimer />
      <MonitorStatusTab />
    </div>
  )
}
