# Snapshot — card #850 `card-850-dsh-isolate-reload` (Assessment B)

- Card: #850 — https://github.com/oalansilva/crypto/issues/850 (OPEN, labels `priority:P0` `front:operacao` `type:operacao` `kaizen`)
- Change: `openspec/changes/card-850-dsh-isolate-reload/`
- Critic: isolated Design Critic B (static + live operational detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-09-05T20:04:28Z
- Tuple: hooks `resolve()` → `q=None` `bound_card=⊥` `q_git=card-850-dsh-isolate-reload`. Board Project 1 **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5mPKs`). Write produto deny. Esta onda só `.impeccable/critique/**`. MUST NOT editar `design.md`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-850-dsh-isolate-reload` (branch `card-850-dsh-isolate-reload`)
- Overlay live: `pin: v1.1.9`; `clients.dsh.auto: false`; `overlay_doc: docs/crypto-overlay.md`
- Produto origin tags: `v1.1.9` (latest) … `v1.0.0`. **`v1.1.10` ainda livre** (`gh api repos/oalansilva/covenant-flow/tags`)
- UI impact: **none** (harness/ops dsh: helper de bounce + sidecar SHA + goldens + pin; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** confirmed — zero HTML desta change; `frontend/public/prototypes/` sem `card-850*`; Playwright visual **não** correu (Browser N/A; `/login` não conta)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector = issue vs OpenSpec vs `dsh_boot.sh` actual vs processo vivo `:3080` vs goldens A7–A9
- `design.md` sha256: `00e7079115770e90735fe527c06ddb9d60c92f8475b939eaff6fbee966140f1a` (**1966** palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 3 spec deltas: `developer-tooling`, `process-harness`, `covenant-flow`)
- `openspec validate card-850-dsh-isolate-reload --type change --strict`: **valid**
- `openspec` tasks: **17** checkboxes
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Git: change **untracked** (`?? openspec/changes/card-850-dsh-isolate-reload/`); zero diff de produto nesta onda
- Clone gate T5: isento pelo ramo `ui==none`. `live_route: N/A — harness-only` / `surface: new — isento…` fora do regex estrito (passa porque none)
- Issue REST: body grelhado (Proposta / Problema / História / Entra / Critérios 1–5 / Relacionados). 0 comments.

---

## Brief

A GUI `http://127.0.0.1:3080` não é o pin `v1.1.9`. Isolate Node arrancou 2026-08-30; blobs `#817`/`#839` no git desde 2026-09-04/05; ESM cacheia no arranque. Testemunha `session-968db235`: root turno 1 = 400 `reasoning.effort` `none`; filhos 401 CreditsError com settlement genérico. Residual = reload-após-pin + evidência SHA + dump `:3080`, não outro sanitizer.

Audience: operador na GUI dsh e Homologação/Pronto de card de Guard dsh. Outcome: bounce via `dsh_boot.sh` substitui o listener; sidecar PID+SHA; `--check` fail-closed; dump autenticado. Direction: sibling `dsh_isolate_reload.sh` (SIGTERM `dsh web`, fail-closed se não-dsh) chamado **antes** do `mktemp`; boot bg curto + TCP wait + sidecar + `wait`; pin próximo patch após `v1.1.9`. Scope: pele `covenant-flow` (`dsh_boot.sh` + sibling + goldens R* + overlay_doc 1–3 frases); zero UI Cripto; MUST NOT reimplementar sanitizer/Diagnostic.

---

## Probes (live, este worktree, pré-Apply)

### Isolate vivo `:3080` (o que o Apply vai substituir)

| Claim do Design | Live 2026-09-05T20:04Z | Resultado |
| --- | --- | --- |
| Isolate desde 2026-08-30 08:12, PID testemunha 223762, patch `/tmp/covenant-flow-dsh-TbJZ2F.patch.yml` | `ss`: `127.0.0.1:3080` → pid **223762** (`MainThread`). `ps`: `node …/dsh web --patch /tmp/covenant-flow-dsh-TbJZ2F.patch.yml --no-open --port 3080`, lstart **Sun Aug 30 08:12:51 2026** | **LIVE** |
| `dsh_boot.sh` actual lança `dsh web --patch` **sem** substituir o listener | Boot worktree = source (sha256 `bdb01629…`): `mktemp` + `trap cleanup EXIT` (`rm -f "$TMP_PATCH"`) + último comando **foreground** `dsh web --patch "$TMP_PATCH"` — **sem** SIGTERM, **sem** `--no-open`, **sem** `--port` | **LIVE** |
| Segundo boot deixa o velho a servir | Parent do listener: **PID 223735** `bash /srv/apps/dev/criptofarol/source/scripts/process-fsm/dsh_boot.sh`, **PPID=1**, lstart 08:12:50. Bash ainda **espera o filho foreground**. Patch tmp **ainda no disco** (trap **não** disparou em 6 dias) | **LIVE** (holding = foreground, não `&`+`wait`) |
| Sidecar `/tmp/covenant-flow-dsh-isolate.json` | **Ausente** (pré-Apply) | **esperado** |
| ESM / pin morto | Plugin disco worktree mtime 2026-09-05; processo 30/08. `tmpfiles.d`: `D /tmp 1777 root root 30d` | **LIVE** |

`ss -tlnp` nomeia o occupant **`MainThread`**, não `dsh`. `ps -o args` contém `dsh web`. Sibling que classificar por nome `ss`/`comm` trata o isolate vivo como **não-dsh** → fail-closed e **não bounceia** o processo que o card existe para substituir.

Live cmdline tem `--no-open --port 3080`; `dsh_boot.sh` actual **não** passa esses flags (processo congelado desde 30/08, boot já sem eles no git). Bounce pelo helper novo **omite** `--no-open` salvo o Apply os preservar.

### Goldens que já invocam o boot (o que o Apply vai estender)

`scripts/process-fsm/test_dsh_adapter.py`:

- `_boot_tree`: copia **só** `dsh_boot.sh` (não um sibling).
- `test_a7_*`: `canonical_paths.dev` não-dir → exit ≠0 **antes** do `mktemp` (hoje). Se sibling ficar *depois* do check A7, A7 não mata `:3080`.
- `test_a8_*` / `test_a9_*`: correm `bash …/dsh_boot.sh` com fake `dsh` no `PATH` que faz `echo`+`exit 0`. **Não** setam `DSH_ISOLATE_LISTEN`. **Não** usam porta efémera. Env = `os.environ` (herda o default `127.0.0.1:3080`).

Nenhum outro `*.sh` de produto chama `dsh_boot.sh`. Único caller de produção = o bash 223735 + a receita em `docs/crypto-overlay.md` (`scripts/process-fsm/dsh_boot.sh`).

### Pin / overlay_doc / AGENTS.md

- Overlay worktree **e** source: `pin: v1.1.9`, `dsh.auto: false`. Origin: `v1.1.10` livre.
- Pin-tests existentes (`test_dsh_adapter.py`, `test_dsh_reasoning_effort.py`) hardcode **`v1.1.9`** — Design/task 3.3 pedem a tag que Apply cravar, não `v1.1.10` no vácuo.
- `docs/crypto-overlay.md` § dsh: boot + «Não systemd» + «Não ligar `:3080` em services». **Sem** frase bounce-após-pin.
- `AGENTS.md`: 14 linhas não-vazias (≤40). Não cita isolate/3080; manda `Read docs/crypto-overlay.md` para portas.

---

## Hunt (furos pedidos) — issue vs Design vs live

| Furo | Issue / aceite | Design / tasks / spec | Live | Disposition |
| --- | --- | --- | --- | --- |
| Boot foreground vs `&`+`wait` race | Aceite 1: isolate passa a ser o pin (bounce) | D2: bg só para sidecar, depois `wait`; «Ctrl-C / EXIT continua a ser o fim do isolate»; trap actual ainda `rm` o tmp | Holding vivo = **foreground** filho de `dsh_boot.sh` 223735 (PPID=1). `ss` nome `MainThread`. Task 2.2 **não** trap INT/TERM a matar `$DSH_PID` | **P1** |
| Trap apaga patch | Isolate precisa do `--patch` path (ficheiro vivo há 6d) | Task 2.2: «Trap ainda apaga o tmp patch no EXIT». Risk: «se o Apply backgroundar mal» | Trap **não** corre enquanto o bash segura o foreground. EXIT no `wait` interrompido + `&` → `rm` **com o Node ainda up** | **P1** (mesmo furo que a race) |
| Sidecar `/tmp` limpo no reboot | Aceite 1 evidência PID/SHA | D3: `/tmp/covenant-flow-dsh-isolate.json` estável; MUST NOT `.dsh/` | Sem sidecar hoje. `tmpfiles` **30d**. Reboot apaga `/tmp`; isolate morre (sem unit #793) → `--check` fail-closed | **P2** (fail-closed correcto; 30d com isolate vivo = falso pin morto) |
| `--check` compara disco não ESM | Aceite 1: processo **carregou** os blobs, não o ficheiro no disco | D4 + risk: bounce substitui o processo; sidecar SHA **no arranque**. Sem cache-bust | Mitigação = bounce. `--check` **não** lê ESM. TCP up ≠ plugin loaded. Spec R3 escreve o path canónico | mitigação **CLOSED** se bounce ganhar; residual **P2**; path de teste **P1** |
| Pytest R* a tocar 3080 live | Não matar a GUI | R1–R6: `DSH_ISOLATE_LISTEN` efémero. Apply contract: «pytest **não** mata `:3080`». Task 3.3: A7–A9 «intactos» **sem** env | A8/A9 já correm o boot **sem** `DSH_ISOLATE_LISTEN`. Sibling-antes-`mktemp` + default 3080 = **SIGTERM 223762**. Sidecar canónico sem override | **P1** (A8/A9 + sidecar; R* porta só no contrato) |
| `dsh_boot` sem reload noutro script | Canal = helper de boot | D1: sibling **só** via `dsh_boot.sh` | Zero outros `*.sh`. overlay_doc aponta ao boot. Live = 223735 | **CLOSED** |
| Pin `v1.1.10` hardcoded | Próximo patch após origin | D6 rejeita cravar sem check; task 3.3 «não hardcode no vácuo»; spec «`v1.1.10` when free» | Origin `v1.1.9` ocupado; `v1.1.10` livre. Pin-tests ainda `v1.1.9` | **CLOSED** no contrato Design; Apply MUST `ls-remote` |
| Dual-write T0–T17 | Não entra | Non-goal; tasks 3.3/5.2/6.2; spec covenant-flow | Pacote não adiciona tabela nem `process-fsm.yaml` | **CLOSED** |
| overlay_doc vs `AGENTS.md` | Portas/3080 = overlay | D6 MUST 1–3 frases em `docs/crypto-overlay.md`; `AGENTS.md` MUST NOT crescer. Proposal/spec **MAY** | Canal certo = overlay_doc (já tem § dsh). AGENTS 14 linhas, sem 3080 | **CLOSED** (MUST vs MAY = P3 wording) |

---

## Rubrica (UI none)

- **Escopo:** issue critérios 1–5 sintetizados (bounce após pin/merge plugin/lib; 1º turno root sem 400 none; Diagnostic no filho; #817/#839 fechados como trabalho; dump `:3080`). Pin neste card. Não reentrevista. Não reabre #817/#839/#837/#793/#846. Não vendorar `@deepseek-ai/dsh*` / `pi-ai`.
- **Regressão:** A7–A9 `canonical_paths.dev`; E1–E12 / F1–F8 / G1 / write deny. A8/A9 **não** estão isoladas da porta live depois do sibling.
- **Riscos operacionais:** `&`+`wait` vs holding foreground vivo; trap `rm` no EXIT; sidecar `/tmp` vs pytest e tmpfiles 30d; `--check` proxy disco; `ss` nome `MainThread`.
- **Superfície visual:** nenhuma. Prototype N/A.

---

## Critique (contrato vs live)

`openspec validate --strict` verde. Prototype N/A justificado. Sem HTML. Sem `## Design Critique` pré-preenchido. Clone gate T5 passaria pelo ramo none. Pin origin correcto (`v1.1.10` livre). Canal sibling-via-boot alinhado com o único caller vivo. `AGENTS.md` / T0–T17 / outro script de boot: limpos.

**D1 (SIGTERM do `dsh web` + patch novo) é o aceite 1.** O boot actual **não** substitui; o parent 223735 segura o Node 223762 em foreground com o patch de 30/08 ainda no disco. Isso confirma o problema do issue.

**D2 não assenta no process tree vivo.** Hoje o isolate **é** o último comando foreground de `dsh_boot.sh`. Passar a `dsh web &` + `wait` **sem** trap INT/TERM/EXIT a matar `$DSH_PID` parte o holding: SIGINT/`wait` interrompido dispara o trap actual (`rm -f` patch) e o Node pode ficar órfão (PPID=1) — o contrário de «Ctrl-C / EXIT continua a ser o fim do isolate». O risk do Design trata só «Apply backgroundar mal», não o `&` **dentro** do boot.

**Tasks 3.1 isolam R*; tasks 3.3 deixam A8/A9 a invocar o boot novo no default `127.0.0.1:3080`.** Apply que copie o sibling para `_boot_tree` (preciso para A8 não 127) **sem** `DSH_ISOLATE_LISTEN` SIGTERM o listener vivo. Spec R3 **obriga** escrever `/tmp/covenant-flow-dsh-isolate.json` no fake launch — clobber do sidecar de Homologação. Apply contract «pytest não mata `:3080`» não chega: falta env **e** path de sidecar nos goldens que **já** existem.

P0 de API inventada / pin cravado / dual-write / AGENTS.md: **não**. P1 operacional no veículo do bounce: **sim**.

---

## Findings

### P0

*(nenhum aberto — sibling via `dsh_boot.sh`, `mktemp` novo, `--check` fail-closed, pin `ls-remote`, overlay_doc vs AGENTS, T0–T17, ausência de outro caller, Prototype N/A, e APIs de ficheiro/processo existem no checkout)*

### P1

- **P1-1 — A8/A9 + sidecar canónico fazem `pytest scripts/process-fsm` tocar o isolate live.** `test_a8_empty_canonical_dev_launches_repo_root` e `test_a9_directory_canonical_dev_still_preferred` já executam `dsh_boot.sh` **sem** `DSH_ISOLATE_LISTEN`, com fake `dsh` que sai 0, copiando só o boot. D1/task 2.1: sibling **antes** do `mktemp`, default `127.0.0.1:3080`. Live nesse endereço: PID **223762** (filho de **223735** `dsh_boot.sh`). R1–R6 pedem porta efémera; task 3.3 diz A7–A9 intactos **sem** exigir o env. Spec sidecar: path **fixo** `/tmp/covenant-flow-dsh-isolate.json` no fake launch (R3/R4) — overwrite da evidência de Homologação mesmo com porta efémera. Fechar: (a) A8/A9 MUST set `DSH_ISOLATE_LISTEN` efémero **e** copiar o sibling; (b) MUST haver override de sidecar (`DSH_ISOLATE_SIDECAR` ou `$TMPDIR`) nos goldens, default o path estável só no bounce do operador; (c) A8/A9 MUST NOT esperar TCP em 3080 nem herdar o default; (d) golden que prova que A8/A9 **não** SIGTERM `127.0.0.1:3080`.

- **P1-2 — D2 `&`+`wait` + trap actual `rm` parte o holding vivo e pode apagar o patch com o Node ainda up.** Live: bash 223735 foreground espera 223762; trap **não** corre; patch de 30/08 ainda existe. Task 2.2: «Trap ainda apaga o tmp patch no EXIT» + `dsh web` em background + `wait`. Script bash: `&` põe o Node noutro process group; SIGINT no `wait` / SIGTERM no boot dispara EXIT → `rm -f "$TMP_PATCH"` **sem** matar `$DSH_PID` (huponexit off). D2 afirma «Ctrl-C / EXIT = fim do isolate» — contradiz o trap que só apaga o patch. Timeout do TCP wait (`set -e`) sai ≠0, apaga o tmp, deixa órfão. Fechar: trap INT/TERM/EXIT MUST SIGTERM/SIGKILL `$DSH_PID` **depois** confirmar porta livre, **depois** `rm` o patch; MUST NOT `rm` enquanto o listener viver; golden de SIGINT no boot a matar o fake listener **e** a não deixar órfão.

### P2

- **`--check` é proxy disco+PID, não ESM.** Bounce no arranque é a mitigação certa (risk D4). Residual: TCP listen ≠ plugin `apply()` concluído; SHA não inclui `impeccable-hook.js` (issue entra `.dsh/plugin/**`). Aceite se o sidecar for escrito **após** listen **e** o bounce for o único writer; MUST NOT vender `--check` PASS como prova ESM sem o dump 7.2.
- **Sidecar `/tmp` × reboot × tmpfiles 30d.** Reboot: fail-closed correcto (isolate morto, sem #793). Isolate a viver >30d (o actual já vai em 6d): `--check` falha com processo saudável. overlay_doc SHOULD dizer «sidecar some com `/tmp`; bounce de novo».
- **Occupant `dsh web` vs `ss` `MainThread`.** Identificação MUST ser cmdline/args (`dsh web`), não `comm`/`ss` name. Senão fail-closed no PID 223762 e aceite 1 não fecha.
- **Live `--no-open --port 3080` ausente do boot git.** Bounce pelo helper novo pode abrir browser e ignora `DSH_ISOLATE_LISTEN` no `dsh web` (só o sibling lê o env). Pytest com fake tapa; operador real MUST mapear listen → `--port` / `--no-open`.
- **`live_route` / `surface` fora do regex T5.** Passa porque `ui==none`. SHOULD `live_route: N/A harness-only` na mesma forma que #817/#839.

### P3

- Proposal/spec overlay_doc **MAY** vs design/task **MUST** 1–3 frases — o Apply segue tasks; unificar o modal.
- Sidecar world-writable em `/tmp` (forge PID/SHA). Aceite para v1; Homologação humana continua o dump.
- 401 billing permanece residual (issue `_Avoid:`). 7.2 «falha, se houver» pode verde sem exercitar aceite 3 se o spawn passar.
- Change #817/#839 Pronto; este card MUST NOT as reabrir. #793 unit MAY `ExecStart` este helper noutro card.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento. T1/T7 Alan; T5 parent. Dual-write T0–T17 **proibido** no pacote — **CLOSED**.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; specs MUST NOT reivindicar.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.
- Vendor `@deepseek-ai/dsh*` / `pi-ai`: proibido.
- `dsh_boot` noutro script de produto: **CLOSED** (único live = 223735).
- Pin `v1.1.10` hardcoded no Design: **CLOSED** (esperado se livre; Apply `ls-remote`).
- overlay_doc vs `AGENTS.md`: **CLOSED** (frases no overlay_doc; AGENTS não cresce).

---

## Trace

1. Issue #850 REST: 5 aceites; pin morto; 400 none no root t1; 401 filho opaco; #793 não substitui reload-após-pin.
2. Live: 223735 `dsh_boot.sh` (PPID=1) foreground segura 223762 `dsh web --patch …TbJZ2F… --no-open --port 3080` desde 30/08; `ss` name `MainThread`; patch tmp ainda no disco; sidecar ausente.
3. Design D1 (sibling SIGTERM + patch novo) alinha com aceite 1. D2 (`&`+`wait`+trap `rm`) **não** alinha com o holding vivo. Tasks 3.1 isolam R*; A8/A9 + sidecar canónico não.
4. Origin `v1.1.9`; `v1.1.10` livre; AGENTS 14 linhas; overlay_doc § dsh sem bounce; `openspec validate --strict` valid.
5. Clone gate / HTML / Design Critique / outro caller / T0–T17: limpos.

---

## Disposition

Zero P0 de API inventada, pin cravado, dual-write T0–T17, `AGENTS.md`, ou segundo script de boot. Dois P1 abertos no **veículo** do bounce: (1) goldens A8/A9 + sidecar `/tmp` fixo fazem pytest tocar o isolate live 223762 / clobber Homologação; (2) D2 `&`+`wait` com trap actual `rm` contradiz o holding foreground vivo e apaga o patch sem matar o Node. Mitigação `--check` disco≠ESM é aceite **se** o bounce substituir o PID; residual P2 (TCP≠ESM, tmpfiles 30d, `ss` `MainThread`, `--no-open`/`--port`). UI none / Prototype N/A / T5 / pin `ls-remote` / overlay_doc vs AGENTS / #817/#839-não-reabrir estão fechados. Sem polish visual. MUST NOT editar `design.md` daqui. Filho autor MUST fechar P1-1 e P1-2 no pacote OpenSpec antes de T5.

### Verdict

**BLOCKED**
