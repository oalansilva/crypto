## 1. Remover com confirmação no gráfico

- [x] 1.1 Add `confirmRemove` step to `SpotProtectStopPanel` (summary qty/stop/limit + origem com rótulo explícito app "criada no app (Farol)" e externa, `Confirmar remoção`/`Cancelar`, `data-testid` dedicato; foco move para a confirmação ao abrir — contêiner `tabindex="-1"` ou botão primário, sinal acessível `role="group"`+`aria-label` e `aria-expanded`/`aria-controls` — e volta ao gatilho ao fechar) sem mudar a regra de oferta (HOLD long + `protected=true`)
- [x] 1.2 Keep `ChartModal` wiring unchanged (painel já montado no `timeframeToolbar`) e verificar `Remover stop` alcançável com Posicionado HOLD + stop aberta (app e só-exchange)
- [x] 1.3 Cover chart remove with tests: confirmação antes do DELETE; cancelar não chama API; remover não dispara venda; sem HOLD/stop não é oferecido

## 2. Remover no fluxo de venda quando travada pela stop

- [x] 2.1 Detect stop-blocked SELL failure in `SpotMarketTradePanel` (sinal de saldo travado pela stop) e renderizar bloco "Venda travada pela stop" com `Remover stop` sem sair do fluxo
- [x] 2.2 Add own remove confirmation in the sell flow (identifica qty/stop/limit + origem com rótulo explícito app "criada no app (Farol)" e externa; foco move para a confirmação ao abrir e volta ao gatilho ao fechar — `data-trade-remove-confirm` focusable, `aria-expanded`/`aria-controls`; `DELETE /monitor/spot-stop-order`); após remover, voltar a `entry` exigindo nova prévia → revisão → confirmação de venda
- [x] 2.3 Guard non-stop failures: outros erros de venda mantêm o caminho atual sem oferecer remover
- [x] 2.4 Cover sell-flow remove with tests: bloqueada→remove→nova prévia→venda normal; remover sozinho não vende; falha não-stop não oferece remover

## 3. Backend (reuso, sem mudança de regra)

- [x] 3.1 Confirm `DELETE /monitor/spot-stop-order` + `cancel_protective_stop` cobrem `cfstop_` e só-exchange sem tocar não-stop (nenhuma mudança esperada; registrar evidência)
- [ ] 3.2 Witness BTC Spot USDT HOLD: HOLD + stop aberta → remover no gráfico ou no fluxo de venda limpa a ordem e destrava o saldo; depois, venda segue fluxo normal

## 4. Portas de skill e gate (sem código antes de Pronto para Dev)

- [x] 4.1 Use project skills available to Cursor when applicable (`.cursor/skills`, p. ex. `covenant-flow`); UI-impact work segue o gate Design → Aprovação de Design → Pronto para Dev, usando a skill `design-critic` e aguardando aprovação humana de Alan

## 5. T18 residual — detector alcança o erro real da prévia SELL

- [x] 5.1 Expand `STOP_BLOCKED_MESSAGE_RE` to also match real SELL preview errors when free qty is 0/dust (`quantidade abaixo do m[ií]nimo`, `valor abaixo do m[ií]nimo`); `requestPreview` passa `responseMessage` + `responseCode` em `looksStopBlocked` (como o submit); `enterBlockedIfStopOpen` permanece o segundo gate; teste de fonte executa o regex; e2e mocka `{ detail: { code: "BINANCE_VALIDATION_ERROR", message: "Quantidade abaixo do mínimo permitido pela Binance" } }`. Sem código novo de backend.
