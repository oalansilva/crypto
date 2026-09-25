# card-1040-antigravity-adapter — Suporte ao cliente agy no Covenant Flow (stubs, guard e AGENTS.md)

O ecossistema Google Antigravity CLI (`agy`) opera nesta VM como cliente agentic leve de terminal, mas atualmente não está integrado ao Covenant Flow: as skills canônicas em `.cursor/skills/` não são descobertas em `.agents/skills/`, as ferramentas de escrita e execução (`write_to_file`, `replace_file_content`, `run_command`) não são interceptadas pelo Write Guard determinístico (`guard.py`), e o cliente não está catalogado em `AGENTS.md`.

Este card implementa o adapter para o Antigravity CLI com paridade operacional aos clientes cooperativos já existentes (Cursor, Grok, OpenCode e dsh), sob o princípio de Zero Dual-Write.

## Problema

Operadores que utilizam o Antigravity CLI (`agy`) no repositório não possuem as skills do fluxo descobertas pelo agente e não possuem a proteção determinística do Write Guard em ferramentas nativas do Antigravity, impedindo a operação segura de cards no terminal através do `agy`.

## História

Como operador do Antigravity CLI (`agy`), quero operar cards do repositório respeitando integralmente o Covenant Flow (FSM, Write Guard e Zero Dual-Write), para executar refinamento, design, desenvolvimento, review e QA com as regras e gates do projeto plenamente ativos.

## Entra

- `scripts/process-fsm/antigravity_stubs.py`: gerador e validador de stubs leves em `.agents/skills/` apontando para as skills canônicas em `.cursor/skills/` (seguindo o padrão de `grok_stubs.py` e `opencode_stubs.py`).
- `.agents/skills/*`: stubs gerados para as skills canônicas (`covenant-flow`, `covenant-flow-environments`, `github-project-board`, `grill-card`, `kaizen`, `implantar`, `openspec-*`).
- `scripts/process-fsm/antigravity_guard.py`: adapter que recebe o payload JSON do hook `PreToolUse` do Antigravity CLI (stdin), normaliza as chamadas de ferramentas (`write_to_file`, `replace_file_content`, `run_command`), avalia no `guard.py` e retorna a decisão JSON (`allow` ou `deny`).
- `.agents/hooks.json`: configuração de hooks do Antigravity registrando `fsm-guard` em `PreToolUse` com matcher `write_to_file|replace_file_content|run_command`.
- `scripts/process-fsm/guard.py`: adição das ferramentas do Antigravity ao `WRITE_TOOLS` e `SHELL_TOOLS`, com suporte aos parâmetros `TargetFile` e `CommandLine` em `normalize()`.
- `AGENTS.md`: inclusão do `Antigravity CLI (agy)` na lista de clientes cooperativos.
- `scripts/process-fsm/test_antigravity_adapter.py`: suíte pytest validando:
  - Sincronização e integridade dos stubs em `.agents/skills/`.
  - Negação de escrita em arquivos de produto em status `Todo` e `Design` via payload Antigravity.
  - Negação de mutações perigosas via `run_command`.
  - Permissão de escrita após `Pronto para Dev`.

Critérios observáveis:
- Dado o repo com a integração, `pytest scripts/process-fsm` executa e passa 100% verde sem regressões.
- Dado um payload de escrita de produto via Antigravity em status de design, `antigravity_guard.py` retorna `{"decision": "deny", "reason": "..."}` com exit code 0.
- Dado o Antigravity CLI rodando na raiz do repositório, ele descobre as skills em `.agents/skills/` com os runbooks canônicos acessíveis sob demanda.

## Não entra

- Alterar a máquina de estados `.cursor/process-fsm.yaml` (estados, transições ou gates permanecem intocados).
- Dual-write de runbooks (o corpo do runbook continua exclusivamente em `.cursor/skills/`).
- Alterar código de produto (`backend/**`, `frontend/src/**`).
- Burlar qualquer gate humano de Alan (T1, T7, T15, T18 continuam estritamente de Alan).

## Perfil da mudança

Harness (adapter de cliente Antigravity CLI). Sem UI de produto.
