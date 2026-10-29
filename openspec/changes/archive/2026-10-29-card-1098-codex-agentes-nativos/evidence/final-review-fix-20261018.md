# #1098 — candidato consolidado após a revisão incompleta (18/10/2026)

O pai confirmou a nova entrada Code Review → Em desenvolvimento por T10 `achar_bloqueante`, sem novo T8. Este é o único Apply da entrada, com captura original `.cursor/tmp/card-1098-apply-review-wave.capture.json`, nascimento `0826730d-d4e4-48a4-bc70-08236ea91625` e par `gpt-6.1-sol/high` revalidado pelo pai. Não houve spawn neste Apply, process_event, commit/push/PR, trust, alteração de conta/permissões ou escrita no nucleus.

## O que as ondas anteriores demonstraram

O code-reviewer `e373050e-eedd-47ef-888d-c14a1b031183` e o diff-reviewer `08f00ba5-138e-4db2-ad4f-01c7dbdcd403` leram integralmente o mesmo diff de 763353 bytes/755809 caracteres/57 páginas, mas **em ondas diferentes**. Seus proxies bem-sucedidos informados pelo pai têm SHA `89a65b3debe1149aea34686379cd1d45afadd8150d62d9cb1fb1367f93e26222` e `98dd7f088b326e62d6e026d1c08e5e510c3e170966427e51e761e48205912f93`. Isso não forma uma onda aprovada. O verify-wave da `1c276cefcf8b4cf92dab7a6a` recusou apenas um proxy; checklist precommit recusou tasks pendentes. Sem Review aprovado, QA, commit ou PR.

A tentativa assíncrona anterior terminou o turno antes do processo do preflight porque perdeu o `session_id`. Outras recusas confundiram bytes/páginas ou allowance de geração/work com janela de entrada. Esses fatos não autorizam remover gates nem promover diagnóstico antigo à versão candidata.

## Candidato inativo

Pacote: `.cursor/tmp/card-1098-final-review-fix/`.

- Manifesto selado SHA-256: `0edd927633381eeb863ee9161db1d0ebdfc4c706d635e1b0d76d0882da8ea8ff`.
- Patch de cada destino SHA-256: `5f0a30c189379885134ee15203d778924c844e11732f36bcce8263211d878208` (iguais; oito payloads).
- `before/`, `initial.json`, manifestos por destino, `SHA256SUMS`, README, logs, candidatos completos e `deliver.py` estão preparados. Nenhum `--apply` foi executado.

Os oito payloads atuais do nucleus/consumidor convergem byte a byte e não têm conflito de conteúdo. HEADs preservados: nucleus `14aa9d6f046219b6a00a5f89333c50a68b3103ef`, consumidor `bf7cd24595f3216f91dcf3eb576f91780252e86b`. O distribuidor valida ambos os destinos, aplica primeiro no nucleus e redistribui os bytes efetivos ao consumidor; regenera o manifesto consumidor localmente e deixa trust para o ato humano separado. Recusa execução de aplicação em sessões/terminais de agente e qualquer drift protegido. Não cria overlay no nucleus nem publica novo pin/release.

Correções candidatas:

1. O gate de contexto considera tentativas, planos e nascimentos do pai/root corretos, inclusive falhas e incompletos. Usa ordem da fonte nativa, não só recibos de sucesso ou mtime. A tentativa mais recente sem qualificação válida impede o uso do sucesso antigo, inclusive por caminho explícito. A descoberta histórica não dispensa revalidação atual de fonte/escopo/artefatos/permissões.
2. Restaura o trecho Claude Code/Desktop preexistente no HEAD do consumidor, mantendo byte a byte tudo fora desse trecho, inclusive o contrato Codex atual. É reparo de regressão documental de outro cliente, sem nova qualificação Desktop.
3. Prompts imutáveis exigem preflight único, resultado completo, retenção de `session_id`, polling do mesmo processo e espera da mesma célula até término, com todos os fragmentos e avaliação final de exit/JSON/ready. Não concluir turno/spawnar com processo pendente, não repetir preflight/probe.
4. Ambos os perfis e prompts de nascimento distinguem janela de entrada, bytes/caracteres/páginas, geração/raciocínio/work budget e limites por retorno. Metadata real é usada se exposta, sem janela fixa garantida ou estimativa apresentada como observação. Exigem todas as partes; falta real de contexto/entrega continua recusando o parecer.

Modelo/esforço, read-only, deny/readback único, SHA, leitura integral nas duas camadas, duas identidades/mesma onda/turno, proxy, verify-wave e checklist permanecem estritos. Materializador e helper de paginação não foram alterados; nenhum arquivo/byte foi retirado do diff.

## Verificação local

148 testes focados passaram: contexto 55, sessão dedicada 19, distribuição/contratos 22, gates Cursor/OpenCode/Claude/T5/I4 40 e entrega integral/truncamento12. Incluem sucessão sucesso → falha/S/controle incorreto/incompleto, nascimento sem execução/plano, contexto alheio, novo sucesso legítimo, histórico após atualização de helpers, preflight sem writes/cache/rede, settings, leitura paginada e recusas de drift/conflito concorrente. Quatro avisos pytest preexistentes permanecem.

O ensaio local separado lançou um processo uma vez, recebeu `session_id` e aguardou o mesmo processo até o JSON completo. Não é qualificação do preflight vivo. O diff real SHA `df57a803a0e4f4d2cacca2541517c612c1af637ed96fcdfe42f96722432a5604` reconstruiu os mesmos bytes em 57 páginas, com máximos 14461 bytes no JSON nativo e 16660 no envelope, abaixo dos limites existentes 16000/28000. Escapes/controles, BMP e não BMP também passaram. Não há prova inventada de tokenização nativa ou atestação interna.

Imports prospectivos com as dependências atuais canônicas, sintaxe dos candidatos, dry-run real dos dois patches e manifesto ativo passaram. A auditoria preservou 167 paths ativos no nucleus e 170 no consumidor, além dos pacotes/receipts anteriores, captura/nascimento originais e `.design-digest`. Adapter ativo permanece `d174776e2c16a162b949a392fd56c4e9c73aea5ce235fa2be01856bb3a7b8d6c`.

## Nota documental autorizada e limites

Depois do selo, foi acrescentada **somente** a nota factual de recorte ao final de `design.md`, por orientação explícita do pai após a decisão de Alan. Hash anterior `685305bec5e7664246b6304cfb9b24ee0f930ab53db45a7c171fc4124677d9b3`; posterior `8b283d4c8ff11fc04189f3ad7dbe70e5b6375eab0783d748945196bbf288723f`. Todo o conteúdo anterior e `.design-digest` foram preservados. A nota não declara T7 nem atualiza aprovação/specs/checklist.

Alan escolheu concluir CLI e separar os ensaios restantes em [#1128](https://github.com/oalansilva/crypto/issues/1128), confirmado Em Refinamento pelo pai. O mapeamento informado está na nota; o pai conduzirá a revalidação pela FSM e delegará autor antes da aplicação humana. A change OpenSpec não integra os oito payloads: o distribuidor registra e preserva seus bytes correntes antes/depois, sem exigir Design obsoleto nem sobrescrever a futura revisão. O snapshot histórico permanece selado.

Nenhum checkbox avançou: **25/35**. Tasks 3.3/6.3 e 5.1–5.8 mantêm o estado até revalidação/aceites próprios. Distribuição real anterior 4.5/6.4 não qualifica o novo candidato. Aplicação humana, novo manifesto/trust pertinente e bootstrap/contexto/probes/rota/Review completos sobre os novos hashes continuam necessários. Sem alegação nova de App/IDE/principal exec independente/refinamento ou QA; `internal_context_attestation=unavailable`.

proxy modelo: apply-coluna → GPT-6.1 Sol (`gpt-6.1-sol`), high original, observado/revalidado pelo pai. Spawns deste Apply: 0; HTML gerado/copied: N/A.
