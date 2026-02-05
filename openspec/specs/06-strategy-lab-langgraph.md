---
spec: openspec.v1
id: crypto.lab.langgraph.v1
title: Strategy Lab (LangGraph) com 3 personas + autosave de templates/favoritos
status: validated
owner: Alan
created_at: 2026-02-05
updated_at: 2026-02-05
---

# 0) Resumo (one-liner)

Adicionar uma nova feature "Strategy Lab" (nova tela + endpoints no backend) que executa um fluxo LangGraph com 3 personas (Coordenador, Dev Sênior, Trader/Validador) para gerar/melhorar estratégias usando templates existentes, rodar backtests e **salvar automaticamente** o combo_template + favorito.

# 1) Contexto

- O sistema atual já suporta:
  - combo_templates (templates)
  - backtesting
  - favorites
  - agent chat sobre favorites
- Queremos um fluxo estruturado com múltiplas personas colaborando e usando as ferramentas existentes para criar novas estratégias/templates.
- Não podemos quebrar o app atual: isso precisa ficar como **feature separada / nova tela**.

# 2) Objetivo

## Guardrails (obrigatório)

- **Nunca quebrar o sistema atual**: desenvolvimento e mudanças longas devem acontecer em branch (ex.: `feature/long-change`).
- **Merge somente com OK final do Alan** após testes manuais no UI (USER TEST) + smoke automatizado.
- Sempre manter uma tag estável para rollback (ex.: `stable-2026-02-05`).
- **Foco do Lab:** priorizar exclusivamente a criação/melhoria de estratégias e templates (backtest, validação, autosave). **Não** gastar ciclos propondo novas telas, notas, features gerais ou refactors não relacionados à estratégia.
- **Sem lookahead/leakage:** o motor/validações devem garantir que sinais/indicadores usem apenas dados até o candle atual.
- **Walk-forward mínimo obrigatório:** usar split temporal **70% antigo / 30% recente**; critérios de aprovação usam principalmente o **30% mais recente** (holdout). Não confiar apenas em "all".
- **Custos sempre ligados por padrão:** fee+slippage default (não permitir backtest "limpo" por padrão no Lab).
- **Deep backtest obrigatório:** no Lab, sempre executar backtests com `deep_backtest=true` para que o stop considere candles de 15 minutos (consistência com o seu critério de stop).
- **Controle de complexidade:** no máximo **4 indicadores** por template (evitar overfit e templates ilegíveis).
- **Rate limit/limites de execução:** limitar número de candidatos/backtests por run e por janela de tempo.
- **Engine-fix permitido com gate:** se houver erro no motor, o Dev pode fazer ajustes pequenos **somente em branch** e **somente** se passar um smoke fixo antes de qualquer merge: `BTC/USDT 1d` + template base `multi_ma_crossover` + `deep_backtest=true` (rodar sem erro e produzir métricas/trades válidos).
- **Autosave com critérios:** somente **salvar quando aprovado** (reprovados não salvam nada). Favoritos/templates aprovados devem ser salvos com naming padrão e `notes` contendo `lab_run_id`.
- **Observabilidade do Lab (obrigatório):** registrar as interações do grafo/personas (mensagens + chamadas de tools + métricas/usage) para auditoria/debug pelo Alan.
- **Orçamento de tokens/turnos (obrigatório):** limitar o número de interações e o custo por run (**turns_max=12**, **tokens_max=60000**). Se atingir o limite, o Coordenador deve resumir o estado e **pedir confirmação na UI para continuar**.

## Dentro do escopo (in scope)
- Nova tela: `/lab`
- Página de inspeção: `/lab/runs/:run_id` para visualizar trace/interações (mensagens/tool calls/usage)
- Endpoints no backend para:
  - criar uma requisição de "lab run"
  - executar um fluxo LangGraph **no mesmo processo do backend (FastAPI)**
  - **rodar backtests via o backtest assíncrono existente** (jobs/status/result), sem bloquear o request principal
  - persistir resultados:
    - salvar automaticamente um combo_template (com novo nome)
    - salvar automaticamente uma FavoriteStrategy vinculada ao run
- Três personas (prompts/roles):
  1) **Coordenador**: orquestração + decisão final
  2) **Dev Sênior**: mudanças em template + notas de implementação
  3) **Trader/Validador**: checagens de risco/robustez + aprovar/reprovar
- Ferramentas (tools) dentro do grafo (reutilizar o que já existe):
  - listar/ler/criar templates (reutilizar `combo_templates` e a lógica atual)
  - **buscar candles** (reutilizar o storage/cache/parquet + exchange fetch existente)
  - rodar backtest (reutilizar o motor atual de backtest, sem duplicar lógica)
  - salvar favoritos (reutilizar a tabela/endpoint de favorites)
  - **computar indicadores via pandas-ta** por adapter genérico (para suportar "qualquer" indicador sem code changes por indicador)
  - (quando necessário) propor patch de código do motor, mas **somente em branch + com gates + OK final do Alan**

## Fora do escopo (v1)
- Criar classes novas de estratégia em Python (v1 foca em **usar/modificar templates**; ajustes pontuais no motor são permitidos via guardrails)
- Multi-tenant / autenticação avançada
- Otimização avançada (grid grande / BO) além de poucos candidatos
- Streaming avançado (SSE/WebSocket) além do que já existe

# 3) User stories

- Como Alan, quero descrever um objetivo (symbol/timeframe/restrições) e deixar o sistema propor + validar uma estratégia.
- Como Alan, quero que o sistema salve automaticamente o template vencedor e o favorito para eu revisar em Favorites.

# 4) UX / UI

## Rota: `/lab`

- A execução do Lab deve ser assíncrona do ponto de vista do frontend:
  - `POST /api/lab/run` retorna `accepted` + `run_id`
  - UI faz polling em `GET /api/lab/runs/{run_id}` até finalizar

- Inputs:
  - Symbol (dropdown)
  - Timeframe
  - Template base (dropdown)
  - Restrições (max DD, min Sharpe, direction etc.)
  - Objetivo em texto livre (opcional)
- Ações:
  - Botão "Run Lab"
- Outputs:
  - Sumário do Coordenador
  - Veredito do Validador (approved/rejected + motivos)
  - Resumo do Dev (mudanças sugeridas)
  - Links:
    - Abrir Favorite salvo
    - Abrir Template salvo (tela de edição)

Estados:
- Loading (grafo rodando)
- Error
- Success (mostrar ids salvos)

# 5) API / Contratos

## Backend

### POST /api/lab/run

Observação: a execução deve registrar logs e usage por persona/tool, vinculados a `run_id`.

Request:
```json
{
  "symbol": "SOL/USDT",
  "timeframe": "1d",
  "base_template": "multi_ma_crossover",
  "direction": "long",
  "constraints": {
    "max_drawdown": 0.20,
    "min_sharpe": 0.4
  },
  "objective": "Gerar uma versão mais robusta para bear",
  "thinking": "low",
  "deep_backtest": true
}
```

Response (accepted):
```json
{
  "run_id": "...",
  "status": "accepted",
  "trace": {
    "viewer_url": "http://31.97.92.212:5173/lab/runs/...",
    "api_url": "/api/lab/runs/..."
  }
}
```

O frontend acompanha o progresso consultando o run (inclui status dos backtests assíncronos).

Response (error):
- 4xx: erro de validação
- 5xx: erro de execução do grafo/backtest/salvamento

### GET /api/lab/runs/{run_id}

Retorna o estado atual do run, incluindo o estado dos backtests assíncronos.

Response (example):
```json
{
  "run_id": "...",
  "status": "running",
  "step": "backtest",
  "backtests": [
    { "candidate": 1, "job_run_id": "...", "status": "RUNNING", "progress": 0.4 }
  ],
  "budget": { "turns_used": 5, "turns_max": 12, "tokens_total": 25000, "tokens_max": 60000, "on_limit": "ask_user" },
  "trace": { "viewer_url": "..." }
}
```

## OpenClaw / LLM

- Usar OpenClaw Gateway (mesmo OAuth já existente) no estilo do agent chat.
- Personas implementadas como prompts distintos e instruções de uso de tools.
- Importante: o grafo deve preferir **tools do sistema** (candle fetch, backtest, favorites, templates) em vez de “simular” resultados.

# 6) Mudanças de modelo/dados

- Recomendado (v1): criar tabela `lab_runs` para persistir:
  - inputs
  - outputs do grafo
  - template criado
  - favorite criado
  - timestamps
  - **logs/trace do grafo** (mensagens por persona + tool calls + usage de tokens)

Se não criarmos tabela no v1, salvar ao menos um JSONL em disco em `backend/logs/lab_runs/<run_id>.jsonl` e retornar `run_id` para consulta.

# 7) VALIDATE (obrigatório)

## Link da proposta

- Proposal URL: http://31.97.92.212:5173/openspec/06-strategy-lab-langgraph
- Status: draft → validated → approved → implemented

Checklist (preencher antes de implementar):

- [x] Escopo sem ambiguidades (in-scope/out-of-scope explícitos)
- [x] Critérios de aceite testáveis (pass/fail)
- [x] API/contratos definidos (request/response/error) quando aplicável
- [x] Estados de UI cobertos (loading/empty/error)
- [x] Segurança anotada (auth/exposição) quando aplicável
- [x] Plano de testes inclui smoke manual + pelo menos 1 check automatizado
- [x] Perguntas em aberto resolvidas ou explicitamente listadas (ver seção 13)

# 8) Critérios de aceite (DoD)

- [ ] Existe a página `/lab` e ela dispara um lab run.
- [ ] Um lab run gera:
  - um resultado de backtest
  - um sumário do Coordenador
  - um veredito do Validador
  - um resumo do Dev
- [ ] Em caso de sucesso, salva automaticamente:
  - um novo combo_template
  - um novo FavoriteStrategy
- [ ] O Favorite salvo aparece em `/favorites` e o Agent chat funciona nele.
- [ ] Sem regressão nas rotas atuais (`/favorites`, `/combo/*`).
- [ ] Qualquer mudança de código (se ocorrer) acontece em branch e **não é mergeada** sem:
  - (a) smoke automatizado passando
  - (b) teste manual do Alan
  - (c) OK final explícito

# 9) Plano de testes

## Smoke manual
1. Abrir `/lab`
2. Rodar com template base `multi_ma_crossover` em `BTC/USDT 1d`
3. Confirmar approved/rejected + sumário
4. Confirmar novo Favorite em `/favorites`

## Automatizado
- Backend: teste unitário para validação do request + nome seguro/único do template
- Frontend: `npm run build`

# 10) Rollout / rollback

- Rollout: deploy de backend + frontend, feature disponível em `/lab`
- Rollback: voltar para a tag `stable-2026-02-05`

# 11) USER TEST (obrigatório)

Após deploy/restart, Alan valida na UI.

- URL(s) para testar:
  - http://31.97.92.212:5173/lab
- O que testar (smoke):
  1) Rodar um lab task e verificar autosave.
  2) Confirmar que o Favorite salvo existe e Agent chat funciona.
- Resultado:
  - [ ] Alan confirmou: OK

# 12) ARQUIVAR / FECHAR (obrigatório)

Somente depois do OK do Alan:

- [ ] Atualizar frontmatter do spec para `status: implemented`
- [ ] Atualizar `updated_at`
- [ ] Adicionar evidência breve (hash do commit + URL testada) no spec

# 13) Notas / dúvidas em aberto

- Precisamos de jobs assíncronos (fila/progresso) no v1, ou síncrono é aceitável?
- Convenção de nome para templates/favorites aprovados (formato + unicidade)
- Quantos candidatos por run? (default: 3–5)
- Thresholds mínimos de aprovação (ex.: trades mínimos, sharpe mínimo, DD máximo)
