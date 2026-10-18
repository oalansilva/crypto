# Snapshot de crítica independente — #1130

Data: 2026-10-18. Status informado no nascimento: Design. Branch: `card-1130-codex-cli-fluxo-completo`. Modalidade: sem-tela; uma crítica independente documental, sem Code Review de implementação. Responsabilidade de escrita limitada a este snapshot. Não foram executados eventos da FSM, ensaios, trust, publicação, commit ou push.

## Modelo e evidência

- model_selection_capture: `/tmp/card-1130-design-critic-20261018-01.json`
- attempt_id: `10b7fce8-c54e-4e43-8b1f-f8a8c1f7f2bf`
- requested: `gpt-6-astra`, reasoning_effort `medium`, label `GPT-6 Astra`; client `codex`, band `juizo`, role `design-critic`.
- capture_sha256: `43603d31b4eee5f4c1a5153d416f9b42a9f3437010ae88436918941088176389`
- runtime_evidence_birth: `.cursor/tmp/codex-evidence/10b7fce8-c54e-4e43-8b1f-f8a8c1f7f2bf.birth.json`
- observed: `unavailable`; coleta/verificação posterior pertencem ao pai. Nenhum valor observado foi inferido da captura, do nome do agente ou desta conclusão.

## Fontes e limites

Lidos os canônicos `.cursor/skills/design-critic/SKILL.md` e `.cursor/skills/covenant-flow/SKILL.md`, os cinco artefatos abaixo e o body vivo por `gh api repos/oalansilva/crypto/issues/1130`. A sequência Problema, História, Entra e Não entra do issue está literalmente contida na proposal (comparação programática: true). Para contrato de release, consultados `docs/crypto-overlay.md` e `.cursor/skills/covenant-flow-environments/SKILL.md`, somente leitura. Sem acesso a traces privados, controles ou sentinelas.

Esta crítica avalia se o Design orienta a entrega solicitada. Não prova capacidade de exec, rebind, sandbox, onda real, distribuição ou release. Ausência dessas provas hoje está explicitamente preservada no Design e deve permanecer visível na matriz.

## Rubrica

| Dimensão | Resultado documental |
| --- | --- |
| Escopo integral | Criação/refinamento, gates humanos, Design/crítica, Apply, Review, correção, QA, integração, T15/T18 e release constam de contrato e matriz. Apenas App/IDE e outros clientes ficam excluídos. CLI pendente permanece #1130. |
| Antes/depois operacional | Contexto descreve bloqueio real #1117 e descoberta por destino; decisões 2–4 especificam descoberta verificável, preparação conduzida, checkpoint, retry limitado e retomada nativa. Não encerra entrega em instruções genéricas de ensaio manual. |
| Sessões novas e reuso | TUI e principal exec são separados, com sessões novas em source/worktree e retomadas. Capacidade por superfície/schema não substitui contexto chat/root/binário nem prova de produto. Fontes são reabertas; índice é localizador. |
| Rebind | Workdir/--root não comprovam cwd nativo. API automática só com capacidade observada; ausência exige ação nativa do operador com UUID e revalidação. Não promete API fictícia. |
| Principal exec | Está explicitamente dentro do escopo, inclusive perguntas/checkpoints/respostas e Review exec→exec→filhos. Capacidade insuficiente bloqueia célula; não é desviada para #1128. |
| Preparação e autorização | Diagnóstico já autorizado é conduzido pelo pai sem produto/transição; trust R/A e /hooks permanecem humanos. Recuperação mecânica não inventa aprovação nem muda estado. |
| Review | Principal gravável, coordenador efetivamente read-only, par nativo independente, diff/SHA, leitura integral, deny/readback, payload, verify-wave e checklist são exigidos. Diagnóstico não substitui onda de produto. |
| Recusas e recuperação | Estado/card/root/modelo/fontes/permissões/interrupção/TTL e ausência de payload têm recusa e preservação. Teto de correção e retorno T18 sem T8 estão contemplados. |
| #1117 | Reprodução condicionada a estado vivo; não retrocede card para ensaio. Caso equivalente autorizado cobre mudança de estado sem apagar incidente. |
| Aceitação e release | Matriz exige provas reais nas duas rotas. Done técnico pode preceder atos humanos/release sem alegar integralidade. Evidência posterior permanece vinculada ao compromisso; não exige release antes do primeiro commit. |
| Distribuição | Nucleus→consumidor, revisão/pin e manifests reais, trust separado e instalação limpa estão nas tasks. |
| Sem-tela e tokens | `UI impact: none`, `live_route: N/A`, `surface: terminal Codex CLI (TUI e exec)` presentes em linhas próprias. Justificativa corresponde à ausência de mudança visual no produto; nenhuma rota de catálogo foi emprestada. |

## Achado

P3 — detalhe de Apply: `tasks.md` 6.1 agrupa onda pré-commit e onda de fechamento com anotação `after-commit`. A anotação pode tornar ambígua a hora de registrar cada resultado. O contrato normativo está correto: decisão 5 e requirement de Review exigem verify-wave/checklist antes do commit. Separar os registros por fase na execução melhora rastreabilidade; a anotação não autoriza postergar os gates pré-commit. Disposition: aceito para Apply, sem rework de Design.

Não foram encontrados P0, P1 ou P2. Nenhuma segunda rodada ou rework é necessário. O mérito documental não substitui o gate de evidência runtime desta própria crítica nem T7 de Alan.

## Bloco exato sugerido para Design Critique

- P0–P2: nenhum defeito de produto, escopo ou contrato visível identificado.
- P3: separar no Apply os registros pré-commit e de fechamento agrupados na task 6.1; `after-commit` não posterga verify-wave/checklist exigidos antes do commit.
- disposition: P3 aceito como detalhe de Apply; nenhum rework necessário.
- verdict: aprovado pela crítica documental sem-tela; capacidades e aceitação integral continuam dependentes das provas reais da matriz.

## Hashes dos artefatos avaliados

SHA-256, relativo a `openspec/changes/card-1130-codex-cli-fluxo-completo/`:

| Artefato | SHA-256 |
| --- | --- |
| proposal.md | dde259f6c9f673df4c9e75489336bfc570a6acb8fec75add1144b3731e9a2b95 |
| design.md | 511607c4666b4f2bdc29211f1ba77bf7ef6fd5e3e5ffaf03a4a0f4bc01233068 |
| tasks.md | a7b2301213f133a800b2d9b2ded317951e8f2acb0105cc1b015ca53f77bf9bbb |
| specs/codex-runtime-evidence/spec.md | bf00527bed8d5011a14019e45cdfffb381acb8f1460f8b0b7cf3e93780c0ca56 |
| specs/codex-terminal-flow/spec.md | 8309521932d21ff347aa0f63b9d6ef3070f572292fcae984e4a371c9b7e497fd |

## Registro posterior do orquestrador — 18/10/2026

A coleta autoritativa confirmou autor e crítico `completed` com payload, modelo observado `gpt-6-astra` e esforço `medium`, iguais às capturas de nascimento. Evidência original do autor: `80227a4915e3f8ec2661068d01a405fe2da2adbfaf56eb4fe4c31e70550e5671`; evidência do crítico: `7f470ea260732f02c2e3e34811ae29b8617baffb500146ec92dceb8cf48a0388`. A continuação do autor foi recoletada pelo mesmo receipt, preservando a âncora e a captura originais.

O gate T5 detectou erro de formato que esta crítica não identificou: a linha livre `surface: terminal Codex CLI (TUI e exec)` não satisfazia o parser. O mesmo autor corrigiu para `surface: none`, manteve a descrição operacional em prosa e esclareceu no Context as provas históricas de Review/QA do #1098. O predicado real `design_token_gap` retornou `None` e OpenSpec strict passou. Este registro factual não é uma segunda crítica; os hashes acima identificam os bytes originalmente avaliados, antes do bloco Design Critique e desse rework pontual. Dois filhos de Design, uma crítica e uma continuação do autor; nenhuma alteração de escopo ou dispensa de gate humano.
