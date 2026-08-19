# Tasks: unify-strategy-title-description

## 0. Backend — identidade persistida

- [x] 0.1 Migration: `combo_templates.display_name` nullable
- [x] 0.2 `PUT /api/combos/meta/{template_name}/identity` (admin); aceita templates `is_readonly`; validação nome/descrição não vazios
- [x] 0.3 Resolvedor banco > mapa > fallback; override pareado `display_name` + `description` no catálogo
- [x] 0.4 Testes: save identity readonly, validação vazia, paridade serialização (unit)

## 1. Frontend — Combo resultado (edição)

- [x] 1.1 Lápis admin no bloco `combo-result-summary`; modo inline título + descrição; Salvar/Cancelar
- [x] 1.2 Chamar endpoint identity; atualizar UI local após sucesso; ocultar lápis para não-admin
- [x] 1.3 `data-testid`: `combo-edit-identity`, `combo-identity-title-input`, `combo-identity-description-input`, `combo-identity-save`, `combo-identity-cancel`
- [x] 1.4 Combo select (`/combo/select`): título = `display_name` resolvido; descrição pública abaixo; `name` técnico só como chave/meta

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

- [x] 6.1 Playwright visual: Combo (lápis/edição), Combo select, Descoberta, Favoritos, Monitor (baselines intencionais)
- [x] 6.2 Validar paridade `multi_ma_crossover` entre Combo select, Descoberta, Favoritos e Monitor (override pós-save já coberto pelo fluxo Combo resultado + resolvedor global)
- [ ] 6.3 `qa-gate` verde
