# Design — card-1040-antigravity-adapter (Harness Antigravity CLI)

UI impact: none
live_route: N/A Suporte ao cliente Antigravity CLI no Covenant Flow (harness de processo); sem tela, rota ou HTML de produto
surface: new

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card **#1040**, Status=Design.
Este card trata da integração completa do ecossistema Google Antigravity CLI (`agy`) ao Covenant Flow, estabelecendo paridade operacional com os demais clientes cooperativos do projeto (Cursor Agent, Grok Build, OpenCode e dsh), sob o princípio inegociável de **Zero Dual-Write**.

O `agy` opera como ferramenta CLI agentic no ambiente desta VM Linux, interagindo diretamente com o repositório por meio de ferramentas nativas de inspeção e mutação: leitura de arquivos (`view_file`), escrita (`write_to_file`), substituição de trechos (`replace_file_content`) e execução de comandos shell (`run_command`). Atualmente, o repositório não expõe para o Antigravity as convenções e runbooks do processo (pois as skills canônicas residem exclusivamente sob `.cursor/skills/` e o Antigravity descobre skills em `.agents/skills/`), nem intercepta suas ferramentas nativas no Write Guard determinístico (`guard.py`). Adicionalmente, o cliente não consta no catálogo formal de clientes em `AGENTS.md`.

Esta entrega é puramente de **harness de processo** (`UI impact: none`, `live_route: N/A`, `surface: new`): não altera telas, rotas, protótipos, endpoints de aplicação, modelos de dados ou scripts de produção. Não modifica a máquina de estados `.cursor/process-fsm.yaml` e preserva integralmente todos os gates humanos de Alan (T1, T7, T15, T18).

## Factos do código

A análise direta dos arquivos do repositório no worktree revela os seguintes fatos:

1. **`scripts/process-fsm/guard.py` (Write Guard determinístico):**
   - Em `:46-59`, `WRITE_TOOLS` é um `frozenset` contendo ferramentas do Cursor, Grok e OpenCode: `{"Write", "StrReplace", "Delete", "EditNotebook", "write", "search_replace", "Edit", "MultiEdit", "edit", "apply_patch"}`. As ferramentas de escrita e edição do Antigravity — `write_to_file` e `replace_file_content` — **não constam** no conjunto.
   - Em `:63-65`, `SHELL_TOOLS` contém `{"Shell", "Bash", "run_terminal_command", "run_terminal_cmd", "bash"}`. A ferramenta de execução shell do Antigravity — `run_command` — **não consta** no conjunto.
   - Em `:66`, `PATH_KEYS` lista `("path", "file_path", "file", "target_file", "target_notebook", "filePath")`. O Antigravity utiliza o parâmetro em PascalCase `TargetFile`.
   - Em `:164-194`, `normalize()` extrai o comando shell de `src.get("command")` ou `data.get("command")`. No Antigravity, `run_command` recebe o comando no parâmetro `CommandLine` dentro do dicionário de argumentos (`tool_input`/`args`).
   - Em `:196-207`, `emit()` já gera a chave `"decision": "allow" | "deny"`, além de `"permission"`, `"reason"`, `"agent_message"` e `"user_message"`. A chave `decision` coincide com a especificação formal de saída do hook `PreToolUse` do Antigravity.
   - Em `:730-746`, `main()` consome JSON de `sys.stdin` e escreve o JSON resultante em `sys.stdout` com `return 0`.

2. **Padrão de stubs leves (`grok_stubs.py` e `opencode_stubs.py`):**
   - Em `scripts/process-fsm/grok_stubs.py` e `scripts/process-fsm/opencode_stubs.py`, o repositório mantém geradores e validadores que criam stubs leves contendo apenas o frontmatter extraído das skills canônicas em `.cursor/skills/` e um corpo curto (máximo de 8 linhas) com uma diretiva explícita de leitura do runbook canônico (`MUST Read .../SKILL.md`).
   - O validador `stub_errors()` verifica que nenhum stub esteja ausente, obsoleto, com corpo longo ou contendo cópia integral do runbook (garantia de Zero Dual-Write).
   - No diretório `.agents/skills/`, existem atualmente três subdiretórios: `impeccable`, `playwright-cli` e `design-critic`. As skills `impeccable` e `playwright-cli` são canônicas em `.agents/skills/` (não devem ser sobrescritas por geradores de stubs). A skill `design-critic` tornou-se canônica em `.cursor/skills/design-critic/` no card #854; portanto, `.agents/skills/design-critic/SKILL.md` deve ser convertida em stub apontando para o seu correspondente canônico em `.cursor/skills/`.

3. **Hooks do Antigravity CLI:**
   - O ecossistema Antigravity CLI suporta configuração de hooks de ciclo de vida em `.agents/hooks.json`.
   - Para interceptar a execução de ferramentas, utiliza-se o evento `PreToolUse` com uma expressão regular no campo `matcher` (ex.: `"write_to_file|replace_file_content|run_command"`).
   - O comando configurado no hook recebe o payload via `stdin` com a estrutura `{"toolCall": {"name": ..., "args": ...}, "cwd": ..., ...}` e aguarda na saída padrão `stdout` um JSON com `{"decision": "allow" | "deny", "reason": "..."}`.
   - Qualquer saída com `decision: "deny"` bloqueia a execução da ferramenta no Antigravity CLI imediatamente.

4. **`AGENTS.md`:**
   - Em `:8-9`, o arquivo define os clientes cooperativos:
     `Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).`
     `Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.`
   - O Antigravity CLI (`agy`) deve ser integrado explicitamente a ambas as diretivas para manter coerência operacional.

## Goals / Non-Goals

**Goals:**

- Integrar o Antigravity CLI (`agy`) ao ecossistema do Covenant Flow com paridade aos demais clientes cooperativos.
- Garantir Zero Dual-Write: disponibilizar stubs leves em `.agents/skills/` apontando para as skills canônicas em `.cursor/skills/`, preservando as skills canônicas locais (`impeccable` e `playwright-cli`).
- Interceptar deterministamente ferramentas de escrita (`write_to_file`, `replace_file_content`) e de execução shell (`run_command`) do Antigravity via `guard.py` e `.agents/hooks.json`.
- Bloquear qualquer tentativa de escrita em arquivos de produto (`backend/**`, `frontend/src/**`) antes do card atingir `Status=Pronto para Dev` (T8).
- Bloquear redirecionamentos e mutações perigosas em comandos de terminal executados via `run_command`.
- Catalogar o `Antigravity CLI (agy)` em `AGENTS.md` como cliente cooperativo com proibição de alegação de modo Auto.
- Entregar suíte automatizada `scripts/process-fsm/test_antigravity_adapter.py` com cobertura completa e 100% verde sem regressões no conjunto `scripts/process-fsm`.

**Non-Goals:**

- Não alterar a máquina de estados do processo em `.cursor/process-fsm.yaml` (estados, transições, atores e gates permanecem intactos).
- Não duplicar o corpo de nenhum runbook (runbooks canônicos continuam exclusivamente em `.cursor/skills/`).
- Não alterar código de produto (`backend/**`, `frontend/src/**`).
- Não alterar ou afrouxar os gates de aprovação humana de Alan (T1, T7, T15, T18 continuam exclusivos de Alan autenticado).
- Não criar rotas, páginas, mockups visuais ou telas (entrega sem UI).

## Decisions

### 1. Antigravity stubs em `.agents/skills/*` via `scripts/process-fsm/antigravity_stubs.py`

Implementar o módulo `scripts/process-fsm/antigravity_stubs.py` seguindo a arquitetura estabelecida em `grok_stubs.py` e `opencode_stubs.py`. O módulo gerencia stubs sob `.agents/skills/` que apontam para as skills canônicas em `.cursor/skills/`.

- **Formato do stub:**
  ```markdown
  ---
  name: <skill-name>
  description: <raw-description-from-canonical>
  ---

  # <skill-name>

  Cliente: Antigravity CLI (agy). MUST Read `.cursor/skills/<skill-name>/SKILL.md` and follow it as the runbook.
  Do not copy the runbook here.
  ```
- **Preservação de skills canônicas locais:** as skills `impeccable` e `playwright-cli`, cujo arquivo canônico reside em `.agents/skills/`, não são sobrescritas nem validadas como stubs.
- **Migração de `design-critic`:** o arquivo existente em `.agents/skills/design-critic/SKILL.md` (remanescente do período anterior ao card #854) é substituído por um stub leve apontando para o canônico em `.cursor/skills/design-critic/SKILL.md`.
- **Validação de integridade (`stub_errors`):** detecta stubs ausentes, obsoletos (conteúdo divergente do gerado), stubs com corpo excedendo 8 linhas não vazias, ou ausência do ponteiro canônico.

*Alternativas rejeitadas:*
- *Symlinks simbólicos:* rejeitados por complexidade de compatibilidade entre ambientes Linux/Windows e histórico do git.
- *Dual-write de runbooks:* rejeitado categoricamente por violar o princípio de Zero Dual-Write e introduzir risco de dessincronização de regras de processo.

### 2. Adapter `antigravity_guard.py` e `.agents/hooks.json` PreToolUse

Criar o adaptador `scripts/process-fsm/antigravity_guard.py` e registrar o hook em `.agents/hooks.json`.

- **`.agents/hooks.json`:**
  Define o hook `fsm-guard` para o evento de ciclo de vida `PreToolUse` com a expressão de correspondência:
  `"matcher": "write_to_file|replace_file_content|run_command"`.
  Invoca `python3 scripts/process-fsm/antigravity_guard.py` (ou resolução de caminho absoluto relativa à raiz do repositório identificada via git).
- **Contrato de entrada e saída de `antigravity_guard.py`:**
  - Entrada (`sys.stdin`): JSON contendo `{"toolCall": {"name": ..., "args": ...}, "cwd": ...}`.
  - O adapter converte o payload para o envelope padrão do `guard.py` (`tool_name`, `tool_input`, `command`, `cwd`), invoca a função `decide()` de `guard.py` e extrai os campos de resultado.
  - Saída (`sys.stdout`): JSON contendo estritamente `{"decision": "allow" | "deny", "reason": "..."}`.
  - Saída sempre com exit code 0 para conformidade com a especificação de hooks do Antigravity CLI.
  - Comportamento **fail-closed**: em caso de erro na leitura do JSON ou exceção interna, o script emite `{"decision": "deny", "reason": "Fail-closed: malformed payload or internal guard error"}` com exit code 0.

*Alternativas rejeitadas:*
- *Executar `guard.py` diretamente no hook:* rejeitado porque o Antigravity envia o envelope com chaves específicas (`toolCall`, `name`, `args`), exigindo descompactação e conformidade estrita de schema de saída (`decision` e `reason`).
- *Script shell intermediário:* rejeitado para evitar acoplamento desnecessário e garantir tratamento seguro de JSON via Python stdlib.

### 3. Normalização em `scripts/process-fsm/guard.py`

Estender diretamente `guard.py` para suportar nativamente as assinaturas das ferramentas do Antigravity:

- **`WRITE_TOOLS`:** adicionar `"write_to_file"` e `"replace_file_content"`.
- **`SHELL_TOOLS`:** adicionar `"run_command"`.
- **`PATH_KEYS`:** adicionar `"TargetFile"` e `"targetFile"`.
- **`normalize()`:**
  - Extrair `CommandLine` de `data` (`tool_input`/`args`) caso `command` ainda não esteja preenchido.
  - Suportar extração de `tool` e `data` a partir de `toolCall` caso o payload seja passado diretamente ao `guard.py`.

*Alternativas rejeitadas:*
- *Fazer toda a tradução unicamente no adapter sem tocar em `guard.py`:* rejeitado porque `guard.py` é o componente central de segurança determinística do repositório e deve ter conhecimento de primeira classe sobre todas as ferramentas permitidas/gated no ecossistema de agentes.

### 4. Catálogo de clientes em `AGENTS.md`

Atualizar o arquivo `AGENTS.md` no bloco de clientes:
- Incluir `Antigravity CLI (agy)` na lista de clientes cooperativos sujeitos a ensaio deny na branch de integração.
- Incluir o `agy` na restrição de alegação de modo Auto.

*Alternativas rejeitadas:*
- *Omitir o cliente do `AGENTS.md`:* rejeitado por violar a transparência operacional e impedir que agentes reconheçam formalmente o runtime do terminal.

### 5. Suíte pytest `scripts/process-fsm/test_antigravity_adapter.py`

Construir uma suíte de testes dedicada no padrão das suítes de harness existentes (`test_opencode_adapter.py`, `test_dsh_adapter.py`):
- `test_antigravity_stubs_integrity()`: valida que todos os stubs existem, estão atualizados, não excedem 8 linhas e contêm o ponteiro canônico (`stub_errors() == []`).
- `test_antigravity_write_product_denied_in_design_and_todo()`: valida a recusa de escritas em `backend/**` e `frontend/src/**` para `write_to_file` e `replace_file_content` nos status `Todo` e `Design`.
- `test_antigravity_shell_mutations_denied()`: valida que `run_command` com mutações (`> backend/app/main.py` ou `tee`) é recusado.
- `test_antigravity_product_write_allowed_in_pronto_para_dev()`: valida que chamadas de escrita são permitidas quando o status é `Pronto para Dev`.
- `test_antigravity_design_write_allowed_in_design()`: valida que escritas em `openspec/changes/` são autorizadas durante `Status=Design`.
- `test_antigravity_guard_cli_execution()`: valida o comportamento do script `antigravity_guard.py` via `subprocess` e entrada por `stdin`, testando casos de `allow`, `deny` e `fail-closed` em payloads inválidos.

## Risks / Trade-offs

- **[Risco: Sobrescrita de skills canônicas em `.agents/skills/`]**
  *Mitigação:* `antigravity_stubs.py` mantém uma tupla explícita de exceções (`AGENTS_CANONICAL_SKILLS = ("impeccable", "playwright-cli")`) e o validador ignora essas pastas na checagem de stubs.

- **[Risco: Variação de CWD na invocação de hooks]**
  *Mitigação:* `antigravity_guard.py` detecta a raiz do repositório procurando a pasta `.git` a partir de `__file__` e do diretório corrente, assegurando importação correta de `guard.py` independentemente do diretório de execução do hook.

- **[Risco: Latência na execução de PreToolUse]**
  *Mitigação:* O adaptador utiliza apenas módulos da biblioteca padrão de Python (`json`, `sys`, `pathlib`, `os`), executando em poucos milissegundos (< 30ms), sem overhead sensível para o operador.

- **[Trade-off: Dependência de Python 3 no ambiente do host]**
  *Aceito:* O repositório e o ecossistema do projeto já exigem Python 3 para o backend e para todos os outros hooks e ferramentas do Covenant Flow (`guard.py`, `fsm.py`, `process_event.py`).

## Apply contract

**Arquivos adicionados:**
- `scripts/process-fsm/antigravity_stubs.py`
- `scripts/process-fsm/antigravity_guard.py`
- `scripts/process-fsm/test_antigravity_adapter.py`
- `.agents/hooks.json`
- `.agents/skills/*/SKILL.md` (stubs leves gerados)

**Arquivos modificados:**
- `scripts/process-fsm/guard.py` (suporte a ferramentas e argumentos do Antigravity)
- `AGENTS.md` (catálogo de clientes cooperativos)

**Arquivos expressamente NÃO tocados:**
- `.cursor/process-fsm.yaml` (máquina de estados permanece estritamente inalterada)
- Código de produto (`backend/**`, `frontend/src/**`)
- Migrações, modelos, rotas e testes de aplicação
- Gates humanos de Alan (T1, T7, T15, T18)

**P3 — detalhes de Apply aceitos (resolvidos no Apply, sem gerar P0/P1):**
- Variações mecânicas de comandos de fallback na localização do script em `.agents/hooks.json`.
- Ordem interna de imports e tipagem estrita em `antigravity_stubs.py` e `antigravity_guard.py`.

## Prototype

N/A Suporte ao cliente Antigravity CLI no Covenant Flow (harness de processo); sem tela, rota ou HTML de produto

## Open Questions

Nenhuma. O escopo está plenamente delimitado no briefing do issue #1040 e a arquitetura segue os padrões já testados e aprovados de Grok, OpenCode e dsh.

## Design Critique

Publicada pelo pai após a onda de crítica (excepção prevista no runbook). Sem-tela: o crítico é **um**; sem onda A/B, sem protótipo, sem clone de página viva e sem Snapshot Impeccable.

**Onda desta entrada (teto 1+1+1, sem-tela):** 1 autor → 1 crítico → **sem rework**. `rework: nao`, `p0_p1_count: 0`. A coluna segue para `Aprovação de Design`.

**Crítico (ronda única):** rubrica **10/10 `ok`** — tokens do gate, briefing verbatim, **âmbito completo**, causa e fatos do código confirmados, formato fixado, `process-fsm.yaml` inalterado, escopo, cobertura dos critérios observáveis, tasks e a nota de processo. Dois achados, todos **P3** com `bloqueia_merge: nao` — gravidade e classe copiadas do dump, sem reclassificação:

| id | gravidade | classe | bloqueia_merge | achado | fecho |
| --- | --- | --- | --- | --- | --- |
| FIND-1040-01 | **P3** | Detalhe de Apply | nao | Resolução de path e CWD em `antigravity_guard.py` para suportar invocações de hook com CWD em subpastas sem depender de `PYTHONPATH`. | **Aceito** (detalhe de Apply): resolvido na task 3.1 do Apply usando resolução relativa a `Path(__file__).resolve()`. |
| FIND-1040-02 | **P3** | Detalhe de Apply | nao | `.agents/skills/design-critic/SKILL.md` existente (158 linhas legadas) precisa ser sobrescrito pelo stub leve apontando para o canônico `.cursor/skills/design-critic/SKILL.md`. | **Aceito** (detalhe de Apply): resolvido na task 1.2 do Apply via `antigravity_stubs.py`. |

**Âmbito completo?** **SIM** — veredicto explícito do crítico: nenhum item de integração ficou de fora (`antigravity_stubs.py`, `.agents/skills/*`, `antigravity_guard.py`, `.agents/hooks.json`, `guard.py`, `AGENTS.md` e `test_antigravity_adapter.py`).

**Sem achados de produto/escopo:** confirmado — nenhum P0/P1.

**Proxies desta entrada:**
- Spawns: **2** (Design-autor, Design-critic; sem rework)
- `design.md` words: 2.348
- HTML generated vs copied: **N/A vs N/A**
- Prototype: **N/A**
- Impeccable: **N/A**
- proxy modelo: design-autor → deepseek-flash (deepseek-flash)
- proxy modelo: design-critic → deepseek-flash (deepseek-flash)
