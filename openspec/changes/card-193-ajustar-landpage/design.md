## Context

A landing do Cripto Farol ja tem marca, hero, explicacao do Monitor e formulario funcional de leads. O card #193 pede uma revisao de marketing para deixar mais claras solucoes que o sistema oferece: backtest historico em Binance, gratuidade inicial, metricas de escolha de estrategias e conexao com carteira Binance.

## Goals / Non-Goals

**Goals:**
- Aumentar a chance de cadastro com uma proposta de valor mais especifica antes do primeiro CTA.
- Tornar os quatro itens do card #193 visiveis em blocos escaneaveis.
- Preservar a identidade visual vigente: azul oceano, amarelo de CTA/feixe, cards de raio curto e linguagem sem hype.
- Manter o formulario e endpoint de lead existentes.

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

## Risks / Trade-offs

- [Risk] Copy comercial soar como promessa de resultado.
  - Mitigation: usar "apoio", "comparar", "acompanhar" e manter disclaimer etico.
- [Risk] Excesso de metricas tecnicas reduzir clareza para iniciantes.
  - Mitigation: apresentar metricas como criterio de comparacao e explicar em uma frase simples.
- [Risk] Citar carteira Binance gerar medo de seguranca.
  - Mitigation: explicitar conexao read-only e sem ordens/saques.
