## Why

Evitar que a falta de comprovação da execução Codex só bloqueie uma etapa depois do trabalho produzido (#1086).

## Problema

Alan só descobre ao final de uma etapa que o processo não conseguiu comprovar o modelo e o esforço usados pelos agentes Codex, bloqueando trabalho já produzido. No #1086, autor e crítico devolveram os artefatos e o conteúdo foi validado, mas faltou evidência de execução para submeter o Design.

## História

Como operador do Covenant Flow, quero que a comprovação da execução dos agentes Codex seja coletada automaticamente e sua disponibilidade verificada antes de iniciar uma etapa, para não gastar trabalho em um fluxo que só revelará o bloqueio no final.

## Entra

- Antes de iniciar o trabalho delegado ou mover o card para a etapa que depende dele, verificar se o ambiente oferece uma fonte utilizável de evidência de execução. Quando não oferecer, informar o bloqueio e a causa imediatamente, preservando o estado e os artefatos existentes.
- Em uma execução suportada, registrar automaticamente o modelo e o esforço observados, a identidade do agente e da execução, o resultado e a origem verificável da evidência, distinguindo-os da seleção solicitada.
- Vincular a evidência ao nascimento e ao turno corretos do agente; dados de outro agente, outra execução ou uma escolha posteriormente alterada não podem validar o trabalho atual.
- Uma execução concluída com conteúdo retornado e evidência correspondente à seleção solicitada deve passar pela comprovação sem preenchimento manual do operador.
- Evidência ausente, divergente ou que não pertença à execução deve produzir recusa explícita; configuração solicitada e declaração do próprio agente não substituem observação do runtime.
- Demonstrar o caminho positivo no host realmente suportado e os casos de recusa. Testes simulados complementam, mas não substituem, a prova real.
- Documentar capacidades e limitações por host/versão e o caminho de recuperação, preservando artefatos úteis quando a coleta falhar durante uma etapa.

## Não entra

- Corrigir a estratégia Donchian do #1086 ou alterar seu escopo.
- Preencher dados observados copiando os solicitados, transformar ausência de evidência em aprovação ou flexibilizar silenciosamente os gates.
- Trocar modelos, retunar agentes vivos ou encaminhar o trabalho a outro cliente como fallback.
- Alterar os gates humanos, dispensar a crítica de Design ou remover as exigências de sandbox e diff exato do Code Review.
- Ampliar esta correção para os demais adapters.

## What Changes

- Preflight da fonte no host ativo antes da delegação e da transição dependente.
- Coleta automática por nascimento/turno, integrada aos proxies e gates existentes.
- Recusa explícita, recuperação e prova real por host/versão.

## Capabilities

### New Capabilities

- `codex-runtime-evidence`: disponibilidade antecipada, coleta, vínculo e validação da evidência de execução Codex.

### Modified Capabilities

Nenhuma: complementa os contratos existentes de codex-harness e machine-model-selection sem relaxá-los.

## Impact

Adapter Codex em scripts/process-fsm, integração de process_event/guard/orquestração, documentação e testes do harness. Sem alteração de produto, demais adapters ou gates humanos.
