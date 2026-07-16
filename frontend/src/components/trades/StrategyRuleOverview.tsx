import type { StrategyTransparency } from '@/lib/strategyTransparency'
import { buildStrategyRuleOverview } from '@/lib/strategyTransparency'

interface StrategyRuleOverviewProps {
    strategyTransparency?: StrategyTransparency | Record<string, unknown> | null
    direction?: string | null
    id?: string
}

export function StrategyRuleOverview({
    strategyTransparency,
    direction,
    id = 'strategy-rule-overview',
}: StrategyRuleOverviewProps) {
    const rules = buildStrategyRuleOverview(strategyTransparency, direction)

    return (
        <section
            className="min-w-0 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3"
            aria-labelledby={`${id}-title`}
            data-testid={id}
        >
            <div>
                <h4 id={`${id}-title`} className="text-sm font-semibold text-[#eaecef]">
                    Como funciona a estratégia
                </h4>
                <p className="mt-1 text-xs leading-5 text-[#929aa5]">
                    Estas regras não mudam com a posição atual do trade.
                </p>
            </div>
            <dl className="mt-3 grid min-w-0 gap-2 md:grid-cols-2">
                {[rules.entry, rules.exit].map((rule) => (
                    <div key={rule.title} className="min-w-0 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                        <dt className="text-xs font-semibold text-[#eaecef]">{rule.title}</dt>
                        <dd className="mt-1 min-w-0">
                            <span className="block text-xs font-medium text-[#fcd535]">{rule.action}</span>
                            <span className={`mt-1 block break-words text-sm leading-6 ${rule.available ? 'text-[#eaecef]' : 'text-[#929aa5]'}`}>
                                {rule.summary}
                            </span>
                        </dd>
                    </div>
                ))}
            </dl>
        </section>
    )
}
