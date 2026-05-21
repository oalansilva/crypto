import { Link } from 'react-router-dom'
import { Activity, Bookmark, HelpCircle, ShieldCheck, Wallet } from 'lucide-react'

const journeySteps = [
  {
    title: 'Favoritos',
    description: 'Comece por aqui: compare estrategias, veja graficos, revise trades e separe as melhores opcoes.',
    icon: Bookmark,
  },
  {
    title: 'Selecionar estrategias',
    description: 'Use as estrelas para priorizar o que merece acompanhamento e levar apenas o essencial ao Monitor.',
    icon: Bookmark,
  },
  {
    title: 'Monitor',
    description: 'Acompanhe as estrategias selecionadas com status, contexto e distancia para a proxima decisao.',
    icon: Activity,
  },
  {
    title: 'Carteira Binance opcional',
    description: 'Configure a carteira depois, se quiser complementar a leitura. Ela nao e requisito para comecar.',
    icon: Wallet,
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
        O Cripto Farol comeca pelos Favoritos: avalie graficos e trades, selecione as melhores estrategias e acompanhe
        no Monitor. A Binance e opcional e entra depois, como complemento.
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
        <Link to="/favorites" className="onboarding-secondary-action">
          Ir para Favoritos
        </Link>
      </div>

      <div className="onboarding-guardrail">
        <ShieldCheck className="h-4 w-4" />
        <span>Apoio a decisao, com leitura de contexto e disciplina. Nao e recomendacao financeira.</span>
      </div>
    </section>
  )
}
