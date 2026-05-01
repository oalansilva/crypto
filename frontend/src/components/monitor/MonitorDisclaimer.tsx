import { AlertTriangle, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

const DISCLAIMER_SESSION_KEY = 'crypto-monitor-disclaimer-seen-v1'

const DISCLAIMER_TEXT =
  'Produto educacional com finalidade informativa. As informações apresentadas ajudam no processo de decisão, mas não configuram recomendação financeira nem garantia de resultado.'

type MonitorDisclaimerProps = {
  text?: string
  className?: string
}

export function MonitorDisclaimer({ text = DISCLAIMER_TEXT, className = '' }: MonitorDisclaimerProps) {
  const [visible, setVisible] = useState(true)

  const storageSupported = useMemo(() => typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined', [])

  useEffect(() => {
    if (!storageSupported) return

    const alreadySeen = window.sessionStorage.getItem(DISCLAIMER_SESSION_KEY) === '1'
    if (alreadySeen) {
      setVisible(false)
    }
  }, [storageSupported])

  const handleClose = () => {
    if (storageSupported) {
      window.sessionStorage.setItem(DISCLAIMER_SESSION_KEY, '1')
    }
    setVisible(false)
  }

  if (!visible) {
    return null
  }

  return (
    <div
      className={`rounded-2xl border border-amber-400/30 bg-[rgba(43,28,6,0.95)] px-4 py-3 text-amber-100 shadow-[0_18px_32px_rgba(0,0,0,0.28)] ${className}`}
      role="note"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
        <p className="min-w-0 text-sm leading-6">{text}</p>
        <button
          type="button"
          onClick={handleClose}
          className="shrink-0 rounded-md px-2 py-1 text-amber-200 transition-colors hover:bg-amber-500/15"
          aria-label="Fechar aviso"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
