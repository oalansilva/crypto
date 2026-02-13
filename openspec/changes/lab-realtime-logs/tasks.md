# Implementation Tasks: Lab Real-time Logs

## Backend Tasks

### B1: Criar endpoint SSE para streaming de logs
- [ ] Criar arquivo `backend/api/lab/logs_sse.py`
- [ ] Implementar função `stream_lab_logs(run_id: str, step: str)`
- [ ] Usar `asyncio` + `aiofiles` para tail não-bloqueante
- [ ] Adicionar rota `GET /api/lab/{run_id}/logs/stream` em `main.py`
- [ ] Implementar autenticação JWT na conexão SSE

### B2: Integrar sistema de logs do combo com o Lab
- [ ] Identificar onde o combo salva logs (`/tmp/combo_*` ou similar)
- [ ] Garantir que logs do Lab usem o mesmo padrão de arquivo
- [ ] Criar função `get_log_path(run_id: str, step: str) -> Path`

### B3: Testes backend
- [ ] Teste unitário: conexão SSE abre corretamente
- [ ] Teste unitário: logs são enviados em tempo real
- [ ] Teste de integração: endpoint funciona com autenticação

## Frontend Tasks

### F1: Criar hook useLogSSE
- [ ] Criar arquivo `frontend/src/hooks/useLogSSE.ts`
- [ ] Implementar conexão EventSource
- [ ] Implementar parse de mensagens SSE para LogEntry[]
- [ ] Gerenciar estados: connecting, connected, error, closed
- [ ] Implementar cleanup ao desmontar componente

### F2: Criar componente LogPanel
- [ ] Criar arquivo `frontend/src/components/lab/LogPanel.tsx`
- [ ] Implementar UI de panel expansível
- [ ] Implementar lista de logs com scroll
- [ ] Implementar auto-scroll para última entrada
- [ ] Adicionar color coding por log level
- [ ] Adicionar botões: "Copiar logs", "Pausar scroll"
- [ ] Estilizar igual ao painel de logs do combo/configure

### F3: Integrar na página LabRun
- [ ] Modificar `frontend/src/pages/lab/LabRun.tsx`
- [ ] Adicionar botão "Ver Logs" quando step está running
- [ ] Integrar LogPanel com dados do useLogSSE
- [ ] Mostrar estado de conexão (indicador visual)

### F4: Testes E2E
- [ ] Criar teste Playwright: abrir Lab, iniciar run, clicar "Ver Logs"
- [ ] Validar que logs aparecem em tempo real
- [ ] Validar que panel fecha/reabre corretamente

## DevOps Tasks

### D1: Configurar Vite proxy (se necessário)
- [ ] Verificar se endpoint SSE precisa de config especial no Vite
- [ ] Atualizar `vite.config.ts` se necessário

### D2: Deploy
- [ ] Commit e push na branch `feature/long-change`
- [ ] Restart backend + frontend na VPS
- [ ] Validar funcionalidade na UI

## Acceptance Criteria Checklist

- [ ] Endpoint SSE `/api/lab/{run_id}/logs/stream` retorna logs em tempo real
- [ ] Hook useLogSSE gerencia conexão e estado corretamente
- [ ] Componente LogPanel tem aparência consistente com combo/configure
- [ ] Botão "Ver Logs" aparece apenas durante execução
- [ ] Logs são exibidos com timestamp e color coding
- [ ] Auto-scroll funciona durante streaming
- [ ] Logs persistem após conclusão do step
- [ ] Testes E2E passam
- [ ] Testes backend passam
