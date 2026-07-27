import { Settings } from 'lucide-react'
import { BinanceCredentialsForm } from '@/components/binance/BinanceCredentialsForm'

export default function UserPreferencesPage() {
  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card p-6 sm:p-7 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-sky-300/20 bg-[linear-gradient(135deg,rgba(56,189,248,0.18),rgba(252,213,53,0.12))]">
            <Settings className="h-6 w-6 text-sky-100" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Conta</span>
            </div>
            <h1 className="section-title mt-2">Preferências</h1>
            <p className="section-copy mt-2">
              Configure integrações da sua conta. A Home e a carteira usam a chave API vinculada ao usuário logado.
            </p>
          </div>
        </div>
      </section>

      <BinanceCredentialsForm mode="full" />
    </div>
  )
}
