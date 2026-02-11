# Design

## Overview
Adicionar `create_template` no `ComboService` para transformar um `strategy_draft` em um template persistido no banco `combo_templates`.

## Key decisions
- Reusar `save_template` internamente para persistência.
- Normalizar `stop_loss` para float default se não vier no draft.
- Gerar `entry_logic`/`exit_logic` a partir de `entry_idea`/`exit_idea` do draft (string direta na primeira versão).

## Components
- `ComboService.create_template` (novo método)
- Conversor no fluxo de upstream (onde hoje chama `create_template`)

## Data flow
1. Upstream aprova strategy_draft.
2. Conversor monta payload (`name`, `description`, `indicators`, `entry_logic`, `exit_logic`, `stop_loss`).
3. `create_template` salva via `save_template`.
4. Retorna metadados e segue para seed selection.

## Error handling
- Validar campos obrigatórios: `name`, `indicators`, `entry_logic`, `exit_logic`.
- Lançar `ValueError` com mensagem clara e logar erro.

## Tests
- Unit test para `create_template` com draft válido.
- Unit test para draft inválido.
