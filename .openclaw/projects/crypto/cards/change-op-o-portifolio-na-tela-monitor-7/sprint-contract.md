# Contrato de sprint

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta sprint
Opção Portifolio na tela Monitor

## Fora de escopo
- Alterar comportamento de ativos nao cripto.
- Alterar a regra para provedores diferentes de Binance.

## Comportamentos esperados
- O Monitor consulta o status canonico em `/api/user/binance-credentials`.
- A classificacao canonica normaliza `cryptomoeda` e `crypto` antes de usar fallback por simbolo.
- A regra derivada considera `configured=true` apenas para ativos `crypto`.
- Quando a regra derivada estiver ativa, o toggle/botao `Portfolio` fica somente leitura na UI.
- O estado exibido em `Portfolio` para ativos `crypto` passa a vir da Carteira Binance (`/api/external/binance/spot/balances?min_usd=0`).
- Quando a carteira estiver vazia ou indisponivel, o Monitor mantém o campo bloqueado e exibe feedback contextual.
- Ativos `stock` continuam com a regra derivada desativada mesmo com Binance configurada.

## Sensores obrigatorios
- `npm --prefix frontend run build`
- `cd frontend && npx tsc --noEmit`
- Playwright direcionado para o Monitor quando houver alteracao visual ou de fluxo.

## Evidencias esperadas
- Typecheck frontend sem erro.
- Build frontend sem erro.
- Cobertura E2E do Monitor mockando o status de credenciais Binance.

## Riscos conhecidos
- O endpoint de credenciais pode falhar; nesse caso o Monitor deve cair para `configured=false`.
- A deteccao nao pode tratar simbolo com `/` como unica fonte se `asset_type` canonico estiver presente.
- O matching entre `symbol` do Monitor e `asset` retornado pela Carteira precisa continuar baseado no ativo-base para nao marcar holdings incorretos.
