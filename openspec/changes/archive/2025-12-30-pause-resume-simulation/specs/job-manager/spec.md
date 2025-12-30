# Spec: Job Manager & Persistência

## ADDED Requirements

### Requirement: Persistência de Estado
O sistema DEVE (MUST) garantir que o estado da simulação seja salvo periodicamente para evitar perda de dados.

#### Scenario: Persistência no Backend
> Como um sistema
> Eu quero persistir o estado das otimizações em execução no disco
> Para que o progresso não seja perdido ao desligar

- O sistema DEVE salvar o estado das otimizações ativas em `backend/data/jobs/job_<id>.json`.
- O estado salvo DEVE incluir: `config`, `current_iteration`, `results` (lista parcial) e `status`.
- O sistema DEVE salvar automaticamente este estado pelo menos a cada 50 iterações ou 1 minuto.
- O sistema DEVE suportar um sinal de `PAUSE` que aciona um salvamento imediato e para o loop.

### Requirement: Retomada de Otimização
O sistema DEVE (MUST) ser capaz de restaurar e continuar uma simulação a partir do último ponto salvo.

#### Scenario: Lógica de Retomada
> Como um usuário
> Eu quero retomar uma otimização pausada
> Para que eu possa continuar de onde parei

- Dado um `job_id` com status `PAUSED`, chamar `resume(job_id)` DEVE reiniciar o processo.
- O processo DEVE recarregar a configuração e regerar EXATAMENTE O MESMO grid de parâmetros da execução original.
- O processo DEVE PULAR as primeiras `current_iteration` combinações no grid.
- O processo DEVE anexar novos resultados à lista `results` existente do estado salvo.
