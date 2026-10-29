# Snapshot de crítica de Design — #1098

Data: 2026-10-13. Papel: design-critic. Modalidade: sem tela. Rodada: 1 crítico após 1 autor; nenhum rework necessário. Esta é crítica do contrato proposto, não Code Review nem comprovação operacional.

## Identidade e limites

Card: https://github.com/oalansilva/crypto/issues/1098
Status informado pelo orquestrador: Design; não reconsultado no board por este filho.
Branch observada por git status: card-1098-codex-agentes-nativos.
Worktree usado explicitamente em todos os comandos: /srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos.
Task nativa informada pelo runtime: /root/design_critic_1098.
Chat/parent id autoritativo: unavailable. Child id de runtime distinto do task_name: unavailable.
model_selection_capture: /tmp/card-1098-design-critic-20261013.json
Requested model: gpt-6-astra. Requested effort: medium. Rótulo da captura: GPT-6 Astra.
Observed model: unavailable. Observed effort: unavailable. Host version: unavailable.
Argumentos reais do spawn: unavailable neste filho; captura prova solicitação, não aplicação.
Contexto de permissões informado neste turno: filesystem unrestricted, danger-full-access, approval never. Não há prova read-only.
Isolamento efetivo de contexto: unavailable; prompt autocontido não o comprova.
Retorno: conteúdo desta crítica será devolvido ao pai; completed e vinculação do payload devem ser registrados pelo pai a partir do retorno real.
Gate operacional de seleção observada: não satisfeito. Não registrar este parecer ou o autor como proxy successful com base em requested. O pai informou proxy do autor successful=false pelos campos observados ausentes; isso não foi confundido com defeito do contrato de produto.

## Fontes e método

Lidas as skills canônicas .cursor/skills/design-critic/SKILL.md e .cursor/skills/covenant-flow/SKILL.md e os quatro artefatos listados abaixo. Briefing obtido diretamente por gh api repos/oalansilva/crypto/issues/1098 em 2026-10-13. Comparação mecânica do trecho Problema/História/Entra/Não entra com proposal.md: BRIEF_LITERAL_MATCH=True. Conteúdo do contexto técnico REST também lido para verificar #1049/#1095 e restrições reais do spawn.

Validação OpenSpec strict PASS 4/4 foi informada pelo autor/pai; não repetida e não tratada como prova viva. Nenhuma sessão externa, implementação, mudança de Status, commit, push, teste de mutação do produto ou outro agente foi iniciado nesta crítica. Única escrita deste filho: este snapshot.

## Rubrica e rastreabilidade

1. Problema e escopo: PASS. A perda de visibilidade no chat é atendida por nativo ou recusa explícita, sem executar etapas no pai, disfarçar processos externos ou afetar #1095 em andamento. Outros clientes, PROD e gates humanos ficam fora.
2. Capacidade do host: PASS para honestidade do Design. O inventário distingue schema, configuração e evidência real. Explicita inexistência de parâmetros de diretório/sandbox no spawn disponível e ausência de observação independente. A substituição integral não é prometida.
3. Barreira anterior ao trabalho: PASS de contrato. Ausência conhecida recusa antes do spawn; observação pós-nascimento só permite diagnóstico com barreira efetiva. Sem capacidade de assegurar a barreira, recusa. Isso não afirma que essa barreira já existe.
4. Card e worktree: PASS de contrato. Identidade autorizada é independente de workdir/prompt; alvos, symlinks, branch e Guard devem convergir. Cobertura/trust ausentes e checkout divergente impedem trabalho. Escrita destes documentos não é vendida como correção comprovada de #1095.
5. Seleção e contexto: PASS de contrato. Captura por nascimento e requested/observed separados; contexto sem transcript exige sinal efetivo; sentinela é apenas complemento. unavailable falha os gates dependentes.
6. Ciclo de vida e operação: PASS de contrato. Identidade estável vincula nascimento, execução, interrupção, payload e retorno; o operador deve localizar, acompanhar e interagir na superfície real. Não promete botão específico nem usa completed sem conteúdo.
7. Revisão: PASS de contrato. Dois papéis/filhos, mesmo turno/diff/SHA, isolamento efetivo governando pai e filhos, leitura e deny por reviewer. Perfil, instrução e proxy declaratório não equivalem a isolamento. O host gravável atual não habilita a onda. verify-wave/checklist preservados.
8. Aceitação: PASS de contrato. Tasks 3.3 e 5.1–5.5 permanecem pendentes sem evidência. after-qa não libera preflight, revisão ou commit; recusa correta não substitui a prova positiva exigida. Pode existir bloqueio por fornecedor mesmo após código implementado, declarado como tal.
9. Tokens: PASS. proposal.md e design.md declaram em linhas próprias UI impact: none, live_route: N/A com justificativa e surface: none. Nenhuma rota emprestada, HTML ou protótipo necessário. Interface operacional pertence ao host, não a tela Cripto alterada.
10. Escopo da crítica: PASS. Não há detalhe de implementação elevado a P0/P1; nem especificação de API inventada ou promessa de que cwd, prompt ou perfil read-only resolvam isolamento.

## Achados e disposição

- P0: nenhum achado de produto/escopo/contrato visível.
- P1: nenhum achado de produto/escopo/contrato visível.
- P2: nenhum achado.
- P3 — disposition: aceito; implementar e ensaiar a proveniência das observações e a barreira de diagnóstico no Apply somente quando o host oferecer capacidade comprovável. Já coberto por Decisions 1/3, tasks 1.1–1.4 e cenários de startup; sem alteração obrigatória de Design.
- P3 — disposition: limitação operacional explícita, não defeito da proposta; observed model/effort/host version e garantias reais de isolamento/interface permanecem unavailable ou não comprovadas. Manter os gates dependentes falhos e as tasks vivas pendentes; a qualidade deste parecer não torna o proxy bem-sucedido.
- verdict: proposta adequada ao briefing, sem rework necessário. Aprovação técnica do texto condicionada aos gates de processo aplicáveis; não certifica operação do host, não autoriza avanço de Status, não equivale a T7 e não declara substituição concluída.

## Artefatos criticados (SHA-256 no momento da leitura)

- `proposal.md`: `c5b09e02902af223db93bc5993c4714e8b4d23fef10e530c282aab3dc95fd318`
- `design.md`: `1e1adb157960075cafc71c6b47cfb1fe83c87a81645f00a179560055f844f7fa`
- `tasks.md`: `2d0dc9451d936a8f4511e2c8d7d7da9f0def7d7bb44a559d0f573ab342091484`
- `specs/codex-harness/spec.md`: `a664804df4c0821e7b2a97bf7461421c6db6ae2fad30024a154305cfd2f5c044`

## Captura de seleção integral

```json
{
  "arguments": {
    "model": "gpt-6-astra",
    "reasoning_effort": "medium"
  },
  "attempt_id": "7ad7ca5f-e25b-4f7c-b42c-b81dda4375b7",
  "band": "juizo",
  "capability_version": "codex-agent-pair-v1",
  "capture_sha256": "b5468e5d521a6925c7605a6593ab04e0d388d135fd4d2c5efbc52317ff727d38",
  "client": "codex",
  "effective_sha256": "2334a11eb0294b59da5d5a60b5244fe6a735e2253ddbbbe87f22f5577ae33deb",
  "policy_sha256": "f5ce0eb818f27797e0fca52037aef0af80cbe0c2305927b222ca8bec197f2d16",
  "policy_version": 1,
  "role": "design-critic",
  "selection": {
    "effort": "medium",
    "label": "GPT-6 Astra",
    "model": "gpt-6-astra"
  },
  "source_path": "/home/ubuntu/.config/covenant-flow/model-selection.yaml",
  "source_sha256": "6167e38fd93f8f00577de4adab6f73ab0c0f6942d72f610e85e989d78eabe9c4",
  "version": 1
}
```
