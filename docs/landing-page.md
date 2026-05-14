# Landing Page - Cripto Farol

## Objetivo

Captar interessados para o beta fechado do Cripto Farol com uma pagina simples, clara e pronta para compartilhar por link.

## CTA Principal

**Quero 6 meses grátis**

CTA secundario: **Já tenho acesso**
Link ancora: **Como funciona ↓**

## Estrutura da Pagina

1. Hero
2. Melhores ativos para olhar hoje
3. Como funciona a sua rotina
4. Print/tela do produto
5. Beneficios do beta
6. Os dois sinais
7. Confianca e seguranca
8. Prova social
9. FAQ
10. Formulario de cadastro em 2 passos
11. Guardrail etico

## Copy Base

### Hero

- Headline: **Saiba quando faz sentido comprar e quando faz sentido vender cripto, sem virar trader.**
- Subheadline: O Cripto Farol le o historico real da Binance, compara estrategias e acompanha sua carteira em uma tela so. Acesso gratuito por 6 meses para os primeiros do beta.
- CTA: **Quero meus 6 meses grátis**
- Apoio acima da dobra:
  - 6 meses gratuitos no beta;
  - histórico de mercado da Binance;
  - carteira read-only para acompanhamento.

### Melhores Ativos Para Olhar Hoje

- Previa do beta com cards BTC/USDT em `Compra` e ADA/USDT em `Venda`.
- Outras moedas em monitoramento: ETH, SOL, BNB, LINK, AVAX e MATIC.
- Microcopy deve explicar que a previa e simplificada e que o painel completo mostra contexto e risco em linguagem clara.

### Como Funciona

- Veja primeiro quais moedas merecem atencao.
- Rode backtest no historico real da Binance antes de seguir o sinal atual.
- Experimente o beta por 6 meses sem pagar.

### Print / Tela do Produto

- Mostrar uma previa sanitizada da tela que o usuario vai usar.
- A previa deve mostrar compra, venda e resultado de estrategia no historico da Binance.
- Nao expor parametros internos, valores sensiveis ou controles administrativos.

### Beneficios Comerciais do Card #193

- Backtest dos ativos usando todo o periodo disponivel na Binance.
- Beta gratuito nos primeiros 6 meses para os participantes iniciais.
- Comparacao de estrategias com metricas: Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L e ATR.
- Conexao read-only com carteira Binance para acompanhar saldos e resultados sem ordens ou saques.
- As metricas devem ter explicacao via hover/tooltips quando exibidas como chips.

### Dois Sinais

- `Compra`: ajuda a avaliar melhor momento de entrar e sugere ponto de saida se o mercado virar.
- `Venda`: indica quando pode ser hora de sair, reduzir ou proteger o que o usuario ja tem.

### Confianca e Seguranca

- Leitura objetiva em linguagem simples.
- Menos complexidade para nao depender de interpretacao de grafico ou indicador tecnico.
- API Binance somente leitura; o Cripto Farol nunca movimenta dinheiro, envia ordem ou faz saque.

### Prova Social E FAQ

- Prova social segue a copy enviada em `refazer.txt` ate haver depoimentos reais definitivos.
- FAQ deve responder: necessidade de saber operar, se e robo, acesso ao dinheiro, motivo dos 6 meses gratis, pos-beta e exchanges suportadas.

### Formulario

Fluxo:

- Passo 1 captura nome e email com o botao `Garantir minha vaga`.
- Passo 2 aparece depois e qualifica o lead.
- O envio ao endpoint ocorre no submit final do passo 2.

Campos:

- nome;
- email;
- WhatsApp opcional;
- nivel com cripto;
- principal dificuldade hoje;

## Captacao Operacional

- Formulario da landing envia os leads para o endpoint VPS `http://72.60.150.140:5174/api/leads`.
- O endpoint operacional de leads fica neste repo em `ops/landing-leads/`; o antigo repo/diretorio separado `cripto-farol-landing` nao deve mais ser usado como fonte de codigo.
- Os leads sao gravados em uma planilha `.xlsx` no Google Drive da Clara: `https://docs.google.com/spreadsheets/d/1cWFpAEfbTHcPJ8akzTf-oHRLRS-QmVNf/edit?usp=drivesdk&ouid=109602176178341361243&rtpof=true&sd=true`.
- A cada inscricao, o endpoint tambem envia aviso no topico Telegram do projeto cripto, e-mail para Alan em `o.alan.silva@gmail.com` e e-mail de boas-vindas para o lead com link de acesso.
- Se o e-mail ainda nao existir no sistema, o endpoint cria automaticamente um usuario ativo do beta com senha temporaria aleatoria, salva apenas o hash no banco e envia a senha somente no e-mail de boas-vindas com copia para Alan.
- Observacao tecnica: a API nativa do Google Sheets esta bloqueada no OAuth atual; por isso a integracao usa arquivo `.xlsx` no Drive, atualizado pela VPS.

## Disclaimer

O Cripto Farol e uma ferramenta de apoio a leitura de mercado.
As decisoes de investimento e os riscos continuam sendo do usuario.
Evitar no topo frases defensivas como "sem lucro garantido"; o guardrail deve aparecer de forma discreta no fim da pagina ou em contexto juridico/regulatorio.

## Entregavel Tecnico

Protótipo estatico em:

- `frontend/public/prototypes/cripto-farol-landing/index.html`
- `frontend/public/prototypes/cripto-farol-landing/styles.css`

## Opcao Comparativa V4

Quarta opcao de landing criada para comparacao comercial:

- `frontend/public/prototypes/cripto-farol-landing-v4/index.html`
- `frontend/public/prototypes/cripto-farol-landing-v4/styles.css`
- `frontend/public/prototypes/cripto-farol-landing-v4/rationale.md`

Direcao: rotina curta de decisao, lista de atencao, menos dispersao e acesso ao beta. A versao comparativa V4 usa `Compra` e `Venda` por decisao explicita do Alan, preserva o endpoint de leads e evita expor parametros internos.

## Regra Visual dos Prints

Nao usar screenshots que exponham parametros internos, valores de indicadores, medias moveis ou informacoes que o cliente beta nao tera acesso.

A landing deve mostrar uma previa sanitizada da experiencia: status, leitura de contexto, oportunidade e risco, sem detalhes tecnicos internos.

## Direcao Visual

A landing deve usar azul oceano como base visual, mantendo o amarelo como feixe/CTA. A metafora do farol precisa aparecer de forma clara, com sensacao de mar e um feixe de luz no hero, sem abandonar a percepcao de produto tecnico e confiavel.

## Regra de Status

Nao usar `Espera`/`waiting` na landing. Verificacao no codigo em 2026-05-09 mostrou que o board principal do Monitor exibe `Compra` e `Venda`; `Espera`, `NEUTRAL`, `BUY_SIGNAL` e `BUY_NEAR` ficam ocultos/nao acionaveis na tela principal. A landing deve comunicar dois sinais visiveis: acompanhamento/manutencao (`Compra`) e saida/venda (`Venda`).

## Revisao Card #193

Revisao de marketing para aumentar cadastros:

- CTA principal orientado a beneficio: `Quero 6 meses grátis`.
- Proposta de valor mais concreta antes da primeira rolagem.
- Nova secao `Por que entrar agora` com backtest Binance, 6 meses gratis, metricas e carteira Binance.
- Nova secao de metricas de backtest para tornar o diferencial tangivel.
- Guardrail mantido: ferramenta de apoio a leitura de mercado, sem promessa de lucro.

## Publicacao Atual

Em producao, `https://criptofarol.com.br/` serve a variante `frontend/public/prototypes/cripto-farol-landing-v4/`.
O frontend publico roda via `cripto-farol-frontend.service`, apontando para o frontend deste repo `crypto`.
Mudancas de conversao que precisam aparecer no dominio publico devem ser feitas nesta variante canônica; nao manter copia paralela da landing em repo ou diretorio externo.
