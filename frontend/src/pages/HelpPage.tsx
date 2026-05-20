import { Link } from 'react-router-dom'
import { Activity, ArrowRight, Bookmark, ShieldCheck, Wallet } from 'lucide-react'
import { OnboardingGuide } from '@/components/onboarding/OnboardingGuide'

const quickActions = [
  { to: '/external/balances', label: 'Abrir Carteira', icon: Wallet },
  { to: '/favorites', label: 'Abrir Favoritos', icon: Bookmark },
  { to: '/monitor', label: 'Abrir Monitor', icon: Activity },
]

export default function HelpPage() {
  return (
    <main className="app-page help-page page-stack" data-testid="help-page">
      <section className="help-page-header">
        <div>
          <p className="eyebrow">Guia do beta</p>
          <h1>Como usar o Cripto Farol no primeiro acesso</h1>
          <p>
            Use este fluxo para sair do primeiro login ate uma leitura util no Monitor, sem depender de explicacao manual.
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
            E o catalogo de estrategias que voce decidiu acompanhar. As estrelas ajudam a separar prioridade antes de
            levar a leitura para o Monitor.
          </p>
        </article>
        <article>
          <h2>Monitor</h2>
          <p>
            E a tela de acompanhamento diario. Ela mostra Compra, Venda, contexto e distancia para decisao, sempre como
            informacao para sua propria analise.
          </p>
        </article>
        <article>
          <h2>Grafico e Trades</h2>
          <p>
            Use Abrir Grafico para leitura visual da estrategia. Use Ver Trades quando precisar entender o historico e
            a consistencia do setup.
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
