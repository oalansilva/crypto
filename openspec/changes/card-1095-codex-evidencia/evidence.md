# Apply e prova #1095

Status vivo reconfirmado `Em desenvolvimento`; cwd/branch `card-1095-codex-evidencia`. T8 não repetido. Sem transição, commit, push, trust/hooks ou produto/release/PROD no ensaio. UI impact: none; HTML N/A. Uma criança nativa adicional exclusivamente para qualificação, sem trabalho de produto. A implementação pertence ao único filho Apply desta entrada.

## Prova real positiva

Ensaio explícito em 2026-10-13, pelo filho nativo `/root/apply_coluna/evidence_essay_1095`, após captura local de execução e `codex_evidence.py prepare --qualification`. O spawn recebeu literalmente `gpt-6.1-sol` / `high`. Conteúdo cifrado do prompt não foi usado ou persistido.

| Campo | Observação/fonte |
| --- | --- |
| Driver / envelope | `codex_exec/0.162.1/rollout-v1` / `codex-rollout-evidence-v1` |
| Parent / child UUID | `01a13324-0004-7981-92bc-3c2d8cd6107a` / `01a13328-df7c-7f13-bb15-2e5ad740862e` |
| Parent / child turno | `01a13324-0033-7611-b502-4a6e14abfa92` / `01a13328-dfa3-7c81-84c4-f9026f22a42a` |
| Native call_id | `call_00df656c7a644caa84074987d67144e3` |
| Tentativa / captura SHA-256 | `9f56750b-b6c0-4ed8-8211-672d98213079` / `ad100dfb99f308f8ea727ec52f3a580816a4e050001d492ba4566a96efa1479b` |
| Requested | captura: `gpt-6.1-sol/high` |
| Observed | `turn_context`: `gpt-6.1-sol/high` |
| Host / versão | `session_meta`: `codex_exec/0.162.1`; sem consultar versão instalada |
| Filiação | `session_meta.source.subagent.thread_spawn`: mesmo parent UUID e agent_path do retorno do spawn |
| Terminal / retorno | `task_started` e `task_complete` no mesmo turno; payload não vazio idêntico ao `FINAL_ANSWER` nativo no pai |
| Sandbox | workspace-write observado no pai e filho; não comprova uma onda real read-only |
| Payload SHA-256 | `de7ba0542ac2e2c0cbefeb3e468d7a434fe0592bbaafc688599341aa3e63bccf` |
| Extração SHA-256 | `46c3322dc8c583c98d16c71c1d2dfc6f4e4afbe49efe2cf38ed17695dd1d43a4` |
| Consumidor | `codex_proxy.py --birth`: successful=true; `verify_proxy` relê e valida fonte/binding. Repetição retorna o mesmo registro (uma linha no log de qualificação). |

Fontes originais privadas: `$HOME/.codex/sessions/2026/10/13/rollout-2026-10-13T02-42-39-01a13324-0004-7981-92bc-3c2d8cd6107a.jsonl` e `rollout-2026-10-13T02-47-59-01a13328-df7c-7f13-bb15-2e5ad740862e.jsonl`. O índice foi usado apenas como localizador por identidade/path exatos; nenhuma seleção por mtime/último filho. A extração referencia os ordinais 0/7/112/115/125 do pai e 0/1/7/16 do filho, com digests dos bytes usados; os bytes completos/payload/prompt não são copiados.

Artefatos locais protegidos: `.cursor/tmp/codex-evidence/<tentativa>.birth.json`, `<tentativa>.evidence.json`, `qualification-proxies.jsonl`, `qualification.json`; captura original `/tmp/card-1095-qualification-birth.json`, mantida imutável. Nenhum desses paths serve de fallback se a fonte ficar indisponível.

Revalidação reproduzível, preservando os arquivos atuais:

```bash
python3 scripts/process-fsm/codex_evidence.py verify \
  --evidence .cursor/tmp/codex-evidence/9f56750b-b6c0-4ed8-8211-672d98213079.evidence.json
python3 scripts/process-fsm/codex_proxy.py \
  --capture /tmp/card-1095-qualification-birth.json --activity qa-gate --band execucao \
  --birth .cursor/tmp/codex-evidence/9f56750b-b6c0-4ed8-8211-672d98213079.birth.json \
  --output .cursor/tmp/codex-evidence/qualification-proxies.jsonl
python3 scripts/process-fsm/codex_evidence.py preflight
```

## Recusas reais e recuperação

- Coleta inicial com janela 0s recebeu `return_payload_mismatch`, exit 2: o `FINAL_ANSWER` ainda não havia sido entregue/flushed no pai. Failure privado `<tentativa>.failure-3a94dfb09ea2.json`. Após o retorno real, a mesma tentativa/captura passou, sem apagar failure ou duplicar proxy. Esse é o negativo real associado à qualificação.
- `codex_evidence.py preflight --review` nesta sessão workspace-write: `parent_sandbox_mismatch`, exit 2. Nenhum reviewer nasceu. Não usar perfil de Agent como prova de sandbox do pai.
- `codex_proxy.py ... --evidence <prova-real> --observed-model gpt-6.1-sol`: recusa de flags manuais, exit 2; o par observado vem exclusivamente da fonte.
- `verify` sobre cópia deliberadamente adulterada do envelope real: `integrity_mismatch`, exit 2. O original permaneceu íntegro.
- `preflight --thread no-such-real-thread`: `source_unavailable`, exit 2, consultando o índice real. É uma contraprova com identidade inválida, não uma alegação de outage/permissão revogada real.

Os quatro últimos resultados foram registrados em `.cursor/tmp/codex-evidence/negative-results.json`. Permissão revogada, modelo divergente e host/schema desconhecidos foram ensaiados em fixtures; não são apresentados como eventos reais deste host. Fonte perdida após trabalho preserva Status/artefatos; recollection exige a mesma origem/captura íntegra. Divergência/origem irrecuperável exige novo nascimento, nunca retune/resume.

## Requisitos e implementação

| Requisito | Implementação / evidência |
| --- | --- |
| Availability before dependent work | `codex_evidence.preflight/prepare`, hook Agent com receipt, preflight Codex no `process_event`; fixture prova recusa sem mover board. Sessão atual e a do pai passaram preflight real. |
| Automatically collected observations | `Rollout.session/extract`, chamada nativa + retorno + UUID/filiação/turnos; proxy real aprovado sem observação manual. |
| Immutable birth and all relevant turns | captura completa/digest e boundary pré-spawn; namespace/call_id/turn metadata; tests de identidade, nascimento, captura alterada e divergência anterior ao último turno. |
| Bounded recovery | limite 0..10s, padrão 5; failure privado separado, coleta exclusiva/idempotente; caso de flush real recuperado. |
| Existing gates and Codex scope | `verify_proxy`, `model_proxy`, `verify_wave`; fixtures mantêm dois papéis/capturas/filhos, mesma sessão/turno read-only, diff, onda e payload. Demais adapters preservados na suíte de regressão. |
| Real host support | positivo + gate real + recusas acima; matriz/limites em `docs/codex-runtime-evidence.md`. Somente `codex_exec/0.162.1` rollout-v1 qualificado, sem promessa para outros hosts/versões. |

## Validação

- `python3 -m pytest -q scripts/process-fsm`: 710 passed, 9 skipped; quatro avisos preexistentes de plugins/opções pytest ausentes.
- `python3 -m pytest -q scripts/process-fsm/test_codex_evidence.py`: 30 passed após ajuste final apenas dos campos do diagnóstico CLI.
- `node --test scripts/process-fsm/test_codex_impeccable.mjs`: 3 passed.
- `openspec validate card-1095-codex-evidencia --strict`: PASS. Sintaxe final usa slug posicional, sem `--change`.
- `git diff --check`: PASS.

## Handoff e limites

Comandos completos de captura/receipt, transição e coordenação da sessão Code Review estão em `docs/codex-runtime-evidence.md` e no runbook canônico. O pai pode executar `preflight`, depois o evento permitido (`--client codex`) e preparar a onda; o Apply não muda estado. A qualificação aceita o host/fonte atual, não garante execução futura nem substitui Design/critique/QA/review/gates humanos.

O próprio Apply nasceu antes do mecanismo e não tem receipt pré-spawn deste coletor; sua observação real `gpt-6.1-sol/high` existe no rollout, mas não foi promovida a envelope novo nem recebeu receipt retroativo. Isso não altera o T8 já executado. O pai registra esse limite no handoff; novas tentativas/ondas usam o caminho obrigatório. Hooks/trust permaneceram intocados. Hashes locais não constituem atestado independente do servidor. Os nove skips não foram convertidos em prova positiva.

Proxy: Design com 1.564 palavras, sem reescrita pelo Apply; HTML N/A; um spawn adicional de ensaio.
proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol)
proxy modelo: qa-gate (ensaio sem produto) → GPT-6.1 Sol (gpt-6.1-sol)

## Follow-up operacional: recusa na sessão read-only (2026-10-13)

Correção feita pelo único filho Apply-correcao desta entrada, após T10 executada pelo pai; T8 não repetido. Nenhum reviewer/filho nasceu neste Apply. Design/proposal/spec aprovados preservados; nenhuma alteração de sandbox, trust, FSM, gate, commit ou push.

A fonte real `$HOME/.codex/sessions/2026/10/13/rollout-2026-10-13T03-17-45-01a13344-215c-78f0-914f-a6d3fe8f1c47.jsonl` identifica `codex_exec/0.162.1`, sessão `01a13344-215c-78f0-914f-a6d3fe8f1c47`, turno `01a13344-21c9-7841-8f45-b0e4ece90d9f`, sandbox observado `read-only`. O índice foi usado somente para localizar essa identidade. O `custom_tool_call_output` de ordinal 35 contém a recusa real `destination_unwritable` e a mensagem `writable orchestrator must prepare private destination before read-only wave`; SHA-256 dos bytes desse evento: `5ad3a2912d8d8c3035e769ceac2a043c89a13a97aaafcf08230518e97c6cebb7`. Não há chamada nativa `collaboration.spawn_agent` nessa sessão.

O destino `.cursor/tmp/codex-evidence/` observado está em 0700. Os receipts preparados antes da tentativa, `941f5b9b-5851-4d36-96b6-7a0d04ddb3fc.birth.json` (diff-reviewer) e `9e9e71d6-8690-4055-9601-6888e154a346.birth.json` (code-reviewer), passaram `check_seal`; ambos apontam à sessão/turno acima, onda `card-1095-w2`, diff SHA-256 `861af90f0df8352d962bb2be1edf046fd405d69922b5e218a864098b6eb964f2`. Permaneceram intactos e não são prova de reviewers executados. Capturas/receipts novos para outra sessão/turno são responsabilidade do pai; não adaptar os existentes retroativamente.

Causa: `preflight(review=True)` exigia `os.access(out, os.W_OK)` dentro do próprio sandbox read-only. Isso confundia a permissão da sessão de inspeção com a do orquestrador gravável. Correção mínima em `codex_evidence.py`: inspeção exige diretório privado 0700, rejeita symlinks/traversal e abre `os.scandir` sem escrita; `check_writable_destination` realiza a sondagem efetiva com arquivo temporário no preflight normal e no `prepare` de review executado pelo pai gravável, antes da persistência do receipt. Destino ausente/ilegível/inseguro continua negado. Falha de escrita no pai continua `destination_unwritable`, sem alterar receipt existente. Integridade, qualificação, observação de sandbox, identidade/turno, SHA do diff, dois papéis/filhos e completed/payload seguem exigidos pelos consumidores.

As regressões em `test_codex_evidence.py` negam `W_OK` e tornam criação de diretório/arquivo, chmod e persistência erros durante inspeção; comprovam retorno ready e bytes/modo intactos. Os negativos cobrem destino ausente, arquivo, modo público, symlink, leitura negada e escrita revogada no `prepare` normal e de review, antes de qualquer receipt novo. São fixtures controladas; não comprovam uma nova onda nativa read-only.

O ensaio real read-only após esta correção está **pendente do pai externo**: nova sessão ativa comprovada read-only, receipts preparados pelo pai gravável, dois reviewers no mesmo turno, coleta posterior e verify-wave/checklist. Este Apply não declara que tal ensaio passou.

Validação do follow-up:

- `python3 -m pytest -q scripts/process-fsm/test_codex_evidence.py`: **37 passed**, quatro avisos de configuração pytest preexistentes.
- `python3 -m pytest -q scripts/process-fsm`: **717 passed, 9 skipped**, quatro avisos preexistentes, 57,00s; sete casos novos frente ao baseline 710/9.
- `node --test scripts/process-fsm/test_codex_impeccable.mjs`: **3 passed**.
- `openspec validate card-1095-codex-evidencia --strict` e `git diff --check`: **PASS**.
- Tasks: as 16 originais preservadas e três follow-ups 5.1–5.3 completos; a pendência da onda real do pai é explícita acima.

Antes da republicação, proposal/design/spec locais foram comparados com os arquivos do Gist existente e correspondem ao conteúdo aprovado. SHA-256 local de `design.md` preservado: `a136ff447157d398b2077d9583c64ceaa1897834bf70cc7e6c62ee5cefb2393a`. As tasks e o diagnóstico são follow-up de implementação, sem reescrita do Design.

Republicação efetivada pelo helper canônico `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh --repo oalansilva/crypto --issue 1095 --change card-1095-codex-evidencia --gist-id 3d0efb3237ff4488968f6dc8ee8dfd13` (exit 0). Gist secreto existente: https://gist.github.com/oalansilva/3d0efb3237ff4488968f6dc8ee8dfd13. A API confirmou `public=false` e conteúdo proposal/design/tasks/spec correspondente aos arquivos locais (o helper remove somente newlines finais); 19 checkboxes completos. Nenhum comentário novo ou alteração do comentário aprovado foi feito. `evidence.md` e o runbook ficam locais no pacote: o helper publica somente proposal/design/tasks/specs. Os dois receipts originais foram novamente revalidados após a correção, com seal íntegro e modo 0600.

## Correção conjunta dos achados mecânicos da primeira onda real w3 (2026-10-13)

O pai forneceu o payload integral da primeira onda real `card-1095-w3` em `/tmp/card-1095-review3-result.txt`. Os achados copiados do diff-reviewer são P2 / defeito funcional / bloqueia_merge: sim (`codex_evidence.py`, persistência de continuação) e P2 / violação de contrato / bloqueia_merge: sim (`codex_review.py`, aceitação de qualificação como review de produto). O code-reviewer retornou `No findings`. Este registro usa o handoff da onda; não declara novas observações runtime coletadas pelo filho Apply.

Correção feita conjuntamente pelo único filho Apply-correcao desta entrada após T10, sem T8, novos filhos, reviewers, transições, commit/push ou alterações de trust/sandbox. Captura de nascimento fornecida pelo pai: `/tmp/card-1095-apply-correcao-w3-capture.json`; receipt: `.cursor/tmp/codex-evidence/7d2be033-76ee-49b0-8268-c3402fc9bc81.birth.json`. A coleta automática/proxy deste filho cabe ao pai após completed; nenhuma observação foi preenchida manualmente.

`codex_evidence.py` mantém o primeiro envelope imutável e publica revisões determinísticas por digest para os novos turnos da mesma captura. Recoleta do mesmo estado reutiliza a revisão. Coleta/verificação relê todos os turnos atuais e compara campos fixos, prefixos de turnos e hashes de payload e cada registro usado por path/ordinal/digest contra todos os snapshots aceitos. Alterar/remover um turno anterior, corromper uma revisão, acrescentar divergência mesmo seguida de último turno válido ou apresentar turno incompleto recusa também a âncora antiga, sem sobrescrever evidência anterior. Os snapshots devem permanecer juntos da captura/receipt; hash local conserva seu limite de detecção de adulteração e não é atestado do servidor.

`codex_proxy.py` deduplica a tentativa mantendo a referência/digest original quando os demais campos coincidem e revalida a âncora antes de reutilizar o registro. `verify_proxy` também confere o digest registrado. Assim, novos snapshots válidos não acrescentam uma terceira entrada à onda. `codex_review.py verify-wave` recusa explicitamente `qualification=true` após verificar proveniência; a qualificação continua disponível exclusivamente para ensaios. O teste que antes legitimava uma onda de qualificação foi substituído por caminhos de review normal com qualificação prévia do host simulado e por rejeição explícita de qualificações, inclusive quando estas dispensam o papel nativo.

Regressões controladas: duas continuações aceitas depois de editar a seleção local, bytes/modos privados imutáveis, recoleta e proxy único; alteração de registro/payload ou remoção de turno aceito; divergência seguida de turno correto; turno incompleto e corrupção de revisão; onda normal aceita e onda de qualificação recusada. Essas fixtures não qualificam o host real nem comprovam nova onda nativa.

Validação desta correção:

- `python3 -m pytest -q scripts/process-fsm/test_codex_evidence.py scripts/process-fsm/test_codex_proxy.py scripts/process-fsm/test_codex_review.py`: **76 passed** no marco intermediário; a suíte final abaixo inclui o caso adicional de continuação incompleta/corrupção de revisão e o binding de digest do proxy.
- `python3 -m pytest -q scripts/process-fsm`: **724 passed, 9 skipped**, quatro avisos preexistentes de opções pytest, 60,33s; sete casos adicionais frente ao baseline 717/9.
- `node --test scripts/process-fsm/test_codex_impeccable.mjs`: **3 passed**.
- `openspec validate card-1095-codex-evidencia --strict` e `git diff --check`: **PASS**.
- Uma verificação de conteúdo da própria correção: conferidas a extensão por prefixo/registro, a revalidação de todos os snapshots em coleta e consumo, a deduplicação com âncora íntegra e a rejeição de qualificação no consumidor. Sem nova rodada de reviewers neste Apply.
- Design aprovado preservado, SHA-256 `a136ff447157d398b2077d9583c64ceaa1897834bf70cc7e6c62ee5cefb2393a`; tasks **22/22** completas. HTML gerado/copiado: **N/A**; spawns neste filho: **0**.

Proxies de handoff: `design.md` tem 1564 palavras; HTML gerado/copiado N/A; um nascimento Apply-correcao fornecido pelo pai, zero spawns neste filho. Modelo solicitado na captura (observação runtime pendente da coleta do pai):

proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol)

A republicação das tasks 6.1–6.3 no Gist existente `3d0efb3237ff4488968f6dc8ee8dfd13` fica para o pai após completed, conforme coordenação explícita; não foi executada neste filho. Paths de entrega: `tasks.md`, este `evidence.md` e `docs/codex-runtime-evidence.md`. O conteúdo de Design/proposal/spec aprovado permanece preservado. A coleta do proxy Apply e a verificação da correção na onda do pai continuam fora da evidência produzida por este filho.
