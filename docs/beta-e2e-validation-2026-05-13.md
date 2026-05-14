# Validacao Ponta a Ponta do Beta - 2026-05-13

## Escopo

Card: `#75` - validar fluxo `login -> Monitor -> card -> grafico -> contexto/historico -> risco`.

Base validada:

- Branch: `card-75-beta-e2e-validation`
- Base: `origin/develop`
- Commit: `3709e19` (`Merge pull request #198 from oalansilva/release-20260513-commercial-beta`)

## Ambiente

- Backend: `http://127.0.0.1:8003`
- Frontend: `http://127.0.0.1:5173`
- Redis: `127.0.0.1:6379`
- Healthcheck backend: OK
- Frontend `/login`: HTTP 200

## Usuario QA

- Usuario comum local criado para teste: `qa-card75-20260513@example.com`
- Login real validado via frontend.
- `mustChangePassword=false`.

## Resultado

### Passou

- Login com senha valida redireciona para `/monitor`.
- Login sem senha mostra validacao `Senha e obrigatoria`.
- Monitor carrega para usuario comum.
- Monitor exibiu 3 resultados acionaveis para o usuario QA:
  - `SOL/USDT` como `Compra`
  - `AVAX/USDT` como `Compra`
  - `ETH/USDT` como `Venda`
- Card/linha de `SOL/USDT` expande no Monitor.
- Grafico detalhado de `SOL/USDT` abre.
- No modo `Compacto`, o grafico mostra:
  - contexto do sinal;
  - risco/stop;
  - historico de sinais;
  - parametros/indicadores protegidos para usuario comum.

### Falhou / Bloqueia Liberacao Sem Ajuste

- A lista do Monitor mostra `SOL/USDT` como `Compra`, mas o modal do grafico em modo padrao mostra badge `ESPERA` para o mesmo ativo.
- O modo padrao `Algoritmica` do grafico nao mostra `Signal Context`, `Risco / Stop` nem `Historico de sinais`.
- Para o tester enxergar contexto, risco e historico, foi necessario trocar manualmente para `Compacto`.

Issue derivada criada:

- `#199` - `P0: Grafico detalhado diverge do Monitor e esconde contexto por padrao`

## Artefatos Locais

- `qa_artifacts/card-75-beta-e2e/01-login.png`
- `qa_artifacts/card-75-beta-e2e/02-monitor.png`
- `qa_artifacts/card-75-beta-e2e/03-sol-expanded.png`
- `qa_artifacts/card-75-beta-e2e/04-chart-modal-sol-current.png`
- `qa_artifacts/card-75-beta-e2e/05-chart-modal-sol-compact.png`
- `qa_artifacts/card-75-beta-e2e/06-login-empty-password-validation.png`

## Decisao Operacional

O card `#75` nao deve ir para `Done` ainda. O fluxo principal foi validado parcialmente, mas permanece bloqueado para beta externo ate resolver a divergencia registrada no `#199`.
