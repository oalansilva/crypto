Usar as skills canônicas em `.cursor/skills/` e suas pontes `.agents/skills/` quando aplicável. Implementação somente após crítica independente, T5, aprovação humana T7 e T8 pelo pai. Nenhuma task autoriza produção, confiança ou movimento humano da FSM. Tasks de execução pertencem ao filho Apply; eventos, Git, publicação e evidências posteriores pertencem ao pai nos gates correspondentes.

Registro deste Apply: tasks de implementação marcadas referem-se ao candidato inativo `implementation/nucleus/`, com patches/manifests reproduzíveis e testes em cópia descartável; não significam pin/trust ativados nem etapa viva comprovada. Relatório: `evidence/apply-report.md`; matriz: `evidence/acceptance-matrix.md`. As tasks de ensaios vivos não satisfeitas e as fases posteriores permanecem abertas.

Fases dos ensaios: as partes ainda pendentes de 3.4/3.5/4.3/4.4 são a aceitação do comportamento novo sob instalação canônica, não implementação/testes de contrato por fazer. Vencem em postpin: o adapter ativo anterior e o clone descartável não exercitam o índice/prepare/controller instalado. Diagnósticos e recusas reais já possíveis antes da instalação permanecem registrados, sem substituir esses ensaios. Justificativa por tarefa e vínculo à decisão 6 do Design: `evidence/phase-resolution.md`. Anotar a fase não marca conclusão, autoriza trust, dispensa etapa elegível ou libera T9 automaticamente; o checklist estrito e postpin continuam exigindo essas provas antes do fechamento/aceitação correspondente. O gate pré-commit de onda/verify-wave/checklist abaixo permanece obrigatório.

## 1. Contratos e reprodução

- [x] 1.1 Inventariar base integrada #1098, pendências CLI #1128 e estado vivo #1117; registrar em matriz as provas existentes como diagnóstico e as faltantes por etapa e rota.
- [x] 1.2 Identificar checkout/revisão canônica do nucleus, arquivos distribuídos, manifests e política local vigente; definir alterações genéricas e integração no consumidor sem dual-write nem confiança automática.
- [x] 1.3 Reproduzir de forma autorizada a falha de descoberta em destino novo e distinguir unverified, contexto ausente e vínculo incorreto, preservando causas separadas e sem retroceder #1117.

## 2. Descoberta e recuperação de evidências

- [x] 2.1 Implementar índice privado de referências por superfície/schema com escrita atômica, permissões restritas, validação de destino e verificação das fontes originais; não alterar o containment do escritor local.
- [x] 2.2 Integrar descoberta explícita/índice/legado ao preflight; recusar conflito, symlink, origem adulterada ou inacessível, sem seleção por mtime e sem copiar receipts como qualificação atual.
- [x] 2.3 Preservar escopo chat/root/binário/contrato do contexto e sessão/rota/perfis do Review; detectar mudanças e impedir reutilização cruzada apesar de capacidade compatível.
- [x] 2.4 Orquestrar preparo diagnóstico já autorizado, coleta, qualificação e retry da operação pendente com checkpoint e limite por causa; reportar atos humanos concretos sem loop manual repetitivo.
- [x] 2.5 Cobrir testes de índice vazio/corrompido, fonte alterada, legacy íntegro, superfície errada, versão compatível, novo chat/root/binário, flush tardio e recoleta idempotente mantendo failure original.

## 3. Rotas terminal e contexto nativo

- [x] 3.1 Implementar orientação e checkpoints TUI/exec desde source ou worktree, revalidando estado e cwd nativo; medir capacidade de rebind sem inferir de workdir/--root.
- [x] 3.2 Implementar retomada do principal exec para respostas humanas no mesmo chat quando suportada, com pergunta/identidade/checkpoint explícitos; registrar e corrigir bloqueios de capacidade sem remover a rota do escopo.
- [x] 3.3 Preservar opção de resume pelo operador quando rebind automático não existir, entregando comando literal e continuando preparo/verificação automaticamente após o ato observado.
- [ ] 3.4 Ensaiar novas sessões nas duas raízes e retomadas nas duas rotas com agentes nativos, seleção por nascimento, filiação, isolamento, conclusão/payload e falha/interrupção sem perda dos artefatos, sobre o novo comportamento instalado pelo pin real. <!-- covenant-flow:after-pin -->
- [ ] 3.5 Validar refinamento autorizado de #1117 se seu estado permitir e diálogo pergunta/resposta/body correto pelo novo prepare/checkpoint instalado; se não permitir, registrar limite e executar caso real equivalente autorizado sem alterar o histórico do incidente. <!-- covenant-flow:after-pin -->

## 4. Review automático e demais etapas

- [x] 4.1 Integrar preparação automática do coordenador exec read-only a ambas as rotas principais, preservando bootstrap/contexto/probes próprios e cadeia nativa de lançamento/retorno.
- [x] 4.2 Garantir par nativo no mesmo turno, diff/SHA fixos, leitura integral em chunks, deny/readback e pareceres completos; manter persistência/verify-wave/checklist no principal gravável.
- [ ] 4.3 Testar expiração de stage-check, Status alterado, SHA trocado, chunk faltante, sandbox divergente, interrupção e payload ausente; complementar testes de contrato e recusas pré-commit já registrados com recusas vivas seguras do novo controller instalado, além das fixtures. <!-- covenant-flow:after-pin -->
- [ ] 4.4 Conduzir provas vivas autorizadas de Design/crítica/Apply e Review de produto nas duas rotas pelo suporte instalado, em cards/etapas elegíveis; registrar lacunas ainda dependentes de gate no relatório sem usar bootstrap como aceite. <!-- covenant-flow:after-pin -->
- [x] 4.5 Implementar e testar continuação do teto de correção/residual, QA/checks/integração e retorno T18 sem T8; comprovar retornos reais quando autorizados e manter pendentes na matriz os atos humanos ainda não ocorridos.
- [x] 4.6 Integrar suporte terminal a fecho-lote, seleção de execução observada, guards, archive/sync/Kaizen e contratos de deploy do overlay, com testes de recusa sem executar produção neste Apply.

## 5. Distribuição e documentação verificável

- [x] 5.1 Atualizar runbook e documentação Codex com recuperação conduzida, rotas, comandos reais, causas de recusa e limites; retirar aceites CLI indevidamente atribuídos a App/IDE sem apagar história.
- [x] 5.2 Preparar matriz pública sanitizada e seu procedimento de atualização pós-QA/homologação/release, com referências privadas verificáveis, estados de prova e critérios explícitos para alegação integral.
- [x] 5.3 Publicar reconciliação rastreável em #1098/#1128/#1130 mantendo diagnósticos históricos como diagnósticos e pendências CLI neste card (pai).

  Pai confirmou publicação em 18/10/2026: [#1098](https://github.com/oalansilva/crypto/issues/1098#issuecomment-6254660236), [#1128](https://github.com/oalansilva/crypto/issues/1128#issuecomment-6254660522), [#1130](https://github.com/oalansilva/crypto/issues/1130#issuecomment-6254660804).
- [x] 5.4 Validar testes proporcionais, contratos existentes e `openspec validate card-1130-codex-cli-fluxo-completo --strict`; registrar resultado e lacunas vivas sem marcar provas ausentes como concluídas.
- [ ] 5.5 Registrar revisão/pin reais nucleus → consumidor, verificar manifests e retestar descoberta em instalação limpa; trust humano separado e nenhuma confiança gravada pelo agente. <!-- covenant-flow:after-pin -->

## 6. Evidência nas fases do próprio card

Critério pré-commit do pai (sem checkbox circular no diff): executar a onda canônica com diff real, capturas e ambos os payloads; exigir verify-wave e checklist precommit verdes antes de commit, preservando residuais do teto. Os registros privados/comentário do pai constituem a evidência; a task pós-commit abaixo não posterga esse gate.

- [ ] 6.1 Executar a onda canônica de fechamento sobre o intervalo commitado, guardar verify-wave/checklist, capturas e payloads e anexar resultados ao SHA; a anotação não posterga o gate pré-commit normativo acima (pai). <!-- covenant-flow:after-commit -->
- [ ] 6.2 Coletar QA real do SHA, checks, PR e resultado T14/DEV; revalidar checklist em postqa, atualizar matriz e declarar precisamente quais provas humanas/release permanecem pendentes (pai). <!-- covenant-flow:after-qa -->

## 7. Aceitação posterior vinculada à matriz

Esta seção descreve critérios de aceite posteriores, não tasks pendentes que forçariam release antes de commit/QA. O pai mantém a matriz e o card como registro vivo: T15 por Alan; T18 com motivo quando exercido realmente, correção e novo ciclo até Done; release somente após pedido explícito próprio, fecho-lote, guards, deploy, saúde, Kaizen, higiene, sync quando aplicável e T16. Cada rota terminal conserva sua célula, sem aceitação por fixture ou transferência para #1128. A espera por ato humano fica visível e não se transforma em aprovação nem em promessa de fluxo integral. O chat de release anexa prova ao mesmo compromisso após executar a operação autorizada. Somente matriz obrigatória inteiramente comprovada permite anunciar fluxo completo; Done técnico ou tasks marcadas isoladamente não permitem essa alegação.
