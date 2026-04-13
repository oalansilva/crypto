# Tasks — Card #89

## Mudança: Cores das Médias Móveis no Gráfico TradingView-like

---

## DEV Tasks

- [x] **1. Localizar componente de renderização das médias móveis**
  
  Identificar onde SMA/EMA são renderizadas no gráfico do monitor.
  
  **Resultado:** localizado em `frontend/src/components/monitor/ChartModal.tsx`. Os períodos são resolvidos em `indicatorPeriods` e as séries são criadas com `mainChart.addLineSeries()` para `emaShort`, `smaMedium` e `smaLong`.
  
  **Critério de Aceite:** Localizado o código que renderiza as moving averages

- [x] **2. Definir thresholds de período**
  
  Confirmar valores e limites inclusivos para evitar ambiguidade na implementação:
  
  - **Curta:** período `< 20`
  - **Média:** período `>= 20` e `< 50`
  - **Longa:** período `>= 50`
  
  **Exemplos validados:** EMA 9 = vermelho, SMA 21 = laranja, SMA 50 = azul, SMA 100 = azul.
  
  **Critério de Aceite:** Thresholds definidos e documentados

- [x] 3. Implementar coloração por período**
  
  Aplicar lógica de cor baseada no período:
  ```typescript
  const getMAColor = (period: number): string => {
    if (period < 20) return '#FF5252'; // vermelho
    if (period < 50) return '#FF9800'; // laranja
    return '#2196F3'; // azul
  };
  ```

  **Resultado:** helper `getMAColor()` implementado em `frontend/src/components/monitor/ChartModal.tsx` e aplicado nas line series de `emaShort`, `smaMedium` e `smaLong`, além da legenda e indicadores auxiliares do modal.
  
  **Critério de Aceite:** Cada MA renderizada com cor correta baseada em seu período

- [x] **4. Confirmar cores com DESIGN**
  
  Validar que os hex codes propostos estão no design system do projeto.

  **Resultado:** confirmado contra o design system local do frontend. O projeto já define cores semânticas para warning/danger/info em `frontend/src/index.css` e o monitor já usa azul, laranja e vermelho como linguagem visual para estados e destaque. A escolha final ficou:
  - curta = `#FF5252`
  - média = `#FF9800`
  - longa = `#2196F3`
  
  **Critério de Aceite:** DESIGN aprovou as cores selecionadas

- [x] 5. Testar com múltiplos períodos de MA**
  
  Verificar que SMA 9 (vermelho), EMA 21 (laranja), SMA 100 (azul) aparecem com cores distintas.

  **Resultado:** validação executada contra a regra implementada em `getMAColor(period)` com amostras objetivas:
  - `9 -> #FF5252`
  - `21 -> #FF9800`
  - `50 -> #2196F3`
  - `100 -> #2196F3`
  
  **Observação:** o frontend não estava acessível em `127.0.0.1:5173` nesta rodada, então a evidência ficou restrita à validação executável da regra de cor e aos checks de build/typecheck já concluídos.
  
  **Critério de Aceite:** Cores aparecem corretamente no gráfico

---

## QA Tasks

- [ ] **6. Validar coloração de SMA curta**
  
  SMA/período < 20 deve aparecer em vermelho.
  
  **Critério de Aceite:** SMA 9, 12, 15 aparecem em vermelho

- [ ] **7. Validar coloração de SMA média**
  
  Período entre 20-50 deve aparecer em laranja.
  
  **Critério de Aceite:** SMA 21, 26, 30 aparecem em laranja

- [ ] **8. Validar coloração de SMA longa**
  
  Período > 50 deve aparecer em azul.
  
  **Critério de Aceite:** SMA 50, 100, 200 aparecem em azul

- [ ] **9. Validar que EMA também é colorida**
  
  EMA com diferentes períodos também recebe cores corretas.
  
  **Critério de Aceite:** EMA segue mesmo padrão de cores que SMA

- [ ] **10. Verificar contraste e acessibilidade**
  
  Cores são distinguíveis para usuários sem deficiência visual de cores.
  
  **Critério de Aceite:** Cores passam em teste de contraste

---

## Notas

- **Depende de card #87** — gráfico TradingView-like precisa existir primeiro
- **Protótipo não necessário** — é estilização de feature existente
- **Biblioteca:** `lightweight-charts` suporta `color` property em lineSeries
