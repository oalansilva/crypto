# Recalibrar o gate walk-forward para Treino (IS) e Holdout (OOS)

## Contexto

O gate walk-forward hoje aplica ao Holdout (OOS), que representa 30% da janela, os mesmos mínimos globais de 100 trades e Sharpe 0.8. Isso confunde baixa amostragem esperada do segmento com ausência de evidência e não mede diretamente a degradação entre Treino (IS) e OOS.

**Status observado:** Design  
**UI impact: none.** A mudança altera regra de negócio e o texto dinâmico exibido em blocos já existentes; não cria nem reorganiza superfície visual, componente ou interação.

## Objetivo

Separar a avaliação de IS e OOS, reduzir os mínimos absolutos do OOS de forma controlada e preservar uma evidência out-of-sample obrigatória por meio de um piso próprio e de consistência em relação ao IS.

## Decisões de negócio

### 1. Quantidade de trades no OOS

**DECISÃO:** IS e OOS terão mínimos independentes; trades não serão somados para satisfazer um único mínimo.

- IS mantém o mínimo atual de **100 trades fechados**.
- OOS passa a exigir no mínimo **20 trades fechados**.
- De **20 a 29 trades OOS**, o segmento pode ser aprovado, mas gera aviso de amostra pequena.
- Abaixo de 20 trades OOS, o resultado é NO-GO.

Somar IS+OOS foi rejeitado porque permitiria que uma amostra grande de treino ocultasse um holdout sem evidência suficiente.

### 2. Sharpe no OOS e consistência IS→OOS

**DECISÃO:** IS mantém Sharpe mínimo **0.8**. O OOS deve atender simultaneamente:

1. Sharpe absoluto OOS maior ou igual a **0.30**; e
2. Sharpe OOS maior ou igual a **50% do Sharpe IS**.

Equivalentemente, o limiar efetivo do OOS será `max(0.30, 0.50 × Sharpe IS)`. A igualdade ao limiar é aprovada. Essa regra reduz o piso absoluto do OOS sem aceitar degradação desproporcional em relação ao resultado de treino.

### 3. Significância estatística

**DECISÃO:** t-test não será critério de bloqueio nem substituto da contagem de trades nesta change.

Um t-test simples pressupõe independência e distribuição dos retornos que não estão garantidas em trades de estratégia e tem baixa potência em amostras OOS pequenas. A change mantém um piso observável de trades, adiciona aviso de baixa amostragem e usa consistência de Sharpe. Uma evolução futura poderá avaliar bootstrap ou outro teste robusto com contrato de dados próprio.

### 4. Papel do IS

**DECISÃO:** IS continua bloqueante e conserva todos os critérios atuais de `DEFAULT_CRITERIA`, inclusive 100 trades e Sharpe 0.8. OOS recebe perfil próprio somente para `min_trades` e `min_sharpe_ratio`; os demais critérios atuais continuam aplicáveis ao OOS.

O gate combinado será GO apenas quando IS, OOS e consistência IS→OOS forem aprovados. IS fraco não pode ser compensado por OOS forte, e OOS fraco não pode ser compensado por IS forte.

### 5. Comunicação do resultado

**DECISÃO:** motivos e avisos identificarão o segmento (`Treino (IS)`, `Holdout (OOS)` ou `Consistência IS→OOS`), o valor observado e o limiar aplicável.

Exemplos:

- `Holdout (OOS) — NO-GO: 19 trades fechados; mínimo 20.`
- `Consistência IS→OOS — NO-GO: Sharpe caiu de 0.80 para 0.32 (retenção 40%; mínimo 50%; exigido 0.40).`
- `Holdout (OOS) — aviso: 23 trades; amostra pequena, embora acima do mínimo 20.`
- `GO walk-forward: Treino (IS), Holdout (OOS) e consistência aprovados.`

O override administrativo explícito existente permanece disponível e auditável; esta change não o amplia nem o torna automático.

## Caso de referência: 23 trades e Sharpe OOS 0.32

**DECISÃO: REPROVADO (NO-GO).** Os 23 trades aprovam a contagem OOS e geram aviso de amostra pequena. O Sharpe 0.32 supera o piso absoluto 0.30, mas, como um IS aprovado tem Sharpe de pelo menos 0.80, ele retém no máximo 40% do Sharpe IS e não alcança a retenção mínima de 50%. Para IS=0.80, o limiar OOS efetivo é 0.40.

## Escopo

- Criar perfil de critérios OOS sem alterar `DEFAULT_CRITERIA` global.
- Produzir veredito combinado para IS, OOS e consistência.
- Aplicar o veredito combinado no bloqueio de criação de favorito.
- Tornar razões, avisos e resumo GO legíveis e segmentados.
- Cobrir limites, ausência de métricas e os cenários de regressão do card.

## Fora de escopo

- Alterar a divisão padrão `split_train_ratio=0.7`.
- Introduzir t-test, bootstrap ou nova biblioteca estatística.
- Alterar os demais limiares de qualidade, o fluxo de override administrativo ou a apresentação visual dos blocos de status.
- Criar protótipo ou nova superfície de UI.

## Resultado esperado

O gate deixa de exigir uma amostra OOS equivalente à janela cheia, mas continua fail-closed: exige IS válido, ao menos 20 trades OOS, qualidade OOS mínima e retenção de pelo menos 50% do Sharpe IS. O usuário recebe a causa exata de cada bloqueio sem precisar inferir qual segmento falhou.
