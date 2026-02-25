import { useState } from 'react'
import { MonitorDashboardTab } from '@/components/monitor/MonitorDashboardTab'
import { MonitorStatusTab } from '@/components/monitor/MonitorStatusTab'

type MonitorTab = 'status' | 'dashboard'

export function MonitorPage() {
  const [activeTab, setActiveTab] = useState<MonitorTab>('status')

  return (
    <div className="container mx-auto p-4 md:p-6 space-y-6 max-w-full overflow-x-hidden">
      <div className="flex items-center gap-2 p-1 rounded-xl bg-white/5 border border-white/10 w-full sm:w-fit" role="tablist" aria-label="Monitor tabs">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'status'}
          onClick={() => setActiveTab('status')}
          className={`rounded-lg px-4 py-2 min-h-11 text-sm font-semibold transition-colors ${
            activeTab === 'status'
              ? 'bg-blue-500/20 text-white border border-blue-400/60'
              : 'text-gray-300 border border-transparent hover:bg-white/10'
          }`}
        >
          Status
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'dashboard'}
          onClick={() => setActiveTab('dashboard')}
          className={`rounded-lg px-4 py-2 min-h-11 text-sm font-semibold transition-colors ${
            activeTab === 'dashboard'
              ? 'bg-blue-500/20 text-white border border-blue-400/60'
              : 'text-gray-300 border border-transparent hover:bg-white/10'
          }`}
        >
          Dashboard
        </button>
      </div>

      <div role="tabpanel">
        {activeTab === 'status' ? <MonitorStatusTab /> : <MonitorDashboardTab />}
      </div>
    </div>
  )
}
