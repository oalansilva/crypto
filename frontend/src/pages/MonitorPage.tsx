import { useCallback, useState } from 'react'
import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel'

export function MonitorPage() {
  // Card #1122 (d2): a frase do alerta vale para as estratégias próprias; some na vitrine do catálogo.
  const [catalogView, setCatalogView] = useState<boolean | null>(null)
  const handleCatalogViewChange = useCallback((value: boolean | null) => setCatalogView(value), [])

  return (
    <div className="app-page monitor-page">
      <ScreenHelpPanel title="Como usar o Monitor">
        Acompanhe as estrategias que voce selecionou em Favoritos. Use Em posição, Saída / cobertura, contexto, Abrir Grafico e Ver Trades sempre como apoio a decisao.
        {catalogView === false ? (
          <span data-testid="monitor-help-alert">
            {' '}Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha.
          </span>
        ) : null}
      </ScreenHelpPanel>
      <MonitorDisclaimer />
      <MonitorStatusTab onCatalogViewChange={handleCatalogViewChange} />
    </div>
  )
}
