## Context

Card [#787](https://github.com/oalansilva/crypto/issues/787). Q1–Q8 da grelha estão fechadas no issue; este Design não as reabre. Relacionado e **não** reaberto: #773 (Pronto), #784 (Done), #608 (lei).

Produto: GitHub **privado** [`oalansilva/covenant-flow`](https://github.com/oalansilva/covenant-flow), branch `main`, tag live **`v1.1.1`**. Description actual (EN): `Covenant Flow — portable 12-column process (nucleus + adapters)`.

README live (`/srv/apps/dev/covenant-flow/README.md`, 37 linhas, inglês): título «portable process product»; **primeiro bloco útil = clone + `install.sh --init` / `--pin v1.1.1` + Layout**. Assume que o leitor já sabe o que o produto é. Não lista os quatro clientes nem Auto vs cooperativo. Não walkthrough das 12 colunas.

`--pin` **não** copia `README.md`: `install.sh` copia nucleus (`.cursor/process-fsm.yaml`, `scripts/process-fsm/`), adapters (`.cursor/` `.grok/` `.opencode/` `.dsh/`), `.agents/skills/` (impeccable, design-critic, playwright-cli), helpers e `AGENTS.md` gerado; não há `README.md` na lista de `copy_tree`. Overlay Cripto live: `pin: v1.1.1`. Spec main `covenant-flow` já tem o cenário «Product README does not require host backup paths» — este card **não** o altera.

Visitante = quem abre o GitHub sem já saber o processo (repo privado; convidado ou Alan daqui a meses). Skill `covenant-flow` continua o runbook do operador; o README não a substitui.

**UI impact: none.** Documentação do produto de processo no repo `oalansilva/covenant-flow`. Nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol. Sem HTML. Sem `DESIGN.md` de produto. Sem Playwright visual.

## Goals / Non-Goals

**Goals (Entra):**

- Um `README.md` PT-BR na raiz de `oalansilva/covenant-flow` (não no consumidor Cripto).
- Ordem: estranho primeiro, depois Install / Pin / Layout. Clone não é o primeiro parágrafo.
- Bloco do estranho: o que resolve; quem usa; núcleo vs consumidor vs overlay; canal v1 = copiar + commitar; primeiro consumidor = Cripto (`oalansilva/crypto`); Cursor, Grok, OpenCode e dsh por nome; Auto vs cooperativo (Auto ≠ autorização de coluna).
- Walkthrough das 12 colunas yaml (incluindo `Cancelado` terminal): uma linha por coluna + uma frase dos 3 gates humanos, sem IDs T0–T17.
- Description GitHub no mesmo entregável, exactamente: `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`.
- Secção operador em PT-BR. Exemplo `--pin` = tag deste entregável (`v1.1.2` após o bump).
- Consumidor Cripto só re-pin depois do bump de tag.

**Non-Goals (Não entra):**

- Segundo ficheiro (`CONTRIBUTING.md`, `docs/` de install).
- Nomes EN das colunas. Tabela T0–T17 / I1–I9. Parágrafo por coluna. Hooks, ordem OpenSpec, playbook de release no README.
- Reescrever skills, hooks, yaml, `install.sh`, `AGENTS.md` gerado, adapters.
- Copiar o README para o consumidor no `--pin`. Overlay no repo do produto.
- Reabrir #773/#784. Código de produto Cripto (`backend/**`, `frontend/src/**`).
- Canal v1 via submodule, gitignore-as-install, marketplace ou template-clone.
- LICENSE, homepage GitHub. `--pin latest` / placeholder sem número.

## Decisions

1. **Q1 = A — README em PT-BR.**  
   O visitante do GitHub (e Alan daqui a meses) lê português. Alternativa rejeitada: inglês (README actual) ou bilingue (segundo ficheiro / coluna EN).

2. **Q2 = C — walkthrough humano das 12 colunas, sem tabela T0–T17.**  
   Nomes PT-BR do yaml, uma linha cada. A lei T0–T17 / I1–I9 permanece no yaml e na skill; o README não dual-write eventos nem invariantes.

3. **Q3 = A — description GitHub no mesmo entregável.**  
   Frase congelada, alinhada à linguagem do README. Alternativa rejeitada: description EN residual, ou description noutro card.

4. **Q4 = A — um README; estranho primeiro; clone não é o primeiro parágrafo.**  
   Sem `CONTRIBUTING.md` nem `docs/` de install. Ordem das secções (contrato do Apply):

   1. Título + uma linha alinhada à description: *Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)*.
   2. **O que é** — problema (processo de 12 colunas que viaja com o git do consumidor; sem o produto, cada repo reimplementa e diverge); quem usa (Alan + agentes nos quatro clientes); núcleo vs consumidor vs overlay; canal v1 = copiar peles e **commitar**; primeiro consumidor = Cripto (`oalansilva/crypto`). Repo do produto **não** tem overlay.
   3. **Clientes** — Cursor, Grok, OpenCode, dsh por nome; Auto vs cooperativo (ver D6).
   4. **As 12 colunas** — lista (D5) + uma frase de gates; uma linha a apontar a skill `covenant-flow` como runbook (sem despejar hooks/OpenSpec/release).
   5. **Install** — clone + `--init` em PT-BR (`--init` escreve chaves vazias e não chuta valores).
   6. **Pin** — `--pin` + semver; exemplo = tag deste entregável.
   7. **Layout** — nucleus, adapters, overlay no consumidor, skills (lista curta como hoje, em PT-BR).

5. **Q5 = A — uma linha por coluna + uma frase dos 3 gates; skill continua o runbook.**  
   Texto canónico do walkthrough (Apply MUST usar estes significados; MUST NOT expandir a parágrafo nem inserir IDs T*):

   - Em Refinamento — entrada do card e afiação da história; Alan escolhe, prioriza ou cancela.
   - Todo — backlog com história afiada; não é código; a próxima coluna é Design.
   - Design — síntese OpenSpec do issue grelhado e crítica; Gist no card; protótipo se houver UI.
   - Aprovação de Design — espera decisão de Alan sobre o design.
   - Pronto para Dev — design aprovado; único status que libera `/opsx:apply`.
   - Em desenvolvimento — implementação no worktree do card.
   - Code Review — diff pronto; review antes do commit.
   - QA — SHA revisado nos checks.
   - Done — done técnico em `develop`.
   - Homologado — Alan aprovou em `develop`.
   - Pronto — publicado em `main` e deploy PROD validado.
   - Cancelado — não será feito (coluna terminal).

   Frase dos 3 gates (exactamente uma, sem IDs T*): *Alan prioriza Em Refinamento→Todo; só Alan Aprovação de Design→Pronto para Dev; Alan homologa Done→Homologado.*

6. **Q6 = B — quatro clientes no bloco do estranho; Auto ≠ autorização de coluna.**  
   Vocabulário congelado: **Auto** = Cursor `clients.cursor.auto: true`; o cliente pode correr sem prompt de permissão de ferramenta; **não** autoriza cruzar colunas (o agente não arrasta). **Cooperativo** = Grok, OpenCode e dsh (`clients.*.auto: false`) até ensaio deny PASS na branch de integração. MUST NOT reivindicar Auto nesses três.

7. **Q7 = A — exemplo `--pin` = tag deste entregável.**  
   Live hoje: `v1.1.1`. Este card **bumps** o produto para patch **`v1.1.2`** no commit do README; o exemplo no README passa a `v1.1.2`. Apply de uma tag nova futura actualiza o exemplo outra vez. MUST NOT escrever `latest` nem placeholder sem número.

8. **Q8 = A — description exacta.**  
   `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`  
   Apply: `gh repo edit oalansilva/covenant-flow --description` com essa string. Sem homepage, sem LICENSE.

9. **Tag patch `v1.1.2` + re-pin Cripto, apesar de o README não viajar no pin.**  
   Evidência: `install.sh --pin` não lista `README.md` (só nucleus, adapters, `.agents/skills/`, helpers, `AGENTS.md` gerado). O runtime Cripto **não** precisa do README pinado para o Guard/hooks.  
   Mesmo assim o issue exige «Consumidor Cripto só re-pin depois do bump» **e** Q7 exige que o exemplo `--pin` seja a tag do entregável. Sem tag nova, o exemplo ficaria `v1.1.1` enquanto a árvore `v1.1.1` continuaria com o README inglês; `main` e a tag anunciada divergiriam.  
   **Escolha:** commit do README no produto → tag **`v1.1.2`** (patch, não major: schema overlay inalterado) → exemplo `--pin v1.1.2` → `implantar --pin v1.1.2` no Cripto para gravar overlay `pin: v1.1.2`. O re-pin é alinhamento da tag documentada, não payload de docs. Alternativa rejeitada: só `main` sem tag (quebra Q7). Alternativa rejeitada: re-pin Cripto sem bump (o issue proíbe). Skill `implantar` **não** é reescrita (Não entra); o exemplo `v1.1.1` nessa skill pode ficar stale — residual aceite.

## Apply contract

Ordem (produto primeiro; zero UI Cripto):

1. Reescrever `/srv/apps/dev/covenant-flow/README.md` em PT-BR segundo D4–D7 (estranho → 12 colunas → Install/Pin/Layout). Exemplo `--pin v1.1.2`. Sem segundo ficheiro. Sem tabela T0–T17. Sem host backup paths (`/home/ubuntu/backups/covenant-flow-pre-773-*`, SHA `94f8ed41`).
2. `gh repo edit oalansilva/covenant-flow --description 'Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)'`.
3. Commit no produto + tag **`v1.1.2`** (patch docs; não `v2.0.0`).
4. No worktree Cripto deste card: `implantar --pin v1.1.2`. Overlay `pin: v1.1.2`. MUST NOT copiar README para o consumidor. MUST NOT editar `backend/**` nem `frontend/src/**`. MUST NOT reabrir #773/#784. MUST NOT reescrever skills/hooks/yaml/`install.sh`/adapters.

Rollback = description EN anterior + pin Cripto `v1.1.1` + tag produto `v1.1.1` (README inglês). Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [Walkthrough dual-write o significado das colunas vs skill `covenant-flow`] → aceite neste card (issue). A skill permanece canónica para o operador (hooks, OpenSpec, release). Se a skill mudar o significado de uma coluna, o README pode desactualizar. Mitigação: tecto = uma linha/coluna + uma frase de gates; Design não expande.
- [Tag `v1.1.2` sem mudança no payload do pin] → re-pin Cripto é no-op de peles + `pin:` no overlay. Custo pequeno; alinha Q7 e o «só re-pin depois do bump». Sem bump, o exemplo mentiria sobre qual tag contém o README novo.
- [Skill `implantar` continua a exemplificar `v1.1.1`] → Não entra reescrever skills. Residual: operador que abrir a skill em vez do README vê a tag antiga. O README (superfície do estranho) é a fonte do exemplo deste card.
- [Description GitHub vs README] → a frase da description é o título/lead; o README elabora. Drift futuro = outro card; este congela as duas no mesmo Apply.

## Migration Plan

Aditivo de docs no produto. Sem schema overlay. Sem canal novo. Ordem = Apply contract. Consumidor Cripto não recebe o README no pin; quem lê o produto lê GitHub/`main`/`v1.1.2`.

## Open Questions

Nenhuma. Q1–Q8 congeladas. Fronteira vazia.

## UI impact

**none** — documentação do produto de processo `oalansilva/covenant-flow` (README + description GitHub). Nenhuma rota, shell, componente ou copy de ecrã do CriptoFarol. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`. Não há tela CriptoFarol a prototipar; o aceite é texto no GitHub do núcleo. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B.

## Design Critique

- **P0:** nenhum.
- **P1:** nenhum.
- **P2 (accepted-residual):** `--pin` copia o working tree de `SOURCE`, não o peel da tag — Apply MUST taggar só o README e pinar árvore `v1.1.2` limpa (worktree produto tem diff sujo em `design-critic/SKILL.md` fora deste card). `gh repo edit` (passo 2) pode publicar description PT antes do push do README (passo 3). Spec ilustra a frase dos 3 gates em inglês; copy canónica é D5 PT-BR. Tag `v1.1.2` não mete README no pin (D9). Skill `implantar` fica com exemplo `v1.1.1`. Dual-write uma linha/coluna vs skill (issue aceite). «Até ensaio deny PASS» MUST NOT ler-se como Auto a desbloquear nos três clientes.
- **P3 (accepted-residual):** significados D5 só no design, não no delta spec. Main spec ainda diz «three client adapters». Vocabulário Auto do issue traz T1/T7/T15 — D6 já os tirou; não colar no README. Spec «#773/#784 remain closed» ≠ `gh issue close`. Apply contract não nomeia `git push` de `main`+tag.
- Prototype: N/A — docs do produto de processo, sem superfície visual.
- Snapshot: `.impeccable/critique/787-card-787-covenant-flow-readme-A.md` e `…-B.md` (r1 PASS). Apply e Code Review não lêem essa pasta. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS**
