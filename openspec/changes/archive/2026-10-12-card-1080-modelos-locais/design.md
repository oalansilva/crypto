## Context

#1080 externaliza escolhas dos cinco harnesses: Cursor, Codex, Grok Build, OpenCode e dsh. A lei continua versionada; seleção não concede autorização. O mapa observado em `/srv/apps/dev/criptofarol/source/.cursor/model-map.yaml` conserva Cursor/Grok e contém a escolha Codex de Alan. A versão commitada antiga no worktree não revoga essa escolha.

UI impact: none
live_route: N/A
surface: none

Prototype: N/A. Impeccable: N/A — mudança de configuração e contratos dos adapters, sem interface, rota ou copy do produto. Crítica sem-tela e T7 continuam obrigatórios.

## Goals / Non-Goals

**Goals:** escolhas por cliente/faixa fora do Git e compartilhadas na máquina; novo spawn explícito; capacidade própria por harness; falha visível; evidência pedida/observada separadas.

**Non-Goals:** perfis por projeto, uniformização entre clientes, alteração de agentes vivos, suporte inventado, relaxamento dos gates/proibições, solução de trace ausente ou release. Escopo é o proposal copiado do issue.

## Decisions

### Arquivo e precedência

Adotar `$HOME/.config/covenant-flow/model-selection.yaml` na conta operacional do host executor (VM no Desktop+SSH). Todos seus repositórios e worktrees usam esse arquivo. Não depender de cwd, raiz Git, overlay, variável de override por projeto ou picker. Contas distintas não são agregadas automaticamente; migração registra a conta executora. Não ler mapa versionado como fallback.

Schema `version: 1`, `clients.<cursor|codex|grok|opencode|dsh>.<juizo|execucao>`, com `label`, `model` e, conforme capacidade, `provider`, `effort` ou `variant`. Esforço não aplicável é diferente de esforço obrigatório ausente. Não aceitar configuração local de papéis, proibições, capacidades ou projetos. Valores de exemplo nunca são defaults executáveis.

Resolver Python compartilhado (`scripts/process-fsm/model_selection.py`, nome proposto) com CLI JSON e funções; plugins JS chamam a CLI, sem segunda lei. Política versionada mantém papéis/faixas, `composer-2.5-fast` e `inherit`, schema e tradução por cliente. Rejeitar YAML duplicado, schema desconhecido, valores vazios e campos inválidos. Sintaxe/schema são globais; compatibilidade é validada para cliente/faixa solicitado, sem reescrever outras escolhas.

### Inventário e passagem

| Cliente | Evidência | Seleção inicial e passagem |
| --- | --- | --- |
| Cursor | mapa, agents, harness.mdc, runbook | Juízo `cursor-grok-4.6-high`; execução `composer-2.5`. Task `model` explícito nos dois caminhos. Sem parâmetro de esforço separado demonstrado; sufixo não autoriza inventá-lo. |
| Codex | codex_models.py, adapter, proxy, review | `gpt-6-astra`/`medium` e `gpt-6.1-sol`/`high`. Agent nativo com `model`/`reasoning_effort`; schema/catálogo do host valida compatibilidade. |
| Grok Build | mapa, stubs, cursor-harness | `grok-4.7` e `grok-4.6`, ambos com `high` legado. Passar `spawn_subagent.model`; esforço somente se schema aceita. Se high é fixo do host, preservar comportamento e rejeitar tentativa de variar; não inventar argumento. |
| dsh | plugin, dsh_plugin_lib.js, pacote instalado dsh-tool-subagent/lib/index.js | Repo herda rota, sem escolha fixa. Runtime aceita `provider`, `model`, `reasoning_effort` quando modelSelectionSettings/política permitem. Migrar rota efetiva; high somente onde sanitizer atual efetivamente o aplica. |
| OpenCode | plugin, opencode_plugin_lib.js, SDK/plugin locais | Repo herda rota. SDK expõe providerID/modelID e variant na mensagem; chat.params não troca modelo. Migrar rota efetiva e variant existente, sem equiparar esforço ao Codex. |

dsh: conferir `agentOptions`, política de rotas e schema de `subagent`/`subagent_fork`; seleção explícita preserva grill deny e isolamento. Sem capacidade habilitada, `capability_unavailable` antes de spawn. Descriptor captura parâmetros; guard de cada agent.ctx usa captura da criança em todas as requisições, não arquivo corrente. Sanitizer deixa de substituir ausência/incompatibilidade por high nos filhos geridos. Root/filhos já vivos mantêm contrato de nascimento.

OpenCode: passagem explícita no task não está demonstrada. Integrar plugin ao caminho nativo de criação usando SDK de sessão com parentID e primeiro prompt com provider/model e variant suportado, preservando ferramentas, restrições e retorno do task. Se a versão não permite preservar essa semântica, recusar antes da criação; não simular por chat.params, opencode.json ou preset Git. Apply ensaia versão instalada e registra capacidade concreta. Recusa não prova sucesso: cobertura pendente permanece visível, sem excluir cliente da matriz.

Capacidades vêm de schema/catálogo nativo ou contrato testado por versão do adapter. Sintaxe válida não prova disponibilidade; recusa do provedor é propagada sem substituição. Não criar allowlist fixa de escolhas operacionais que exija commit para novos modelos já aceitos pelo host.

### Captura por spawn e onda

Cada novo spawn relê arquivo e captura cliente, faixa, parâmetros, digest dos bytes, versão da política/capacidade e tentativa. Guard valida faixa do papel, não apenas coincidência com qualquer par. Argumentos, proxy, retorno e auditoria usam essa captura imutável. Edição posterior não modifica filho nem faz proxy comparar com escolha nova.

Reviewers/A-B: reler antes de cada nascimento e comparar seleção daquela faixa com captura da onda. Se mudar entre dois spawns, cancelar tentativa parcial, registrar selection_changed e iniciar nova onda explicitamente; nunca aceitar dupla divergente. Mudança só em outra faixa/cliente não invalida onda. Nenhum filho é retunado; captura não vira cache do próximo agente independente.

Autor/crítico não nascem como onda: mudança entre ambos vale para o próximo filho, com evidência explícita. Remover igualdade histórica autor/crítico como pin operacional, preservando juízo e isolamento; A/B da mesma onda mantém igualdade. Resume/destape mantém captura original; modelo diferente exige spawn novo. Release compara pai observado à captura de execução da operação, recusa divergência e não muda sessão viva ou T16.

Proxies separam requested/observed, host/versão reais, status, payload e captura. Esforço não suportado = not_applicable; aplicável sem trace = unavailable. Nunca inferir observado do request. Gates que exigem prova continuam falhando; esta história não cria trace.

### Migração e pin

Separar migrate/validate/resolve da instalação. Migração recebe fonte identificada e produz plano antes de escrita atômica; não roda implicitamente no pin/spawn. Arquivo existente prevalece, sem sobrescrever/completar silenciosamente. Conflitos são mostrados; rota OpenCode/dsh ausente impede marcar cliente migrado. Materializar identificador efetivo da configuração nativa, sem reutilizar outro cliente nem inherit; isso não atesta execução.

Nesta máquina Cursor/Grok partem do mapa em source acima; Codex usa pares pedidos por Alan. Extrair só rotas não secretas OpenCode/dsh, sem credenciais. Usar temporário/rename no mesmo diretório; edição manual incompleta falha visivelmente até corrigida.

Atualizar callers Codex, guards/proxies/review, paging.py, release_closeout.py, JS, runbook/kaizen/skills e stubs. Remover escolhas e YAML model redundante dos reviewers, mantendo spawn explícito. Retirar PIN_PAIRS e exigência do mapa no instalador; pin atualiza mecanismos/política sem escrever configuração local. Mapa Git deixa de ser fonte operacional; proibições migram à política, com diagnóstico sem fallback. Inventariar referências com rg incluindo testes/helpers Covenant Flow. Consumidor antigo não recebe comportamento novo até atualizar processo.

## Risks / Trade-offs

- Capacidade ausente → recusa e cobertura pendente; mock não é prova viva.
- Edição durante onda → captura/comparação por faixa e falha explícita da tentativa parcial.
- Consumidor antigo → atualização inicial necessária; futuras escolhas nos migrados dispensam card/commit/release.
- Política nova proíbe modelo capturado → recusar continuidade sem substituir.
- Outra conta na máquina → registrar conta executora; não criar cópia por repo.

## Migration Plan

1. Após T7/T8, fechar schemas/fontes não secretas e plano preservando clientes.
2. Implementar resolver/política, adapters/evidência, instruções/pins sem mutar configuração operacional nos testes.
3. Ensaiar HOME temporário, dois repos/dois worktrees, mudança por faixa/onda e falhas.
4. Migrar explicitamente no host autorizado e ensaiar caminhos; sem trace, observado continua unavailable.
5. Rollback preserva arquivo local e backup; incompatibilidade é diagnosticada, nunca sobrescrita por pin antigo. Sem release neste Design.

## Open Questions

Apply fecha capacidade de esforço Grok, ligação nativa OpenCode, seleção habilitada dsh e suas rotas não secretas. São pendências técnicas com falha fechada definida; não autorizam declarar cobertura completa sem ensaio. Mérito do Design, validade OpenSpec e atestação runtime são resultados distintos.

## Design Critique

- P0–P2 — Nenhum achado de escopo ou contrato observável; disposition: sem rework; verdict de conteúdo: PASS.
- P3 — Confirmar capacidades e ligação dos adapters no Apply; disposition: aceito como detalhe de Apply, já previsto nas tasks; verdict: não bloqueia o conteúdo.
- Design Agent verdict: PASS — conteúdo e atestação validados; traces `session_meta`/`turn_context`/`task_complete` confirmam autor e crítico em `gpt-6-astra` / `medium`, Codex CLI `0.162.0`, com retorno e payload. O bloqueio anterior por `unavailable` foi resolvido pela coleta da evidência existente, sem nova rodada de crítica.
