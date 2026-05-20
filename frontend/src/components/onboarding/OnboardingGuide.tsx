import { Link } from 'react-router-dom'
import { Activity, BarChart3, Bookmark, HelpCircle, ShieldCheck, Wallet } from 'lucide-react'

const journeySteps = [
  {
    title: 'Carteira',
    description: 'Confirme o contexto dos ativos que voce acompanha. Isso ajuda a leitura do Monitor.',
    icon: Wallet,
  },
  {
    title: 'Favoritos',
    description: 'Escolha as estrategias que merecem acompanhamento e use estrelas para priorizar.',
    icon: Bookmark,
  },
  {
    title: 'Monitor',
    description: 'Veja sinais, contexto e distancia para a proxima decisao sem depender de suporte manual.',
    icon: Activity,
  },
  {
    title: 'Grafico e Trades',
    description: 'Abra o grafico para leitura visual ou Ver Trades para entender o historico da estrategia.',
    icon: BarChart3,
  },
]

type OnboardingGuideProps = {
  compact?: boolean
  onDismiss?: () => void
}

export function OnboardingGuide({ compact = false, onDismiss }: OnboardingGuideProps) {
  return (
    <section
      className={compact ? 'onboarding-guide onboarding-guide-compact' : 'onboarding-guide'}
      aria-label="Guia inicial do Cripto Farol"
      data-testid={compact ? 'onboarding-prompt' : 'onboarding-guide'}
    >
      <div className="onboarding-guide-head">
        <div className="onboarding-guide-title">
          <span className="onboarding-guide-icon">
            <HelpCircle className="h-5 w-5" />
          </span>
          <div>
            <p className="onboarding-guide-kicker">Primeiros passos</p>
            <h2>Comece pelo fluxo certo</h2>
          </div>
        </div>
        {onDismiss ? (
          <button type="button" className="onboarding-dismiss" onClick={onDismiss}>
            Dispensar
          </button>
        ) : null}
      </div>

      <p className="onboarding-guide-copy">
        O Cripto Farol organiza informacao para apoiar sua decisao. Ele nao promete resultado, nao substitui sua analise
        e nao incentiva alavancagem.
      </p>

      <div className="onboarding-steps">
        {journeySteps.map(({ title, description, icon: Icon }, index) => (
          <article key={title} className="onboarding-step">
            <div className="onboarding-step-index">{index + 1}</div>
            <Icon className="onboarding-step-icon h-5 w-5" />
            <div>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="onboarding-guide-actions">
        <Link to="/help" className="onboarding-primary-action">
          Ver guia completo
        </Link>
        <Link to="/monitor" className="onboarding-secondary-action">
          Ir para Monitor
        </Link>
      </div>

      <div className="onboarding-guardrail">
        <ShieldCheck className="h-4 w-4" />
        <span>Apoio a decisao, com leitura de contexto e disciplina. Nao e recomendacao financeira.</span>
      </div>
    </section>
  )
}
