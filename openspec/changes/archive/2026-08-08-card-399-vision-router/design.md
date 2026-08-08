## Context

O opencode é a ferramenta única de desenvolvimento (card #395). O modelo default da sessão é `opencode-go/deepseek-v4-flash`, que não aceita imagens (`attachment: false` no models.dev). `opencode-go/gpt-5.6-luna` aceita imagens (`attachment: true`) e está disponível no mesmo provider, já autenticado.

O opencode 1.18.15 não tem switch nativo de modelo por necessidade de imagem (sem `vision_model` no schema; `chat.params` não troca modelo; `session/update` não aceita `modelID`). O roteamento é feito por composição das capacidades existentes: agentes com `model` fixo + subagents (`task`) + hooks de plugin + commands.

### Mapeamento do fluxo de trabalho (situações com imagem)

Análise do fluxo completo do repo (AGENTS.md, rules.md, alan-workflow, QA visual, design gate) — todas as situações em que o agente precisa **ver** pixels:

| # | Situação | Onde no fluxo | Já mapeado |
|---|---|---|---|
| 1 | Imagem anexada/colada no chat | conversa com Alan | sim (plugin chat.message) |
| 2 | Screenshot gerado por tool (Playwright, browser-debugger) em tarefa visual | QA, diagnóstico de bug | sim (tool.execute.after) |
| 3 | Validação de design/impeccable (critique/audit com evidência visual) | Status=Design | sim (tool.execute.after + regra) |
| 4 | Imagem anexada em card/issue do GitHub | board/issue | sim (tool.execute.after + /vision URL) |
| 5 | **Julgamento de `diff.png`/`actual.png` de falha do Playwright visual** | QA visual — AGENTS.md: "revisar somente o diff.png... para confirmar que a mudança é esperada" | **não** |
| 6 | **Atualização de baselines com mudança de UI intencional** (`--update-snapshots`) — revisar os novos PNGs | QA visual | **não** |
| 7 | **Browser gate / Prototype Validation (desktop+mobile, fidelidade ao sistema atual)** | Status=Design (design-critic) | parcial (3) — formalizar |
| 8 | **Diagnóstico de bug de UI (browser-debugger): screenshots em `qa_artifacts/`** | Em desenvolvimento / investigação | parcial (2) — formalizar |
| 9 | **Artifacts de falha do CI** (screenshots do e2e no GitHub Actions — baixar e analisar) | QA/CI | **não** |
| 10 | **Gráficos/sinais exportados do domínio cripto** (`artifacts-signals-*.png`, `output/`) | análise de produto | **não** |
| 11 | **Comparação visual antes/depois** (fidelidade de protótipo, mudança de UI, multi-imagem) | design/QA | **não** (requer /vision multi) |
| 12 | **Code review de UI** com snapshots/evidência visual no diff | Code Review | **não** |

## Decisions

- `UI impact: none` — mudança de ferramenta de desenvolvimento e processo; nenhuma tela ou comportamento de produto é alterado.
- **Modelo default da sessão permanece flash** (`opencode-go/deepseek-v4-flash`); Luna entra automaticamente apenas quando há imagem (menor custo).
- **`small_model: opencode-go/deepseek-v4-flash`** — tarefas internas baratas (título, resumo, compactação) ficam no flash.
- **Agente `vision` (subagent)** com `model: opencode-go/gpt-5.6-luna` fixo no frontmatter — toda análise de imagem roda com o Luna por definição, independente do modelo da sessão. Exceção explícita à regra de roteamento de LLM (subagents herdam o modelo da sessão) — registrada no AGENTS.md.
- **Plugin `vision-router`** com os hooks:
  - `chat.message`: detecta `image` part na mensagem do usuário → grava o anexo (data URL) em `.impeccable/attachments/<sessionID>-<timestamp>.<ext>` e marca a sessão em memória (`hasImage`).
  - `experimental.chat.messages.transform`: se a sessão tem imagem e o modelo não tem visão → substitui a image part por texto `[imagem anexada: <path> — delegar análise ao agente vision]` (o flash nunca recebe pixels; evita request inválido).
  - `experimental.chat.system.transform`: injeta instrução de sistema — "imagem presente; delegue a análise ao subagent vision (Luna); nunca interprete pixels".
  - `tool.execute.after`: quando um tool gera `.png`/screenshot (Playwright, browser-debugger) ou baixa/grava uma imagem de anexo de card/issue do GitHub, e a tarefa envolve análise visual, injeta contexto de delegação no próximo turno (via estado de sessão reutilizado pelo system.transform).
  - Log de evidência: `.impeccable/vision-router.jsonl` (sessão, origem, destino, arquivo, timestamp).
- **Command `/vision <arquivo>`** em `.opencode/command/vision.md` — análise explícita de imagem/screenshot no Luna (ex: `diff.png` de baseline, screenshot de protótipo). Aceita também URL de anexo de card/issue do GitHub: baixa o anexo e delega ao `vision`.
- **Anexos de imagem em cards/issues do GitHub**: quando a tarefa exige analisar uma imagem colada/anexada em card do GitHub, o agente baixa o anexo (via `gh` ou URL) e delega a análise ao agente `vision` (Luna). O plugin `tool.execute.after` detecta arquivos de imagem recém-gravados/baixados (extensão `.png/.jpg/.jpeg/.webp`) e o `system.transform` instrui a delegação — mesmo mecanismo dos screenshots de tools. Regra documentada no AGENTS.md.
- **Detecção genérica de imagem no contexto (cobre situações 5-12)**: o plugin marca a sessão quando há imagem em qualquer forma (anexo, arquivo recém-escrito/baixado, referência a snapshot/baseline/`diff.png`/`actual.png`/artifact/`qa_artifacts`/`artifacts-signals-*.png` no contexto da tarefa) e o `system.transform` injeta a regra: "julgamento visual obrigatório via agente vision (Luna)". Isso cobre QA visual (diff/baseline), browser gate, bugs de UI, artifacts do CI, gráficos de sinais e code review de UI sem lista exaustiva.
- **`/vision` multi-imagem**: comparação antes/depois (fidelidade de protótipo, diffs) — aceita vários arquivos/URLs (inclusive URL de artifact do GitHub Actions via `gh run download`).
- **Limpeza**: remover `.opencode/opencode.json` (lixo criado acidentalmente por `opencode plugin list` durante investigação).
- **Não alterar**: runtime de produto, banco, API, frontend; hermes/gateway não é usado para este roteamento (a análise visual roda no provider opencode-go via opencode).

## Goals / Non-Goals

**Goals:**
- Chaveamento automático flash→Luna quando houver imagem, sem ação do usuário.
- Análise visual de qualidade (Luna com visão real dos pixels) em testes visuais, validações de design e screenshots de tools.
- Evidência auditável de cada roteamento.

**Non-Goals:**
- Trocar o modelo default da sessão para Luna.
- Analisar pixels com o flash (não suporta visão).
- Alterar produto/runtime.

## Risks

- **Request inválido se o flash receber imagem**: mitigado pelo placeholder no `messages.transform` (o flash nunca recebe image part).
- **Subagent vision sem a imagem**: o anexo vira arquivo em `.impeccable/attachments/` e o placeholder passa o caminho; o subagent vision abre o arquivo via `read`. Screenshots de tools já estão em disco.
- **Transform/system hooks experimentais**: comportamento pode mudar em versões futuras do opencode — mantém fallback documental (AGENTS.md) para análise via `/vision` e agente vision.
- **Custo**: turnos com imagem usam Luna (mais caro que flash) — esperado e limitado aos gatilhos definidos.

## Prototype

`N/A` — sem superfície visual nova ou alterada (`UI impact: none`). Não há protótipo HTML nem mudança em `frontend/**`.

## Design Critique

Sem UI, a crítica cobre escopo, regressão e riscos operacionais:

- **Escopo:** adequado — apenas ferramenta de dev (agente, plugin, command, config e docs de processo); zero impacto em runtime de produto.
- **Regressão de produto:** nenhuma — nenhum arquivo de backend/frontend/banco é alterado.
- **Riscos operacionais:** (1) hooks experimentais do opencode — fallback documental via `/vision`; (2) anexo colado precisa ser persistido antes do transform — o `chat.message` roda antes do request do turno; (3) delegação depende do modelo principal seguir a instrução de sistema — mitigado com placeholder claro e regra no AGENTS.md.
- **Achados bloqueantes:** nenhum.
- **Pendências não bloqueantes:** validação real com imagem anexada e screenshot (evidência do request no Luna) fica registrada no card antes do Done.

`Design Agent verdict: PASS` — sem achados bloqueantes, `UI impact: none`, Prototype `N/A` justificado.
