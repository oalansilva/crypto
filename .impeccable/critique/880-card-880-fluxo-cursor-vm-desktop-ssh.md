# Snapshot — Design Critic (sem-tela, 1 crítico, NÃO A/B) · card #880 `card-880-fluxo-cursor-vm-desktop-ssh`

- Card: #880 — kaizen: fluxo Cursor completo via terminal na VM e via Desktop + SSH
- Change: `openspec/changes/card-880-fluxo-cursor-vm-desktop-ssh/`
- Critic: 1 isolado (inherit de modelo; sem transcript do pai; sem Assessment B; sem nested critic)
- Modelo: inherit
- UTC: 2026-09-09T23:20:00Z
- Round: 1 (teto sem-tela = 1 autor + 1 crítico + 1 rework; este ficheiro = o único crítico)
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Write produto deny. Só `.impeccable/critique/**`. Não T5. Não commit. Não Gist. Não `process_event`. **Não editei `design.md`.**
- Digest `design.md` **medido**: sha256 `2ef8829a643e17599dd8c7924f94c799c07f022fafff3b04c86dba3a3c2e33b1` · **1645** palavras (`wc -w`) · 10990 bytes
- Issue: REST `gh api repos/oalansilva/crypto/issues/880` (não `gh issue view`). Title, labels `priority:P1` `front:operacao` `type:operacao` `kaizen`, state open, body DoD com Q1–Q6 fechadas.
- UI impact: **none** (harness Cursor; zero rota/shell/componente/HTML de produto CriptoFarol)
- Prototype: **N/A** — justificado (harness only; sem `frontend/public/prototypes/`; sem clone de catálogo)
- Snapshot visual de UI: **N/A**. Este ficheiro de crítica de processo **não** é vazio.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois desta onda)
- Method: issue #880 body (Entra/não entra + vocabulário + critérios 1–10); `proposal.md`; `design.md` D1–D5 + Apply contract + C1–C8; `tasks.md` 1–5; deltas `specs/{cursor-host-modes,cursor-harness,llm-flow-emission}/spec.md`. Sem browser. Sem Impeccable visual.

---

## Brief (só neste snapshot)

Quem opera Covenant Flow no Cursor nesta VM tem um modo que passa (Agent/CLI no terminal Linux da VM) e outro partido (Cursor Desktop Windows + Remote SSH à mesma VM). Testemunha 2026-09-09 no #879: T8 no terminal passou; no Desktop+SSH, `move_agent_to_root` 2× `InstantiationService has been disposed`; Shell `workspace_readwrite` Landlock/`uid_map`; filho Apply `Task was interrupted by the user after 163713ms`. Card #880 não é produto Cripto, não é aresta FSM, não é Grok/OpenCode/dsh, não reabre #879/#864/#822/#729. Operador fechou Q1–Q6 no issue: dois modos; cada etapa nos dois (Q1 option b); pasta sem abrir à mão (Q2); sem clique extra (Q3); filho termina (Q4); prova viva + ensaio (Q5); só Windows+esta VM (Q6). Autor propõe *como*: MUST NOT `move_agent_to_root` neste par → janela Remote-SSH nova no worktree título `#<id>`; Shell `required_permissions: ["all"]` à primeira; sucesso do filho = `completed`; ensaio `test_cursor_host_modes.py` C1–C8 + prova viva pasta/comando/filho; outros clientes fora.

---

## 1. Escopo vs grill #880 (Q1–Q6 congeladas; não reabrir como Q)

Body live: «Fronteira deste adapter: vazia. Nenhuma decisão de operador observável em aberto.» Design não reentrevista. Letras D1–D5 batem com Entra/vocabulário (não com um transcript de Qs).

| Q congelada (issue) | Onde no pacote | Honrada? |
| --- | --- | --- |
| Q1 option b: cada etapa (grelha→Design→Apply→review→QA→Done técnico) nos **dois** modos; não vale misturar sítios; Homologado/Release fora | Goals; proposal What; spec `cursor-host-modes` req «Each chat stage passes in both host modes» + cenário Homologado stays out; tasks 1.1 | Sim. Ensaio = C1 needles, não card inteiro (Q5). |
| Q2: depois do Apply arrancar, sessão continua na pasta do card **sem o operador abrir à mão** | D1; Non-Goals File > Open; spec «Visible session root… without File > Open»; `working_directory` sozinho ≠ Q2; tasks 1.2 / 5.3 | Sim no contrato. Residual de aceite-de-janela = P3 Apply (secção 3). |
| Q3: passo do comando acaba no mesmo turno **sem clique extra**; ecrã não some sem explicação | D2; spec «Flow command finishes in the same turn»; C4; tasks 1.3 | Sim no contrato. Residual `all` ainda pedir clique = P3 já nomeado. |
| Q4: filho tem de terminar nos dois modos; host derrubar = falha deste card; pai não substitui; cadáver não se retoma | D3; spec host-modes + `llm-flow-emission` + harness interrupt; C5–C7; tasks 1.4 | Sim. Destape/hang = #879. |
| Q5: aceite escrito; prova viva = pasta+comando+filho no par que partiu; resto por ensaio; sem card inteiro; sem só runbook | D4; C1–C8; tasks 3.1 / 5.3 | Sim. |
| Q6: só Windows + SSH a esta VM; outro PC não é aceite | D5; spec cenário Other Desktop pairs are out; task 1.5 | Sim. |

**Não entra — não reaberto:** produto `backend/`/`frontend/src/`; aresta FSM / T1 T7 T15 T18; forçar um único modo; Grok/OpenCode/dsh (Design declara ausência do mesmo bug); dual-write `.dsh/`/`.grok/`/`.opencode/`; Homologado/Release/lote neste chat; recorte estreito só três sítios da testemunha como *todo* o aceite (Q1 recusou; Q5 delimita prova viva a esses três **e** exige ensaio do resto); operador File > Open; clique extra como contrato; pai executar a etapa no Desktop; operador retomar filho morto; sessão viva de um card inteiro; só runbook; qualquer PC; reabrir #879/#864/#822/#729 como o mesmo trabalho.

**Entra extra (além das Q):** falha tool/MCP visível — D2 / Goals. Hooks no host certo de cada modo — coberto por Q2 (raiz visível = worktree) + #822 já fora (locator cwd-independente; não é o mesmo bug). Não falta decisão de operador.

**Q1 option b vs ensaio:** o aceite «cada etapa passa nos dois modos» vive no runbook (C1) e na prova viva dos três sítios que partiram (Q5). Não exige replay de um card inteiro no Desktop. Autor alinhado ao issue, não ao recorte estreito recusado.

---

## 2. Tokens parseáveis (gate no autor) — item da rubrica

Medidos em `design.md` linhas 16–18 (linha própria, não enterados num parágrafo):

```
UI impact: none
live_route: N/A harness-only; Cursor Desktop Windows + SSH a esta VM vs Agent/CLI no terminal da mesma VM; no product route
surface: new
```

- `UI impact`: **presente** verbatim `none`.
- `live_route`: **presente** verbatim começando `N/A harness-only; … no product route`. Ausência + justificativa curta. **Não** é rota de catálogo (`/monitor` `/favorites` `/combo/*` `landing`).
- `surface`: **presente** verbatim `new` (capability nova de harness, não clone de tela). Proposal L32–34 e tasks 5.2 batem. Sem-tela: ausência de produto está no `live_route: N/A` + Prototype N/A.

`proposal.md` repete os três tokens. Prototype § N/A recusa clone de catálogo por nome. **Gate tokens: PASS.** Nenhuma rodada extra nasce só para o parser.

Bloco D4 (teto 1+1+1 / classificação P0–P1 vs P3 Apply / gate tokens): **presente** em `design.md` (blockquote após os tokens), texto alinhado à skill canónica.

---

## 3. Stress D1–D5 (decisões do autor)

### D1 Pasta (Q2) — janela Remote-SSH nova; MUST NOT `move_agent_to_root`

**Contrato Q2:** a sessão que o operador *vê* passa a ter a pasta do card como raiz, sem o operador abrir à mão. Vocabulário: File > Open / conversa na pasta de casa recusados.

Autor: neste par o MCP `move_agent_to_root` já matou o workbench (2× InstantiationService). Bind = janela **nova** Remote-SSH no URI do worktree, título `#<id>` (não `#<id> Apply`). `working_directory` necessário, não suficiente. Rejeitado: só cwd; retry do MCP após dispose; reload da mesma janela; locator #822 como Q2; File > Open. P3: comando host exacto (`cursor --folder-uri` vs MCP que não dispose o serviço actual).

**Stress — a janela nova ainda exige acção do operador (abrir/aceitar) → fura Q2?**

Não como P0/P1. «Abrir à mão» no issue é o *operador* a fazer File > Open / escolher a pasta. O bind é do **pai**. Um diálogo de aceite do host, se existir, é o mesmo residual empírico que D2 já escreveu para Q3 («se `all` ainda pedir clique, Q3 falha até haver caminho»). Não é furo de escopo: a decisão já proíbe File > Open e não conta `working_directory` sozinho. Apply MUST NOT tratar aceite/clique de «abrir esta pasta» como Q2 cumprido — espelho da frase Q3. Detalhe de Apply, **P3 aceite**, nunca reabrir como P0.

**Stress — conflito com um chat `#<id>` (#729 fora como o mesmo trabalho)?**

Q2 é pasta visível, não contagem de transcripts. Autor: bind de pasta, não chat de coluna; título `#<id>`; recusa `#<id> Apply`. Risco nomeado: janela nova parece chat novo; residual = operador ainda na janela antiga em `source` (continuar Apply aí = falha). #729 não é reaberto como trabalho; o contrato de título evita o anti-padrão de coluna. Não P0.

**Reload da mesma janela / URI exacta:** rejeitado com razão (mesma classe InstantiationService). URI exacta já P3 no design. Confirmado P3, não promovido.

### D2 Comando (Q3) — `["all"]` no primeiro Shell

**Contrato Q3:** acaba no mesmo turno sem clique extra. Testemunha: `workspace_readwrite` Landlock; `all` no worktree = evento Apply OK.

Autor: MUST `all` à primeira; MUST NOT `workspace_readwrite` + clique; falha visível; não fail-open; não `sandbox.mode: disabled` como contrato sem prova. Residual explícito: se `all` ainda pedir clique, Q3 falha até haver caminho; `.cursor/cli.json` só com prova viva.

**Stress — `all` no Desktop ainda mostra cartão de aprovação? Furo de contrato (P0/P1) ou P3?**

**P3 de Apply, não P0.** O contrato visível (sem clique extra) está escrito e não foi relaxado. `all` é o *como* candidato que a testemunha mostrou a passar o evento — não a afirmação de que o host nunca pinta cartão. O próprio design já classifica «`all` ainda pede clique» como falha Q3 até haver caminho. Elevar isso a P0 seria reabrir *como* (permissão / flag / prova viva) como Q de operador. Prova = Q5 viva, não segunda rodada de Design.

### D3 Filho (Q4) — `completed`; interrupt sem Stop = kill

Honrado: pai MUST NOT mutar workbench (MCP de raiz, reload) enquanto o filho corre; MUST NOT substituir no Desktop; operador MUST NOT retomar Task id morto; Stop explícito = aborto + spawn novo, não resume; destape pós-`completed` e hang S2 = #879. Spec `llm-flow-emission` cobre misturar modos para esconder kill. C5–C7. Helper interrupt vs Stop já P3. Sem furo.

### D4 Ensaio (Q5) — pytest C1–C8 + prova viva do que partiu

Honrado: artefact `test_cursor_host_modes.py`; goldens `completed` vs interrupt; needles MUST NOT `move_agent_to_root`, Shell `all`, recusa pai-substituto/resume, dual-write ausente. Rubrica viva no QA (task 5.3), não card inteiro, não só runbook. Grelha/Design/review/QA = needles de que o runbook as exige nos dois modos (Q1 via ensaio). Sem furo.

### D5 Outros clientes — fora

Honrado: InstantiationService e Landlock são Cursor; #822 não autoriza alargar. C8. Spec cenário No InstantiationService on Grok means out. Sem furo.

---

## 4. Riscos operacionais (não bloqueantes)

- Janela nova vs InstantiationService: se `cursor --folder-uri` também dispose, o host ainda está partido; autor proíbe voltar ao MCP; P3 procura InstantiationService **nova**.
- Operador a olhar a janela antiga: aceite Q2 exige raiz visível = worktree.
- `all` vs cartão: Q3 falha até caminho; sem pin de `cli.json`.
- Interrupt vs Stop: mesma string do vendor; C6 + prova viva «sem Stop visível = kill»; residual aceite.
- Filho longo: ensaio, não card inteiro; filho curto o bastante para `completed`.
- Guard `canonical_card_branch` fica; furo é sandbox Shell, não `decide()`.
- Prova viva depende do par Windows desta VM (Q6).

Nenhum destes é tela/acessibilidade/escopo furado. Nenhum P0/P1 novo.

---

## 5. Rubrica sem-tela (produto / regressão / ops / UI)

- **Produto:** não há. `UI impact: none` justificado. Nenhuma superfície visual nova/alterada sem classificação.
- **Escopo:** Entra Q1–Q6 + falha visível + hooks-via-Q2+#822. Não entra intacto. Zero alargamento a Grok/OpenCode/dsh, FSM, produto, Homologado.
- **Contrato visível:** Q2 pasta sem File > Open; Q3 sem clique extra; Q4 filho `completed`. Mecanismos e residuais são *como* / Apply.
- **Regressão:** MUST NOT `backend/` `frontend/src/` `process-fsm.yaml` `AGENTS.md` always-on a crescer overlay `clients.*.auto` pin HTML `CONTEXT.md` `docs/adr/`. Tasks 5.1–5.2. Spec C8 dual-write ausente.
- **Ops:** Apply contract executável após Pronto para Dev + T8; pytest sem GitHub; rollback = reverter skill + pytest. Homologação deste card ≠ T15.
- **Prototype:** N/A justificado; sem rota emprestada.
- **Apply contract:** skill `covenant-flow` + prompts da lista fechada + `test_cursor_host_modes.py` C1–C8 + P3 já listados. Sem este Design a aplicar.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: URI exacta da janela nova (`cursor --folder-uri` vs equivalente MCP que crie InstantiationService nova, sem dispose do serviço actual). Já em `design.md` Apply contract. Disposition: **accepted-residual** (detalhe de Apply).
- P3: se `required_permissions: ["all"]` ainda pedir clique neste Desktop, Q3 falha até haver caminho; `.cursor/cli.json` só com prova viva, sem pin. Já no design. **Não é furo de contrato visível** — o aceite Q3 (mesmo turno sem clique) permanece; `all` é candidato testemunhado, não garantia do host. Disposition: **accepted-residual**.
- P3: helper de classificação `completed` vs `Task was interrupted by the user` vs Stop visível. Já em tasks 3.2. Disposition: **accepted-residual**.
- P3: se a janela Remote-SSH nova ainda pintar diálogo de aceite/abrir ao operador, isso **não** conta como Q2 (é a mesma classe «abrir à mão» que File > Open). Bind continua a ser do pai; Q2 falha até haver spawn sem clique — espelho da frase Q3 já escrita. Não reabre Q2 como Q; não promove a P0. Disposition: **accepted-residual**.

Dual-write lei noutros clientes / aresta FSM / produto / HTML / rota de catálogo / reabrir #879 #864 #822 #729: **false**.

---

## Disposition

Zero P0/P1. Q1–Q6 congeladas e mapeadas a D1–D5 + specs + tasks. Tokens parseáveis presentes em linha própria; Prototype N/A justificado; sem rota de catálogo emprestada. Residuais de host (URI, cartão `all`, aceite de janela, helper interrupt) são detalhe de Apply — aceitos, resolvidos no Apply, nunca reabertos como P0/P1. Teto 1+1+1: sem segundo rework (não há P0 novo de produto).

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; harness Cursor (modos de hospedagem, runbook, pytest); nenhuma tela CriptoFarol.

`design.md`: **não editado** por este crítico.
)
