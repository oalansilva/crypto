# SPEC — Unificar Sinais (#92) v2

## Mudança de Escopo (Alan)

**REJEITADO:** Sinais separados por fonte com badges + filtros
**NOVO:** Um único sinal consolidado por ativo, combinando as 3 fontes

> "não quero sinais isolados por fonte. Quero um único sinal consolidado por ativo, combinando AI Dashboard, On-chain e Signals."

---

## 1. Conceito & Visão

Um único sinal por ativo — o trader vê a decisão final consolidada, não as fontes separadas. Detalhes das fontes aparecem sob demanda (expandir). Interface limpa e decisive.

## 2. Domínio

- **Projeto:** crypto
- **Rota:** `/ai-dashboard` (unificar aqui)
- **Fontes:**
  - `/ai-dashboard` — AI
  - `/signals/onchain` — On-chain
  - `/signals` — Signals

## 3. Data Model

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `symbol` | string | Par de trading |
| `action` | "COMPRA" \| "VENDA" \| "NEUTRO" | Ação final consolidada |
| `direction` | string | Direção textual: "Alta forte", "Baixa", etc |
| `sources` | array | Array de {source, direction, status} |
| `strength` | 0-3 | Quantas fontes confirmam |
| `price` | number | Preço atual |

## 3.1 Contratos Reais das Fontes

Este levantamento registra o formato atual consumido por cada tela no código. A consolidação deve partir destes contratos reais, sem assumir que as três fontes já expõem o mesmo schema.

### Fonte 1 — AI Dashboard (`GET /api/ai/dashboard`)

Wrapper atual:

```json
{
  "generated_at": "2026-04-14T19:00:00Z",
  "recent_signals": [
    {
      "id": "btc-ai",
      "asset": "BTCUSDT",
      "action": "BUY",
      "confidence": 84,
      "reason": "AI bullish"
    }
  ],
  "stats": { "...": "..." },
  "section_errors": {}
}
```

Campos relevantes para consolidação:

| Campo | Tipo | Observação |
|-------|------|------------|
| `recent_signals[].id` | string | ID do sinal na seção de AI |
| `recent_signals[].asset` | string | Símbolo do ativo já em formato de par (`BTCUSDT`) |
| `recent_signals[].action` | `BUY \| SELL \| HOLD` | Direção da fonte AI |
| `recent_signals[].confidence` | number | Escala 0-100 |
| `recent_signals[].reason` | string | Texto explicativo da fonte |

Observações:
- O endpoint não expõe `price` no bloco `recent_signals`.
- A lista vem embutida dentro do payload completo do dashboard.
- O frontend atual usa apenas `recent_signals` para a seção de sinais.

### Fonte 2 — On-chain (`GET /api/signals/onchain/snapshot` e `GET /api/signals/onchain/history`)

O frontend da rota `/signals/onchain` usa duas superfícies:

1. `snapshot` para sinais ativos.
2. `history` para contexto recente.

`snapshot` atual:

```json
{
  "signals": [
    {
      "signal": "BUY",
      "confidence": 78,
      "breakdown": {
        "tvl": 22.1,
        "active_addresses": 18.4
      },
      "metrics": {
        "token": "BTC",
        "chain": "ethereum",
        "tvl": 123456.0
      },
      "timestamp": "2026-04-14T19:00:00Z",
      "market": {
        "symbol": "BTCUSDT",
        "quote_volume": 1000000,
        "trade_count": 5000,
        "last_price": 67234.0
      }
    }
  ]
}
```

`history` atual:

```json
{
  "signals": [
    {
      "id": "uuid",
      "token": "BTC",
      "chain": "ethereum",
      "signal_type": "BUY",
      "confidence": 78,
      "breakdown": {},
      "status": "active",
      "tvl": 123456.0,
      "active_addresses": 999,
      "exchange_flow": 10.5,
      "github_commits": 8,
      "github_stars": 12,
      "github_prs": 2,
      "github_issues": 1,
      "created_at": "2026-04-14T19:00:00Z"
    }
  ]
}
```

Campos relevantes para consolidação:

| Campo | Tipo | Observação |
|-------|------|------------|
| `snapshot.signals[].signal` | `BUY \| SELL \| HOLD` | Direção atual da fonte on-chain |
| `snapshot.signals[].confidence` | number | Escala 0-100 |
| `snapshot.signals[].metrics.token` | string | Token base |
| `snapshot.signals[].metrics.chain` | string | Chain da análise |
| `snapshot.signals[].market.symbol` | string | Melhor campo para reconciliar com `BTCUSDT` das outras fontes |
| `snapshot.signals[].market.last_price` | number \| null | Preço atual disponível |
| `history.signals[].signal_type` | `BUY \| SELL \| HOLD` | Direção histórica |
| `history.signals[].created_at` | datetime | Timestamp histórico |

Observações:
- O contrato on-chain não usa `asset`; usa `token` + `chain` e, no snapshot, também `market.symbol`.
- O preço está disponível no `snapshot.market.last_price`, não no histórico.
- O frontend já faz normalização local para unir `history` e `snapshot`.

### Fonte 3 — Signals (`GET /api/signals`)

Wrapper atual:

```json
{
  "signals": [
    {
      "id": "uuid",
      "asset": "BTCUSDT",
      "type": "BUY",
      "confidence": 82,
      "target_price": 97500.0,
      "stop_loss": 91000.0,
      "indicators": {
        "RSI": 35,
        "MACD": "bullish",
        "BollingerBands": {
          "upper": 98000,
          "middle": 95000,
          "lower": 92000
        }
      },
      "created_at": "2026-03-26T12:00:00Z",
      "risk_profile": "moderate",
      "entry_price": 94000.0,
      "current_price": 94500.0,
      "pnl_percent": 0.53,
      "is_open_position": false,
      "breakdown": {
        "rsiContribution": 40.18,
        "macdContribution": 17.22,
        "sentimentContribution": 22.2,
        "displayTotal": 79.6
      }
    }
  ],
  "total": 1,
  "cached_at": "2026-03-26T12:05:00Z",
  "is_stale": false,
  "available_assets": ["BTCUSDT"]
}
```

Campos relevantes para consolidação:

| Campo | Tipo | Observação |
|-------|------|------------|
| `signals[].id` | string | ID do sinal |
| `signals[].asset` | string | Símbolo do ativo já em formato de par |
| `signals[].type` | `BUY \| SELL \| HOLD` | Direção da fonte Signals |
| `signals[].confidence` | number | Escala 0-100 |
| `signals[].current_price` | number \| null | Melhor preço disponível nessa fonte |
| `signals[].entry_price` | number \| null | Preço da entrada do sinal |
| `signals[].indicators` | objeto | Indicadores técnicos usados na geração |
| `signals[].breakdown` | objeto \| null | Breakdown de confiança técnico/sentimento |

Observações:
- Esta fonte usa `type` em vez de `action` ou `signal`.
- O schema é o mais rico em indicadores técnicos.
- `current_price` pode preencher lacunas de preço quando AI Dashboard não trouxer preço.

## 3.2 Normalização Necessária para o Sinal Unificado

Antes de consolidar, DEV precisa mapear os campos heterogêneos para um contrato comum:

| Campo unificado | AI Dashboard | On-chain | Signals |
|-----------------|--------------|----------|---------|
| `symbol` | `asset` | `market.symbol` (preferencial) | `asset` |
| `source_action` | `action` | `signal` / `signal_type` | `type` |
| `source_confidence` | `confidence` | `confidence` | `confidence` |
| `source_price` | n/d | `market.last_price` | `current_price` |
| `source_reason` | `reason` | derivado do breakdown/metrics | derivado de indicators/breakdown |

Decisões já esclarecidas por este levantamento:

- O join principal entre as três fontes deve usar símbolo de mercado (`BTCUSDT`), não `token + chain`.
- On-chain exige adaptação explícita porque o contrato nativo não é orientado a `asset`.
- AI Dashboard hoje é a fonte mais pobre em metadados e não pode ser tratada como schema mestre.

## 4. Layout — Tabela Unificada

```
┌─────────────┬──────────┬──────────────────────┬────────────┬──────────┐
│ PAR         │ AÇÃO     │ SINAL CONSOLIDADO    │ FORÇA     │ PREÇO    │
├─────────────┼──────────┼──────────────────────┼────────────┼──────────┤
│ BTCUSDT     │ [COMPRA] │ Alta forte 🤖⛓️📊    │ [███░░] 2/3│ $67,234  │
│ ETHUSDT     │ [COMPRA] │ Alta    🤖⛓️📊       │ [██░░░] 1/3│ $3,456   │
│ SOLUSDT     │ [VENDA]  │ Baixa    🤖⛓️📊      │ [░░░░░] 0/3│ $178     │
└─────────────┴──────────┴──────────────────────┴────────────┴──────────┘
```

## 5. Signal Row

| Coluna | Conteúdo |
|--------|----------|
| PAR | BTCUSDT, ETHUSDT, etc |
| AÇÃO | Badge COMPRA/VENDA/NEUTRO |
| SINAL CONSOLIDADO | Direção + ícones das fontes (🤖⛓️📊) |
| FORÇA | Barra visual + fração (3/3, 2/3, 1/3, 0/3) |
| PREÇO | Preço atual |

## 6. Detail Panel (expandido)

Ao clicar na row, expande painel mostrando:

```
Fontes do sinal — BTCUSDT

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 🤖 AI        │ │ ⛓️ On-chain  │ │ 📊 Signals  │
│ ▲ Alta       │ │ ▲ Alta       │ │ ▲ Alta       │
│ ✓ Confirmado │ │ ✓ Confirmado │ │ ✓ Confirmado │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 7. Visual Decisions

| Elemento | Valor |
|----------|-------|
| **COMPRA badge** | `#26a641` green bg, `#26a641` text |
| **VENDA badge** | `#f85149` red bg, `#f85149` text |
| **NEUTRO badge** | `#8b949e` gray bg, `#8b949e` text |
| **Força 3/3** | Verde `#26a641` |
| **Força 2/3** | Âmbar `#d29922` |
| **Força 0-1/3** | Vermelho `#f85149` |
| **Source icons** | AI=blue, On-chain=amber, Signals=purple |
| **Confirmado** | Verde ✓ |
| **Contradiz** | Vermelho ✗ |

## 8. Strength Calculation

```
strength = count of sources confirming the consolidated direction
```

| Fração | Cor | Significado |
|--------|-----|------------|
| 3/3 | Verde | Todas fontes concordam |
| 2/3 | Âmbar | Maioria concorda |
| 1/3 | Vermelho | Apenas uma fonte confirma |
| 0/3 | Vermelho | Nenhuma fonte confirma — neutro |

## 9. Consolidation Logic (Backend)

1.收集三个源的信号
2.确定主导方向（买入/卖出/中性）
3.计算多少源确认该方向
4.返回单一信号

## 10. Rejeições

- ❌ **Sem badges por fonte na listagem** — apenas sinal consolidado
- ❌ **Sem filtros por fonte** — não filtra por origem
- ❌ **Telas individuais permanecem** — coexistem

## 11. Componentes

```
src/pages/AIDashboard.tsx
  ├── SignalTable
  │   ├── SignalRow
  │   │   ├── ActionBadge
  │   │   ├── ConsolidatedSignal (direction + source icons)
  │   │   ├── StrengthBar
  │   │   └── Price
  │   └── DetailPanel
  │       ├── SourceCard (x3)
  │       └── SourceIcon + SourceValue + SourceStatus
  └── Legend

src/components/signals/ActionBadge.tsx
src/components/signals/SourceIcons.tsx
src/components/signals/StrengthBar.tsx
src/components/signals/DetailPanel.tsx
```

## 12. Próximo Passo DEV

1. Backend: endpoint que agrega 3 sinais em 1
2. frontend: SignalRow component
3. frontend: DetailPanel com 3 SourceCards
4. frontend: StrengthBar visual
5. Testar com dados reais
