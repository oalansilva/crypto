## UX alvo (estilo ChatGPT)

### Entry point
- `/lab/runs/:run_id` → seção **Conversa** com **abas**:
  - **Chat (simplificado)** (default)
  - **Eventos (debug)** (equivalente ao trace bruto)

### Chat (simplificado)

- Header com:
  - status do run
  - fase atual (`data.phase` quando existir)
  - contador de mensagens
  - filtros rápidos (chips): `coordinator`, `dev_senior`, `validator`, `system`
  - toggle: **Mostrar eventos técnicos** (off por padrão)

- Timeline linear (vertical), com:
  - separadores de fase (ex.: **Upstream** e **Execução**) quando houver eventos `upstream_started/upstream_done` e/ou `data.step/phase`.
  - bolhas por persona (mensagens `persona_done`), com:
    - nome da persona
    - timestamp
    - duração/tokens (em badge opcional)
    - conteúdo em `pre` com wrap
  - eventos-chave como cards menores:
    - `selection_gate`
    - `backtest_done`
    - `final_decision`

### Eventos (debug)
- Mantém a lista reversa existente de `trace_events` (JSON), sem opinião.

## Mapeamento de eventos → mensagens

- Mensagem principal de agente:
  - `type === 'persona_done'` e `data.persona` presente
  - `text = data.text` (já truncado no backend)

- Separador de fase:
  - `type in ('upstream_started','upstream_done')` → marcador “Upstream”
  - quando o run sair de upstream para execução (ex.: primeiro `persona_started` após upstream aprovado) → marcador “Execução”

- Eventos técnicos (colapsados por padrão):
  - `persona_started`, `iteration_started`, `param_tuned`, etc.

## Implementação (frontend)

- Extrair um componente:
  - `frontend/src/components/lab/RunChatView.tsx`
  - recebe `trace_events: TraceEvent[]`
  - expõe `messages` (normalizadas) e render.

- Atualizar `LabRunPage.tsx`:
  - adicionar tabs (`Chat` / `Debug`)
  - substituir bloco atual “Conversa dos agentes” pelo `RunChatView`

## Critérios de usabilidade

- O Alan consegue bater o olho e entender:
  - por que o upstream bloqueou (se bloqueou)
  - o que cada persona respondeu
  - qual foi a decisão do gate

## Riscos / trade-offs

- Sem um browser local (relay), a visualização é a melhor forma de “entender o run” sem depender de Studio.
- Se `trace_events` vier vazio (runs antigos), UI precisa degradar com estado “sem conversa disponível”.
