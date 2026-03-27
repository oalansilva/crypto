import { AlertTriangle } from 'lucide-react'

type DisclaimerBannerProps = {
  text?: string
}

export function DisclaimerBanner({ text = 'Isenção de responsabilidade: este não é advice financeiro.' }: DisclaimerBannerProps) {
  return (
    <div className="sticky bottom-4 z-20 rounded-2xl border border-amber-400/25 bg-[rgba(43,28,6,0.92)] px-4 py-3 text-sm text-amber-100 shadow-[0_18px_32px_rgba(0,0,0,0.28)] backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-5 w-5 shrink-0 text-amber-300" />
        <span>{text}</span>
      </div>
    </div>
  )
}
