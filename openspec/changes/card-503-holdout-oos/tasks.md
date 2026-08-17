# Tasks — card 503 holdout OOS

## 1. Critérios e composição do gate

- [x] 1.1 Definir perfil OOS explícito com `min_trades=20` e `min_sharpe_ratio=0.30`, preservando uma cópia dos demais `DEFAULT_CRITERIA` sem mutar o default global.
- [x] 1.2 Implementar helper puro de avaliação walk-forward que receba `is_metrics` e `oos_metrics`, avalie os segmentos separadamente e componha um único `CriteriaResult` fail-closed.
- [x] 1.3 Adicionar critério bloqueante de retenção `oos_sharpe >= 0.50 * is_sharpe`, com limiar efetivo `max(0.30, 0.50 * is_sharpe)` e limites inclusivos.
- [x] 1.4 Tratar métricas obrigatórias ausentes, nulas, `NaN` ou infinitas como NO-GO segmentado; não calcular percentual de retenção quando Sharpe IS for inválido ou não positivo.
- [x] 1.5 Adicionar aviso não bloqueante para OOS entre 20 e 29 trades fechados.

## 2. Integração walk-forward

- [x] 2.1 Substituir a avaliação isolada de `oos_metrics` no combo optimizer pela avaliação combinada de IS, OOS e consistência.
- [x] 2.2 Preservar o contrato consumido pelo bloqueio de favorito, documentando a semântica combinada caso o nome legado `oos_verdict` seja mantido.
- [x] 2.3 Confirmar que NO-GO combinado continua bloqueando sem override e que somente admin com override explícito segue pelo fluxo atual.
- [x] 2.4 Confirmar que avaliações não walk-forward continuam usando `DEFAULT_CRITERIA` inalterado.

## 3. Mensagens

- [x] 3.1 Prefixar razões e avisos com `Treino (IS)`, `Holdout (OOS)` ou `Consistência IS→OOS`.
- [x] 3.2 Incluir valor observado, limiar e, para degradação, Sharpe IS, Sharpe OOS, retenção e Sharpe OOS exigido.
- [x] 3.3 Ordenar razões por IS, OOS e consistência; preservar múltiplas falhas sem duplicação confusa.
- [x] 3.4 Adicionar resumo GO que confirme aprovação de IS, OOS e consistência.

## 4. Testes unitários obrigatórios

- [x] 4.1 Cobrir **IS ok + OOS poucos trades**: 19 trades retorna NO-GO; 20–29 aprova a contagem e gera aviso.
- [x] 4.2 Cobrir **IS ok + OOS Sharpe baixo**: Sharpe 0.29 retorna NO-GO pelo piso absoluto 0.30.
- [x] 4.3 Cobrir **degradação IS→OOS acima do tolerado**: IS 1.00 e OOS 0.45 retornam NO-GO, retenção 45% e limiar 0.50.
- [x] 4.4 Cobrir o caso de referência: IS 0.80, OOS com 23 trades e Sharpe 0.32 retorna NO-GO por retenção 40%, com aviso de amostra pequena.
- [x] 4.5 Cobrir limite aprovado: IS 0.80 e OOS 0.40 com 20 trades aprova os critérios de trades e Sharpe, sujeito aos demais critérios.
- [x] 4.6 Cobrir **IS fraco + OOS ok** e **IS ok + OOS fraco**, garantindo que um segmento não compensa o outro.
- [x] 4.7 Cobrir valores ausentes/não finitos e confirmar comportamento fail-closed.
- [x] 4.8 Cobrir ordem, prefixos e conteúdo legível das razões, avisos e resumo GO.
- [x] 4.9 Cobrir que o override administrativo existente não muda de autorização e preserva as razões originais.
- [x] 4.10 Cobrir regressão: `DEFAULT_CRITERIA` e avaliações fora do walk-forward permanecem inalterados.

## 5. Validação e handoff

- [x] 5.1 Executar os testes unitários focados de métricas e walk-forward após a implementação.
- [x] 5.2 Validar a change OpenSpec e reconciliar implementação, specs e tasks.
- [x] 5.3 Registrar evidência da aprovação humana de Design antes de iniciar `/opsx:apply` ou editar código de produção.
- [ ] 5.4 Executar o QA visual obrigatório do card ou registrar dispensa válida de Alan, mesmo com `UI impact: none`, conforme o fluxo do projeto.
- [x] 5.5 Registrar no handoff que t-test/bootstrap ficou fora de escopo e que 20–29 trades produz aviso de baixa amostragem.
