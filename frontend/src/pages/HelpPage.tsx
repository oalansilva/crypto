import { Link } from 'react-router-dom'
import { Activity, ArrowRight, Bookmark, ShieldCheck, Wallet } from 'lucide-react'
import { OnboardingGuide } from '@/components/onboarding/OnboardingGuide'

const quickActions = [
  { to: '/favorites', label: 'Abrir Favoritos', icon: Bookmark },
  { to: '/monitor', label: 'Abrir Monitor', icon: Activity },
  { to: '/external/balances', label: 'Configurar Carteira', icon: Wallet },
]

export default function HelpPage() {
  return (
    <main className="app-page help-page page-stack" data-testid="help-page">
      <section className="help-page-header">
        <div>
          <p className="eyebrow">Guia do beta</p>
          <h1>Como usar o Cripto Farol no primeiro acesso</h1>
          <p>
            Comece pelos Favoritos, escolha as estrategias que merecem acompanhamento e depois use o Monitor. A carteira
            Binance e opcional e pode ficar para depois.
          </p>
        </div>
        <div className="help-page-guardrail">
          <ShieldCheck className="h-5 w-5" />
          <span>Apoio a decisao. Sem promessa de lucro, call milagrosa ou incentivo a alavancagem.</span>
        </div>
      </section>

      <OnboardingGuide />

      <section className="help-usage-grid" aria-label="Como interpretar as telas">
        <article>
          <h2>Favoritos</h2>
          <p>
            E o ponto de partida. Compare estrategias, abra graficos, revise trades e use estrelas para separar o que
            realmente merece acompanhamento.
          </p>
        </article>
        <article>
          <h2>Monitor</h2>
          <p>
            E a tela de acompanhamento das estrategias selecionadas. Ela mostra Compra, Venda, contexto e distancia para
            decisao, sempre como informacao para sua propria analise.
          </p>
        </article>
        <article>
          <h2>Carteira Binance opcional</h2>
          <p>
            Configure a carteira apenas se quiser complementar o acompanhamento com saldos read-only. Ela nao e
            pre-requisito para usar Favoritos ou Monitor.
          </p>
        </article>
      </section>

      <section className="help-actions" aria-label="Acoes principais">
        {quickActions.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} className="help-action">
            <Icon className="h-5 w-5" />
            <span>{label}</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        ))}
      </section>
    </main>
  )
}
