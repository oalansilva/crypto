# Design: Lab Real-time Logs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐  │
│  │   LabRun     │────▶│ LogPanel     │◀───│  useLogSSE   │  │
│  │   Component  │     │ Component    │    │   Hook       │  │
│  └──────────────┘     └──────────────┘    └──────┬───────┘  │
│                                                  │          │
└──────────────────────────────────────────────────┼──────────┘
                                                   │ SSE
┌──────────────────────────────────────────────────┼──────────┐
│                        BACKEND                   │          │
│  ┌───────────────────────────────────────────────┼───────┐  │
│  │           SSE Endpoint                        │       │  │
│  │     /api/lab/{run_id}/logs/stream             ▼       │  │
│  │                                                    │  │
│  │  ┌─────────────┐    ┌─────────────┐   ┌────────┐  │  │
│  │  │ LogReader   │───▶│  SSE Queue  │──▶│ Client │──┘  │
│  │  │ (tail file) │    │             │   │        │     │
│  │  └─────────────┘    └─────────────┘   └────────┘     │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Log File (shared)                      │   │
│  │         /tmp/lab_{run_id}_{step}.log                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Backend

#### 1. SSE Endpoint: `GET /api/lab/{run_id}/logs/stream`
- Headers: `Content-Type: text/event-stream`
- Autenticação: Bearer token
- Quando conectado, inicia tail no arquivo de log do step atual
- Envia cada linha nova como evento SSE: `data: {"timestamp": "...", "level": "...", "message": "..."}\n\n`
- Fecha conexão quando step termina (ou após timeout de inatividade)

#### 2. Log File Location
- Path: `/tmp/lab_{run_id}_{step_name}.log`
- Rotacionado automaticamente pelo processo do step
- Formato: `[TIMESTAMP] [LEVEL] Message`

### Frontend

#### 1. Hook: `useLogSSE(runId: string)`
```typescript
interface UseLogSSEOptions {
  runId: string;
  enabled: boolean; // só conecta quando step está running
}

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  message: string;
}

// Retorna: { logs: LogEntry[], isConnected: boolean, error: Error | null }
```

#### 2. Component: `<LogPanel />`
- Props: `logs: LogEntry[], isLoading: boolean`
- UI: Panel expansível (similar ao combo/configure)
- Features:
  - Auto-scroll para última linha
  - Color coding por log level
  - Timestamp formatado
  - Botão "Copiar logs"
  - Botão "Pausar/Continuar" auto-scroll

#### 3. Integration: Lab Run Page
- Adicionar botão "Ver Logs" quando `status === 'running'`
- Posicionar ao lado do indicador de progresso
- Abrir panel abaixo do status do step

## Data Flow

1. Step inicia execução → cria arquivo de log
2. Frontend detecta `status === 'running'` → habilita botão "Ver Logs"
3. Usuário clica em "Ver Logs" → conecta SSE endpoint
4. Backend tail no arquivo → envia linhas via SSE
5. Frontend recebe → adiciona ao array de logs → re-renderiza panel
6. Step termina → backend fecha SSE → frontend mostra "Concluído"
7. Logs ficam disponíveis para visualização até sair da página

## API Changes

### New Endpoint
```
GET /api/lab/{run_id}/logs/stream
Headers:
  Authorization: Bearer {token}
  Accept: text/event-stream

Response (SSE):
  data: {"timestamp":"2026-02-13T17:10:00Z","level":"INFO","message":"Starting combo optimization..."}
  
  data: {"timestamp":"2026-02-13T17:10:05Z","level":"DEBUG","message":"Evaluating EMA(12) crossover..."}
```

### New Types
```typescript
// shared/types/lab.ts
interface LabLogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  message: string;
  step: string;
  phase?: string;
}
```

## UI/UX

### Log Panel Design (combo/configure como referência)
- Largura: 100% do container
- Altura: 300px (fixa) com scroll
- Background: `bg-gray-900` (dark theme)
- Font: `font-mono text-sm`
- Cores:
  - INFO: `text-gray-300`
  - WARN: `text-yellow-400`
  - ERROR: `text-red-400`
  - DEBUG: `text-blue-400`

### Estados
1. **Closed**: Apenas botão "Ver Logs" visível
2. **Open + Loading**: Panel aberto, mensagem "Conectando..."
3. **Open + Streaming**: Panel mostrando logs em tempo real
4. **Open + Completed**: Panel mostrando logs históricos (conexão fechada)

## Error Handling

- **Falha na conexão**: Mostrar mensagem de erro e botão "Tentar novamente"
- **Step finalizado**: Fechar SSE gracefully, manter logs visíveis
- **Arquivo de log não encontrado**: Retornar 404 com mensagem apropriada
