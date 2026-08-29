## Context

Card [#798](https://github.com/oalansilva/crypto/issues/798). O briefing é o issue (DoD grelhado). Q1–Q4 fechadas; este Design não as reabre e não inventa Qs novas. Relacionado e **não** reaberto: #773 (Pronto), #786/#784 (Done), #554 (Pronto). Não absorver #780.

Consumidor `oalansilva/crypto`, overlay `pin: v1.1.4`, `overlay_doc: docs/crypto-overlay.md`. `--pin` copia núcleo/peles e regenera `AGENTS.md`; **não** toca o Markdown `overlay_doc`. Stub `AGENTS.md`, `harness.mdc` e catálogo dsh já dizem `covenant-flow`. Pasta `.cursor/skills/alan-workflow*` ausente neste git. Helper vivo: `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`.

Hits pré-Apply do token `alan-workflow` (issue T0): `docs/crypto-overlay.md` 19; `rules.md` 8; `docs/backlog-operating-model.md` 1; `docs/analytics/funil-social-site-leads-plan.md` 1. Facto da grelha: sessão dsh `Read` overlay → path `.cursor/skills/alan-workflow/SKILL.md` → `FsError` / `FS_NOT_FOUND`.

**UI impact: none.** Só Markdown de carga no consumidor. Sem rota, shell, componente, token, HTML, Playwright, pipeline Impeccable, `DESIGN.md` de produto.

## Goals / Non-Goals

**Goals (Entra):**

- Os quatro docs vivos de carga deste consumidor apontam só `covenant-flow` / `covenant-flow-environments`.
- Profundidade Q2=A: **toda instrução de carga** — path sob `.cursor/skills/alan-workflow*` **ou** verbo `siga`/`seguir`/`carregue`/`use`/`aplique` + `alan-workflow*` — passa a `covenant-flow` / `covenant-flow-environments`.
- Helper → `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`.
- Zero token `alan-workflow` nos 4; zero notas formerly/avoid (Q4=A).
- Banner do funil: nomes novos; aviso DEV por omissão / PROD só com pedido explícito permanece.
- Evidência: `rg -n 'alan-workflow'` nos 4 devolve vazio; pasta `.cursor/skills/alan-workflow*` continua ausente.

**Non-Goals (Não entra):**

- Recriar alias/stub `alan-workflow*` no git do consumidor.
- Renomear host `~/.cursor/skills/alan-workflow*`.
- Card, teste ou regressão no núcleo `oalansilva/covenant-flow`.
- Editar `.covenant-flow/overlay.yaml`, `AGENTS.md`, `.cursor/rules/harness.mdc`, peles `.dsh` `.grok` `.opencode`.
- Relançar dsh, mudar plugin ou forçar a tool `skill`.
- Reescrever histórico (`docs/release-*`, `docs/decision-log.md`, palestra, `.impeccable/critique/**`, `openspec/changes/archive/**`).
- Reescrever `openspec/specs/**` main («formerly» / AND de pin #773).
- Redefinir o papel de `rules.md` vs stub `AGENTS.md`.
- Apagar o banner do funil.
- Nota formerly/avoid em qualquer dos 4.
- Código `backend/` `frontend/src/`.
- Reabrir #773 / #554 / #786 / #784. Absorver #780.

## Decisions

1. **Q1 = B — overlay_doc + `rules.md` + dois cinzentos.**  
   Superfície: `docs/crypto-overlay.md`, `rules.md`, `docs/backlog-operating-model.md`, banner em `docs/analytics/funil-social-site-leads-plan.md`. Alternativa rejeitada: só overlay_doc (deixa `rules.md` e cinzentos a mandar o path morto). Alternativa rejeitada: varrer histórico/archive.

2. **Q2 = A — toda instrução de carga.**  
   Path **e** verbo de seguir/usar. Apply MUST substituir também «seguir `alan-workflow`», «Siga `alan-workflow`», «aplique `alan-workflow`», «Use `alan-workflow` + `alan-workflow-ambientes`», «inventario/classificacao de `alan-workflow`», não só linhas com `.cursor/skills/alan-workflow/`. Alternativa rejeitada: só paths de `SKILL.md`.

3. **Q3 = A — só consumidor; sem card no produto.**  
   Pin `v1.1.4`/HEAD do núcleo já sem o token; `--pin` não sobrescreve `overlay_doc`. Alternativa rejeitada: card em `oalansilva/covenant-flow` ou bump de pin como «fix» deste furo.

4. **Q4 = A — zero notas; os 4 sem o token `alan-workflow`.**  
   Sem «formerly», sem `_Avoid:` nos 4. AND «formerly» das specs main de pin (#773) **permanece** — este card não as apaga. Alternativa rejeitada: deixar o token «só para história».

5. **Mapeamento canónico (Apply MUST usar estes alvos; MUST NOT inventar sinónimos).**

   | Origem | Destino |
   | --- | --- |
   | `.cursor/skills/alan-workflow/` | `.cursor/skills/covenant-flow/` |
   | `.cursor/skills/alan-workflow` | `.cursor/skills/covenant-flow` |
   | `.cursor/skills/alan-workflow-ambientes/` | `.cursor/skills/covenant-flow-environments/` |
   | `alan-workflow-ambientes` | `covenant-flow-environments` |
   | skill / verbo + `alan-workflow` | `covenant-flow` |
   | `.cursor/skills/alan-workflow/scripts/publish-openspec-card-artifacts.sh` | `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh` |

   Runbook: `.cursor/skills/covenant-flow/SKILL.md`. Ambientes: `.cursor/skills/covenant-flow-environments/SKILL.md`.

6. **Banner do funil: retarget, não apagar.**  
   Após Apply o banner MUST dizer para usar `covenant-flow` + `covenant-flow-environments`. Ambiente padrão **DEV**. Não alterar PROD sem pedido explícito do Alan. MUST NOT remover o bloco.

7. **Spec de change, não rewrite de `covenant-flow` main.**  
   Capability nova `consumer-load-docs` cobre overlay_doc/`rules.md`/cinzentos. MUST NOT MODIFIED/REMOVED das requirements de pin em `openspec/specs/covenant-flow` (incluindo AND «formerly»).

8. **`overlay.yaml` não é `overlay_doc`.**  
   Máquina já tem nomes novos e `pin: v1.1.4`. Apply MUST NOT editar `.covenant-flow/overlay.yaml`.

## Apply contract

Ficheiros exactos (e só estes) neste worktree, após `Status=Pronto para Dev`:

1. `docs/crypto-overlay.md` — todas as instruções de carga (19 hits hoje): paths, «seguir/siga/carregue», helper, TL;DR skills, release `alan-workflow` + `alan-workflow-ambientes`, Visual QA no fim do overlay. Profundidade D2.
2. `rules.md` — as 8 hits: path `.cursor/skills/alan-workflow/`, «Siga/aplique/execute/seguem `alan-workflow*`».
3. `docs/backlog-operating-model.md` — Visual QA aponta `covenant-flow` (não o path morto).
4. `docs/analytics/funil-social-site-leads-plan.md` — só nomes de skill no banner; aviso DEV/PROD intacto (D6).

Helper canónico: `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`.

Profundidade: Q2=A (D2). Zero notas formerly/avoid (D4).

Evidência MUST: `rg -n 'alan-workflow' docs/crypto-overlay.md rules.md docs/backlog-operating-model.md docs/analytics/funil-social-site-leads-plan.md` devolve **vazio**. Pasta `.cursor/skills/alan-workflow*` continua ausente (MUST NOT recriá-la).

MUST NOT: `backend/**`, `frontend/src/**`, `frontend/public/prototypes/**`, `.covenant-flow/overlay.yaml`, `AGENTS.md`, `.cursor/rules/harness.mdc`, peles, produto `oalansilva/covenant-flow`, `openspec/specs/**` main, histórico listado em Non-Goals, HTML de protótipo.

Rollback = reverter os 4 Markdowns. Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [Alinhar o texto tira o path morto; não impede `cat` overlay fora de portas/Drive/banco/release (sycophancy)] → residual do issue; fora deste card. Mitigação deste card: quando o agente *seguir* os 4, o path existe.
- [Substituição parcial deixa token residual e `rg` falha] → Apply varre os 4 com `rg` até vazio; Q2=A cobre verbo+nome, não só path.
- [Nota formerly reintroduz o token] → Q4=A; Apply MUST NOT escrever formerly/avoid nos 4. Specs main de #773 ficam com AND «formerly».
- [`rules.md` vs stub `AGENTS.md`] → Não entra redefinir papéis. Só retarget de carga. Residual: `rules.md` continua a apontar `AGENTS.md` como manual operacional (já é o contrato actual).

## Migration Plan

Aditivo de docs no consumidor. Sem schema overlay. Sem bump de pin. Ordem = Apply contract. Sem canal novo. Histórico (`docs/release-*` etc.) permanece com o token antigo de propósito.

## Open Questions

Nenhuma. Q1=B, Q2=A, Q3=A, Q4=A congeladas. Fronteira vazia.

## UI impact

**none** — só Markdown de carga no consumidor (`overlay_doc`, `rules.md`, dois cinzentos). Nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`. Aceite é retarget de paths e verbos nos 4 Markdowns; não há tela CriptoFarol a prototipar. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 accepted-residual:** Apply MUST substituir `alan-workflow-ambientes` **antes** de `alan-workflow` (D5 row curto é prefixo; senão `covenant-flow-ambientes`). Gate = `rg` vazio, não a contagem T0 de linhas. SHALL agregador vs Visual QA no backlog: MUST NOT inventar ambientes nessa frase. Sycophancy (`cat` overlay fora de portas/Drive/banco/release) fora deste card.
- **P3 accepted-residual:** `openspec validate <change> --type change --strict` (não `--change`). Histórico/palestra ficam com o token (Q1=B). Papel `rules.md` vs stub `AGENTS.md` não redefinido.
- **Prototype:** N/A — `UI impact: none`; aceite = retarget nos 4 Markdowns; sem HTML.
- **Snapshot Impeccable:** `.impeccable/critique/798-card-798-overlay-doc-covenant-flow-A.md` e `…-B.md` (r1). Apply/Code Review não lêem. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS** — zero P0/P1; A e B isolados; sem superfície visual por classificar; browser N/A justificado.
