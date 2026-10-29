# Crítica independente — #1098 — opção 2 — 2026-10-17

## Resultado

- P0–P2: nenhum achado novo no delta do critério.
- P3 — disposition: aceito para Apply; materializar e validar a procedência do contrato aplicável, a chamada real e o ensaio não contaminado conforme as tasks 1.7–1.9 e 4.5. Não é novo requisito nem reabertura dos P3 históricos.
- verdict: delta consistente com a opção 2 escolhida por Alan; nenhum rework necessário. Não concede T7, não comprova implementação ou qualificação e não libera revisão sem as demais garantias.

## Escopo

Retomada do mesmo crítico, limitada ao critério de contexto e sua consistência em design.md, specs/codex-harness/spec.md e tasks.md. Decisão recebida do pai: Alan retirou a exigência de atestação interna completa e escolheu contrato documentado aplicável + chamada registrada fork_turns=none + ensaio complementar com controle positivo e sentinela exclusiva do pai. Essa decisão rege esta avaliação; não se exige novamente a atestação retirada.

Estado Design informado pelo pai após I4/T17 em pedir_review; branch local card-1098-codex-agentes-nativos conferida. Não consultei board nem executei process_event. Não fiz Code Review, inspeção da correção process_event, testes ou novo ensaio. Os 337 testes e a falta de sincronização do nucleus são contexto informado pelo pai, não validação deste crítico. A entrega anterior e os snapshots históricos permanecem preservados.

## Avaliação do delta

| Aspecto | Parecer |
| --- | --- |
| Conjunto cumulativo | Design decisão 3 e novo Requirement da spec exigem as três partes. Configuração, receipt, declaração do filho ou ausência isolada de sentinela não passam. Tasks 1.7–1.9 implementam e verificam o mesmo conjunto. |
| Contrato aplicável | A fonte deve corresponder a ferramenta, runtime e superfície; referência verificável e digest preservam procedência. Documentação genérica de outro produto e excludeTurns não são aceitos como equivalência. Esta crítica avalia o requisito e não atesta que uma fonte externa já o satisfez. |
| Chamada real | Exige registro nativo de fork_turns=none com call id, chat/parent/turno/child e fonte íntegra. Argumentos preparados são conferidos antes; a chamada real é revalidada por nascimento. Divergência invalida a tentativa sem transformar execução passada em bloqueio anterior. |
| Controle e sentinela | C é explicitamente entregue; S é nova, não secreta e exclusiva do contexto anterior do pai. O protocolo exclui prompt, steering, arquivos, nomes, ambiente e consultas a fontes que contaminem o diagnóstico. Controle correto, completed/payload, filiação e origem são obrigatórios. |
| Negativos | S devolvida sem entrega autorizada ou fork divergente bloqueiam. Controle errado, silêncio, interrupção, falta de payload/proveniência e contaminação não qualificam. Repetição ou troca de modelo não apagam divergência registrada. |
| Limites | O positivo é contratual/empírico e restrito ao escopo observado. Não prova ausência universal de herança nem o contexto interno completo. internal_context_attestation=unavailable permanece explícito e não reprova sozinho o critério escolhido. |
| Outras garantias | Modelo/esforço observados, Guard/worktree, filiação, ciclo de vida, read-only efetivo do pai/filhos, leitura/deny/readback de ambos reviewers e gates humanos continuam exigidos. A decisão não converte contexto em prova de permissões. |
| Qualificação e migração | Qualificação própria de superfície/contrato e revalidação por mudança relevante são exigidas. Novas tasks ficam pendentes; a integração anterior e as tasks concluídas não são promovidas a implementação do critério novo. Task 4.5 cobre documentação, verificadores, testes e distribuição posterior. |

O controle C verifica instrução e canal de retorno; não é um detector completo de herança oculta. O Design reconhece essa limitação e usa o ensaio apenas como complemento ao contrato e à chamada. Não há motivo para elevar essa limitação explicitamente escolhida a P0/P1 ou reintroduzir a atestação interna como gate.

A nota final de tasks.md sobre o dry-run que não mudou Status registra o estado anterior à correção relatada pelo pai. Não a usei como estado vivo. Ela não muda o contrato nem autoriza Apply; o estado atual informado é Design e a revalidação canônica continua necessária. A seção histórica Design Critique é explicitamente delimitada pela abertura da revisão e não vale como aprovação do novo digest.

## Superfície e teto

UI impact: none
live_route: N/A — delta documental do processo, sem rota do produto.
surface: none

Tokens mantidos em design.md; HTML gerado/copiado N/A. Nenhuma reabertura visual ou dos P3 históricos. Esta retomada examina a decisão nova de produto; não é segunda rodada de polish nem autorização de Apply. Rework objetivo: nenhum.

## Metadata e limites da evidência

- Papel design-critic; cliente codex; faixa juizo.
- Captura original mantida: /tmp/card-1098-design-critic-20261017-v2.json.
- Requested: GPT-6 Astra (gpt-6-astra), medium.
- Attempt original: d14573c1-edee-498b-ad39-e15682602fa2.
- Pai informou verify_continuation PASS antes desta retomada, contra captura original; não executei essa verificação novamente.
- Observação autoritativa dos turnos desta continuação: coleta pelo pai após retorno, pendente neste snapshot. Não extrapolo a evidência do nascimento anterior como prova desta conclusão.
- Nenhum spawn, alteração de código/design/tasks, commit, push, process_event, confiança ou publicação feito pelo crítico.

## SHA-256 dos artefatos avaliados

- `openspec/changes/card-1098-codex-agentes-nativos/design.md`: `7f9625d474b36536be8cf828a6d5b9a881e17c755df8b057a98a8e4aebb9e6dd`
- `openspec/changes/card-1098-codex-agentes-nativos/specs/codex-harness/spec.md`: `9c338108b269905190e63cbc3524b4858894051937c9f3974af0f5310a5d49bd`
- `openspec/changes/card-1098-codex-agentes-nativos/tasks.md`: `2bfe70a6b2fb21505f4626f79fdbbf9002dd20021e9c4dfc92f534b6c910125c`
