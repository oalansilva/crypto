## Context

Card [#795](https://github.com/oalansilva/crypto/issues/795). Q1–Q4 da grelha estão fechadas no issue (todas A); este Design não as reabre. Relacionado e **não** reaberto como Apply: #787 (Homologado, README PT-BR), #784/#782 (peles). Guard / T0–T17 / `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.

Factos live (worktree + produto `oalansilva/covenant-flow` tag **`v1.1.4`**):

- Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.4`; `clients.cursor.auto: true`; grok/opencode/dsh `false`.
- `render_agents()` em `scripts/process-fsm/overlay.py` hardcode: `Clientes: Cursor Agent (Auto permitido); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).` e `Não reivindique modo Auto no Grok, no OpenCode nem no dsh.` Não lê `clients.*.auto`.
- `AGENTS.md` do consumidor coincide com esse hardcode.
- `validate_overlay` exige as três `CLIENT_KEYS` e aceita extra `dsh`; **não** lê o boolean `auto`.
- `empty_template` já emite `clients.*.auto: false` para as três chaves.
- README produto (GitHub `main` / `v1.1.4`) bloco **Clientes**: Auto = só Cursor `clients.cursor.auto: true`; cooperativo = os outros três até ensaio deny.
- Spec main `covenant-flow` herda esse bloco de #787. Spec main `process-harness` Always-on ainda SHALL «Cursor Auto is allowed» (delta #782, quatro nomes, ainda não arquivado, também afirma Cursor Auto).
- `test_agents_md_is_stub` exige quatro nomes e proíbe Auto Grok/OpenCode/dsh; **não** exige «Auto permitido». `test_harness_mdc_body_budget` já proíbe «Auto permitido» no `harness.mdc` (não no stub). Pin-tests cravam `v1.1.4`.

Visitante do produto = quem abre o GitHub sem já saber o processo. Operador = skill `covenant-flow` (inalterada neste card).

**UI impact: none.** Claim Auto no overlay + texto hardcoded do stub/README do produto de processo. Nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol.

## Goals / Non-Goals

**Goals:**

- Overlay Cripto: `clients.cursor.auto: false` (os outros `false`).
- `render_agents()` hardcode quatro cooperativos; stub **nunca** diz «Auto permitido»; yaml **não** interpola o texto.
- `implantar --pin` da tag patch deste card regenera `AGENTS.md` a partir do novo hardcode.
- README produto: bloco do estranho no mesmo tag/pin; quatro nomes; não afirma que Auto é Cursor `clients.cursor.auto: true`; Auto não autoriza cruzar colunas; MUST NOT reivindicar Auto em Grok/OpenCode/dsh.
- Specs MODIFIED: `covenant-flow` e `process-harness`.
- Cláusula «até ensaio deny» só em Grok, OpenCode e dsh.

**Non-Goals:**

- Pular colunas; chat/NLU como δ; `implemente` como autorização.
- Herdar Auto para Grok, OpenCode ou dsh sem ensaio deny PASS (#782/#784).
- «Todos Auto»; interpolar `clients.*.auto` no stub (Q2 ≠ B).
- Reabrir #787 como Apply; reescrita geral do README; código de app do Cripto (`backend/**`, `frontend/src/**`).
- Alterar Guard, tabela T0–T17, `CLIENT_KEYS`, `SCHEMA_MAJOR`.
- Tocar config local da IDE/CLI Cursor (`approvalMode` / Run Everything) — Q3=A.
- Hand-edit do stub no Cripto sem mudar o produto (o próximo pin desfaz).
- Tocar `docs/crypto-overlay.md`. HTML, Impeccable visual, Playwright, rewrite de `DESIGN.md`.

## Decisions

1. **Q1=A — contrato yaml+stub cooperativo.**  
   Overlay Cripto grava `clients.cursor.auto: false` como claim de máquina. Stub deixa de reivindicar Auto no Cursor. Alternativa rejeitada: só yaml ou só stub (Q1 ≠ B/C). `clients.*.auto` fica vestigial para stub e Guard (aceite em Q2=A); o overlay mesmo assim grava `false`.

2. **Q2=A — hardcode em `render_agents`; yaml não conduz o stub.**  
   `render_agents()` **não** interpola `clients.*.auto`. `validate_overlay` continua a não ler o boolean. Alternativa rejeitada: interpolar o yaml no stub (Q2 ≠ B) — faria o texto depender do overlay e reabriria «Auto permitido» se alguém pusesse `true`.

3. **Q3=A — Auto IDE/CLI fora de escopo.**  
   `approvalMode` / Run Everything na UI ou na config local do CLI **não** entram. Este card não edita `~/.cursor/`, `cli-config.json`, nem settings da IDE. Claim Auto ≠ toggle do produto Cursor.

4. **Q4=A — README bloco do estranho neste card / mesmo pin.**  
   Só a secção **Clientes** (e o exemplo `--pin` da tag). Sem reescrita geral. Sem reabrir #787 como Apply. Description GitHub, walkthrough das 12 colunas e frase dos 3 gates permanecem os de #787.

5. **Frase exacta PT-BR do stub (fecha residual da grelha).**  
   Apply MUST emitir estas duas linhas, nesta ordem, sem interpolar overlay:

   `Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).`

   `Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.`

   Delta vs live `v1.1.4`: `(Auto permitido)` → `(cooperativo)`; a segunda linha passa a nomear também o Cursor. A cláusula «até ensaio deny» permanece só nos três. Cursor é cooperativo por contrato, não por ensaio pendente. Stub ≤ 40 linhas não vazias. Alternativa rejeitada: uma linha «os quatro cooperativos até ensaio deny» (aplicaria o ensaio ao Cursor). Alternativa rejeitada: omitir a segunda linha (o aceite exige MUST NOT reivindicar Auto nos quatro).

6. **Frase exacta PT-BR do bloco README Clientes (fecha residual da grelha).**  
   Apply MUST substituir o bloco live **Clientes** por:

   Título: `Quatro clientes, por nome: **Cursor**, **Grok**, **OpenCode** e **dsh**. Os quatro são cooperativos.`

   - `**Cooperativo** — Cursor por contrato; Grok, OpenCode e dsh até ensaio deny PASS na branch de integração. Overlay \`clients.*.auto\` é claim de máquina e **não** conduz o stub \`AGENTS.md\`.`
   - `**Auto** — **não** autoriza cruzar colunas: o agente não arrasta o card. MUST NOT reivindicar Auto em Grok, OpenCode ou dsh.`

   O texto MUST NOT afirmar que Auto é Cursor `clients.cursor.auto: true`. MUST NOT mencionar `approvalMode` / Run Everything (Q3). Resto do README (O que é, 12 colunas, Install, Pin, Layout) inalterado salvo o exemplo `--pin`.

7. **Tag patch `v1.1.5`.**  
   Origin live = `v1.1.4`. Sem tag intermédia à data deste Design. Apply MUST confirmar `gh api repos/oalansilva/covenant-flow/tags` antes de taggar; se existir tag mais nova, bump patch seguinte (não major). `SCHEMA_MAJOR` 1; `CLIENT_KEYS` três. Pin-tests que cravam `v1.1.4` sobem para a tag deste card. Alternativa rejeitada: major `v2.0.0` (schema inalterado). Alternativa rejeitada: só `main` sem tag (quebra o exemplo `--pin` e o pin Cripto).

8. **Ordem produto → pin Cripto.**  
   Commit no `oalansilva/covenant-flow` (`render_agents` + README + goldens) + tag → `implantar --pin` no worktree Cripto. Overlay `pin:` = essa tag; `clients.cursor.auto: false`. `AGENTS.md` regenerado pelo pin, não hand-edit. #787 não reabre como Apply.

## Apply contract

Ordem (produto primeiro; zero UI Cripto):

1. Em `oalansilva/covenant-flow` `scripts/process-fsm/overlay.py`: `render_agents()` emite as duas linhas da D5; MUST NOT interpolar `clients.*.auto`; MUST NOT conter «Auto permitido»; `SCHEMA_MAJOR` 1; `CLIENT_KEYS` três; `validate_overlay` inalterado quanto ao boolean `auto`.
2. README produto: só bloco **Clientes** = D6; exemplo `--pin` = tag deste card (D7). Sem segundo ficheiro. Sem tabela T0–T17. Sem rewrite geral. Sem `docs/crypto-overlay.md`. Sem `gh repo edit` da description (#787).
3. Goldens: `test_agents_md_is_stub` (e/ou teste de `render_agents`) afirma as duas linhas D5, quatro nomes, ausência de «Auto permitido», ausência de Auto Grok/OpenCode/dsh; pin-tests esperam a tag deste card. Fixture `clients.cursor.auto: true` MAY permanecer — prova que o yaml não conduz o stub.
4. Commit + tag patch no produto (esperado **`v1.1.5`**; Apply confirma origin).
5. No worktree Cripto deste card: gravar `clients.cursor.auto: false`; `implantar --pin` da tag; `AGENTS.md` coincide com o `render_agents()` novo. MUST NOT hand-edit o stub. MUST NOT editar `backend/**` nem `frontend/src/**`. MUST NOT alterar Guard, T0–T17, config local IDE/CLI. MUST NOT reabrir #787 como Apply.

Rollback = pin Cripto `v1.1.4` + tag produto `v1.1.4` (stub «Auto permitido» + README Auto=Cursor). Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [`clients.*.auto` vestigial para stub e Guard] → aceite em Q2=A. Overlay Cripto mesmo assim grava `false`. Residual: um leitor do yaml pode achar que `true` ligaria Auto no stub — o hardcode impede. Mitigação: README D6 diz que o yaml não conduz o stub.
- [Tag `v1.1.5` ocupada entre Design e Apply] → Apply confirma tags origin e bump patch seguinte; nunca major.
- [#787 Homologado, spec main ainda diz Auto=Cursor `true`] → este card MODIFIED essa requirement; não reabre #787 como Apply.
- [`test_agents_md_is_stub` hoje passa com «Auto permitido»] → Apply acrescenta o assert de ausência; sem isso o hardcode cooperativo não tem rede.
- [Hand-edit do stub no Cripto] → o próximo pin desfaz. Apply MUST regenerar via `implantar --pin`.
- [Auto IDE/CLI residual no host] → Q3=A; fora deste card. Claim ≠ toggle. Não misturar vocabulário.

## Migration Plan

Aditivo de claim/texto sobre `v1.1.4`. Sem schema overlay. Sem canal novo. Ordem = Apply contract. Consumidor Cripto recebe o stub novo no pin; o README novo vive no GitHub do produto ( `--pin` não copia README). Rollback = pin `v1.1.4`.

## Open Questions

Nenhuma bloqueante. Q1–Q4 congeladas. Residuais da grelha fechados aqui: frases D5/D6; tag esperada `v1.1.5` (Apply confirma).

## UI impact

**none** — overlay `clients.cursor.auto` + texto hardcoded de `render_agents()` / `AGENTS.md` / bloco README do produto `oalansilva/covenant-flow`. Nenhuma rota, shell, componente ou copy de ecrã do CriptoFarol. Nenhuma superfície visual nova ou alterada. O aceite visível é texto de processo, não uma tela.

## Prototype

N/A — `UI impact: none`. Não há tela CriptoFarol a prototipar; o aceite é stub + overlay + README do núcleo. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 accepted-residual:** spec EN vs D5/D6 PT-BR (Apply usa D5/D6). Golden de interpolação MAY — Apply MUST ter fixture `clients.cursor.auto: true` ou promover 3.2 a MUST. `--pin` copia worktree SOURCE; taggar só overlay.py / README / goldens. Leftover #782 Always-on SHALL «Cursor Auto is allowed» — archive depois deste card. `clients.*.auto` vestigial (Q2=A). Push `main`+tag e skill `implantar` ainda em `v1.1.4`.
- **P3 accepted-residual:** D6 Auto só proíbe os três (título+D5 cobrem Cursor). Golden actual passa com «Auto permitido». Main `process-harness` ainda 3 clientes até archive. Overlay Cripto-específico no spec portátil.
- **Prototype:** N/A — `UI impact: none`; aceite = stub + overlay + README do núcleo; sem HTML.
- **Snapshot Impeccable:** `.impeccable/critique/795-card-795-quatro-clientes-cooperativos-A.md` e `…-B.md` (r1). Apply/Code Review não lêem. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS** — zero P0/P1; A e B isolados; sem superfície visual por classificar; browser N/A justificado.
