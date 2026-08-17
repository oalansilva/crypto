## ADDED Requirements

### Requirement: Excluir templates de teste Quant e favoritos órfãos
Os templates de teste com nome iniciando em `quant_` SHALL ser excluídos fisicamente da tabela `combo_templates`, e os favoritos que os referenciam SHALL ser excluídos de `favorite_strategies` (sem órfãos no Monitor).

#### Scenario: Exclusão física dos templates
- **WHEN** a rotina de exclusão é executada
- **THEN** todos os templates com nome `quant_*` (case-insensitive) são deletados de `combo_templates`
- **AND** `GET /api/combos/templates` não retorna nenhum template `quant_*`

#### Scenario: Exclusão dos favoritos órfãos
- **WHEN** a rotina de exclusão é executada
- **THEN** todos os favoritos cujo `strategy_name` é um template `quant_*` são deletados de `favorite_strategies`
- **AND** não restam favoritos referenciando templates inexistentes `quant_*`

#### Scenario: Dados de descoberta preservados para auditoria
- **WHEN** a rotina de exclusão é executada
- **THEN** um registro da deleção (nomes e IDs) é gravado antes da exclusão (backup/audit)
- **AND** templates não-Quant e favoritos não-Quant permanecem intactos
