## Context

Card [#720](https://github.com/oalansilva/crypto/issues/720) (kaizen P0). Núcleo e dois adapters já entregues no [#668](https://github.com/oalansilva/crypto/issues/668). Relacionado: [#608](https://github.com/oalansilva/crypto/issues/608) (EFSM), [#562](https://github.com/oalansilva/crypto/issues/562) (cutover; este card revoga **só** a unicidade, não o lock machine), [#611](https://github.com/oalansilva/crypto/issues/611) (tool desconhecida = allow), [#395](https://github.com/oalansilva/crypto/issues/395) (path `.opencode/plugin/` singular). Fora: artigo [#614](https://github.com/oalansilva/crypto/issues/614).

Hoje `decide()` / `page()` compilam Cursor (`tool_name`/`tool_input`) e Grok (`toolName`/`toolInput`). Abrir o repo no OpenCode **1.18.18** (binário live `/home/ubuntu/.opencode/bin/opencode`, `--version 1.18.18`) não é contrato: o Guard não vê `{ tool, args }`, e um write ilegal em `backend/` com `q_git=develop` passa. Detector Impeccable está só no Cursor (`.cursor/hooks.json` `afterFileEdit`/`stop` → `impeccable.sh` → `hook.mjs`). Grok `.grok/hooks/process-fsm.json` tem Guard `PreToolUse` + `SessionStart`, sem `PostToolUse`/`Stop`. `.opencode/` não existe neste worktree.

Observação Design no binário 1.18.18 (strings + `plugin.trigger`):

- Auto-load: qualquer `*.js` / `*.ts` em `.opencode/plugin/` **ou** `.opencode/plugins/` — versionar só o singular (#395).
- Export: `Plugin = (input, options?) => Promise<Hooks>` (função, não objeto literal).
- Guard: `tool.execute.before` (`input.tool`, `output.args`). Deny = **throw** (o produto não honra JSON `{permission,decision}`).
- Detector: `tool.execute.after` + bus `session.idle` (`type:"session.idle"`, schema `{sessionID}`).
- Paging: `experimental.chat.system.transform` dispara com `{sessionID, model}` e `{system: string[]}`.
- Tools nativas: `write`/`edit` usam `args.filePath`; `apply_patch` usa `args.patchText`; `bash` usa `args.command`.
- Marcadores live de `patchText`: `*** Add File:`, `*** Update File:`, `*** Delete File:`, `*** Move to:` (o issue diz “Move File”; o binário usa `*** Move to:`). Lista canônica = golden + ensaio neste binário.

**UI impact: none.** Harness/hooks/docs. Nenhuma superfície de produto. Prototype N/A. Pipeline Impeccable *desta* coluna Design (shape/protótipo/crítica de tela) = N/A. Detector automático em sessões futuras nos três clientes = entra (pele de harness, não tela).

## Goals / Non-Goals

**Goals:**

- Terceiro adapter OpenCode 1.18.18 sobre o mesmo `decide()` / `page()`. Uma mudança de glob/coluna/Moore no yaml vale nos três clientes.
- Dialeto nativo `{ tool, args }` no `normalize()` / `extract_path()`. Path vazio / `patchText` sem path extraível **não** vira allow.
- Plugin auto-load em `.opencode/plugin/`, **sem** `opencode.json`, throw no deny.
- Paging OpenCode = inject `experimental.chat.system.transform` (mesmo texto que Cursor `additional_context`).
- Detector Impeccable nos três: mesmo `hook.mjs`; Grok `PostToolUse`+`Stop`; OpenCode `tool.execute.after`+`session.idle`; fail-open.
- `AGENTS.md` nomeia os três clientes; sem Auto OpenCode (nem Auto Grok até #668 4.5).
- Specs: dois → três adapters; detector deixa de ser só Cursor; lock machine permanece morto.
- Golden pytest em `scripts/process-fsm` (sem GitHub) + ensaio humano deny/detector.

**Non-Goals:**

- Upgrade do OpenCode neste card.
- Restaurar lock machine (`design-planner`, lease, packet, `design_artifact_write`, attestation, `opencode.db` no kaizen).
- Segundo Guard / segundo detector / tabela T0–T17 / I1–I9 em `.opencode/` / `permission: { edit: deny }` estático.
- `opencode.json` (mínimo ou completo).
- Commands `/opsx-*` no OpenCode.
- Código de produto; `--auto` / Auto sem ensaio; artigo #614; dual-write Hermes / `~/.codex/skills/`.
- Reabrir o núcleo do #668 (yaml, `decide()` dual emit). Este card **acresce** detector Grok que o #668 deixou fora, sem relitigar Guard/paging Grok.
- Arquivo Moore gitignored + MUST Read no OpenCode (decisão: inject).
- Reivindicar Auto OpenCode ou herdar Auto do Cursor.

## Decisions

1. **Alvo fixo 1.18.18; sem upgrade.**  
   Lista canônica de tools/hooks = o que golden + ensaio cobrirem neste binário. Se a API divergir depois, card filho. Alternativa rejeitada: upgrade agora para “pegar o fix #5894”.

2. **Terceiro dialeto no mesmo `normalize()`, não um segundo Guard.**  
   Envelope nativo `{ tool, args }` entra ao lado de Cursor e Grok. `decide()` permanece canônico. Plugin serializa e chama `guard.py`. Alternativa rejeitada: fork `guard.py` para OpenCode (dual-write da política).

3. **Família OpenCode canônica (live 1.18.18).**  
   Write: `write`, `edit`, `apply_patch`. Shell: `bash`. Path: `args.filePath`. Patch: `args.patchText` com `*** Add File:` / `*** Update File:` / `*** Delete File:` / `*** Move to:`. Command: `args.command`. Tool fora da lista → allow (classe #611). Alternativa rejeitada: tratar `apply_patch` como `edit` sem parse de `patchText` (path vazio viraria allow).  
   **Parse `patchText`:** `extract_paths()` devolve todos os paths dos quatro marcadores, na ordem. `*** Move to:` conta o **destino** (não o source do `Update File`). `decide()` classifica `glob_kind` em **cada** path e trata o envelope como `write_produto` se **qualquer** path for `product_globs` (um rename `docs/note.md` → `backend/app/moved.py` é write de produto). `extract_path()` devolve o primeiro path (compat); goldens de `apply_patch` com path extraível MUST assert `extract_paths()` (não só deny, para não colapsar com G4/G5 empty-path). Lista vazia → deny empty-path (G4/G5), não allow.

4. **`write`/`edit`/`apply_patch` sem path extraível = deny, não allow.**  
   Hoje `extract_path` vazio cai no early-return allow (ok para tool desconhecida). Para tools canônicas OpenCode de write isso é furo P0. Alternativa rejeitada: leave missing-path allow and hope the plugin only fires on writes.

5. **Pele = `.opencode/plugin/` auto-load; dois módulos.**  
   - `.opencode/plugin/process-fsm-guard.js` — `tool.execute.before` → `decide()` → **throw** no deny.  
   - `.opencode/plugin/impeccable-hook.js` — `tool.execute.after` + `event` `session.idle` → mesmo `hook.mjs`; **nunca throw** (fail-open).  
   Função default export. Sem `opencode.json`. Não versionar `.opencode/plugins/`. Alternativa rejeitada: um único plugin (crash do detector poderia abortar o turno; Guard throw no caminho do detector). Alternativa rejeitada: `opencode.json` mínimo só para listar plugin.

6. **Throw, não JSON de permission.**  
   OpenCode 1.18.18 não honra `{permission, decision}` como Cursor/Grok. Deny = `throw new Error(reason)`. Allow = return void. `emit()` dual Cursor/Grok permanece para os outros clientes e para o plugin ler `permission`/`decision` antes do throw.

7. **Paging OpenCode = inject, não hop Grok.**  
   `page()` continua o compilador. Hook `experimental.chat.system.transform` faz `output.system.push` do mesmo texto que Cursor `additional_context`. Sem arquivo gitignored, sem MUST Read. Grok permanece arquivo gerado + `00-harness.md`. Alternativa rejeitada: copiar o hop Grok (o issue fecha inject).

8. **Stubs só para o que o 1.18.18 não descobre.**  
   Binário descobre `.opencode/skills/` e `.agents/skills/`, **não** `.cursor/skills/`. Gerar `.opencode/skills/<name>/SKILL.md` (corpo ≤8 linhas, MUST Read canônico) para cada skill em `.cursor/skills/`. Impeccable e `design-critic` já estão em `.agents/skills/` — não duplicar. Sem `/opsx-*` em `.opencode/command(s)/`; modelo usa tool `skill`. Alternativa rejeitada: commands `/opsx-*` “porque o Cursor tem”.

9. **Detector: pele traduz evento; um `hook.mjs`.**  
   Cursor já: `afterFileEdit`/`stop`. Este card: Grok `.grok/hooks/` `PostToolUse`+`Stop` (mapear para `hook_event_name` `PostToolUse`/`Stop` como `impeccable.sh`); OpenCode `tool.execute.after`+`session.idle` → o mesmo stdin contract. Fail-open, exit 0, não aborta. Não é o Guard. Não reabre #668. Double-fire Grok+Cursor-compat aceito (igual Guard #668).  
   OpenCode `tool.execute.after`: copiar `args.filePath` (e paths de `patchText` quando o tool for `apply_patch`) para `file_path` no stdin de `hook.mjs`, com `hook_event_name=PostToolUse`. OpenCode `session.idle` → `hook_event_name=Stop` (paridade Cursor `stop`). Sem `file_path` no after, o detector não vê a tela.

10. **Specs: dois → três; `openspec/config.yaml` é Apply.**  
    Deltas em `process-harness`, `cursor-harness`, `developer-tooling`, `process-fsm-guard`, `process-fsm-paging`. A frase “OpenCode is not an active harness” em `openspec/config.yaml` **não** se edita neste turno Design (task de Apply). Decision log: revoga unicidade #562; não revoga morte do lock machine; registra paridade do detector.

11. **Goldens no `pytest scripts/process-fsm`, sem GitHub.**  
    Fixtures abaixo. Plugin throw: teste de processo (plugin JS + `decide()` mock/stdin) no mesmo tree de testes, sem rede. Ensaio humano não bloqueia o merge do adapter; bloqueia Auto.

12. **Auto continua gated no ensaio.**  
    Cursor Auto permanece. Grok #668 4.5 pendente. OpenCode cooperativo até deny observado na sessão 1.18.18 com plugin carregado. `AGENTS.md` MUST NOT reivindicar Auto OpenCode/Grok.

### Golden cases (pytest `scripts/process-fsm`)

| # | Envelope | `q` / `q_git` | Esperado |
| --- | --- | --- | --- |
| G1 | `{tool:"edit", args:{filePath:"backend/app/tasks/discovery_tasks.py"}}` | develop | deny |
| G2 | `{tool:"write", args:{filePath:"frontend/src/x.tsx"}}` | develop | deny |
| G3 | `{tool:"apply_patch", args:{patchText:"*** Begin Patch\n*** Update File: backend/app/main.py\n*** End Patch"}}` | develop | deny **e** `extract_paths()==["backend/app/main.py"]` (não empty-path) |
| G4 | `{tool:"apply_patch", args:{patchText:""}}` | qualquer | deny (não allow; `extract_paths()` vazio) |
| G5 | `{tool:"apply_patch", args:{patchText:"*** Begin Patch\n*** End Patch"}}` | qualquer | deny (sem path extraível; `extract_paths()` vazio) |
| G6 | `{tool:"edit", args:{filePath:""}}` | qualquer | deny |
| G7 | `{tool:"bash", args:{command:"echo x \| tee backend/app/main.py"}}` | I1 falso | deny |
| G8 | `{tool:"bash", args:{command:"gh project item-edit --id X --field-id PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM --single-select-option-id bd47fbe8"}}` | qualquer | deny (`is_status_edit_command`; usar `process_event`) |
| G9 | `{tool:"edit", args:{filePath:"openspec/changes/card-720-opencode-three-adapters/design.md"}}` | Design + `card-720-*` | allow (não `write_produto`) |
| G10 | `{tool:"grep", args:{}}` | develop | allow (#611) |
| G11 | Cursor `Write` + Grok `write` + OpenCode `edit` no mesmo path/yaml | develop | o mesmo deny |
| G12 | fallback bash: `{tool:"edit", args:{filePath:"backend/…"}}` sem Python | develop | dual `permission`+`decision` deny |
| G13 | `page()` body usado pelo transform OpenCode | Todo | ≤20 linhas, stub yaml, sem `release-guard` |
| G14 | adapter detector OpenCode: `tool.execute.after` com `args.filePath` de UI → stdin `file_path` + `hook_event_name=PostToolUse`; `session.idle` → `hook_event_name=Stop`. Grok `PostToolUse`/`Stop` igual | UI file | `file_path` preenchido no after; idle é Stop; exit 0 |
| G15 | `AGENTS.md` | — | ≤40 linhas; três clientes; sem Auto OpenCode/Grok; sem T0–T17 |
| G16 | `.opencode/` | — | sem tabela T0–T17; sem `opsx-*`; sem `opencode.json`; stubs ≤8 linhas |
| G17 | `{tool:"apply_patch", args:{patchText:"*** Begin Patch\n*** Add File: openspec/changes/card-720-opencode-three-adapters/design.md\n*** End Patch"}}` (path **só** de `patchText`, sem `filePath`) | Design + `card-720-*` | allow **e** `extract_paths()==["openspec/changes/card-720-opencode-three-adapters/design.md"]` |
| G18 | `{tool:"apply_patch", args:{patchText:"*** Begin Patch\n*** Update File: docs/note.md\n*** Move to: backend/app/moved.py\n*** End Patch"}}` | develop | deny **e** `extract_paths()` contém `backend/app/moved.py` (marcador live `*** Move to:`; se o parse ignorasse o dest, `docs/note.md` seria other → allow) |

## Apply contract

- Editar só harness/processo: `scripts/process-fsm/` (`normalize`, `extract_path`, goldens, gerador de stubs OpenCode se extraído), `.opencode/plugin/*.js`, `.opencode/skills/*` stubs, `.grok/hooks/` (só `PostToolUse`/`Stop` Impeccable; **não** relitigar Guard/paging Grok), `AGENTS.md` (≤40, três clientes, sem Auto OpenCode/Grok), `docs/decision-log.md` (revoga unicidade #562; lock machine continua morto; detector nos três), specs main via archive/apply, e `openspec/config.yaml` (tirar “OpenCode is not an active harness”).
- Zero `frontend/src/` e zero produto `backend/`. Zero restauro de lock machine. Zero `opencode.json`. Zero `.opencode/command(s)/opsx-*`. Zero T0–T17 em `.opencode/`.
- Plugin Guard: `tool.execute.before` → serializa `{tool, args}` → `guard.py`/`decide()` → throw no deny. Plugin detector: `tool.execute.after` + `session.idle` → `hook.mjs`; catch-all, nunca throw.
- Paging: `experimental.chat.system.transform` injeta `page().additional_context`. Não gitignore + MUST Read.
- Detector Grok: registrar `PostToolUse`+`Stop` no JSON aninhado `.grok/hooks/`, timeout folgado, mapear stdin como `.cursor/hooks/impeccable.sh`.
- Pytest: G1–G18 acima; sem GitHub nos unitários. G3/G17/G18 MUST assert `extract_paths()` (parse de `patchText`, inclusive `*** Move to:`). G4/G5 continuam deny empty-path.
- Homologação (não bloqueia apply; bloqueia Auto): plugin carregado em `.opencode/plugin/`; `write`/`edit`/`apply_patch`/`bash` ilegal em `backend/` ou `frontend/src/` com `q_git=develop` → throw/deny na sessão 1.18.18; editar UI nos três clientes dispara `hook.mjs` sem abortar o turno.

## Risks / Trade-offs

- [Plugin não carregado = write passa] → residual, igual Grok sem `/hooks-trust`. Homologação registra que o plugin carregou em `.opencode/plugin/`. Guard live não substitui o load.
- [Tool OpenCode nova fora da lista canônica → allow] → classe #611. Golden G10. Upgrade de API = card filho.
- [#5894 `tool.execute.before` pode não disparar em subagent `task`] → aberto em 1.0.182; **não live-testado neste turno Design** (sem sessão TUI/subagent). Residual explícito: ensaio P0 é na sessão principal; detector `after`/`idle` tem o mesmo limite. Se persistir no 1.18.18, documentar no closeout; não upgrade neste card.
- [Ensaio Auto Grok #668 4.5 pendente] → este card não herda Auto do Cursor; OpenCode cooperativo até o próprio ensaio.
- [Grok + compat Cursor dispara o detector duas vezes] → `hook.mjs` informativo e fail-open; double-fire aceito (igual Guard #668). Não desligar compat no home.
- [Detector fail-open] → crash de `hook.mjs` não aborta o turno (já é contrato Cursor). Módulos separados para Guard throw vs detector swallow.
- [`*** Move to:` vs “Move File” do issue] → goldens usam o marcador live; parsear `Move File` extra é barato e não reabre a decisão.
- [Inject `system[]` vs merge no bloco 0] → 1.18.18 junta partes extras depois do header; `push` da página Moore (≤20 linhas) é o contrato. Se um backend recusar multi-system, residual — alvo é o binário local, não vLLM.
- [AGENTS.md > 40 linhas] → teste de orçamento já existe; três nomes de cliente cabem em um bullet.

## Migration Plan

Aditivo. Ordem de apply: (1) `normalize`/`extract_path`/`extract_paths` + goldens G1–G12 e G17–G18 no núcleo; (2) fallback bash parseia `{tool, args}`; (3) `.opencode/plugin/process-fsm-guard.js` throw; (4) paging `experimental.chat.system.transform`; (5) stubs `.opencode/skills/` + zero `opsx-*`; (6) detector Grok hooks + plugin impeccable (G14: `filePath`→`file_path`, `session.idle`→`Stop`); (7) `AGENTS.md` + decision-log + `openspec/config.yaml` + specs main. Rollback = reverter o diff; Cursor/Grok #668 permanece. Sem migration de banco. Sem rebuild de frontend. Homologação = ensaio deny OpenCode + detector nos três, não `./restart` de produto.

## Open Questions

Nenhuma bloqueante de escopo (grelha vazia). Residual #5894 e “plugin carregou” ficam no ensaio humano, não no apply.

Não verificado live neste turno (não BLOCKED de Design): fire de `tool.execute.before` em subagent `task` no 1.18.18; throw abortando a tool numa sessão TUI real (docs + binário confirmam o hook e o padrão throw; ensaio confirma o caminho feliz).

## UI impact

**none** — harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite visível é deny/throw de ferramenta, inject da página Moore, e `hook.mjs` fail-open nos três clientes.

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O **detector** Impeccable como pele de harness (Grok + OpenCode → `hook.mjs`) está no escopo deste card; não é o pipeline Impeccable desta coluna.

## Design Critique

- P0: nenhum (A, B, A2, B2).
- P1 (B, aberto → patch → fechado): goldens G3–G5 de `apply_patch` eram só deny e colapsavam com empty-path; não provavam parse de `patchText` / `*** Move to:`. Disposition: **closed**. G3 agora exige `extract_paths()==["backend/app/main.py"]`; G17 allow Design+`card-*` só de `patchText`; G18 `*** Move to:` dest + develop deny.
- P2 (accepted-residual): #5894 subagent `task`; plugin não carregado = write passa; G12 fallback sh fora do plugin live; tool nova → allow (#611); stubs OpenCode sem gerador CI; Grok+compat double-fire do detector.
- P3 (accepted-residual): heading OpenSpec “two adapters”; `proposal.md` sem G17–G18; sem golden `*** Delete File:`; paging testa `page()` não `system[]`.

Prototype: N/A — harness/hooks/docs; nenhuma tela de produto.

Snapshot (git-tracked; Gist não envia esta pasta):
- `.impeccable/critique/720-card-720-opencode-three-adapters-20260827T202144Z-A2.md`
- `.impeccable/critique/720-card-720-opencode-three-adapters-20260827T202059Z-B2.md`
- (onda 1) `…T201003Z-A.md`, `…T200852Z-B.md`

Design Agent verdict: PASS
