## Why

A funcionalidade Lab adiciona rotas, UI e fluxo backend específicos que não fazem mais parte do produto desejado. Remover esse módulo agora reduz complexidade operacional, elimina superfícies sem uso e simplifica navegação, manutenção e QA.

## What Changes

- Remover a interface do Lab do frontend, incluindo páginas, navegação e links de entrada pela home.
- Remover endpoints, serviços e utilitários backend dedicados ao Lab e ao fluxo de execução associado.
- Remover logs, SSE, trace viewer e artefatos de suporte usados apenas pelo Lab.
- **BREAKING**: deixar de expor rotas HTTP, páginas e fluxos de execução relacionados ao Lab.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `lab-flow`: remover a capacidade de iniciar, acompanhar e continuar execuções do Lab.
- `lab-chat-inputs`: remover a coleta e o processamento de inputs conversacionais específicos do Lab.
- `lab-logs`: remover streaming de logs, leitura de steps e observabilidade específica do Lab.
- `lab-run-hardening`: remover o fluxo de runtime e resiliência dedicado a runs do Lab.
- `home`: remover atalhos, cards e entradas da home que apontam para o Lab.
- `ui`: remover navegação e superfícies visuais que expõem o Lab no produto.
- `backend`: remover endpoints e integração backend que existem apenas para suportar o Lab.

## Impact

- Frontend: rotas `/lab` e `/lab/runs/:runId`, componentes `frontend/src/components/lab/*`, hooks e links de navegação/home.
- Backend: `backend/app/routes/lab.py`, `backend/app/routes/lab_logs_sse.py`, `backend/app/services/lab_graph.py`, `backend/app/trace_viewer.py` e arquivos/logs associados.
- Testes e documentação que assumem a existência do Lab precisarão ser removidos ou ajustados.
