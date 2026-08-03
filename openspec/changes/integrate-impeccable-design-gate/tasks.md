## 1. Instalação e contexto

- [x] 1.1 Instalar o provider Codex do Impeccable em escopo project-local com CLI npm `3.5.0`, payload da skill `4.0.4` e registrar o `gitHead` npm resolvido.
- [x] 1.2 Versionar `.agents/skills/impeccable/` e `.codex/hooks.json`, preservando entradas de hook não relacionadas.
- [x] 1.3 Criar `PRODUCT.md` com contexto do Cripto Farol e referência explícita ao `DESIGN.md` como fonte visual canônica.
- [x] 1.4 Adicionar o bloco oficial de ignore para saídas efêmeras do Impeccable, mantendo artefatos compartilhados de configuração e crítica rastreáveis.

## 2. Contrato do estágio Design

- [x] 2.1 Atualizar `.agents/skills/design-critic/SKILL.md` com o pipeline `context -> shape -> prototype -> critique -> audit -> targeted fixes -> polish -> browser gate`.
- [x] 2.2 Definir no contrato a crítica dual-agent read-only e a herança exata do LLM/modelo e versão da sessão principal do Codex.
- [x] 2.3 Definir no contrato as seções `Impeccable Brief`, `Impeccable Critique`, `Impeccable Audit` e `Impeccable Trace`, os critérios de PASS/BLOCKED e o caminho `UI impact: none`.
- [x] 2.4 Atualizar `AGENTS.md`, `rules.md` e `openspec/config.yaml` para tornar o gate obrigatório no Codex para `UI impact: affected`, sem alterar Cursor ou a aprovação humana de Alan.
- [x] 2.5 Registrar a decisão, versão e rollback em `docs/decision-log.md`.

## 3. Validação e fechamento

- [x] 3.1 Validar sintaxe/configuração do hook, presença da skill local, contexto do produto e ausência de alteração indevida no `DESIGN.md`.
- [x] 3.2 Executar o detector Impeccable contra um protótipo HTML existente e registrar qualquer finding como resolvido ou classificado.
- [x] 3.3 Executar `openspec validate --all`, revisar o diff completo e confirmar que os adapters Cursor permanecem inalterados.
- [x] 3.4 Executar `openspec status --change "integrate-impeccable-design-gate" --json` e marcar somente as tarefas efetivamente implementadas e validadas.
