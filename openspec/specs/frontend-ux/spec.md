# frontend-ux Specification

## Purpose
TBD - created by archiving change pause-resume-simulation. Update Purpose after archive.
## Requirements
### Requirement: Controle via UI
A interface DEVE (MUST) fornecer mecanismos claros para o usuário interromper e controlar a execução.

#### Scenario: Controle de Pausa
> Como um usuário
> Eu quero pausar uma simulação em execução
> Para que eu possa liberar recursos do meu computador

- A barra de progresso DEVE exibir um botão [PAUSAR] quando uma simulação estiver `RUNNING` (Rodando) ou `OPTIMIZING` (Otimizando).
- Clicar em [PAUSAR] DEVE enviar uma requisição para `/api/backtest/pause/{id}` e atualizar o status da UI para `PAUSING...` (Pausando) e então `PAUSED` (Pausado).

### Requirement: Notificação de Retomada
O sistema DEVE (MUST) informar proativamente o usuário sobre trabalhos pendentes ou interrompidos.

#### Scenario: Prompt de Retomada
> Como um usuário
> Eu quero saber se tenho simulações não finalizadas
> Para que eu possa escolher retomá-las

- Ao carregar a aplicação, o sistema DEVE verificar se há jobs com status `PAUSED` ou `RUNNING` (interrompidos).
- Se um job pausado for encontrado, um modal DEVE aparecer: "Estratégia Sem Nome (45% concluída) foi pausada. Continuar? [Sim] [Não]".
- Clicar em [Sim] DEVE chamar `/api/backtest/resume/{id}` e restaurar a visualização de progresso.

