# Snapshot — Assessment A · card #798 `card-798-overlay-doc-covenant-flow`

- Card: #798 — overlay_doc / `rules.md` / cinzentos ainda mandam `alan-workflow` (path morto)
- Change: `openspec/changes/card-798-overlay-doc-covenant-flow/`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- UTC: 2026-08-29T20:26:40Z
- Digest `design.md`: sha256 `efa41abe91802cd1cc270567f72b892ab4f828e82692e0e4dc0e6f5463348899` · 1020 palavras · 8737 bytes
- `openspec validate card-798-overlay-doc-covenant-flow --type change --strict`: **valid**
- UI impact: **none** (só Markdown de carga; zero rota/shell/componente/HTML)
- Prototype: **N/A** — aceite = retarget nos 4 docs; sem `frontend/public/prototypes/*798*`
- `## Design Critique` no `design.md`: ausente (autor correto)

## Rubrica (UI none)

- **Q1=B** → D1 + proposal + spec `consumer-load-docs` + tasks 1–3: os 4 (`docs/crypto-overlay.md`, `rules.md`, `docs/backlog-operating-model.md`, banner `docs/analytics/funil-social-site-leads-plan.md`). Sem varrer palestra/histórico.
- **Q2=A** → D2 + D5 + Apply contract: path `.cursor/skills/alan-workflow*` **e** verbos de carga. Live T0 bate: overlay 19 linhas / 24 ocorrências; `rules.md` 8/9; backlog 1; banner 1.
- **Q3=A** → D3 + Non-Goals: só consumidor; pin `v1.1.4` live; sem card no produto; `--pin` não toca `overlay_doc`.
- **Q4=A** → D4 + spec `rg` vazio + zero formerly/avoid nos 4. AND «formerly» de #773 em `openspec/specs/covenant-flow/spec.md` **permanece** (não MODIFIED).
- **Regressão:** MUST NOT yaml / `AGENTS.md` / `harness.mdc` / peles / `openspec/specs/**` main / produto. Tasks 1.3 / 4.2 / 4.3. Não reabre #773/#554/#786/#784; não absorve #780.
- **Ops:** helper vivo `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`; pasta `alan-workflow*` ausente; banner DEV por omissão / PROD só com pedido explícito (D6 + spec req 2 + task 3.2). Gate: `rg -n 'alan-workflow'` nos 4 = vazio.
- **UI:** nenhuma superfície visual nova/alterada sem classificação — `none` justificado. Sem HTML. Sem Playwright. Sem rewrite `DESIGN.md`.
- **Apply contract:** 4 ficheiros exactos + mapa D5 + helper + `rg` vazio + rollback = reverter os 4. Executável após Pronto para Dev.
- **Spec observável:** cenário `rg over the four live load docs is empty`.

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Mapa D5 lista o token curto `.cursor/skills/alan-workflow` **antes** de `alan-workflow-ambientes`. Substituição sequencial top-down produz `covenant-flow-ambientes` (path ainda morto; banner falharia o aceite). Alvos D5 estão certos; Apply MUST longest-first (`alan-workflow-ambientes` → `covenant-flow-environments` **antes** de `alan-workflow` → `covenant-flow`). Disposition: **accepted-residual**.
- P2: SHALL do req 1 junta `covenant-flow` **e** `covenant-flow-environments` nos 4; o issue no backlog é só Visual QA → `covenant-flow`. Apply MUST NOT inventar ambientes nessa frase. Recorte = cenário Visual QA + D1. Disposition: **accepted-residual**.
- P2: «19 hits» = linhas `rg -c`, não ocorrências (overlay 24; `rules.md` 9). Parar em 19 edits deixa token. Gate = `rg` vazio (Q4), não a contagem T0. Disposition: **accepted-residual**.
- P2: Alinhar texto não impede `cat` overlay fora de portas/Drive/banco/release (sycophancy). Issue já fecha como fora. Disposition: **accepted-residual**.
- P3: Task 4.4 `openspec validate --change …` — CLI medida: `openspec validate card-798-overlay-doc-covenant-flow --type change --strict`. Disposition: **accepted-residual**.
- P3: Palestra/`docs/release-*` ainda têm o token (Q1=B / histórico). Disposition: **accepted-residual**.
- P3: `rules.md` vs stub `AGENTS.md` (papel) não redefinido. Disposition: **accepted-residual**.
- Dual-write yaml/`AGENTS.md`/formerly de pin / reabrir #773 / HTML / superfície visual sem classificar: **false**.

## Disposition

Zero P0/P1. Recorte Q1=B Q2=A Q3=A Q4=A congelado; Non-Goals não alargados. Apply contract executável; spec `rg` vazio observável; banner DEV/PROD e helper pinado cobertos. Residuais P2/P3 são ordem de substituição, SHALL agregador vs cenário backlog, e histórico de propósito — não bloqueiam.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; quatro Markdowns de carga; nenhuma tela CriptoFarol.
