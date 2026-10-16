# Design critique — #1101 rework (2026-10-14)

- Data: 2026-10-14
- Papel: design-critic
- Faixa: juizo
- Cliente: Claude Code (adapter não oficial)
- Rodada: sem-tela 1+1+1 (crítico único do rework de Design disparado por T4 `recriticar`)
- Modelo pedido: `claude/juizo` → Opus 5.5 (`claude-opus-5-5`), esforço `high` (captura `cap-design-critic.json`, attempt `8fe9f5a4-df9f-4d74-b72c-27560758a0c2`, capture_sha256 `0b2efb75…739ba` / policy `f8886c46…`); receipt `.cursor/tmp/claude-evidence/8fe9f5a4-df9f-4d74-b72c-27560758a0c2.birth.json`. Observado: a coletar pelo pai (`claude_proxy.py`).
- Objeto: working tree não commitado de `openspec/changes/card-1101-claude-code-adapter/` (proposal, design, tasks 11–15, specs `claude-code-harness`, `process-harness`, `account-hook-shim`, `host-version-acceptance`, `cursor-harness`, `covenant-flow`) contra o body do #1101 e os comentários de Alan 6167692629, 6167766324, 6167788244 (e origem 6167650110).
- Nielsen / personas: N/A (sem tela; `UI impact: none`).

## Verdict

**REWORK** — três P1 de contrato visível (falha silenciosa ou contradição com critério observável do body). Todos se resolvem com texto de spec/design e, onde a decisão é de Alan, com Open Question explícita; nenhum exige reabrir as decisões de 2026-10-14.

## Rubrica

| Item | Resultado |
| --- | --- |
| `proposal.md` copia Problema/História/Entra/Não entra do body | OK — comparação programática seção a seção: as quatro seções são idênticas ao body atual. |
| Critérios observáveis do Entra → requisito + cenário | OK com ressalva (P1-3): os 13 critérios têm cenário (`claude-code-harness`, `account-hook-shim`, `host-version-acceptance`). O critério "pin novo → não há registro no repositório" é contradito pelo default `registration=project` gravado no spec. |
| Decisão 1 (registro na conta, shim, pin, digest, `/source`→worktree) | Coberta: §13–§16, spec `account-hook-shim` (5 requisitos), `cursor-harness`/`covenant-flow`/`process-harness` MODIFIED, tasks 11–12, 15.2–15.3. Furos: P1-1 (nuvem), P1-2 (conta sem shim em clientes sem preflight). |
| Decisão 2 (versão aceita pelo formato) | Coberta: §17, spec `host-version-acceptance` (Claude + Codex), tasks 13.x, 15.2. `QUALIFIED_VERSIONS` sai; `unsupported_schema` cita tipo/campo/versão; evidência real obrigatória; Codex incluído; Cursor/Grok/OpenCode/dsh sem lista (verificado pelo autor e confere com o código: só `claude_evidence.py`/`codex_evidence.py`). |
| "Não entra" / seguimentos com motivo | OK — §18 lista entram/ficam fora com motivo; Open Questions 1–2 são legitimamente de Alan. OQ3 reabre item já decidido no body (P2-1). |
| T0–T18, estados, gates T1/T7/T15/T18, release | Intactos (Non-Goals, spec "No state, event, edge or human gate SHALL be added or changed"; T16 = `fechar_release`). |
| Lei duplicada fora de `.cursor/` | Não: shim "MUST NOT contain FSM, Guard, paging or model-selection logic"; canal da conta "MUST NOT carry FSM, adapters, skills or policy". |
| Modo Auto | Nenhuma reivindicação. Uma frase ambígua em §15 (P3-4). |
| Claude Code não oficial | Mantido (`AGENTS.md` não muda; oficialização em card de seguimento). |
| Falha visível: host sem mecanismo global | Visível (`registration=project`), mas contraria critério do body (P1-3). |
| Falha visível: sem evidência | OK (`unavailable`/gate reprova em qualquer versão). |
| Falha visível: formato de transcript novo | OK (`unsupported_schema` com campo). Ressalva P3-2 (`QUALIFIED_ENTRYPOINTS`). |
| Falha visível: superfície de nuvem | FALHA (P1-1). |
| Falha visível: conta sem shim | FALHA para Cursor/Grok/OpenCode/dsh (P1-2). |
| Gate do autor (tokens) | OK — `UI impact: none`, `live_route: none`, `surface: none` em linhas próprias + "Ausência justificada" sem rota emprestada. |
| `openspec validate card-1101-claude-code-adapter --strict` | Verde: `Change 'card-1101-claude-code-adapter' is valid` (exit 0). |
| MODIFIED preserva cenários base | OK — `cursor-harness` (3/3), `covenant-flow` (5/5 + 1 novo), `process-harness` (4/4 + 1 novo). |

## Achados

### P1-1 (contrato) — Sessão de nuvem perde o Guard e o spec ainda promete negação

Design §7 (rework): a sessão `--cloud`/claude.ai/code não lê `~/.claude/settings.json` e o repo deixa de registrar hooks, logo **nenhum** hook roda na nuvem (sem página, sem deny). O spec `claude-code-harness` › "Every Claude Code surface either works or fails visibly" › cenário "Cloud session without local selection" continua dizendo "product writing stays denied". Antes do rework isso era verdade (o `.claude/settings.json` do projeto rodava na nuvem); agora é falso, e a escrita de produto na nuvem fica sem proteção e sem aviso até o primeiro `process_event` — fallback silencioso numa superfície que o body inclui ("web (claude.ai/code)") e exige falhar de forma visível.

Disposition: o rework corrige o cenário para o comportamento real e torna a falha visível sem registro no repo (por exemplo: na nuvem a etapa é recusada no primeiro `process_event`/resolver; escrita de produto sem Guard é limite cooperativo declarado), e leva a Alan como Open Question a escolha entre (a) aceitar nuvem como cooperativa sem Guard, ou (b) outro mecanismo. Não reintroduzir registro de projeto sem decisão de Alan (contraria o critério "não há nenhum").

### P1-2 (contrato) — Pin novo sem conta instalada desliga o Guard em silêncio nos clientes sem preflight

Design §16: "O pin novo exige o shim instalado: sem ele, a sessão fica sem hooks e `process_event` recusa com `hooks_inactive`, como hoje." Só é verdade para Claude Code e Codex: `process_event.py` só tem preflight de evidência para `codex` e `claude` (`hooks_inactive` existe só em `claude_evidence.py`). Para Cursor, Grok, OpenCode e dsh, um consumidor no pin novo numa conta sem `install.sh --account` (máquina nova, `--remove`, conta de outro operador) fica sem Guard, sem página e sem nenhuma recusa — antes do rework esses clientes carregavam o registro do projeto. É regressão de proteção introduzida pela decisão e contraria "falha visível" do body.

Disposition: acrescentar requisito + cenário em `account-hook-shim`: consumidor com `registration: account` e sessão sem heartbeat do shim (qualquer cliente) → recusa visível nas transições dependentes de filhos/escrita via `process_event` (heartbeat do shim por cliente), mais nota no `--check`; ou, se o rework entender que isso altera clientes além do permitido no Não entra, levar a Alan como Open Question. O mecanismo exato (onde checar o heartbeat) é P3 de Apply.

### P1-3 (contrato/escopo) — Spec fixa a resposta da Open Question 1 contra um critério observável do body

O body (critério): "Dado um repo com o pin novo, quando se procura registro de hooks do processo dentro do repositório, então **não há nenhum**". O spec `account-hook-shim` (primeiro requisito + cenário "Host without a proven global mechanism") e `cursor-harness` já determinam que host sem mecanismo provado "SHALL keep the pin's project registration for that host only" — exatamente o default que o próprio design §16/Open Question 1 pergunta a Alan. Resultado: o spec antecipa uma decisão de Alan e, com esse default, o critério do body fica falso para Grok/dsh se o ensaio falhar.

Disposition: o spec deve exigir só a falha visível do host sem mecanismo provado e remeter o tratamento (manter registro de projeto daquele host — o que exige Alan emendar o critério do body — ou recusar o cliente) à resposta de Alan na OQ1; a OQ1 deve dizer explicitamente que o default proposto conflita com o critério "não há nenhum".

### P2-1 (escopo) — Open Question 3 reabre item já decidido no body

O body (Não entra) já manda o protótipo 404 do DEV (achado 12) para seguimento. A OQ3 oferece como alternativa "passo de restart no runbook do Design", que seria escopo novo neste card.

Disposition: remover a OQ3 e registrar o achado 12 só como seguimento, como no body (se o autor quiser a alternativa, ela vira sugestão para o card de seguimento).

### P3-1 (apply) — Sessão de pins mistos (registro do projeto carregado da pasta de lançamento)

O Claude Code carrega o registro de projeto da pasta de **lançamento**, não do cwd. "Sem execução dupla"/"o shim não age em pin antigo" decide pelo pin do cwd. Lançar num worktree de pin antigo com registro de projeto e entrar num de pin novo roda os dois (adapter antigo via `$CLAUDE_PROJECT_DIR` + shim); o inverso deixa o worktree de pin antigo sem processo. Na janela do plano de migração a exposição é pequena (só o #1101 tem `.claude/` hoje; cards pausados).

Disposition: aceito como P3 detalhe de Apply — teste "lançada em pin antigo, entra em pin novo" e "lançada em pin novo, entra em pin antigo", com heartbeat registrando o registro carregado no lançamento e aviso na página.

### P3-2 (apply) — `QUALIFIED_ENTRYPOINTS` pode repetir a trava por atualização

§17 mantém a allowlist de entrypoints. Uma atualização que renomeie o valor de `entrypoint` travaria nascimentos do mesmo jeito que a 2.1.299.

Disposition: aceito como P3 detalhe de Apply — valor desconhecido de entrypoint recusa citando o valor observado como mudança de formato/superfície, nunca como versão.

### P3-3 (apply) — Pisos de capacidade decididos pelo número

`host_min_version` 2.1.292/2.1.295 recusa por número. Não trava atualizações (só hosts antigos), então atende à decisão; detectar por presença de capacidade (`tool_input.effort`, `onFailure`) seria mais fiel a "nunca só pelo número".

Disposition: aceito como P3 detalhe de Apply.

### P3-4 (apply) — Frase "modo automático desta conta" em §15

Descreve o classificador de permissão do host que negou o `trust --record` (achado 7), mas pode ser lida como menção a modo Auto.

Disposition: aceito como P3 — reescrever como "o classificador de permissão do host negou", sem citar Auto.

### P3-5 (apply) — Heartbeat em pasta sem pin vs "nada acontece"

O shim grava heartbeat privado na conta mesmo em pasta sem pin. Não há efeito na sessão (o critério do body fala de página e negação) e é a âncora necessária para `/source` → worktree; justificado em §14.

Disposition: aceito como P3; o requisito já limita a "no effect on the session".

### Nota ao pai (não é achado)

A seção `## Design Critique` de `design.md` ainda reflete a rodada de 2026-10-13 e aponta para o snapshot antigo; o pai publica a seção nova com estes bullets e este snapshot depois do rework.
