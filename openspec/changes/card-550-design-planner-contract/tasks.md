## 1. Gate, classificação e limites

- [x] 1.1 Confirmar no início da implementação que o card #550 está em `Pronto para Dev`; bloquear qualquer `/opsx:apply` ou edição de implementação enquanto essa evidência não existir.
- [x] 1.2 Registrar a aprovação humana com autor, referência e horário, vinculada ao digest do pacote normativo aprovado; rejeitar aprovação ausente, ambígua ou referente a digest anterior.
- [x] 1.3 Preservar `UI impact: none`, `Prototype: N/A` e browser gate de protótipo como N/A justificado, sem omitir os gates `Design -> Aprovação de Design -> Pronto para Dev`.
- [x] 1.4 Fixar uma allowlist de escopo para #550 e adicionar check de diff que rejeite migração ampla do #555 ou alterações em defaults/plugins gerais, workflow DB, Hermes e implementações de `/opsx:apply` ou `/opsx:verify`.

## 2. Compatibilidade e perfis candidates

- [x] 2.1 Implementar feature gate para aceitar exatamente OpenCode `1.18.18`; versão, campo ou schema diferente deve produzir evidence e `BLOCKED`.
- [x] 2.2 Criar fixtures dos eventos `session.created`, `chat.message` e `tool.execute.before/after`, além do contexto de custom tool, cobrindo todos os campos usados pelo adapter.
- [x] 2.3 Criar fixtures do SDK para `session.create` e `session.prompt`/`promptAsync`, comprovando parent, directory, child retornado, `messageID`, agent/model/parts selados e ausência de override de tools.
- [x] 2.4 Criar fixture do runtime DB para `AssistantMessage` e parts que prove a semântica de `ToolContext.messageID`, `sessionID` e `parentID`; desabilitar o writer quando a correlação não for única.
- [x] 2.5 Adicionar `design-planner-candidate-v1` como Sol (`openai/gpt-5.6-sol`) variant `high`, com broad deny ordenado antes da única permissão final `design_artifact_write`, e testar a policy efetiva.
- [x] 2.6 Adicionar `design-critic-readonly-candidate-v1` como Sol variant `high`, com deny efetivo para todas as tools, inclusive native, custom, MCP, rede, shell e delegação.

## 3. Guard, manifests, tools e leases

- [x] 3.1 Implementar o guard project-local dedicado `design-gate-guard.ts` sem alterar plugin geral, registrando somente `design_spawn_stage`, `design_openspec_readonly` e `design_artifact_write` para os papéis e fases previstos.
- [x] 3.2 Gerar manifest canônico pre-spawn com `run_id`, stage, nonces single-use, parent/worktree, exact paths, versões, config/profile digests, `build_id`, deployment digest e todos os bytes/digests do packet.
- [x] 3.3 Selar no input a marker e o packet completo com encoding e byte length explícitos, e validar os parts reais observados contra `input_message_id`, manifest e `packet_sha256` antes do binding.
- [x] 3.4 Persistir a lease FSM `CREATED -> BOUND -> FINALIZING -> CLOSED|ABORTED`, com owner, deadline, fsync, tombstones e recovery fail-closed antes de liberar lease órfã.
- [x] 3.5 Implementar `design_spawn_stage` como operação main-only e single-use que cria e prompta exatamente um child via SDK, sem shell, Task ou tool override, e bloqueia retorno vazio ou IDs divergentes.
- [x] 3.6 Implementar `design_openspec_readonly` apenas para `status|instructions|validate`, com argv/cwd/env estruturados, executable absoluto aprovado e `shell: false`; rejeitar command strings e qualquer flag não enumerada.
- [x] 3.7 Implementar o schema data-only de `design_artifact_write` para exatamente uma operação `full_content` ou `safe_patch`, exigindo exact path, base digest, manifest nonce/digest e `operation_nonce` single-use.
- [x] 3.8 Correlacionar `(sessionID, operation_nonce, argsHash)` ao `callID` observado, impor single-flight e broad deny process-scoped durante a lease, e bloquear qualquer diff persistente sem cadeia autorizada completa.

## 4. Writer Linux, build e evidence

- [x] 4.1 Criar o native writer helper Linux com protocolo canônico via stdin, argv fixo, ambiente mínimo, executable absoluto e feature probes de kernel, syscalls, helper build e protocol version.
- [x] 4.2 Resolver worktree e parents por dirfd com `openat2(RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS)`, validando owner, arquivo regular, link count e base digest; bloquear sem fallback TypeScript.
- [x] 4.3 Instalar bytes por temp no mesmo parent com `O_CREAT|O_EXCL|O_NOFOLLOW`, escrita completa, `fstat`, `fsync`, revalidação, `renameat2` ou fallback `renameat` testado e `fsync` do diretório.
- [x] 4.4 Gerar `build_id` independente antes de compilar e embutir somente esse ID e a protocol version no guard, writer helper e readonly runner; testar que nenhum hash final é auto-referente.
- [x] 4.5 Gerar `deployment-manifest.json` canônico somente após todos os builds, com versões e hashes reais finais, e calcular externamente `deployment_manifest_sha256` sem embuti-lo nos componentes.
- [x] 4.6 Registrar no journal/evidence a identidade runtime completa de cada componente do TCB: PID/PPID, executable absoluto, digest real, process start, `build_id`, `module_instance_id`, protocol version e exit/result.
- [x] 4.7 Implementar verifier read-only que reconcilie deployment manifest, bytes carregados/executados, runtime DB/eventos, journal hash-chained, sidecar e artefatos, declarando explicitamente a trust boundary do processo e sem promover workflow.

## 5. Assessments e síntese determinística

- [x] 5.1 Versionar schema UTF-8 JSON canônico para Assessment A/B com assessment, lineage, round, source digest e findings completos; rejeitar output vazio, prose, campos extras inválidos ou bytes não reproduzíveis.
- [x] 5.2 Executar A e B em child sessions distintas, com packet bytes idênticos, zero tools e Sol/high observado, preservando integralmente parts, output bytes e hashes sem acesso cruzado.
- [x] 5.3 Implementar pre-assignment de todo P0/P1 herdado a ambos os critics e merge conservador por lineage, no qual omissão, conflito, stale digest, ID inválido ou `open` de qualquer critic mantém `BLOCKED`.
- [x] 5.4 Gerar deterministicamente `generated_block_bytes` e verdict a partir dos payloads preservados, permitindo ao author apenas substituir o intervalo marcado verbatim e verificando igualdade byte a byte.
- [x] 5.5 Calcular `normative_digest` sobre proposal, design sem o bloco gerado, specs ordenadas e tasks; exigir novo A/B para qualquer byte normativo alterado e falhar fechado para evidence vazia, incompleta ou stale.

## 6. Matriz de testes do contrato

- [x] 6.1 Testar o caminho positivo staged `proposal -> design/specs/prototype enumerado -> tasks`, atribuindo cada diferença aos child authors, exact paths, calls e operation nonces corretos.
- [x] 6.2 Testar positivamente writer full-content/safe-patch, probes Linux, cadeia openat2/rename/fsync, readonly runner e leases normais e recuperadas até estados terminais duráveis.
- [x] 6.3 Testar positivamente A/B independentes, resolução dual, merge conservador, generated block byte-identical, normative digest e reconciliação completa pelo verifier.
- [x] 6.4 Testar negações de profiles e guard: tool não enumerada, read/edit/bash/task/rede/MCP, path fora da allowlist, critic mutante e spawn fora de `design_spawn_stage` devem produzir `BLOCKED` mecânico.
- [x] 6.5 Testar falhas de lifecycle e correlação: spawn vazio, create/prompt mismatch, packet/parts/message IDs divergentes, nonce reusado, mapping ambíguo, chamadas paralelas, deadline, crash e lease órfã.
- [x] 6.6 Testar falhas do helper e build: traversal, symlink, stale base, inode inseguro, probe ausente, rename/fsync failure, `build_id` divergente, deployment manifest/hash incorreto e bytes reais incompatíveis.
- [x] 6.7 Testar falhas de evidence e crítica: process/session stale, campo TCB ausente, journal/DB/evento inconsistente, evidence reconstruída, A/B vazio ou stale, finding omitido/reclassificado, bloco alterado e diff persistente inexplicado.

## 7. Ativação canonical e rollback

- [x] 7.1 Validar os perfis candidates e toda a matriz em worktree dedicada, sob freeze documentado e processo OpenCode novo; registrar que sucesso candidate não ativa nomes canônicos.
- [x] 7.2 Executar cutover canonical quiescente: bloquear runs, terminalizar leases, parar o processo, instalar um build/manifest coerente, copiar os bytes validados para os nomes canônicos, desabilitar candidates e repetir a matriz em processo e sessions novos.
- [x] 7.3 Exercitar rollback quiescente restaurando commit/build/deployment manifest anteriores somente com processo parado e leases terminais, preservando journals e mantendo gates afetados `BLOCKED`, sem fallback de modelo.

## 8. Contrato, verificação e handoff

- [x] 8.1 Atualizar `.opencode/agent/design-planner.md` para o contrato canonical Sol/high e adicionar o critic readonly e a documentação/regras mínimas relacionadas, sem mudar defaults, plugins gerais, #555, apply/verify ou Hermes.
- [x] 8.2 Executar `/opsx:verify` para #550 e a revisão exata do diff; depois cumprir Code Review, QA e Playwright visual padrão (ou dispensa explícita válida), registrando resultados terminais e corrigindo qualquer falha antes de avançar.
- [ ] 8.3 Integrar a entrega aprovada em `develop` conforme o processo, executar `./restart`, validar o runtime em processo novo e exportar evidence bytes/digest/verifier result correlacionados para desbloquear o trabalho separado do #555.
