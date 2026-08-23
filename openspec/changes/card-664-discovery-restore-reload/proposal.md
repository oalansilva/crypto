## Why

O estado do sweep ativo hoje vive apenas na memória da página. Ao recarregar `/combo/discovery`, o painel desaparece mesmo quando o servidor ainda tem uma varredura não terminal, e um `resume` pode deixar combinações pendentes sem novo wake-up do orquestrador. O administrador precisa voltar ao mesmo processo com estado e progresso verdadeiros, sem iniciar outro rascunho nem perder o trabalho já persistido. Card [#664](https://github.com/oalansilva/crypto/issues/664).

## What Changes

- Descoberta passa a localizar, no servidor e por ator autenticado, os sweeps não terminais e a tela reconstitui o mais recente ao abrir/recarregar, mantendo os demais acessíveis no histórico.
- O bloco **Sweep ativo** é restaurado com `sweep_id`, snapshot imutável, contadores reconciliados, estado, controles de lifecycle e leaderboard da própria run.
- O configurador é reidratado pelo snapshot persistido e permanece congelado no reload enquanto houver sweep ativo não terminal; **Novo rascunho** explícito descongela e permite uma segunda run. Sweeps terminais continuam disponíveis no histórico.
- `resume` e a recuperação de um sweep `running` com combinações pendentes garantem um wake-up durável do orquestrador quando a outbox anterior já foi confirmada, sem duplicar trabalho.
- A restauração deve ser idempotente, respeitar pausa/cancelamento e manter o polling somente enquanto a run não for terminal.
- Testes de backend, frontend e browser cobrem reload em cada estado relevante, recuperação do wake-up, separação entre ativo e histórico e ausência de regressão no start existente.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-sweep`: o lifecycle e o snapshot ativo tornam-se recuperáveis após reload, e resume/running incompletos devem manter wake-up reclamável.

## Impact

- **UI impact: affected** — altera a tela existente `frontend/src/pages/DiscoveryPage.tsx` e seu fluxo de estado visual; não redesenha o shell de Combo.
- Frontend: hidratação do sweep ativo, snapshot/rascunho congelado, seleção inicial do leaderboard e estados de loading/erro de recuperação.
- Backend: rota/serviço de consulta do sweep ativo, garantia idempotente de wake-up na transição `resume` e na reconciliação de sweeps incompletos.
- Dados/filas: reutiliza `DiscoverySweep`, `DiscoveryCombination` e `DiscoveryOutbox`; não cria resultados nem combinações novas durante a restauração.
- Fora de escopo: promoção/exclusão de candidatos (#663), Short, worker PROD (#566) e alterações nas fórmulas do otimizador.
