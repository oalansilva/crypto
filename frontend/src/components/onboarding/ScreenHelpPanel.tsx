import { HelpCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

type ScreenHelpPanelProps = {
  title: string
  children: string
}

export function ScreenHelpPanel({ title, children }: ScreenHelpPanelProps) {
  return (
    <section className="screen-help-panel" aria-label={title} data-testid="screen-help-panel">
      <div className="screen-help-panel-icon">
        <HelpCircle className="h-5 w-5" />
      </div>
      <div className="screen-help-panel-copy">
        <h2>{title}</h2>
        <p>{children}</p>
      </div>
      <Link to="/help" className="screen-help-panel-link">
        Ajuda
      </Link>
    </section>
  )
}
