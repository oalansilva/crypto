## Tasks

## 1. Setup

- [ ] 1.1 Remover `.opencode/opencode.json` acidental (lixo do `opencode plugin list`).
- [ ] 1.2 Configurar `small_model: opencode-go/deepseek-v4-flash` no `opencode.json`.

## 2. Agente vision

- [ ] 2.1 Criar `.opencode/agent/vision.md` (mode: subagent, model: opencode-go/gpt-5.6-luna, prompt de análise visual rigorosa).

## 3. Plugin vision-router

- [ ] 3.1 Criar `.opencode/plugin/vision-router.ts` com `chat.message` (detecção + persistência de anexo).
- [ ] 3.2 Implementar `experimental.chat.messages.transform` (placeholder para modelos sem visão).
- [ ] 3.3 Implementar `experimental.chat.system.transform` (instrução de delegação ao vision).
- [ ] 3.4 Implementar `tool.execute.after` (screenshots de tools em tarefas visuais) e log `.impeccable/vision-router.jsonl`.

## 4. Command e docs

- [ ] 4.1 Criar `.opencode/command/vision.md` (`/vision <arquivo|url-do-github>` — baixa anexo de card/issue quando for URL; aceita múltiplas imagens para comparação antes/depois).
- [ ] 4.2 Atualizar `AGENTS.md`/`rules.md` com política de roteamento visual (exceção explícita na regra de roteamento de LLM), cobrindo: anexos de cards/issues do GitHub (baixar com `gh` e delegar ao `vision`), julgamento de `diff.png` do QA visual, baselines, browser gate/protótipos, diagnóstico de bugs, artifacts do CI e gráficos/sinais exportados.

## 5. Validação e integração

- [ ] 5.1 Validar sintaxe do plugin (node --check) e configs (jq).
- [ ] 5.2 Testar `/vision` com screenshot real (evidência: resposta do Luna).
- [ ] 5.3 Commit, push, PR para develop, checks verdes e merge.
