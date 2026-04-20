# Contrato de sprint

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta sprint
Opção Portifolio na tela Monitor  - 1

## Fora de escopo
- Alterar o comportamento de Portfólio para ativos não cripto.
- Permitir override manual do Portfólio quando a regra derivada de Binance estiver ativa.
- Redesenhar o fluxo da Carteira ou a captura de credenciais Binance.

## Comportamentos esperados
- No Monitor, para ativo classificado como criptomoeda com Binance configurada, o estado de `Portfólio` deve ser derivado da Carteira Binance, e não da preferência manual persistida.
- Se a Carteira retornar holding positiva para o ativo-base, o card deve exibir `Portfólio` como ativo.
- Se a Carteira não retornar posição para o ativo-base, o card deve exibir `Portfólio` como inativo, mantendo a origem automática.
- Ativos não cripto, ou cenários sem Binance configurada, devem continuar usando a preferência manual existente.

## Sensores obrigatorios
- `backend/tests/integration/test_monitor_preferences_endpoints.py`
- `backend/tests/integration/test_opportunities_smoke.py`
- `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`

## Evidencias esperadas
- Backend expõe `asset_type` em oportunidades para distinguir cripto de não cripto no Monitor.
- Frontend calcula `portfolioStatusBySymbol` a partir de `asset_type`, status de credencial Binance e holdings vindas de `/external/binance/spot/balances`.
- Teste E2E cobre o cenário em que a preferência manual está `false`, mas a Carteira Binance força `Portfólio` para `true` com mensagem de sincronização.
- O toggle `Portfolio` fica semanticamente bloqueado (`disabled` e `aria-disabled`) para cripto com Binance configurada, enquanto ativos fora da regra continuam editáveis.
- O backend rejeita `PUT /api/monitor/preferences/{symbol}` com `409` quando há tentativa manual de alterar `in_portfolio` para cripto derivado da Binance.

## Riscos conhecidos
- Quando a Carteira estiver indisponível ou vazia, o card continua bloqueado e precisa comunicar o fallback sem ambiguidade.
- O endpoint canônico específico do card falhou neste turno em `127.0.0.1:8004`; a confirmação operacional veio da board canônica.
- O spec Playwright do arquivo `monitor-card-mode-and-portfolio.spec.ts` não pôde ser validado neste ambiente porque o Chromium do Playwright aborta no launch com `sandbox_host_linux.cc:41` e `Operation not permitted`, antes de executar qualquer cenário.

## Estado dos sensores neste turno
- `npm --prefix frontend run build`: passou.
- `./backend/.venv/bin/python -m pytest -q backend/tests/integration/test_monitor_preferences_endpoints.py`: passou.
- `./backend/.venv/bin/python -m pytest -q backend/tests/integration/test_opportunities_smoke.py`: passou.
- `cd frontend && PLAYWRIGHT_SKIP_WEBSERVER=1 PLAYWRIGHT_BASE_URL=http://127.0.0.1:4175 npx playwright test tests/e2e/monitor-card-mode-and-portfolio.spec.ts`: bloqueado por falha de launch do Chromium no sandbox.
