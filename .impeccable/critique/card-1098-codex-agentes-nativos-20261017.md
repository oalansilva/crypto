# Crítica independente de Design — #1098 — 2026-10-17

## Resultado

- P0: nenhum achado.
- P1: nenhum achado.
- P2: nenhum achado.
- P3 — disposition: aceito para Apply; implementar e ensaiar a barreira anterior ao trabalho quando a observação depender do nascimento, a normalização dos caminhos e a coleta do contexto read-only efetivo. O contrato já exige recusa quando a barreira ou a prova não existir; detalhes de implementação não justificam rework de Design.
- verdict: proposta adequada ao briefing atualizado; nenhum rework necessário. Não equivale a T7, implementação aprovada, substituição integral comprovada ou liberação de etapa bloqueada.

## Escopo e método

Crítica do contrato proposto nos quatro artefatos OpenSpec contra o briefing local de 17/10, com leitura de docs/codex-bootstrap-1098.md e docs/codex-runtime-evidence.md para limites observados. Não é Code Review do bootstrap. Status Design informado pelo orquestrador; branch e worktree locais conferidos. Não consultei nem alterei o board. Não executei ensaio runtime, testes ou validação OpenSpec nesta crítica; o PASS strict e os 118 testes são resultados informados/documentados, não uma execução própria.

Esta rodada avalia o escopo ampliado e a recuperação da coleta TUI. O snapshot histórico de 13/10, card-1098-codex-agentes-nativos.md, permanece intacto e não aprova a autoria nova. Sem-tela: 1 autor + 1 crítico; sem rework necessário. Nenhum subagente nasceu desta crítica.

## Rubrica do contrato

| Critério | Avaliação |
| --- | --- |
| Interativo, exec e app/IDE | Atendido: compatibilidade por capacidades/schema/origem; diagnóstico de host não substitui validação. Refinamento interativo positivo e regressão exec são obrigatórios; app/IDE exigem ensaio equivalente ou limitação específica, sem declaração universal. |
| Qualificação por superfície | Atendido: sucesso e recusa reais, origem revalidada, fixtures insuficientes e proibição de reaproveitar prova exec como TUI/app. App e IDE são separados quando suas capacidades diferem. |
| Worktree real e Guard | Atendido: distingue autorização, diretório da ferramenta e targets; exige contexto efetivo, metadata de nascimento, todos os turnos e paths reais. Retomada nativa do mesmo chat não equivale a workdir arbitrário. Refinamento conserva exceção pré-worktree vinculada à issue. |
| Seleção e contexto | Atendido: captura por nascimento, par observado separado do pedido, ausência/divergência recusada e isolamento efetivo além de fork_turns solicitado. Barreira diagnóstica é condicional à capacidade real do host. |
| Chat, identidade e retorno | Atendido: cada etapa mantém chat/card/papel/child e ciclo de vida, retorno com payload e identidade verificável; falha/interrupção não são completed. Aceite vivo inclui lista, estado, inspeção e orientação entregue, sem inventar controles. |
| Dois pareceres read-only | Atendido: mesmo diff/path/SHA, dois filhos/papéis no mesmo turno, contexto efetivo do pai e filhos somente leitura até ambos retornarem. Leitura e deny de escrita por reviewer têm prova própria; proxies persistidos posteriormente. Ausência de mecanismo no chat bloqueia a onda. |
| Sessões externas | Atendido: excluídas tanto como caminho normal quanto fallback; execução no pai e wrappers também excluídos. Retomada pelo operador conserva o mesmo chat. |
| Bootstrap versus entrega | Atendido: 118 testes e qualificação TUI não marcam tasks completas, não alteram T7/T8 ou confiança e não significam pin publicado. Procedência nucleus/consumidor e manifesto entram no Apply. |
| Evidências e lacunas | Atendido: distingue fixtures, fatos runtime, observação da interface e guarantees ausentes. Refinamento, isolamento, Guard, onda read-only e UI continuam com aceites pendentes; recusa correta não encerra positivo obrigatório. |
| Ordenação dos aceites | Atendido: anotações after-qa não dispensam preflight nem permitem commit/Review com onda ausente. Tasks 3.3 e 5.4 permanecem pendentes quando faltar capacidade. |

O runbook e a documentação runtime ainda descrevem a sessão dedicada de revisão. A proposta identifica isso como comportamento vigente a substituir após aprovação e implementação, com task 4.1 explícita; não há alegação de que a substituição já ocorreu. O risco de o host não oferecer a garantia é exposto como bloqueio, não resolvido por uma API presumida.

## Gate de superfície

UI impact: none
live_route: N/A — nenhuma rota do produto é alterada; lista e controles pertencem ao host Codex.
surface: none

Os três tokens constam em linhas próprias no design.md. Protótipo/HTML: N/A, sem bytes gerados ou copiados e sem rota de catálogo emprestada. Avaliação visual, personas e heurísticas de tela: N/A; a experiência operacional é coberta pelos critérios de localização, estado, interação, retorno e falha na rubrica acima.

## Evidência e metadata desta crítica

- Papel: design-critic; faixa juizo; cliente codex.
- model_selection_capture: /tmp/card-1098-design-critic-20261017-v2.json
- requested: gpt-6-astra / medium; rótulo da captura: GPT-6 Astra.
- proxy modelo: design-critic → GPT-6 Astra (gpt-6-astra).
- runtime_evidence_birth: .cursor/tmp/codex-evidence/d14573c1-edee-498b-ad39-e15682602fa2.birth.json
- attempt_id: d14573c1-edee-498b-ad39-e15682602fa2.
- Receipt declara parent_host codex-tui e bound_card 1098; isso não comprova conclusão do crítico.
- Modelo/esforço observados do crítico: unavailable nesta autoria; coleta autoritativa pelo pai somente após retorno. Versão observada do crítico: unavailable. Não inferida da captura, do autor ou do ensaio bootstrap.
- O pai informou proxy successful=true do autor, par gpt-6-astra/medium, host codex-tui/0.163.0 e bound_card=1098. Não transferi essa observação para este crítico e não revalidei sua origem nesta crítica.
- Permissões deste turno: danger-full-access conforme contexto recebido; não é prova de isolamento read-only nem do Guard. A escrita deste snapshot não é ensaio de autorização do card.
- Nenhum T7, commit, push, process_event, alteração de confiança ou publicação realizado.

## Hashes dos artefatos lidos

Hashes SHA-256 dos bytes no momento desta crítica. Atualizações posteriores da seção Design Critique pelo pai alteram o hash de design.md sem alterar quais bytes foram avaliados aqui.

- `openspec/changes/card-1098-codex-agentes-nativos/proposal.md`: `4ae14375784912a8738fd90ff3c9ddcf04e9f227ba8b2037759874bd0ac4577c`
- `openspec/changes/card-1098-codex-agentes-nativos/design.md`: `9d5a1b31974796b8aec06523844d34fdd1d1009f8a8454e1745f8fff00a2d0f9`
- `openspec/changes/card-1098-codex-agentes-nativos/tasks.md`: `5dec1c03890de3ce969b362b9446cbf5d414a9433c807ef61b49ecf292f15af7`
- `openspec/changes/card-1098-codex-agentes-nativos/specs/codex-harness/spec.md`: `6055b99f51f873b4fcea355d97b6b6a7a906bc0d7b34124c82ccb138e10bef8d`
- `docs/codex-bootstrap-1098.md`: `7b5f4e42765e7e14dcc4a02ab3c8b1576c90e7b83a26df021a6f42d62f6deb0c`
- `docs/codex-runtime-evidence.md`: `b9b6ecfe046c7c7b8e3125b98e9bb2bbd53ea0d863c2ddf34b42c371caa3ad32`
- `/tmp/card-1098-briefing-20261017.txt`: `5dfd328f5ea749b701140959f998254669ec464beb4c4885c9b97d10c9a606ca`
