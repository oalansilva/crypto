## Why

Ao abrir **Ver logs** na configuração de Combo, o visualizador reapresenta até 400 linhas anteriores do arquivo `full_execution_log`. Alan precisa separar o que começou depois da abertura do modal do histórico acumulado, mas hoje a primeira tela já chega poluída e o conteúdo novo pode ficar fora da área visível.

## What Changes

- Fazer cada abertura do `BackendLogViewer` iniciar uma nova sessão visual vazia, com estado explícito de espera, e mostrar somente bytes gravados depois do cursor capturado na abertura.
- Manter a visualização no final enquanto eventos novos chegam.
- Pausar a aderência automática quando o usuário se afasta manualmente do final e retomá-la quando ele volta ao final ou aciona **Ir para o fim**.
- Reiniciar conteúdo, cursor e estado de rolagem ao fechar e reabrir o modal.
- Evoluir `GET /api/logs/tail` com cursor opcional por offset de bytes e metadados de próximo cursor, preservando integralmente a resposta e o comportamento dos consumidores sem cursor.
- Manter polling de 2 segundos; streaming/SSE não faz parte desta mudança.

## Capabilities

### New Capabilities

- `log-viewer`: sessão de logs iniciada limpa, leitura incremental ordenada e comportamento de rolagem aderente/pausável no visualizador do backend.

### Modified Capabilities

- Nenhuma. A capability existente `logging` descreve a emissão de progresso do Combo Optimizer, não o contrato de leitura incremental nem a interação do visualizador.

## Impact

- Backend: `backend/app/routes/logs.py`, com cursor opcional e compatível no endpoint `/api/logs/tail`.
- Frontend: `frontend/src/components/BackendLogViewer.tsx`; `ComboConfigurePage.tsx` apenas se for necessário ajustar título/copy de acionamento.
- API: adição compatível de `after_offset` e campos de cursor; chamadas atuais com `name`/`lines` continuam retornando o tail existente.
- UX/a11y: novo estado vazio, indicador de rolagem, ação **Ir para o fim**, foco/fechamento do modal e comportamento responsivo.
- Testes: contrato de cursor/rotação no backend e Playwright funcional desktop/mobile para abertura, polling, pause, retomada, fechamento e reabertura.
