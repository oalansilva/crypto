## Context

O produto ainda expõe a funcionalidade Lab em múltiplas camadas:
- frontend com rotas `/lab` e `/lab/runs/:runId`, links na navegação global e atalhos na Home;
- backend com endpoints `/api/lab`, streaming de logs, trace viewer e serviço de execução dedicado;
- componentes, hooks, tipos e testes específicos do fluxo Lab.

A remoção é um change transversal porque mexe em frontend, backend, navegação, contrato HTTP e cobertura de testes ao mesmo tempo. O objetivo não é substituir o Lab por outro fluxo agora, mas retirar completamente essa superfície do produto sem deixar links quebrados, imports órfãos ou runtime paths mortos.

Restrições:
- manter intactos os fluxos que não dependem do Lab;
- evitar remover infraestrutura compartilhada por engano;
- refletir a remoção no OpenSpec como mudança de capability, não apenas como cleanup de código;
- tratar as rotas/pages do Lab como breaking change explícita.

## Goals / Non-Goals

**Goals:**
- Remover todas as entradas visíveis do Lab no frontend.
- Remover endpoints, serviços e helpers backend exclusivos do Lab.
- Eliminar streaming de logs, trace viewer e tipos/componentes usados apenas pelo Lab.
- Ajustar testes, documentação ativa e referências internas para que o produto continue coerente sem o Lab.

**Non-Goals:**
- Redesenhar a Home além do necessário para remover atalhos do Lab.
- Substituir o Lab por um novo fluxo, wizard ou página alternativa.
- Reestruturar áreas não relacionadas do backend ou da navegação global.
- Limpar artefatos históricos arquivados do OpenSpec que mencionem o Lab.

## Decisions

1. **Remoção completa de superfície, não ocultação**
   - Decisão: remover páginas, rotas, itens de navegação e endpoints do Lab, em vez de apenas esconder links.
   - Rationale: ocultar a entrada deixaria dívida técnica, contratos HTTP ativos e caminhos mortos ainda suportados.
   - Alternativa considerada: manter backend e esconder apenas a UI. Rejeitada porque não remove a capability de fato.

2. **Frontend falha por ausência controlada de rota**
   - Decisão: retirar as rotas `/lab` e `/lab/runs/:runId` do roteador e remover links apontando para elas.
   - Rationale: isso garante que a UI não continue sugerindo um fluxo descontinuado e evita navegação para páginas órfãs.
   - Alternativa considerada: manter rota com placeholder “descontinuado”. Rejeitada porque prolonga uma capability removida.

3. **Backend remove endpoints e helpers exclusivos**
   - Decisão: remover `backend/app/routes/lab.py`, `backend/app/routes/lab_logs_sse.py`, `backend/app/services/lab_graph.py` e `backend/app/trace_viewer.py` se permanecerem exclusivos do Lab, além de desligar seus registros no app principal.
   - Rationale: os specs desta change removem explicitamente run lifecycle, chat inputs, logs e runtime do Lab; o código deve refletir isso.
   - Alternativa considerada: deixar handlers retornando 410/404. Rejeitada como etapa intermediária desnecessária para o escopo atual.

4. **Limpeza por dependência reversa**
   - Decisão: a implementação deve partir dos entrypoints públicos e seguir removendo imports, tipos, componentes, hooks, testes e utilitários que fiquem sem uso.
   - Rationale: começar pelas superfícies públicas reduz o risco de esquecer referências indiretas e facilita validação por build/test.
   - Alternativa considerada: apagar primeiro arquivos internos do Lab. Rejeitada porque tende a quebrar compilação sem um mapa claro do impacto.

5. **Validação por ausência funcional**
   - Decisão: a verificação principal será provar que o produto compila/roda sem qualquer referência ativa ao Lab e que Home/nav não o expõem mais.
   - Rationale: para uma remoção, o critério central é ausência coerente da capability, não novo comportamento positivo.
   - Alternativa considerada: validar só por diff estático. Rejeitada porque não garante que rotas, imports e testes foram reconciliados.

## Risks / Trade-offs

- [Remover arquivo compartilhado por engano] → Mitigação: confirmar antes se cada módulo é exclusivo do Lab e preservar utilitários usados por outros fluxos.
- [Sobrar link, import ou teste quebrado] → Mitigação: buscar referências textuais a `lab`, rodar build/testes relevantes e corrigir resíduos no mesmo change.
- [Clientes internos ainda chamarem `/api/lab`] → Mitigação: tratar a remoção como breaking change explícita no proposal/specs e alinhar documentação ativa.
- [Home/nav perderem equilíbrio visual após remover atalhos] → Mitigação: limitar a mudança visual ao rebalanceamento mínimo de shortcuts existentes, sem redesign amplo.

## Migration Plan

1. Remover referências de navegação e rotas do frontend para `/lab`.
2. Remover páginas, componentes, hooks e tipos exclusivos do Lab.
3. Remover registro e implementação das rotas/backend services exclusivos do Lab.
4. Remover ou ajustar testes que dependem do fluxo Lab.
5. Rodar validações de build/test para confirmar que não há imports órfãos nem referências runtime ao Lab.

Rollback:
- se a remoção causar regressão inesperada, restaurar os entrypoints do frontend e backend em um revert único desta change.

## Open Questions

- Algum endpoint ou artefato de logs do Lab ainda é consumido por tooling operacional externo fora do frontend atual?
- Há necessidade de manter redirecionamento amigável para `/lab`, ou a ausência da rota é suficiente?
- Os arquivos históricos em `backend/logs/lab_runs` e `backend/data/jobs` devem permanecer como evidência técnica ou entrar em limpeza posterior?
