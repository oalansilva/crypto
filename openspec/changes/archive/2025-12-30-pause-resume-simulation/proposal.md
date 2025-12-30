# Proposta: Pausar e Continuar Simulação

## Contexto
Usuários executando otimizações de backtest longas (ex: milhares de combinações) enfrentam perda de dados se a simulação for interrompida ou travar. Atualmente, não há como pausar o processo para liberar recursos ou lidar com desligamentos inesperados sem reiniciar do zero.

## Objetivo
Implementar um mecanismo robusto para:
1.  **Pausar** uma simulação em execução via API ou UI.
2.  **Persistir** o progresso intermediário e resultados em disco.
3.  **Continuar** a simulação a partir do último estado salvo.
4.  **Auto-checkpoint** do progresso para minimizar perda de dados durante travamentos.

## Escopo
*   **Backend**: Modificação no `BacktestService` para suportar loops de interrupção, `JobManager` para persistência de estado.
*   **API**: Endpoints para `/pause`, `/resume`, `/status`.
*   **Frontend**: Controles de UI para Pausar/Continuar e prompts de recuperação de progresso.

## Critérios de Sucesso
*   Usuários podem pausar um backtest em execução e retomá-lo mais tarde, mesmo após reinício do servidor.
*   Resultados gerados antes da pausa são preservados e disponíveis no relatório final.
*   O sistema detecta automaticamente trabalhos interrompidos e oferece a opção de retomá-los.
