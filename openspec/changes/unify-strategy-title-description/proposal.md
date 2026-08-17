## Why

Favoritos, Monitor e Descoberta apresentam a mesma estratégia com hierarquias e fontes de identidade diferentes: há IDs técnicos, rótulos redundantes e descrições rotuladas como metadado. Isso dificulta reconhecer e comparar uma estratégia entre telas; a issue #549 unifica a leitura no padrão já validado em Combo.

## What Changes

- Usar, nas três superfícies, o nome público canônico como título e a descrição pública canônica imediatamente abaixo.
- Expor `display_name` e `description` em cada linha do leaderboard de Descoberta a partir dos resolvedores públicos já usados por Combo.
- Substituir o `template_id` cru no título de Descoberta, preservando ID do resultado, cobertura e parâmetros como metadados secundários.
- Remover de Favoritos a linha intermediária de detalhe que repete a identidade da estratégia, preservando estados operacionais e métricas.
- Remover em OpportunityCard os prefixos visuais “estratégia” e “descrição”, adotando o mesmo empilhamento título + descrição já existente na lista do Monitor.
- Preservar responsividade, redaction de dados protegidos, ações, métricas e comportamento das três telas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `strategy-template-descriptions`: estende o contrato de identidade pública para o leaderboard de Descoberta e fixa a hierarquia título + descrição, sem linha redundante ou rótulos, em Descoberta, Favoritos e Monitor.

## Impact

- Backend: serialização do leaderboard em `backend/app/services/discovery_service.py`, reutilizando `public_strategy_catalog_name` e `public_strategy_description`.
- Frontend: `DiscoveryPage.tsx`/CSS, `FavoritesDashboard.tsx` e `OpportunityCard.tsx`; `MonitorStatusTab.tsx` serve de padrão já alinhado.
- Contrato de API: adição compatível de `display_name` e `description` às linhas do leaderboard; sem remoção de campos existentes.
- Testes: cobertura de integração do leaderboard e E2E/visual das três superfícies, com atualização intencional dos snapshots afetados.
