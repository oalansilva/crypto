## Context

Alan reportou que **USDC** e **USDT** não aparecem na Carteira apesar de saldo Spot na Binance. A Carteira (`/external/balances`) já lista assets, aplica dust e mostra PnL. O card `#333` corrigiu avg cost multi-quote (USDT/USDC) para assets não-stable, mas a listagem das próprias stables permanece frágil: preço ausente → `value_usd=null` → row omitida; e a UI de dust **não envia** `min_usd` à API (só filtra no cliente sobre o que o servidor já cortou).

**UI impact: affected** — Carteira (linhas + total).

Stakeholders: Alan (usuário/trader), Codex (DEV), Designer/Critic Agent (este gate).

## Goals / Non-Goals

### Goals

- Stables Spot com saldo (`USDT`/`USDC` no mínimo) visíveis na lista e no total.
- Valoração estável (`price ≈ 1`) sem depender de par `USDTUSDT`.
- Controle de dust da UI alinhado ao backend (`?min_usd=`).
- Protótipo e crítica prontos para aprovação humana antes do DEV.

### Non-Goals

- Trading/withdraw de stables.
- Redesign completo da Carteira.
- Alterar regra de avg cost multi-quote de assets não-stable (`#333`).
- Unificar KPI Home (`portfolio`) além do necessário para este bug (pode ser card filho se Alan pedir).

## Decisions

1. **Sempre valorar stables suportadas com fallback `1.0`**  
   Em vez de omitir a row quando não há ticker, usar referência USD-stable. Alternativa rejeitada: exigir ticker real `USDCUSDT` — falha quando o mapa de preços não traz o par.

2. **UI deve propagar `min_usd`**  
   O input já existe e dispara `load()` no change; o fetch precisa incluir o query param. Alternativa: só filtrar no cliente — insuficiente porque o servidor já removeu as rows.

3. **Manter layout atual da Carteira**  
   Stables continuam como linhas normais (mesmo card/lista). Badge opcional “Stable” / PnL `≈ 0` se `avg_cost=1` — nice-to-have, não bloqueante. Alternativa rejeitada neste card: seção separada “Caixa” (aumenta escopo UX sem evidência de necessidade).

4. **Tokens `DESIGN.md`**  
   Reusar superfície dark da Workbench, tipografia mono para valores, `trading-up`/`trading-down` só quando PnL ≠ null; stables com PnL ~0 ficam neutros (`muted`).

## Risks / Trade-offs

- [Saldo stable < dust default 0.02 some] → Mitigação: wiring `min_usd=0` funciona; documentar que default continua 0.02 para dust real.
- [Outros stables BUSD/TUSD/FDUSD sem preço] → Mitigação: alinhar set de display-pricing ao `STABLE_ASSETS` no mesmo card se custo for baixo.
- [Caixa em Binance Flexible Earn aparece como `LDUSDT`/`LDUSDC` no `/api/v3/account`, sem ticker] → Mitigação: `is_usd_stable_asset()` cobre Spot stables e wrappers Earn `LD*` + stable; valorizar a `1.0` e listar (rótulo UI “USDT/USDC (Earn)”).
- [Total UI vs `total_usd` server divergem com double-filter] → Mitigação: após wiring, preferir `serverTotalUsd` ou aplicar dust só no servidor.

## Migration Plan

- Deploy junto com release normal; sem migration de DB.
- Rollback: reverter branch; comportamento anterior (stables podem sumir).

## Open Questions

- Confirmar em PROD se os saldos USDT/USDC do Alan estão acima de $0.02 (se não, dust explica; se sim, omissão por preço/null é o bug principal).
- Alan quer badge “Stable” ou basta a linha aparecer? **Default do design: basta aparecer.**

## Prototype

- **URL navegável (revisão Alan):** https://dev.criptofarol.com.br/prototypes/card-346-wallet-stable-balances-display/
- **Path público:** `frontend/public/prototypes/card-346-wallet-stable-balances-display/index.html`
- **Espelho OpenSpec:** `openspec/changes/card-346-wallet-stable-balances-display/prototype/carteira-stables.html`
- **Versão:** `v1` (arquivo versionado; Gist **não** é superfície de visualização)
- **Escopo:** desktop + mobile (viewport meta + layout empilhado)
- **Fluxos/estados:**
  - Lista com USDT e USDC visíveis e total incluindo stables
  - Badge neutro opcional “Stable”
  - Dust control com nota de que `min_usd` vai para a API
  - Estado vazio de stables (não aplicável quando há saldo)
  - Loading skeleton e erro de credencial (bloco lateral)

## Design Critique

### Produto
- Problema claro: caixa em stable invisível → total errado. Escopo apertado e alinhado ao relato.
- Correção: hipóteses de dust + preço nulo cobertas; não inflar com redesign.

### UX
- Hierarquia preservada (total → toolbar → lista).
- Stables como linhas normais reduz carga cognitiva vs nova seção.
- Dust control precisa de feedback de que altera o fetch (copy curta no protótipo).

### Acessibilidade
- Labels no dust input; contraste yellow CTA / body on dark do `DESIGN.md`.
- Tabela/lista com nomes de asset em texto, não só cor.
- Touch: controles da toolbar empilham no mobile.

### Responsividade
- Desktop: colunas valor / PnL.
- Mobile: card por asset com valor e PnL empilhados (já padrão da página).

### Estados
- Loading / erro credencial / lista com stables / dust=0.
- Achado corrigido no protótipo: total do header deve refletir USDT+USDC, não só crypto.

### Pendências não bloqueantes
- Badge “Stable” opcional.
- KPI Home com USDC em `other_usd` fora deste card.

**Design Agent verdict: PASS**

## Handoff

- Change: `card-346-wallet-stable-balances-display`
- Card: `#346`
- UI impact: affected
- Próximo: Alan arrasta `Aprovação de Design → Pronto para Dev` para liberar `/opsx:apply`
