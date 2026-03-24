## Context

Hoje a feature de arbitragem está espalhada por múltiplas camadas: rota e página no frontend, item de navegação, endpoint HTTP, serviço de cálculo de spreads, monitor assíncrono inicializado no startup e testes/documentação específicos. Como o produto atual está centrado em Lab, Monitor, Combo, carteira e fluxo operacional, manter essa superfície ativa gera dívida técnica e expectativa errada para usuários e operadores.

Além da remoção visual, a mudança precisa garantir que o backend deixe de inicializar trabalho em background relacionado à arbitragem e que não sobrem contratos públicos parcialmente suportados. Também é importante limpar checklists e testes para que QA e CI não continuem tratando a feature como obrigatória.

## Goals / Non-Goals

**Goals:**
- Remover completamente a superfície ativa de arbitragem do frontend e do backend.
- Encerrar a inicialização automática do monitor de arbitragem no lifecycle da API.
- Eliminar configurações, testes e referências operacionais que assumem arbitragem como capability suportada.
- Deixar uma especificação clara de aposentadoria para evitar reintrodução acidental do fluxo.

**Non-Goals:**
- Substituir arbitragem por uma nova feature equivalente.
- Alterar os workflows suportados que permanecem ativos (Monitor, Lab, Combo, carteira, Kanban, OpenSpec).
- Fazer limpeza ampla de código não relacionado à arbitragem.

## Decisions

### 1. Hard removal em vez de feature flag
**Decisão:** remover rota, página, endpoint, serviços e bootstrap de background em vez de manter a feature atrás de flag.
**Rationale:** a feature não faz mais parte do roadmap ativo; hard removal reduz custo cognitivo, cobertura morta e risco de reativação parcial.
**Alternativas consideradas:**
- Manter código atrás de flag: preserva código ocioso e complexidade no startup/config.
- Ocultar apenas a UI: deixaria endpoint e monitor ativos sem necessidade.

### 2. Endpoint aposentado deve falhar como recurso inexistente
**Decisão:** deixar `/api/arbitrage/spreads` ausente do router para que a resposta padrão seja not-found.
**Rationale:** comunica claramente que a capability foi removida e evita manter um contrato “stubado” sem valor.
**Alternativas consideradas:**
- Responder 410/501 com handler explícito: adiciona código dedicado para um fluxo que queremos eliminar.
- Retornar payload vazio: mascara a remoção e pode prolongar dependências externas.

### 3. Limpeza de inicialização e configuração dedicada
**Decisão:** remover `arbitrage_monitor_enabled`, estado de app associado e serviços dedicados quando não houver outros consumidores.
**Rationale:** a aposentadoria só fica completa se o backend não carregar mais configuração e background jobs específicos.
**Alternativas consideradas:**
- Manter configuração sem uso: deixa resíduo operacional e confunde manutenção.

### 4. Atualização mínima de specs e docs operacionais
**Decisão:** alterar apenas as specs vivas e documentos operacionais que ainda mencionam arbitragem como parte ativa do produto.
**Rationale:** mantém a mudança cirúrgica, alinhada ao escopo pedido, sem reescrever documentação histórica arquivada.
**Alternativas consideradas:**
- Limpeza documental ampla: maior esforço com baixo retorno imediato.

## Risks / Trade-offs

- **[Risk]** Links salvos ou integrações internas ainda chamarem `/arbitrage` ou `/api/arbitrage/spreads` → **Mitigation:** remover explicitamente o surface no frontend/backend e registrar a remoção nas specs/tasks para orientar QA.
- **[Risk]** Sobrar referência indireta ao monitor de arbitragem em startup/config/tests → **Mitigation:** revisar imports, settings, fixtures e testes dedicados antes de considerar a tarefa concluída.
- **[Risk]** A Home/specs continuarem listando arbitragem como destino suportado → **Mitigation:** manter delta explícito em `home` e revisar checklist operacional.
- **[Risk]** Algum serviço reutilizar `arbitrage_spread_service` de forma implícita → **Mitigation:** confirmar referências com busca global antes da remoção física dos arquivos.

## Migration Plan

1. Remover exposição no frontend (`AppNav`, rotas e `ArbitragePage`) e ajustar qualquer título/atalho associado.
2. Remover endpoint, monitor de startup, flag/configuração e serviços dedicados no backend.
3. Atualizar/remover testes, checklist de QA e demais referências operacionais vivas.
4. Validar com busca global por `arbitrage`/`arbitragem` e executar checks direcionados de frontend/backend.

## Open Questions

- Nenhuma decisão funcional em aberto; se surgir dependência externa do endpoint removido, ela deve ser tratada como follow-up separado de comunicação/migração.
