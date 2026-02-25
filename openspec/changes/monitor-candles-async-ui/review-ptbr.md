# Revisão (PT-BR) — monitor-candles-async-ui

## O que é
Melhorar a experiência do gráfico (candles) no Monitor para não parecer que a interface “tranca” quando você troca o timeframe (ex: 1h).

## Mudanças principais
- Troca de timeframe **não bloqueia** o card inteiro.
- O timeframe selecionado muda **na hora** (otimista).
- Mostra um loading **só na área do gráfico** (não na tela toda).
- Se você clicar rápido em vários timeframes, o sistema **cancela** as requisições antigas (último clique vence).
- Cache em memória por `símbolo+timeframe` para voltar instantâneo quando você retorna para um timeframe recente.

## Como testar
1) No `/monitor`, escolha um cripto (BTC/USDT) e mude timeframe várias vezes rápido.
2) Confirme que:
   - você ainda consegue rolar a tela
   - consegue clicar em ⭐ Portfolio e Price/Strategy enquanto o gráfico carrega
   - o loading aparece só no gráfico
   - ao voltar para um timeframe já visto, ele mostra quase instantâneo.
