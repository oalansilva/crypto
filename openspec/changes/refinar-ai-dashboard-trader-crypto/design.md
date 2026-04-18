## Context

O `AI Dashboard` já consolidou AI, Signals e On-chain em um único card por ativo e passou a exibir critérios por fonte. O próximo problema deixou de ser puramente técnico: a tela ainda mostra ativos de baixa relevância para decisão, não informa se o sinal é operacionalmente acionável e não deixa suficientemente claro o peso de dados stale ou conflitantes.

Essa mudança é transversal porque afeta o agregador backend, o contrato da API e a forma como a UI prioriza e explica cada oportunidade. O objetivo é elevar a utilidade do dashboard para um trader real sem reescrever os motores que geram sinais nas fontes originais.

## Goals / Non-Goals

**Goals:**
- Priorizar no dashboard principal apenas ativos que façam sentido para decisão de trading.
- Tornar o sinal unificado mais acionável com contexto operacional quando houver dados suficientes.
- Expor frescor, convergência e conflitos entre fontes de forma explícita e legível.
- Preservar compatibilidade progressiva do payload para que a UI degrade com fallback quando campos novos estiverem ausentes.

**Non-Goals:**
- Não criar automação de execução de ordens.
- Não alterar a lógica interna de geração de sinais de AI, Signals ou On-chain.
- Não introduzir ainda performance tracking histórico, PnL consolidado ou backtesting do sinal unificado.
- Não depender de uma watchlist persistida para entregar o primeiro incremento da curadoria.

## Decisions

### 1. Curadoria e ranking devem acontecer no backend

O backend passará a classificar cada ativo em uma camada de exibição (`primary`, `secondary`, `excluded`) usando regras determinísticas. A classificação combinará elegibilidade do ativo, liquidez disponível, convergência entre fontes e recência do dado.

Rationale:
- Mantém uma única verdade de priorização para qualquer cliente.
- Reduz payload irrelevante e evita divergência de regra entre frontend e backend.
- Permite testar a regra de curadoria com integração simples.

Alternativas consideradas:
- Aplicar filtros só no frontend: rejeitado porque duplica regra e mantém payload ruidoso.
- Usar apenas allowlist manual: rejeitado porque é rígido e não reage à disponibilidade real das fontes.

### 2. O contrato unificado deve ter um bloco explícito de actionability

Cada sinal unificado ganhará um bloco `actionability` com campos opcionais como `timeframe`, `valid_until`, `entry_zone`, `invalidation_level`, `target_level`, `risk_label` e `unavailable_reason`. O backend deverá popular esses campos a partir da fonte `Signals` quando disponível e complementar apenas com derivação segura; quando não houver base suficiente, o campo deve continuar visível como indisponível, nunca inventado.

Rationale:
- O trader precisa saber se o sinal serve para ação imediata ou apenas leitura contextual.
- O contrato explícito evita inferências frágeis no frontend.

Alternativas consideradas:
- Renderizar contexto operacional diretamente do card de `Signals`: rejeitado porque quebra a visão unificada.
- Exigir os três campos completos para exibir qualquer sinal: rejeitado porque reduziria demais a cobertura.

### 3. Trust/freshness deve ser modelado por fonte e refletido no score final

Cada item em `sources` deverá incluir `updated_at`, `age_seconds`, `stale`, `coverage_status` e `agreement_to_final`. O sinal consolidado deverá expor `convergence_score`, `confidence_band`, `display_reason` e `warnings`. Fontes stale ou em conflito não devem ser ocultadas; elas devem reduzir a confiança e ficar explícitas na UI.

Rationale:
- O usuário precisa distinguir convicção alta de coincidência parcial ou dado velho.
- Transparência melhora confiança mais do que esconder inconsistências.

Alternativas consideradas:
- Apenas um badge visual simples de confiança: rejeitado porque não explica a origem do score.
- Esconder fontes stale automaticamente: rejeitado porque pode mascarar lacunas operacionais.

### 4. A UI deve separar oportunidades principais de cobertura adicional

A tela deve abrir com foco em `Oportunidades principais`, deixando `Cobertura adicional` atrás de um toggle ou seção secundária com contagem explícita de ativos ocultados. Ativos excluídos por elegibilidade, como stablecoin contra stablecoin, não devem disputar atenção com ativos tradáveis.

Rationale:
- O maior problema de percepção do produto hoje é priorização incorreta.
- Separação visual corrige ruído sem sacrificar acesso a quem quer investigar o universo expandido.

Alternativas consideradas:
- Uma única lista com filtro manual: rejeitado porque transfere a curadoria para o usuário.

## Risks / Trade-offs

- [Risco] Regras de curadoria esconderem ativos que o usuário queria monitorar. -> Mitigação: mostrar contagem de ativos ocultados e permitir abrir cobertura adicional sem remover o dado do payload.
- [Risco] Campo operacional parecer mais preciso do que realmente é. -> Mitigação: popular apenas quando houver origem explícita e mostrar `unavailable_reason` nos demais casos.
- [Risco] Freshness desigual entre fontes gerar ruído visual. -> Mitigação: usar uma taxonomia curta (`fresh`, `aging`, `stale`) e refletir isso no resumo final.
- [Risco] Complexidade crescer no agregador atual. -> Mitigação: isolar classificação, actionability e trust em helpers testáveis sem misturar a lógica-base de unificação.

## Migration Plan

1. Estender o payload backend com os novos blocos opcionais mantendo compatibilidade com o contrato atual.
2. Adaptar a UI para consumir os novos campos com fallback seguro para payloads antigos.
3. Ativar a curadoria padrão na lista principal e expor cobertura adicional na interface.
4. Validar com testes de integração e E2E usando payloads completos, parciais e stale.

Rollback:
- Desabilitar a classificação nova e voltar ao conjunto atual de `recent_signals`.
- Manter a UI em modo compatível usando apenas os campos antigos já existentes.

## Open Questions

- Quais thresholds mínimos de liquidez/volume devem definir `secondary` vs `excluded`?
- O primeiro incremento deve considerar apenas universo automático ou já incluir watchlist explícita do usuário?
- `confidence_band` será exibido em faixas fixas (`Alta`, `Média`, `Baixa`) ou combinado com o score numérico atual?
