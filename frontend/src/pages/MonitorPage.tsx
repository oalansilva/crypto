import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'

export function MonitorPage() {
  return (
    <div className="app-page monitor-page">
      <MonitorDisclaimer />
      <MonitorStatusTab />
    </div>
  )
}
