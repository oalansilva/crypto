# Crítica independente — #1098 — Review automático dedicado

Data: 2026-10-17. Status Design informado pelo pai; worktree e branch card-1098-codex-agentes-nativos confirmados localmente. Escopo: contrato revisado em proposal/design/spec/tasks. Sem execução de produto, alteração de OpenSpec, publicação, commit ou mudança de estado. Snapshot exclusivo desta rodada sem-tela, separado dos pareceres históricos.

## Resultado

- P0–P2: nenhum achado novo.
- P3 — disposition: aceito para Apply; concretizar e qualificar o lançamento dedicado, envelopes pendentes e binding autoritativo, contratos dos perfis nomeados e coleta somente após ambos os retornos, conforme tasks 3.2–3.3, 4.5 e 6.1–6.4. São obrigações explícitas de implementação e prova, não funcionalidades exigidas nesta fase Design.
- verdict: contrato revisado consistente; nenhum rework necessário. Submeter o novo digest à revalidação canônica e T7 humana. Este parecer não comprova implementação, sandbox, qualificação da rota ou substituição integral.

## Contrato avaliado

A decisão 4 substitui explicitamente a exigência de mesmo chat exclusivamente na coordenação de Code Review. O principal gravável prepara e persiste; um coordenador dedicado nasce read-only; os dois papéis distintos nascem nativamente no mesmo turno desse coordenador. Nem principal nem coordenador emitem o review no lugar dos filhos. A exceção está declarada no início da proposal e no requisito normativo principal da spec, de modo que as referências anteriores a mesmo chat e proibição de sessões externas não anulam o novo contrato. Demais etapas preservam a delegação nativa no chat do card.

O operador não precisa alternar permissões diariamente. O comando candidato não é apresentado como prova de suporte. A solução exige capacidade e fonte verificáveis, oferece recusa com garantia ausente e conserva estado quando a rota não está disponível. O vínculo por identidades nativas mantém os responsáveis e os retornos localizáveis; o Design exige ensaio de visibilidade e interação na superfície real, sem inventar controles de UI.

Os envelopes preparados antes do lançamento são explicitamente pendentes. Eles não reivindicam parent id final, nascimento nem conclusão. A fonte autoritativa do lançamento e das chamadas nativas precisa resolver principal → coordenador real → dois filhos; receipts ligados ao principal não podem passar pelos do coordenador. O turno comum passa a ser o do coordenador, e isso consta no contrato do schema e na spec. Fontes adulteradas ou cadeia ambígua bloqueiam a execução dependente.

Os reviewers recebem o mesmo path canônico e SHA-256 do diff exato, capturas próprias da mesma onda, prompts autocontidos e chamadas fork_turns=none. Mudança efetiva de seleção invalida a tentativa parcial. Sandbox contínuo do coordenador e filhos precisa ser observado até ambos completed com payload; prompt e TOML não bastam. Cada perfil nomeado deve permitir apenas o probe fixo sobre fixture própria preexistente, exigindo leitura, escrita negada e readback intacto antes do parecer. O texto resolve a dependência circular: verificação prévia do pacote antes do probe; verify-wave final e checklist no principal depois dos retornos, antes do commit.

A opção 2 permanece íntegra: contrato documentado aplicável, chamada nativa registrada e ensaio complementar completo. Atestação interna completa continua unavailable e não é inferida do silêncio ou da ausência da sentinela. Esse critério não substitui seleção observada, Guard, permissões, provas de reviewers ou gates humanos. A nova coordenação também deve ser verificada quanto a seleção, contexto e fonte antes da liberação do trabalho.

A qualificação distingue superfície principal, transporte de lançamento/retorno e coordenador exec. O diagnóstico default TUI relatado é corretamente limitado: não comprova perfis nomeados, sessão dedicada exec ou review de produto. App/IDE sem garantias verificáveis permanecem limitados explicitamente. Fixtures, documentação de comando e ensaio de outra superfície não geram suporte universal.

## Coerência e completude

Proposal declara a revisão de produto e sua prevalência. Design decisão 4 descreve fluxo, falhas, identidade e probe. Spec contém requisito específico e cenários de sucesso, perfil nomeado, fonte ausente e diferença de superfície. Tasks 6.1–6.4 e 3.2–3.3 cobrem o delta; 5.4 exige aceitação viva da onda dedicada. As 20/35 tasks informadas preservam trabalho histórico e deixam a automação nova pendente. As anotações after-qa não dispensam preflight nem review antes do commit, conforme ressalva explícita.

Há referências históricas ao modelo anterior no pacote, mas sua precedência foi explicitamente delimitada. Elas não constituem neste digest uma segunda decisão operacional. A atualização de runbook/documentação afetada está coberta pelas tasks pendentes e não precisa de outra rodada de Design. Design Critique atual contém nota de reabertura e pareceres antigos; o pai atualizará apenas essa seção com o resultado desta rodada.

Tokens parseáveis conferidos: UI impact: none; live_route: N/A com justificativa; surface: none. Não há tela Cripto, protótipo ou HTML exigível. Nielsen/personas: N/A; avaliação operacional considerou Alan localizando responsáveis, acompanhando falhas e recebendo os dois pareceres. O teto de uma autoria, uma crítica e no máximo um rework foi respeitado; este parecer não solicita rework.

## Evidência e limites da crítica

Leitura documental independente dos quatro artefatos e das skills canônicas design-critic/covenant-flow. Git status consultado; alterações preexistentes de outros agentes preservadas. Não fiz ensaio runtime, auditoria de código implementado nem confirmação autônoma do board; Status veio do prompt vinculante do pai. Validação OpenSpec strict e diff check foram informadas pelo autor/pai, não repetidas ou reivindicadas como próprias.

Modelo solicitado: GPT-6 Astra (`gpt-6-astra`), esforço `medium`, faixa `juizo`, papel `design-critic`, conforme captura local. Modelo/esforço observados: unavailable nesta crítica; o pai deve coletar e validar o runtime após o retorno, sem inferir do pedido. Captura: `.cursor/tmp/card-1098-critic-automatic-review.capture.json`. Birth receipt: `.cursor/tmp/codex-evidence/b0af173e-d6b8-44e6-ac1a-2651c0164a07.birth.json`. Attempt: b0af173e-d6b8-44e6-ac1a-2651c0164a07. Nenhum subagente adicional criado; HTML gerado/copied: N/A.

## Identificação dos artefatos lidos

- `openspec/changes/card-1098-codex-agentes-nativos/proposal.md`: `daf3e2d1e2adab0b5af47c50c3f863c1136b3dee5f9393519dab443873cc1b3b`
- `openspec/changes/card-1098-codex-agentes-nativos/design.md`: `fe0a7014eb5bf12b9bd1fd4634ab2daad46e5c69277b0aa328a2c57775edc042`
- `openspec/changes/card-1098-codex-agentes-nativos/tasks.md`: `e6afb2f848a5adc026e1ee52369adec04848fb4ae3a629615846c1ca175a5eab`
- `openspec/changes/card-1098-codex-agentes-nativos/specs/codex-harness/spec.md`: `9fffce3434adb81d306a805e04d546ec15e49a7121575b8db035e37261f4d79d`
