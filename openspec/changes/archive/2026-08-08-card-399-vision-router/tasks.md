## Tasks

## 1. Setup

- [x] 1.1 Remover `.opencode/opencode.json` acidental (lixo do `opencode plugin list`).
- [x] 1.2 Configurar `small_model: opencode-go/deepseek-v4-flash` no `opencode.json`.

## 2. Agente vision

- [x] 2.1 Criar `.opencode/agent/vision.md` (mode: subagent, model: opencode-go/gpt-5.6-luna, prompt de análise visual rigorosa).

## 3. Plugin vision-router

- [x] 3.1 Criar `.opencode/plugin/vision-router.ts` com `chat.message` (detecção + persistência de anexo).
- [x] 3.2 Implementar `experimental.chat.messages.transform` (placeholder para modelos sem visão).
- [x] 3.3 Implementar `experimental.chat.system.transform` (instrução de delegação ao vision).
- [x] 3.4 Implementar `tool.execute.after` (screenshots de tools em tarefas visuais) e log `.impeccable/vision-router.jsonl`.

## 4. Command e docs

- [x] 4.1 Criar `.opencode/command/vision.md` (`/vision <arquivo|url-do-github>` — baixa anexo de card/issue quando for URL; aceita múltiplas imagens para comparação antes/depois).
- [x] 4.2 Atualizar `AGENTS.md`/`rules.md` com política de roteamento visual (exceção explícita na regra de roteamento de LLM), cobrindo: anexos de cards/issues do GitHub (baixar com `gh` e delegar ao `vision`), julgamento de `diff.png` do QA visual, baselines, browser gate/protótipos, diagnóstico de bugs, artifacts do CI e gráficos/sinais exportados.

## 5. Validação e integração

- [x] 5.1 Validar sintaxe do plugin (node --check) e configs (jq).
- [x] 5.2 Testar `/vision` com screenshot real (evidência: resposta do Luna). Testado: unit do plugin (4/4 cenários) + subagent vision com 2 baselines reais (desktop/mobile) rodando com `opencode-go/gpt-5.6-luna` (evidência no banco da sessão `ses_020e3349`); log em `.impeccable/vision-router.jsonl`.
- [x] 5.3 Commit, push, PR para develop, checks verdes e merge.
