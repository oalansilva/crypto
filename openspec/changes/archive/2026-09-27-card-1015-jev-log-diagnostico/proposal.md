Título: Scalp Jev: logar chamadas (entrada/retorno) e recusa por ciclo para diagnóstico
Relacionado com #1006 (Done técnico, em homologação). Observabilidade do Jev para perceber porque o scalp não entra.

## Problema

Quem liga o Scalp BTCUSDT não consegue perceber porque não há compras: o painel mostra «Ligado… Hurdle 20,1 bp…», o contador de consultas sobe (~1/s) e os hits ficam em 0, mas nada regista o que o Jev recebeu nem o que devolveu. Sem histórico da entrada (payload enviado) e do retorno (lado, movimento esperado, tóxico, confiança) — e sem saber qual gate recusou o ciclo (HOLD, confiança, hurdle, livro tóxico, etc.) — resta adivinhar. Os logs de hoje só mostram erros HTTP; as chamadas de sucesso são invisíveis.

## História

Como operador com o scalp ligado, quero que cada chamada ao Jev fique registada em log — o que foi enviado (payload de mercado/conta sem segredos) e o que veio (lado, expected_move_bp, book_toxic, confiança, latência, status HTTP) mais o motivo de recusa do ciclo quando não há ordem — para diagnosticar em minutos porque o bot não entra, sem ter de adivinhar pelos contadores do painel.

## Entra

**Log de cada chamada Jev (SystemOne)**

- Entrada: payload enviado (state/questions: touch, window, account, resting) — **nunca** a chave TypeSafe nem qualquer segredo; conta só resumida (há posição? há saldo?), sem valores exactos de saldo ou posição.
- Retorno: respostas (side, expected_move_bp/score, book_toxic), confiança, latência, status HTTP e, em erro, o corpo do erro resumido.
- Recusa do ciclo: quando não há ordem, registar o `skip_reason` (hold, low_confidence, hurdle, toxic_book, jev_late, jev_target, t_zero, ceiling_reduce_only, floor, window_empty, switch_off, halted, livro indisponível, etc.).
- Nível de log configurável (ex.: INFO para envio/retorno, WARNING para erros) para não inundar em produção; sem alterar a cadência (~1 s), o hurdle, o alvo/stop nem qualquer decisão de trading.
- Correr só no DEV nesta entrega (produção fica para depois da evidência); evidência = log real de várias chamadas (sucesso + uma recusa) observável no runtime-worker.
- Rotação por tamanho do ficheiro de log: quando enche, o registo mais antigo cai; sem prazo fixo.

**Critérios observáveis**

- Uma chamada Jev completa aparece no log com entrada e retorno legíveis.
- Nenhum segredo (chave, token) em logs, painel ou registo.
- Um ciclo sem ordem deixa no log qual gate recusou.
- Payload e decisão de código inalterados (mesmo hurdle, mesmo 1,5 s, mesmo fail-closed de 500 ms).
- Conta no log nunca mostra saldo ou posição em valores exactos.
- O ficheiro de log não cresce sem teto: ao encher, o mais antigo desaparece.

## Não entra

- Reabrir #1006, #1001, #1007 ou #1008 (lookback, cadência, saída, régua, stream).
- Consola TypeSafe, backtest, régua/calibração de acerto por horizonte (#1007, Cancelado).
- Base de dados nova, dashboard/UI novo no Monitor, exportação/Drive.
- Histórico de trades/ciclos navegável (isso é régua #1007) — só log de diagnóstico.
- Mudar regras de entrada/saída, taxa, hurdle, teto ou piso.
- Produção nesta entrega — o registo nasce no DEV.
- Tocar no painel de hoje: o motivo da última recusa só fica no log, não no Monitor.
- Saldos e posições em valores exactos no registo.

Este card é SEM-TELA (log de diagnóstico em ficheiro; nada de UI, nada de painel).

## Como (resumo técnico da solução)

- **Registo nas costuras que já existem, sem camada nova:** a entrada (payload `state`/`questions`: touch, window, account, resting) e o retorno (side, `expected_move_bp`/score, `book_toxic`, confiança, latência, status HTTP; em erro, corpo resumido) são registados dentro de `request_jev` (`backend/app/services/scalp_jev.py`), exactamente onde o corpo SystemOne é montado e mapeado — o que se loga é o que se enviou. A recusa do ciclo é registada no fecho de `tick_user` (`backend/app/services/scalp_service.py`) por um único helper que escreve o token `skip_reason` tal como nasce em `scalp_engine` — em todos os caminhos que fecham o ciclo sem ordem, antes e depois da chamada.
- **Conta só resumida + zero segredos:** o registo de entrada substitui `state.account` por boleanos `has_position` / `has_balance` («há posição? há saldo?»); `inventory_btc`, `t`, `remaining_to_t` e saldos livres nunca entram no registo. A chave TypeSafe (`JEV_API_KEY`/`TYPESAFE_API_KEY`) e o header `Authorization` nunca são registados; corpos de erro passam pelo `_redact` já existente e são truncados. O payload enviado ao Jev e o código de decisão ficam byte-a-byte como estão.
- **Nível configurável:** logger dedicado do diagnóstico com nível por env (entrada/retorno em INFO, erros em WARNING), para o operador desligar o ruído sem tocar no código.
- **Ficheiro único com tecto de 200 MB (209 715 200 bytes) e truncagem de cauda:** o registo vai para um ficheiro de log dedicado, **um só**, com tecto fixo de bytes; ao encher, o registo mais antigo cai dentro do mesmo ficheiro (truncagem de cauda em fronteira de linha, descartando a linha parcial do início). Sem prazo fixo (nada de rotação por tempo, nada de `RotatingFileHandler`/`backupCount`/backups `.1`).
- **Só DEV nesta entrega:** o registo liga-se no runtime-worker DEV (`ops/systemd/criptofarol-dev-runtime-worker.service`, `RUN_SCALP_LOOP=1`); o unit PROD não recebe nada. Evidência = ficheiro real com várias chamadas (sucesso + uma recusa) observável no runtime-worker DEV.
- **Inalterados por contrato e teste:** cadência de pergunta ao Jev (~1 s / `JEV_TARGET_MS`), hurdle (`expected_move_bp > 2 × fee_bp + spread_bp`), alvo 35 bp / stop −28 bp, fail-closed de 1,5 s (`JEV_LATE_MS`) e fail-closed de frescura 500 ms (`age_ms`) seguem exactamente como hoje. O painel do `/monitor` não recebe o motivo da recusa — fica só no log.

## Capabilities

### New Capabilities

- `scalp-jev-diagnostic-log`: registo de diagnóstico por chamada Jev (entrada sem segredos e com conta resumida, retorno com side/move/book_toxic/confiança/latência/status HTTP, corpo de erro resumido), `skip_reason` por ciclo sem ordem, nível de log configurável, ficheiro único com tecto de 200 MB e truncagem de cauda (cai o mais antigo), entrega só no DEV, zero segredos, decisões de trading inalteradas.

### Modified Capabilities

- (nenhuma) — o painel, o payload SystemOne, as regras de entrada/saída e o stream (#1008) não mudam.

## Impact

- `backend/app/services/scalp_jev.py`: registos de entrada/retorno da chamada (INFO) e de erro com corpo resumido (WARNING); redação de segredos; sem mudar o corpo enviado nem o mapeamento do sinal.
- `backend/app/services/scalp_service.py`: um registo de recusa com o token `skip_reason` em cada ciclo que fecha sem ordem; sem mudar nenhuma decisão.
- Logger + ficheiro de log dedicado, único, com tecto de 200 MB (209 715 200 bytes) e truncagem de cauda; nível por env (nomes exactos = P3 de Apply).
- Unit DEV do runtime-worker ganha o registo; PROD e o resto da superfície ficam como estão. Sem `frontend/**`, sem rota nova, sem base de dados, sem exportação/Drive.
