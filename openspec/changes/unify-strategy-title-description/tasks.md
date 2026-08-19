# Tasks: unify-strategy-title-description

## 0. Backend — identidade persistida

- [x] 0.1 Migration: `combo_templates.display_name` nullable
- [x] 0.2 `PUT /api/combos/meta/{template_name}/identity` (admin); aceita templates `is_readonly`; validação nome/descrição não vazios
- [x] 0.3 Resolvedor banco > mapa > fallback; override pareado `display_name` + `description` no catálogo
- [x] 0.4 Testes: save identity readonly, validação vazia, paridade serialização (unit)

## 1. Frontend — Combo edit (identidade)

- [x] 1.1 `/combo/edit/{template}`: campos título público + descrição; Salvar chama `PUT .../identity`
- [x] 1.2 Templates `is_readonly` abrem o editor de identidade (sem wall de clone); JSON/ranges bloqueados
- [x] 1.3 `data-testid`: `combo-edit-identity`, `combo-identity-title-input`, `combo-identity-description-input`, `combo-identity-save`
- [x] 1.4 Combo select: título = `display_name`; botão Edit abre `/combo/edit` também para readonly
- [x] 1.5 Combo resultado: leitura apenas (sem lápis)

## 2. Backend — leaderboard identity fields

- [x] 2.1 Adicionar `display_name` e `description` em `_result_row` via resolvedor unificado
- [x] 2.2 Fallback nome cru + descrição segura para templates sem mapa (sem genérico `Estratégia Cripto Farol`)
- [x] 2.3 Testes de integração: campos aditivos, fallback, compatibilidade rank/filtro/promoção

## 3. Frontend — Descoberta

- [x] 3.1 Leaderboard: renderizar título + descrição; `template_id` só em meta
- [x] 3.2 Modal promover: mesmo título + descrição (não `template_id`)
- [x] 3.3 CSS: largura máxima candidato, wrap copy longa

## 4. Frontend — Favoritos

- [x] 4.1 Tabela desktop: um título + descrição; remover linha intermediária redundante
- [x] 4.2 Card mobile: mesma hierarquia; apelido do favorito como meta secundária
- [x] 4.3 Preservar refresh, tier, métricas e ações

## 5. Frontend — Monitor

- [x] 5.1 OpportunityCard expandido: remover prefixos `estratégia` / `descrição`
- [x] 5.2 Lista e detalhe: título + descrição alinhados ao padrão Combo
- [x] 5.3 Metadados operacionais (tf, candle, alerta) separados

## 6. QA

- [x] 6.1 Playwright visual: Combo edit (identidade), Combo select, Descoberta, Favoritos, Monitor
- [x] 6.2 Validar paridade `multi_ma_crossover` entre Combo select, Combo resultado, Descoberta, Favoritos e Monitor
- [ ] 6.3 `qa-gate` verde
