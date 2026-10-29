# Crítica independente — #1098, recorte CLI — 18/10/2026

## Identidade e limites

Papel: design-critic, único crítico sem tela desta revisão. Status Design após I4/T17 informado pelo pai; nenhuma transição executada nesta crítica. Branch conferida: `card-1098-codex-agentes-nativos`. Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos`.

Skills canônicas lidas: `.cursor/skills/design-critic/SKILL.md` e `.cursor/skills/covenant-flow/SKILL.md`, além de `AGENTS.md`. Revisão limitada a produto, escopo e contrato documental; sem review de código, QA, ensaio de runtime, transição, publicação, commit, trust ou mutação do pacote selado. Nenhum transcript ou marcador diagnóstico foi consultado. Única escrita: este snapshot. Alterações preexistentes de outros agentes foram preservadas.

Briefing utilizado: bloco vigente literal copiado no início de `proposal.md`, conforme fonte permitida pelo prompt. Decisão explícita de Alan: concluir CLI e separar os demais ensaios. Seguimento: https://github.com/oalansilva/crypto/issues/1128, Em Refinamento conforme pai e artefatos; não foi feita consulta independente do board. A crítica não certifica o estado remoto nem a execução das evidências históricas.

## Modelo e procedência

- Cliente/faixa/papel: `codex/juizo/design-critic`.
- Requested: `gpt-6-astra`, `reasoning_effort=medium`; rótulo da captura: GPT-6 Astra.
- Observed model: `unavailable` até coleta autoritativa posterior pelo pai.
- Observed reasoning effort: `unavailable` até coleta autoritativa posterior pelo pai.
- Host/versão observados: `unavailable` neste snapshot; não inferidos da configuração.
- Contrato do nascimento informado: `fork_turns=none`; comprovação da chamada real cabe à coleta, sem autoatestação.
- model_selection_capture: `.cursor/tmp/card-1098-critic-cli.capture.json`.
- capture_sha256 declarado na captura: `f4727841b61df1da01c8355bccef43cde801a38abb959706bd823b51883c9754`.
- runtime_evidence_birth: `.cursor/tmp/codex-evidence/bec7e4c9-a234-4ba2-a9a9-123c2e272611.birth.json` (referência fornecida; não tratado como prova de completed).
- proxy modelo: design-critic → GPT-6 Astra (`gpt-6-astra`), esforço medium solicitado.
- Spawns por este crítico: 0. Rodada prevista: 1 autor + 1 crítico; rework necessário: 0. HTML generated/copied: N/A.

O parecer documental abaixo não transforma requested em observed nem dispensa o gate de coleta que exija runtime verificado/completed com payload.

## Artefatos lidos e SHA-256

Os quatro artefatos foram lidos incluindo seus apêndices históricos. Hashes dos bytes avaliados, antes de eventual inclusão do parecer pelo pai:

| Artefato relativo à change | SHA-256 |
| --- | --- |
| `proposal.md` | `286b5400911916948f4d018eb4efbcce30d2433c89ce231a9423092a95916e83` |
| `design.md` | `5baeec8fdb1f484c20d1391e9f319310302b7116ae1fdf362a7006b41a92dc7e` |
| `tasks.md` | `d912a03833873e92d9cedcfdc3d6f17c31faa555fe5d39e687cb3454c6e89776` |
| `specs/codex-harness/spec.md` | `e1ba3c7f7eeb5bcea0e72a7c6fe7e72a49bb05f225f4b8bd5ac685cbddd0dcd8` |

## Brief e experiência operacional

Alan precisa localizar o responsável, acompanhar estado, interagir pelos controles nativos disponíveis e obter retorno verificável na CLI do card. A rotina proposta mantém o principal gravável; somente Code Review abre automaticamente coordenador exec dedicado, somente leitura desde o nascimento, e dois reviewers nativos distintos no mesmo turno. Demais etapas continuam no chat. Não se promete controle de interface específico não exposto nem alternância diária manual de permissões.

## Rubrica de coerência

| Critério | Resultado e fundamento |
| --- | --- |
| Escopo vigente versus histórico | Consistente. Proposal e Design delimitam explicitamente apêndices não normativos. Histórico amplo e pareceres antigos não aprovam o digest atual. Spec abre com o recorte vigente. |
| Transferência rastreável | 5.5/5.6/5.8 e partes de 5.1/5.7/6.3 mapeadas para #1128. Coordenador exec da CLI permanece no #1098; principal exec independente/App/IDE ficam no seguimento. |
| Progresso honesto | 25/32 no checklist vigente e três transferidas não concluídas. 3.3, 5.1–5.4, 5.7 e 6.3 permanecem abertas. Histórico 25/35 não vira conclusão adicional. |
| Rotina sem alternância manual | Principal prepara e persiste; coordenador e reviewers continuam somente leitura. Ausência de capacidade recusa com motivo; não solicita troca de permissões nem fallback oculto. |
| Contexto escolhido | Contrato aplicável + chamada real fork_turns=none + ensaio complementar completo, com origem e controle. Atuação interna completa unavailable; ausência isolada de sentinela insuficiente. |
| Seleção e binding | Captura por nascimento, par observado separado, cadeia autoritativa, worktree/card/etapa e Guard preservados. Paths e configuração não concedem autorização. |
| Review independente | Dois papéis/filhos no mesmo turno/onda/diff/SHA, leitura integral e retorno ao modelo, deny/readback por reviewer e read-only contínuo. Um papel de cada onda distinta não forma par. |
| Gates e QA | verify-wave/checklist antes do commit e QA CLI obrigatórios. after-qa não dispensa preflight nem autoriza commit com onda ausente. T7 humana preservada. |
| Limites de suporte | Sem universalidade, Auto, confiança automática ou promoção de fixture/diagnóstico a positivo final. Código final precisa de qualificação própria. |
| Estado do candidato | Pacote final inativo; 148 testes/dry-run não constituem runtime. Nenhum par de produto válido alegado. Pendências de execução não viram defeito de Design. |
| Tokens de superfície | UI impact: none; live_route: N/A com justificativa de processo CLI sem rota Cripto; surface: none. Linhas próprias no início do Design. |

## Rubrica de experiência sem tela

| Heurística pertinente | Avaliação |
| --- | --- |
| Visibilidade do estado | Identidade, nascimento, execução, falha/interrupção e completed/payload exigidos separadamente. |
| Controle do operador | Controles reais de inspeção/interação e retorno são aceites explícitos; gates humanos preservados. |
| Consistência | Única exceção externa para coordenar Review identificada nos três artefatos normativos; não é filho falsamente apresentado. |
| Prevenção e recuperação de erro | Falta de evidência/capacidade bloqueia dependentes e mantém razão visível; sem fabricação de receipts ou reaproveitamento indevido de ondas. |
| Reconhecimento e documentação | Contrato atual vem antes do histórico; tabela de transferências permite identificar o destino das obrigações. |
| Eficiência da rotina | Não requer alternância manual de permissões; a coleta gravável fica no principal. |
| Acessibilidade visual, layout, responsividade | N/A: nenhuma tela de produto ou protótipo alterado; não avaliados por analogia com UI do fornecedor. |

Persona operacional única aplicável: Alan, operador da CLI. A experiência futura descrita é clara e verificável, mas a inspeção documental não comprova controles vivos nem desempenho da rotina.

## Achados, disposition e verdict

- P0–P2: nenhum achado de produto, escopo ou contrato visível nesta revisão.
- P3 — disposition: aceito para Apply; executar e qualificar as sete pendências CLI sobre o código final, preservando os aceites especificados. Trata-se de execução pendente já explícita, não de defeito que reabra Design.
- P3 — disposition: N/A para UI/protótipo; tokens e justificativa sem tela presentes.
- verdict: recorte CLI coerente e apto à publicação do Design para a aprovação humana pertinente; nenhum rework necessário. Este parecer não concede T7, não valida runtime final e não aprova implementação, Review ou QA.
