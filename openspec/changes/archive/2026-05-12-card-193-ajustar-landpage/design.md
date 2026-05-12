## Context

A landing do Cripto Farol ja tem marca, hero, explicacao do Monitor e formulario funcional de leads. O card #193 pede uma revisao de marketing para deixar mais claras solucoes que o sistema oferece: backtest historico em Binance, gratuidade inicial, metricas de escolha de estrategias e conexao com carteira Binance. Apos a primeira entrega, Alan anexou `refazer.txt` no card solicitando uma reimplementacao completa da landing V4 publicada.

Confirmacao pos-publicacao: o dominio `https://criptofarol.com.br/` serve a variante `cripto-farol-landing-v4/`. Portanto a revisao de conversao precisa estar tanto no prototipo base quanto na V4 publicada.

## Goals / Non-Goals

**Goals:**
- Aumentar a chance de cadastro com uma proposta de valor mais especifica antes do primeiro CTA.
- Seguir a estrutura de `refazer.txt`: hero, previa de ativos, rotina, tela do produto, beneficios, sinais, confianca, prova social, FAQ e formulario.
- Preservar a identidade visual vigente: azul oceano, amarelo de CTA/feixe, cards de raio curto e linguagem sem hype.
- Manter o endpoint de lead existente com um fluxo visual de formulario em 2 passos.

**Non-Goals:**
- Criar nova rota React ou backend.
- Alterar a regra de acesso do beta.
- Prometer rentabilidade, recomendacao financeira ou operacao automatica na Binance.

## Decisions

- D1: Atualizar o hero com oferta objetiva e microcopy de gratuidade.
  - Rationale: o usuario precisa entender rapidamente o ganho de entrar na lista.
  - Alternative considered: deixar beneficios apenas no meio da pagina; rejeitado porque enfraquece conversao acima da dobra.
- D2: Criar uma faixa de beneficios com os quatro pontos do card.
  - Rationale: cards curtos sao mais escaneaveis que paragrafos longos e ajudam a responder "por que me cadastrar?".
- D3: Adicionar uma secao "O que voce testa" com metricas de backtest e carteira Binance.
  - Rationale: os itens tecnicos precisam parecer produto real, nao jargao solto.
- D4: Manter linguagem de apoio a decisao e API read-only para a carteira.
  - Rationale: evita promessa de lucro e reduz risco de interpretaçao como robo de trade.
- D5: Refletir a mesma proposta na variante V4 publicada.
  - Rationale: o dominio publico aponta para V4; alterar apenas o prototipo base nao muda a experiencia real.
- D6: Implementar a "tela do produto" como previa sanitizada em HTML/CSS.
  - Rationale: nao ha screenshot real novo no card; a previa evita expor parametros internos e segue a regra visual existente.
- D7: Transformar o formulario em 2 passos no cliente, enviando ao endpoint apenas no submit final.
  - Rationale: o backend atual possui um unico endpoint de lead; dividir a UI melhora qualificacao sem mudar contrato de API.
- D8: Usar tooltips nativos (`title`) para explicar metricas.
  - Rationale: atende a exigencia de explicacao ao passar o mouse sem adicionar dependencia ou UI complexa.

## Risks / Trade-offs

- [Risk] Copy comercial soar como promessa de resultado.
  - Mitigation: usar "apoio", "comparar", "acompanhar" e manter disclaimer etico.
- [Risk] Excesso de metricas tecnicas reduzir clareza para iniciantes.
  - Mitigation: apresentar metricas como criterio de comparacao e explicar em uma frase simples.
- [Risk] Citar carteira Binance gerar medo de seguranca.
  - Mitigation: explicitar conexao read-only e sem ordens/saques.
- [Risk] Prova social com nomes genericos parecer depoimento definitivo.
  - Mitigation: usar a copy recebida em `refazer.txt` e manter a secao como conteudo de beta, sem ampliar a promessa.
