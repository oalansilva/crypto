# Enhanced Backtesting Metrics - OpenSpec Change

## Quick Links

- **[Proposal](./proposal.md)** - Overview, objectives, and benefits
- **[Tasks](./tasks.md)** - Detailed implementation breakdown
- **[Design](./design.md)** - Architectural decisions and patterns

## Specs

- **[Performance Metrics](./specs/performance-metrics/spec.md)** - CAGR, monthly returns
- **[Risk Metrics](./specs/risk-metrics/spec.md)** - Drawdown analysis, recovery factor
- **[GO/NO-GO Criteria](./specs/go-nogo-criteria/spec.md)** - Automated strategy validation

## Summary

This change transforms the backtester from a basic tool into a professional-grade validation system by implementing:

### ✅ Mandatory Metrics
1. **Performance**: CAGR, Monthly Returns
2. **Risk**: Max DD, Avg DD, DD Duration, Recovery Factor
3. **Risk-Adjusted**: Sharpe, Sortino, Calmar Ratios
4. **Trade Stats**: Expectancy, Win Streaks, Concentration
5. **Costs**: Fees, Slippage, Net Returns
6. **Benchmark**: Buy & Hold comparison, Alpha

### 🎯 Automated GO/NO-GO
- Clear criteria for strategy approval
- Visual indicators (✓ GO / ✗ NO-GO)
- Actionable feedback

### 📊 Professional UI
- Organized metric sections
- Visual alerts for risky values
- Benchmark comparisons
- Tooltips and explanations

## Key Questions Answered

✅ **"Is this better than doing nothing?"** → Benchmark comparison  
✅ **"Does it compensate for risk?"** → Risk-adjusted ratios  
✅ **"Is it repeatable?"** → Trade statistics & concentration

## Next Steps

1. Review this proposal
2. Run `openspec validate enhance-backtesting-metrics --strict`
3. If approved, run `/openspec-apply` to implement
