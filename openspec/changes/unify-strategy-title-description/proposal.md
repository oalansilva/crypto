## Why

Favoritos, Monitor e Descoberta apresentam a mesma estratégia com hierarquias e fontes de identidade diferentes: há IDs técnicos, rótulos redundantes e descrições rotuladas como metadado. Alan também não consegue ajustar o nome público e a descrição de uma estratégia sem clonar o template ou editar mapas Python. A issue #549 unifica a leitura no padrão Combo **e** permite que o admin edite a identidade pública no resultado do Combo, refletindo em todas as superfícies.

## What Changes

- Admin edita **nome público** e **descrição** no resultado do Combo (lápis inline no bloco de resumo).
- Persistência global em `combo_templates` (`display_name` novo + `description` existente); resolvedor preferindo banco > mapas Python > fallback seguro.
- Usar, nas quatro superfícies de leitura (Combo, Descoberta, Favoritos, Monitor), o mesmo título público + descrição pública imediatamente abaixo.
- Expor `display_name` e `description` em cada linha do leaderboard de Descoberta a partir do resolvedor unificado.
- Substituir o `template_id` cru no título de Descoberta; modal de promover com a mesma identidade.
- Remover de Favoritos a linha intermediária de detalhe redundante; apelido do favorito só como meta secundária.
- Remover em OpportunityCard os prefixos visuais “estratégia” e “descrição”.
- Templates `is_readonly`: identidade editável via endpoint dedicado; lógica/schema continuam bloqueados.
- Preservar responsividade, redaction, ações, métricas e comportamento operacional.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `strategy-template-descriptions`: override persistido editável no Combo; hierarquia título + descrição em Combo, Descoberta, Favoritos e Monitor; paridade pós-save.

## Impact

- Backend: coluna `display_name` em `combo_templates`; `PUT /api/combos/meta/{template_name}/identity` (admin); resolvedor unificado em combo, discovery leaderboard, favorites e opportunities.
- Frontend: `ComboResultsPage.tsx` (lápis admin); `DiscoveryPage.tsx`, `FavoritesDashboard.tsx`, `OpportunityCard.tsx`.
- Contrato de API: campos aditivos no leaderboard; endpoint de identidade separado do PUT técnico.
- Testes: integração identity + paridade; Playwright visual Combo + três superfícies.
