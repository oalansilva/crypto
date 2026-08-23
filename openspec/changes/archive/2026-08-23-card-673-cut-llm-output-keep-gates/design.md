## Context

Card [#673](https://github.com/oalansilva/crypto/issues/673) (kaizen P1 Operacao). História grelhada no issue (fronteira vazia, 2026-08-23). Não reabre [#530](https://github.com/oalansilva/crypto/issues/530) (protótipo = spec de layout; apply lê o arquivo), [#569](https://github.com/oalansilva/crypto/issues/569) (dois reviewers inherit de **modelo**), [#613](https://github.com/oalansilva/crypto/issues/613) (paging de input), [#667](https://github.com/oalansilva/crypto/issues/667) (grill), [#668](https://github.com/oalansilva/crypto/issues/668) (adapters).

Hoje a **avaliação** Impeccable (rubrica em `.agents/skills/impeccable/reference/critique.md`, dual critic, detector, browser) é o gate certo. A **emissão** é o custo: o vendor manda relatório integral no chat; `design-critic` pede Brief/Critique/Audit/Trace no `design.md`; apply relê esse pacote; chats longos misturam colunas (cache × turnos). Preço de referência Grok: output 3× input novo e 12× cache.

**UI impact: none.** Harness/skills/docs. Nenhuma superfície de produto. Prototype N/A. Impeccable N/A neste card.

## Goals / Non-Goals

**Goals:**

- Avaliar com a rubrica completa nos dois clientes; publicar só bullets + disposition + verdict.
- Snapshot git-tracked em `.impeccable/critique/`, linkado no card; apply/review não lêem.
- Clone+delta; critics vêem URL/screenshot/digest; apply continua lendo o HTML do disco.
- Reviewers sem transcript de Design/Apply; saída findings ou `No findings.`
- Um chat por coluna, recusa de mistura; sem evento FSM.
- Apply fatiado: task + spec da capability + `## Apply contract`.
- Folha de tokens operacional; `DESIGN.md` intacto.
- Proxies no handoff (palavras, bytes HTML gerado vs copiado, spawns).

**Non-Goals:**

- Implementar o teto só no Grok ou só no Cursor.
- Enfraquecer avaliação, pular Design/T7/dual critic/dual reviewer.
- Teto rígido de 20 linhas; truncar achado.
- Um reviewer só; Bugbot obrigatório.
- Encolher tools bundled do Grok TUI; cortar OpenSpec; produto/UI do app.
- Gate/hook de “um chat por coluna” na FSM.
- Medidor de $ real Cursor/Grok.
- Reabrir #530/#569/#613/#667/#668.

## Decisions

1. **Lei canônica, adapter Grok é ponte.**  
   Mudanças de comportamento em `.agents/skills/design-critic/SKILL.md`, `rules.md`, bloco Impeccable de `docs/crypto-overlay.md`, `.cursor/skills/alan-workflow` e `openspec-apply-change`. Grok não ganha runbook próprio. Alternativa: copiar o teto em `.grok/skills/` — dual-write, proibida por #668.

2. **Design-column não usa o `$impeccable critique` vendor como emissão.**  
   O vendor (`critique.md`) ainda declara “chat response is the primary deliverable” com tabela Nielsen. O contrato de Design deste repo passa a ser `design-critic`: A avalia com a rubrica (especificidade, heurísticas, carga cognitiva, 2–3 personas, estados); B corre detector + browser; a **emissão** para o operador é bullets. `$impeccable critique` solto fora da coluna Design não é o happy path deste card. Alternativa: fork/reescrita do vendor skill — frágil no upgrade 4.x. Rejeitada.

3. **Critics escrevem só o snapshot; retorno ao pai é curto.**  
   A e B isolados, mesmo modelo, prompt autocontido (URL, digest, screenshot, folha de tokens, rubrica, contrato de saída). Podem escrever **apenas** `.impeccable/critique/**` (path fora de `product_globs` → Guard allow em Design). Não editam `design.md`/protótipo/produto. O spec `cursor-harness` “Design gate is process-based” MUST passar de “not to edit files” para essa allowlist — senão o snapshot nunca nasce. Retorno: bullets P0–P3 + disposition + verdict + path do snapshot. Pai consolida as seções de crítica no `design.md`. Snapshot vazio ⇒ `BLOCKED`. Alternativa: pai recebe o relatório integral e grava o snapshot — o dump entra no transcript do pai (cache). Pior no objetivo. Residual: o produto Cursor/Grok ainda pode injetar o resultado da Task no contexto do pai; mitigado por saída curta + chat novo na próxima coluna.

4. **Path do snapshot.**  
   Continuar `.impeccable/critique/` (já git-tracked; ignore atual não cobre essa pasta). Nome via helper existente `critique-storage.mjs` quando couber; senão `<card>-<change>-<utc>.md`. Gist **não** envia a pasta (o publish script já restringe a proposal/design/specs/tasks). Comentário do card ganha bloco **Snapshot Impeccable** com path (e blob URL da branch quando existir). Alan abre no T7.

5. **Folha de tokens = recorte operacional, não YAML.**  
   Arquivo novo `.agents/skills/impeccable/references/cripto-farol-token-sheet.md`: sidebar 224px, header workspace, `--bg-*` / `--accent-primary` / `--text-*` / `--border-default`, Inter, nav autenticada real, densidade. Aponta `DESIGN.md` como autoridade humana/visual e **proíbe** reescrevê-lo. `context.mjs` / clone+delta lêem a folha + a tela atual. Alternativa: mandar o agente ler o `DESIGN.md` YAML inteiro — é o custo atual e ainda descreve mundo Binance gerado, não o shell do app.

6. **`design.md` tem duas zonas: crítica curta e contrato de apply.**  
   Teto de forma vale para **emissão da crítica** (chat + seções Impeccable/Design Critique): bullets P0–P3, disposition, verdict. Não vale “o arquivo inteiro só tem bullets”. Apply relê só seções curtas: problema/decisões, `## Apply contract`, UI impact, URL/digest. Shape/Brief integral vai para o snapshot; `design.md` guarda recorte (audience, outcome, direction, scope). Apply skill deixa de dizer “Read every contextFiles”. Por task: checkbox atual + spec da capability + Apply contract. Snapshot Impeccable fora. Alternativa: filtrar `contextFiles` no CLI OpenSpec — fora deste repo; alavanca = skill.

7. **Clone+delta e polish = arquivo, não prosa.**  
   Tela existente: copiar shell atual (tokens da folha + estrutura da rota) e patchar o delta. Tela nova: shell autenticado, não landing genérica. Critics nunca recebem o HTML fonte no prompt. Polish = `StrReplace`/patch no arquivo versionado; proibido reemitir o documento HTML inteiro na LLM. Apply lê o path — #530 intacto.

8. **Um chat por coluna é runbook, não δ.**  
   Título `#<id> Design|Apply|Review|Release`. Recusa misturar. Sem estado/evento/hook no yaml (aceite do issue). Sem `enabled_tools` novo. Sempre-on `AGENTS.md` não cresce com essa regra (orçamento 40 linhas); mora em `alan-workflow` + `design-critic`. T7: Alan abre o **Snapshot Impeccable** linkado no comentário do card; o Gist OpenSpec não é a crítica.

9. **Reviewers: inherit de modelo, corte de transcript.**  
   Prompts `.cursor/agents/diff-reviewer.md` e `code-reviewer.md` já saem findings ou `No findings.` — manter. Spawn: corpo do arquivo + diff. Explicitar “não incluir chat de Design/Apply; não ler `.impeccable/critique/`”. Dois papéis permanecem. Bugbot opcional. Não é “um reviewer só”.

10. **Stubs Grok extras para `.agents/skills/`.**  
    `grok_stubs.py` hoje só varre `.cursor/skills/`. Estender com lista explícita `("design-critic", ".agents/skills/design-critic")` e `("impeccable", ".agents/skills/impeccable")`, corpo MUST Read nesse path, ≤8 linhas. CI stale igual. Hop extra stub→canônico é só Grok (risco do issue, aceite). Não stubar `playwright-cli` neste card.

11. **Publish/handoff: snapshot + proxies, sem $.**  
    `publish-openspec-card-artifacts.sh` ganha `--snapshot-path` (bloco separado, como `--prototype-url`) e um bloco **Proxies** (`design.md` words, HTML bytes generated vs copied, spawn count). Generated vs copied: `cp`/clone da tela-base = copied; bytes introduzidos pelo delta do card = generated; sem protótipo = `N/A`. Sem parser de usage.

12. **Este card é `UI impact: none`.**  
    Sem pipeline Impeccable, sem Playwright, sem protótipo. Crítica isolada cobre escopo, regressão de gates, riscos operacionais e confirma ausência de superfície visual. T7 permanece.

## Risks / Trade-offs

- [Cursor/Grok injeta o resultado da Task no pai mesmo com retorno curto] → D3: contrato de saída curto + D8 chat novo na próxima coluna. Residual: a sessão Design ainda paga o cache dos filhos até o chat acabar.
- [Agente Grok não Read o canônico] → stub MUST Read; aceite do issue se só um cliente cumprir na invocação automática; ensaio de homologação observa os dois.
- [Vendor `$impeccable critique` ainda despeja no chat se alguém o invocar] → D2: Design-column = `design-critic`; não fork do 4.x.
- [Apply ignorar o skill e reler o pacote] → D6 normativo no skill; Code Review `code-reviewer` trata dump de snapshot como achado de processo.
- [Folha de tokens divergir do produto] → D5: folha aponta a tela atual + `DESIGN.md`; não é YAML; update da folha é task deste card, drift futuro = card filho.
- [Proxies não provam economia em dólar] → aceite do issue; sem medidor.
- [Clone+delta em tela nova ainda gera HTML] → aceite; base = shell, não landing; bytes generated vs copied distinguem.
- [#667/#668 Homologado, não Pronto] → não reabre; este card assume o canônico já em `develop`.

## Migration Plan

Aditivo, só harness. Ordem de apply: (1) folha de tokens + design-critic/rules/overlay Impeccable; (2) apply skill + alan-workflow (um chat, apply fatiado, proxies); (3) reviewer prompts; (4) grok_stubs extras + stubs; (5) publish script `--snapshot-path` / proxies; (6) spec deltas. Rollback = reverter o diff. Sem migration de banco. Sem rebuild frontend. Homologação = ensaio Design UI-affected **e** um card `UI impact: none` nos dois clientes, mais apply/review sem ler snapshot — não um `./restart`.

## Open Questions

Nenhuma bloqueante. Path da folha e recorte de apply estão em D5/D6. Residual de produto: injeção de Task no transcript do pai.

## Apply contract

- **UI impact:** none.
- **O que o apply muda:** skills/lei/stubs/publish helper/folha de tokens. Não `backend/` nem `frontend/src/`.
- **Protótipo:** N/A.
- **Decisões vinculantes:** D1–D12.
- **Não fazer:** fork de lei em `.grok/`; pular dual critic; mandar HTML/snapshot para apply/review; evento FSM novo; parser de $.

## UI impact

**none** — harness/skills/docs de processo. Nenhuma rota, componente ou token de produto.

## Prototype

N/A — `UI impact: none`. Não há tela de produto a prototipar; o aceite visível é emissão curta + snapshot linkado + recusa de mistura de colunas.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`. Este card não produz superfície visual.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada, mesmo modelo, sem transcript do pai (A + B, depois recrítica A + B). Fontes: proposal, design D1–D12, tasks, specs da change, specs main tocadas. Card #673, change `card-673-cut-llm-output-keep-gates`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`). Snapshot: N/A justificado.

**Rodada 1 — BLOCKED**
- P1 (A/B): teto “`design.md` só bullets” vs Apply contract / URL/digest. Disposition: resolvido — teto = emissão da crítica; arquivo guarda seções curtas de apply.
- P1 (A/B): `cursor-harness` “not to edit files” vs snapshot. Disposition: resolvido — MODIFIED Design gate allowlist `.impeccable/critique/**`.
- P2: Shape brief integral ainda no `design.md` main. Disposition: resolvido — Brief no snapshot; recorte no `design.md`.

**Rodada 2 — PASS (A e B)**
- P1 reabertos: nenhum.
- P2 aceitos: slice apply omite `## Decisions` se o Apply contract bastar; `context.mjs` não é patchado; pasta `references/` vs vendor `reference/`; reviewers vs critics no mesmo requisito transversal.
- P3 aceitos: vendor `$impeccable critique` ainda despeja se invocado; issue body “só bullets” vs OpenSpec superset; “Codex” nos títulos MODIFIED.

- **Escopo:** teto de emissão nos dois harnesses; avaliação intacta; sem produto/UI.
- **Processo:** T7 Alan; dual critic; dual reviewer; #530 apply lê HTML do disco; sem evento FSM.
- **Operação:** snapshot git-tracked + link no card; apply/review não lêem; um chat por coluna; proxies no handoff.

**Design Agent verdict: PASS** — crítica isolada inherit de modelo, sem transcript (recrítica 2). Prototype N/A. Impeccable N/A.
