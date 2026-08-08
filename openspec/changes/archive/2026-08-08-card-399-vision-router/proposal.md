## Why

O modelo default da sessão do opencode (`opencode-go/deepseek-v4-flash`) não aceita imagens (`attachment: false`). Toda análise de imagem — testes visuais, validações de design, screenshots de ferramentas — precisa de um modelo com visão. Alan definiu `opencode-go/gpt-5.6-luna` (`attachment: true`) como modelo de análise visual, com **chaveamento automático**: o usuário não escolhe o modelo; o roteamento detecta a necessidade e delega ao Luna.

## What Changes

- Adicionar agente `vision` (subagent) com `model: opencode-go/gpt-5.6-luna` em `.opencode/agent/vision.md`.
- Adicionar plugin `vision-router` em `.opencode/plugin/vision-router.ts`:
  - `chat.message`: detecta image part na mensagem do usuário, salva o anexo em `.impeccable/attachments/` e marca a sessão;
  - `experimental.chat.messages.transform`: sessão com imagem + modelo sem visão → substitui a image part por placeholder de texto com o caminho do arquivo;
  - `experimental.chat.system.transform`: injeta instrução de delegação ao agente `vision`;
  - `tool.execute.after`: screenshots/PNG produzidos por tools (Playwright, browser-debugger) e imagens baixadas de cards/issues do GitHub (via `gh`/`curl`) em tarefas de análise visual → delegação ao `vision`;
  - log de evidência em `.impeccable/vision-router.jsonl`.
- Adicionar command `/vision <arquivo>` em `.opencode/command/vision.md` (aceita também URL de anexo do GitHub: baixa e analisa).
- Configurar `small_model: opencode-go/deepseek-v4-flash` (tarefas internas baratas); modelo default da sessão permanece flash.
- Atualizar `AGENTS.md`/`rules.md` com a política de roteamento visual (exceção explícita na regra de roteamento de LLM), incluindo: anexos em cards/issues do GitHub, julgamento de `diff.png` do QA visual, atualização de baselines, browser gate/protótipos, diagnóstico de bugs de UI, artifacts de falha do CI e gráficos/sinais exportados.
- Remover `.opencode/opencode.json` criado acidentalmente (lixo do `opencode plugin list`).

## Capabilities

### New Capabilities

- `visual-analysis-routing`: roteamento automático de tarefas com imagem para o modelo com visão (gpt-5.6-luna), sem intervenção do usuário.

### Modified Capabilities

None.

## Impact

- Affected files: `.opencode/agent/vision.md`, `.opencode/plugin/vision-router.ts`, `.opencode/command/vision.md`, `opencode.json`, `AGENTS.md`, `rules.md`, `openspec/changes/card-399-vision-router/**`, `.impeccable/` (runtime).
- Affected workflow: análise de imagens em cards, QA visual, validações de design e testes Playwright.
- Sem mudança de runtime de produto: nenhuma API, banco, worker ou tela é alterada.
