---
spec: openspec.v1
id: indicadores-tecnicos
title: Indicadores Técnicos - Design
card: "#55"
change_id: indicadores-tecnicos
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: Indicadores Técnicos

**Card:** #55  
**change_id:** `indicadores-tecnicos`

---

## 1. Visão Geral do Design

Este card implementa o cálculo de indicadores técnicos (RSI, MACD, Bollinger Bands) como serviço interno. A visualização gráfica será tratada no Card #56 (AI Dashboard).

### Fluxo de Dados

```
Binance API → Indicadores Service → Cache → Cards #53, #56
```

---

## 2. Componentes de Backend

### 2.1 IndicadoresCalculator

**Responsabilidade:** Calcular RSI, MACD e Bollinger Bands.

**Métodos:**
- `calculate_rsi(prices: List[float], period: int = 14) -> float`
- `calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict`
- `calculate_bollinger(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict`

### 2.2 IndicadoresCache

**Responsabilidade:** Cache em memória com TTL.

**Estrutura:**
```python
cache = {
    "BTCUSDT_1h": {
        "data": { "rsi": 45.3, "macd": {...}, "bollinger": {...} },
        "updated_at": "2026-03-27T12:00:00Z",
        "ttl": 300  # 5 minutos
    }
}
```

---

## 3. Interface de API

### GET /indicators/{asset}

Retorna todos os indicadores para um ativo.

**Parâmetros:**
- `asset`: string (ex: BTCUSDT)
- `timeframe`: string (default "1h")
- `period`: int (default 14)

**Resposta (200):**
```json
{
  "asset": "BTCUSDT",
  "timeframe": "1h",
  "timestamp": "2026-03-27T12:00:00Z",
  "rsi": 45.3,
  "macd": {
    "macd_line": 150.25,
    "signal_line": 140.50,
    "histogram": 9.75,
    "crossover": "bullish" | "bearish" | "none"
  },
  "bollinger_bands": {
    "upper": 97500.00,
    "middle": 96500.00,
    "lower": 95500.00,
    "position": 0.65  # 0 = no lower, 1 = no upper
  }
}
```

**Resposta (404):** Ativo não encontrado ou dados insuficientes.

---

## 4. Estados

| Estado | Descrição |
|--------|-----------|
| Loading | Calculando indicadores (async) |
| Cached | Retornando do cache |
| Error | Binance API indisponível ou dados insuficientes |

---

## 5. Integração com Card #53

O Card #53 (Sinais de Trading) consumirá:
- `GET /indicators/{asset}` para obter RSI, MACD e Bollinger
- Indicadores são usados como features no modelo de sinais

```
Indicadores #55 → Features → Modelo #53 → Sinais BUY/SELL/HOLD
```

---

## 6. Próximo Passo

Após DESIGN, passar para Alan approval antes de DEV.

---
