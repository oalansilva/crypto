# Design — gate combinado de Treino (IS) e Holdout (OOS)

## Classificação

- Card: `#503`
- Change: `card-503-holdout-oos`
- Status observado: `Design`
- **UI impact: none.** A entrega muda critérios e mensagens dinâmicas em blocos já existentes. Não há nova superfície, layout, componente, estado interativo ou navegação.

## Problema

O Holdout (OOS) contém apenas 30% da janela, mas é avaliado com os mesmos mínimos absolutos da janela cheia. O mínimo de 100 trades penaliza a divisão por construção; ao mesmo tempo, apenas reduzir 100 e 0.8 poderia enfraquecer a proteção contra overfitting. O gate também não expressa de forma direta quanto o desempenho degradou de IS para OOS.

## Hipótese

Separar os perfis de IS e OOS, mantendo IS rigoroso e exigindo no OOS um piso absoluto mais uma retenção relativa de Sharpe, reduz falsos NO-GO por tamanho do holdout sem permitir que uma estratégia sem evidência out-of-sample seja aprovada.

## Resultado esperado

- IS continua sendo uma barreira independente com os critérios atuais.
- OOS pode demonstrar evidência com 20 ou mais trades, sem precisar replicar o volume da janela cheia.
- A degradação IS→OOS fica explícita e bloqueia quando o OOS preserva menos de 50% do Sharpe IS.
- Todo resultado identifica segmento, valor observado e limiar.
- O fluxo continua fail-closed diante de dados ausentes, inválidos ou de qualquer segmento reprovado.

## Decisões

### Perfis de critérios

| Critério | Treino (IS) | Holdout (OOS) | Comportamento |
| --- | ---: | ---: | --- |
| `min_trades` | 100 | 20 | Inclusivo; somente trades fechados |
| aviso de amostra pequena | N/A | 20–29 | Não bloqueia; mensagem explícita |
| `min_sharpe_ratio` absoluto | 0.80 | 0.30 | Inclusivo |
| retenção Sharpe IS→OOS | N/A | 50% do IS | Bloqueante e inclusivo |
| demais `DEFAULT_CRITERIA` | atuais | atuais | Sem mudança nesta change |

O limiar de Sharpe OOS é:

```text
required_oos_sharpe = max(0.30, 0.50 * is_sharpe)
```

O perfil OOS deve ser uma cópia/override explícito. `DEFAULT_CRITERIA` e o comportamento de avaliações não walk-forward não serão alterados.

### Composição do veredito

O gate walk-forward deverá avaliar separadamente:

1. `is_result = evaluate_go_nogo(is_metrics, DEFAULT_CRITERIA)`;
2. `oos_result = evaluate_go_nogo(oos_metrics, OOS_CRITERIA)`;
3. consistência de Sharpe entre os dois segmentos;
4. composição final, com GO somente se os três resultados forem aprovados.

A implementação deve preferir um helper puro e nomeado para a composição walk-forward, mantendo `evaluate_go_nogo` genérico. O ponto atual em `combo_optimizer.py` que avalia apenas `oos_metrics` passa a fornecer IS e OOS ao helper combinado. O consumidor de bloqueio em `walk_forward_revalidation.py` continua recebendo um `CriteriaResult` final e o override administrativo atual permanece inalterado.

Para evitar uma migração de contrato sem relação com o card, nomes serializados legados como `oos_verdict` podem ser preservados nesta change, desde que o conteúdo seja documentado como veredito final walk-forward e as razões tragam o segmento. Uma renomeação de API/persistência fica fora de escopo.

### Ordem e legibilidade das mensagens

As mensagens devem ser determinísticas e agrupadas nesta ordem:

1. falhas de `Treino (IS)`;
2. falhas de `Holdout (OOS)`;
3. falha de `Consistência IS→OOS`;
4. avisos por segmento.

Cada mensagem inclui nome do segmento, valor observado e mínimo exigido. Falhas simultâneas de Sharpe absoluto e relativo podem ser consolidadas em uma única razão OOS/consistência, sem esconder nenhum limiar. Valores de Sharpe usam duas casas e retenção usa percentual inteiro nos textos.

Exemplos normativos de conteúdo:

```text
Treino (IS) — NO-GO: 87 trades fechados; mínimo 100.
Holdout (OOS) — NO-GO: Sharpe 0.28; mínimo absoluto 0.30.
Consistência IS→OOS — NO-GO: Sharpe caiu de 0.80 para 0.32 (retenção 40%; mínimo 50%; exigido 0.40).
Holdout (OOS) — aviso: 23 trades; amostra pequena, embora acima do mínimo 20.
GO walk-forward: Treino (IS), Holdout (OOS) e consistência aprovados.
```

### Significância estatística

Não será calculado t-test nesta change. Contagem mínima e Sharpe não são declarados como prova estatística completa; são guardrails operacionais. Um t-test paramétrico simples foi rejeitado porque dependência serial, assimetria e baixa amostragem podem tornar o p-value enganoso. Avaliar bootstrap ou teste robusto requer change própria e dados de retorno por trade explicitamente contratados.

## Regras de borda

- **IS aprovado + OOS com 19 trades:** NO-GO por amostra OOS insuficiente.
- **IS aprovado + OOS com 20–29 trades:** a contagem aprova e gera aviso; os demais critérios ainda podem bloquear.
- **IS aprovado + OOS Sharpe abaixo de 0.30:** NO-GO pelo piso absoluto.
- **IS aprovado + OOS Sharpe acima de 0.30, mas abaixo de 50% do IS:** NO-GO por degradação.
- **IS fraco + OOS forte:** NO-GO pelo IS; OOS não compensa treino inválido.
- **IS forte + OOS fraco:** NO-GO pelo OOS e/ou consistência; IS não compensa holdout inválido.
- **Métrica obrigatória ausente, `null`, `NaN` ou infinita:** NO-GO fail-closed, identificando segmento e métrica.
- **IS Sharpe não positivo ou inválido:** IS já reprova; a razão de retenção não é calculada para evitar percentual enganoso.
- **Valor exatamente no limite:** aprovado (`trades >= mínimo`, `Sharpe >= mínimo`, retenção `>= 50%`).
- **Múltiplas falhas:** todas as razões relevantes são preservadas e ordenadas; não parar no primeiro erro.
- **Override administrativo:** continua exigindo admin e ação explícita; não altera o cálculo nem apaga as razões do NO-GO.

## Caso de referência

Para OOS com **23 trades e Sharpe 0.32**, assumindo qualquer IS aprovado:

- contagem OOS: aprovada, com aviso de amostra pequena;
- piso absoluto OOS: aprovado (`0.32 >= 0.30`);
- consistência: reprovada, pois IS aprovado tem Sharpe `>= 0.80`, logo a retenção é no máximo 40%, abaixo dos 50%;
- resultado final: **NO-GO**.

Com IS=0.80, a mensagem deve informar limiar efetivo OOS 0.40 e retenção 40%.

## Riscos e mitigações

| Risco | Severidade | Mitigação |
| --- | --- | --- |
| 20 trades ainda produzem estimativa ruidosa | Média | IS independente com 100 trades, aviso entre 20–29, critérios OOS restantes e retenção de Sharpe |
| Reduzir mínimos globalmente afeta avaliações fora do walk-forward | Alta | Não alterar `DEFAULT_CRITERIA`; usar perfil OOS explícito |
| IS muito alto eleva bastante o limiar relativo OOS | Média | Comportamento intencional para detectar possível overfitting; mensagem mostra o limiar calculado |
| Dados ausentes poderiam liberar o gate por comparação inválida | Alta | Normalização fail-closed para valores ausentes/não finitos |
| Campo legado `oos_verdict` passa a carregar decisão combinada | Baixa | Preservar compatibilidade nesta change e documentar semântica; renomear em change própria |
| Mensagens duplicadas tornam o bloqueio difícil de entender | Média | Agrupar por segmento, ordenar e consolidar falhas de Sharpe sem perder valores |

## Design Critique

### Avaliação

- **Produto:** a primeira versão possível — apenas baixar 100 para 20 e 0.8 para 0.3 — enfraqueceria o gate. O desenho foi corrigido para manter IS bloqueante e adicionar retenção de 50%.
- **Escopo:** alterar `DEFAULT_CRITERIA` seria regressivo para avaliações não walk-forward. A decisão final isola o perfil OOS e mantém os demais critérios.
- **Risco operacional:** amostras de 20–29 trades são ruidosas. O risco permanece não bloqueante porque há aviso explícito, IS com 100 trades, piso OOS e consistência relativa.
- **Integridade:** o desenho é fail-closed para métricas ausentes/não finitas e não permite compensação entre segmentos.
- **Comunicação:** prefixos por segmento e valores observado/exigido resolvem a ambiguidade das mensagens atuais. A implementação deve evitar duplicar duas razões de Sharpe sem contexto.
- **Superfície visual:** confirmado que nenhuma superfície visual nova ou reorganização foi deixada sem classificação. Somente o conteúdo textual dinâmico de blocos existentes muda.

### Findings

- **P1 — resolvido no design:** redução isolada do mínimo OOS enfraqueceria a proteção. Resolvido com IS independente, piso OOS e retenção de Sharpe.
- **P1 — resolvido no design:** mutação do critério global causaria regressões fora do walk-forward. Resolvido com perfil OOS local.
- **P2 — aceito:** o limiar de 20 trades mantém incerteza entre 20–29. Aceito com aviso obrigatório e guardrails combinados; validar por dados reais após adoção.
- **P2 — diferido:** significância por retorno não é coberta. Um teste paramétrico sem contrato de dados seria falsa precisão; requer change própria.

Referências avaliadas: `proposal.md`, este `design.md`, `specs/walk-forward-oos-gate/spec.md` e `tasks.md`.  
Prototype: N/A — regra de negócio sem nova superfície visual.

## Prototype

N/A — `UI impact: none`; não há layout, interação ou componente novo a prototipar. As mensagens serão renderizadas nos blocos existentes.

## Prototype Validation

N/A — nenhum protótipo foi criado para esta mudança de regra de negócio; browser gate de design não se aplica. A legibilidade das mensagens será validada por asserts unitários do conteúdo e pelo QA funcional posterior, sem substituir os gates obrigatórios do card.

## Impeccable Brief

N/A — `UI impact: none`; não existe direção visual ou interação a modelar.

## Impeccable Critique

N/A — `UI impact: none`; não há superfície visual para Assessment A/B. A crítica de produto, escopo, regressão e risco operacional está em `Design Critique`.

## Impeccable Audit

N/A — `UI impact: none`; acessibilidade visual, responsividade, theming e performance de interface não são alterados.

## Impeccable Trace

N/A — `UI impact: none`; pipeline e protótipo Impeccable não foram executados, conforme classificação justificada.

## Handoff

- Entrega pronta para a sessão principal consolidar e, sem autoaprovação, solicitar `Aprovação de Design` a Alan.
- Desenvolvimento permanece proibido até Alan mover o card para `Pronto para Dev`.
- Prototype: N/A.
- Pendências aceitas: incerteza de amostra entre 20–29 trades e avaliação estatística robusta futura.

**Design Agent verdict: PASS**
