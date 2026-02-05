---
spec: openspec.v1
id: crypto.lab.langgraph.v1
title: Strategy Lab (LangGraph) com 3 personas + autosave de templates/favoritos
status: draft
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

## Dentro do escopo (in scope)
- Nova tela: `/lab`
- Endpoints no backend para:
  - criar uma requisição de "lab run"
  - executar um fluxo LangGraph **no mesmo processo do backend (FastAPI)**
  - persistir resultados:
    - salvar automaticamente um combo_template (com novo nome)
    - salvar automaticamente uma FavoriteStrategy vinculada ao run
- Três personas (prompts/roles):
  1) **Coordenador**: orquestração + decisão final
  2) **Dev Sênior**: mudanças em template + notas de implementação
  3) **Trader/Validador**: checagens de risco/robustez + aprovar/reprovar
- Ferramentas (tools) dentro do grafo:
  - listar templates disponíveis
  - propor/criar templates (declarativo)
  - **computar indicadores pandas-ta de forma genérica** (evitar code changes por indicador)
  - rodar backtest usando o motor existente
  - salvar template + favorito
  - (quando necessário) propor patch de código do motor, mas **somente em branch + com gates + OK final do Alan**

## Fora do escopo (v1)
- Criar classes novas de estratégia em Python (v1 foca em **usar/modificar templates**; ajustes pontuais no motor são permitidos via guardrails)
- Multi-tenant / autenticação avançada
- Otimização avançada (grid grande / BO) além de poucos candidatos
- Fila de jobs longos + streaming de progresso (v1 pode ser síncrono)

# 3) User stories

- Como Alan, quero descrever um objetivo (symbol/timeframe/restrições) e deixar o sistema propor + validar uma estratégia.
- Como Alan, quero que o sistema salve automaticamente o template vencedor e o favorito para eu revisar em Favorites.

# 4) UX / UI

## Rota: `/lab`

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
  "thinking": "low"
}
```

Response (success):
```json
{
  "run_id": "...",
  "status": "ok",
  "coordinator_summary": "...",
  "validator": { "verdict": "approved", "notes": "..." },
  "dev": { "changes": "..." },
  "saved": {
    "template_name": "lab_multi_ma_crossover_sol_1d_20260205",
    "favorite_id": 123
  },
  "backtest": {
    "metrics": { "sharpe_ratio": 0.5, "max_drawdown": 0.18 }
  }
}
```

Response (error):
- 4xx: erro de validação
- 5xx: erro de execução do grafo/backtest/salvamento

## OpenClaw / LLM

- Usar OpenClaw Gateway (mesmo OAuth já existente) no estilo do agent chat.
- Personas implementadas como prompts distintos e instruções de uso de tools.

# 6) Mudanças de modelo/dados

- Opcional (v1): criar tabela `lab_runs` para persistir:
  - inputs
  - outputs do grafo
  - template criado
  - favorite criado
  - timestamps

Se não criarmos tabela no v1, ainda assim precisamos retornar ids e depender das tabelas existentes.

# 7) VALIDATE (obrigatório)

## Link da proposta

- Proposal URL: http://31.97.92.212:5173/openspec/06-strategy-lab-langgraph
- Status: draft → validated → approved → implemented

Checklist (preencher antes de implementar):

- [ ] Escopo sem ambiguidades (in-scope/out-of-scope explícitos)
- [ ] Critérios de aceite testáveis (pass/fail)
- [ ] API/contratos definidos (request/response/error) quando aplicável
- [ ] Estados de UI cobertos (loading/empty/error)
- [ ] Segurança anotada (auth/exposição) quando aplicável
- [ ] Plano de testes inclui smoke manual + pelo menos 1 check automatizado
- [ ] Perguntas em aberto resolvidas ou explicitamente listadas

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
- Convenção de nome para templates/favorites auto-salvos (formato + unicidade)
- Quantos candidatos por run? (default: 3–5)
