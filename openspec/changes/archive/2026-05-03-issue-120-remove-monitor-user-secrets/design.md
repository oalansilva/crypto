## Context

O backend já redige oportunidades de usuário comum com `is_strategy_protected=true`, `parameters={}` e `indicator_values=null`. Mesmo assim, o frontend ainda renderiza os blocos `Parâmetros` e `Indicadores` no detalhe expandido, exibindo uma linha `Protegido/Oculto`. A solicitação do card 120 pede remover esses dados da tela do usuário comum e manter para administrador.

## Goals / Non-Goals

**Goals:**
- Remover os blocos técnicos do detalhe expandido para usuário comum.
- Remover controles de operação técnica do detalhe protegido para usuário comum.
- Travar a leitura no timeframe da estratégia para usuário comum protegido.
- Manter a experiência administrativa completa.
- Não mudar payload, cálculo, filtros ou permissões backend.

**Non-Goals:**
- Não remover nome público da estratégia.
- Não alterar o modal do gráfico.
- Não criar nova preferência de usuário.

## Decisions

- Passar `isAdmin` de `MonitorStatusTab` para `OpportunityCard`.
  - Racional: `MonitorStatusTab` já usa `useAuth()` e calcula visibilidade admin da tabela.
- Renderizar `Parâmetros` e `Indicadores` apenas quando `isAdmin` for verdadeiro ou a oportunidade não estiver protegida.
  - Racional: preserva informação completa para admin e evita placeholders técnicos para usuário comum.
- Renderizar ações (`Exportar`, `Reavaliar`, `Ver gráfico`, `Confirmar gestão`), alternância `Price/Strategy` e seleção 15m/1h/4h apenas quando detalhes técnicos forem permitidos.
  - Racional: esses controles alteram ou expõem operação técnica que o usuário comum não deve reproduzir fora do sistema.
- Para detalhe protegido de usuário comum, exibir `chart <timeframe da estratégia>`.
  - Racional: evita sugerir análise em timeframes alternativos que não fazem parte da estratégia exibida.
- Manter exportação sem segredos para oportunidade protegida.
  - Racional: o payload exportado já omite `parameters` e `indicator_values` quando protegido.

## Risks / Trade-offs

- [Risk] Usuário comum perde confirmação visual de que dados estão ocultos.
  - Mitigation: o detalhe continua mostrando estratégia pública, status, preço, risco e ações úteis.
- [Risk] Testes que procuram `Parâmetros`/`Indicadores` no card protegido podem falhar.
  - Mitigation: atualizar/adicionar cobertura focada em perfil comum se necessário.
