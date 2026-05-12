## Why

A landing atual ja recebeu a primeira revisao de marketing do card #193, mas Alan anexou `refazer.txt` no proprio card pedindo uma reimplementacao completa da pagina. A nova versao precisa seguir essa estrutura: hero com oferta de 6 meses, previa dos melhores ativos, rotina de uso, tela do produto, beneficios, dois sinais, confianca, prova social, FAQ e formulario em 2 passos.

## What Changes

- Reimplementar a variante V4 publicada conforme o conteudo de `refazer.txt` anexado ao card #193.
- Reposicionar o hero para "Saiba quando faz sentido comprar..." com CTA `Quero meus 6 meses grátis`.
- Adicionar blocos de previa dos melhores ativos, rotina, print/tela do produto, beneficios, dois sinais, confianca, prova social, FAQ e formulario em 2 passos.
- Manter copy sobre backtests no historico real da Binance, metricas com explicacao por hover e carteira Binance read-only.
- Preservar o endpoint de leads existente e o guardrail etico de apoio a decisao.
- Atualizar a documentacao da landing com as novas mensagens e criterios.

## Capabilities

### New Capabilities
- `landing-conversion-copy`: Define o conteudo minimo da landing para converter interessados do beta fechado com beneficios concretos, CTA claro e guardrail etico.

### Modified Capabilities

## Impact

- `frontend/public/prototypes/cripto-farol-landing-v4/index.html` (variante publicada em `https://criptofarol.com.br/`)
- `frontend/public/prototypes/cripto-farol-landing-v4/styles.css`
- `docs/landing-page.md`
- Sem alteracao de API, banco ou dependencias.
