## Context

Card [#880](https://github.com/oalansilva/crypto/issues/880) (kaizen, Operação, P1). Status observado: **Design**. Briefing = issue grelhado (DoD completo). Q1–Q6 fechadas; este Design não as reabre.

Dois modos de hospedar o **mesmo** cliente Cursor nesta VM. Não é produto Cripto, não é aresta FSM, não é Grok/OpenCode/dsh.

Testemunha 2026-09-09 no #879 (worktree `card-879-destapar-pai-colar-diff`): T8 `iniciar_apply` passou (Status → Em desenvolvimento). No Desktop+SSH Windows, no mesmo card:

- MCP troca de raiz (2×): `Failed to move agent root: InstantiationService has been disposed` (workbench `vscode-app` em `AppData/Local/Programs/cursor`; workspace `19cb1aa9…`).
- Shell `workspace_readwrite`: Landlock / user namespace `Failed to write /proc/self/uid_map (mapping UID 0 -> 1001): Operation not permitted`.
- Shell `required_permissions: ["all"]` no worktree: evento de Apply OK.
- Filho Apply: `Task was interrupted by the user after 163713ms`.

No disco hoje: o pai liga (ou não) a raiz visível via MCP `move_agent_to_root`; filhos usam `working_directory` / `git -C` no worktree; Guard `canonical_card_branch` impede `checkout -b card-*` no source canónico; hooks Cursor já têm locator cwd-independente (#822) só para Impeccable `afterFileEdit`/`stop`. Runbook: um chat `#<id>`, pai spawna filhos, worktree `card-<id>-*` pós-T1. Nada disso cobre o par Desktop+SSH partido.

UI impact: none
live_route: N/A harness-only; Cursor Desktop Windows + SSH a esta VM vs Agent/CLI no terminal da mesma VM; no product route
surface: new

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Os dois modos ficam. Cada etapa do chat (grelha → Design → Apply → review → QA → Done técnico) passa nos dois.
- Depois do Apply arrancar, a sessão que o operador vê **é** a pasta do card, sem File > Open.
- No Desktop o comando do fluxo acaba no mesmo turno sem clique extra; falha de tool/MCP visível.
- Filho da etapa chega a `completed` nos dois modos; host derrubar a meio = falha deste card.
- Prova viva = pasta + comando + filho no par que partiu; resto por ensaio (pytest / goldens / rubrica).
- Aceite Desktop+SSH = só Windows + SSH a esta VM.

**Non-Goals:**

- Produto Cripto. Aresta FSM. T1/T7/T15/T18. Homologado / Release / lote neste chat.
- Forçar um único modo. Operador abrir pasta à mão. Clique extra como contrato. Pai executar a etapa no Desktop. Operador retomar filho morto.
- Hang #879 S2. Destape de pai mudo depois do filho já ter acabado (#879). Apply unbound na `develop` (#864). Impeccable cwd (#822). Um chat por card (#729) como o mesmo trabalho.
- Grok / OpenCode / dsh (InstantiationService e Landlock/`uid_map` são do workbench/Shell Cursor; locator #822 não é o mesmo bug).
- Pin novo, overlay `clients.*.auto`, dual-write lei em `.dsh/`, `AGENTS.md` always-on a crescer, HTML de protótipo, `CONTEXT.md`, `docs/adr/`.

## Decisions

1. **Pasta (Q2) — janela Remote-SSH nova no worktree; MUST NOT `move_agent_to_root` neste par.**  
   No modo Desktop+SSH Windows desta VM o pai MUST NOT chamar MCP `move_agent_to_root` (2× `InstantiationService has been disposed`; o workbench já está a morrer). Liga a raiz visível abrindo uma **janela nova** Remote-SSH no path do worktree (`vscode-remote://ssh-remote+<esta-VM><worktree>`), título `#<id>` — bind de pasta, não chat de coluna (#729). Filhos recebem `working_directory` = worktree (necessário, **não** suficiente). No modo terminal o pai MAY `move_agent_to_root` ou já nascer com cwd no worktree.  
   Rejeitado: só cwd/`git -C` sem mudar a raiz visível — a barra Q2 é a pasta que o operador **vê**.  
   Rejeitado: repetir `move_agent_to_root` após dispose.  
   Rejeitado: reload da **mesma** janela (mesma classe InstantiationService).  
   Rejeitado: locator cwd-independente como mecanismo Q2 (#822; não muda o explorer).  
   Rejeitado: File > Open pelo operador.  
   P3 Apply: comando host exacto (`cursor --folder-uri` vs equivalente MCP que **não** dispose o serviço actual).

2. **Comando (Q3) — `required_permissions: ["all"]` no primeiro Shell do turno.**  
   Comandos do fluxo (git do runbook, `process_event`, pytest do harness) num worktree `card-<id>-*` neste par Desktop+SSH MUST pedir `all` à primeira. MUST NOT começar com `workspace_readwrite` (Landlock `uid_map` UID 0→1001) e depois clique. Falha Landlock fica visível; ecrã em branco sem explicação não passa. Modo terminal já passa; não alargar sandbox global.  
   Rejeitado: fail-open que engole o erro e segue.  
   Rejeitado: clique extra como contrato.  
   Rejeitado: `sandbox.mode: disabled` no CLI config como contrato deste card (skill `update-cli-config` é CLI, não prova que o Desktop SSH a lê; sem pin). Residual: se `all` ainda pedir clique, Apply MAY tentar `.cursor/cli.json` **só** se a prova viva mostrar que este Desktop o honra.

3. **Filho (Q4) — sucesso = `completed`; interrupt sem Stop visível = kill do host.**  
   Pai MUST NOT mutar o workbench (MCP de raiz, reload) enquanto o filho corre. Pai MUST NOT executar a etapa no Desktop em substituição. Operador MUST NOT retomar o Task id morto como aceite. Stop explícito do operador = aborto: não é sucesso; restage = spawn **novo**, não resume. Destape pós-`completed` = #879. Hang S2 = #879. Ensaio: goldens de payload (`completed` vs `Task was interrupted by the user`); prova viva = um filho de etapa a `completed` neste par.

4. **Ensaio (Q5) — pytest + goldens + rubrica; prova viva só do que partiu.**  
   Artefacto: `scripts/process-fsm/test_cursor_host_modes.py` (needles no runbook `covenant-flow`, classificação de interrupt, MUST NOT `move_agent_to_root` neste par, Shell `all` à primeira). Rubrica da prova viva (pasta visível = worktree; comando mesmo turno sem clique; filho `completed`) no QA deste card, não um card inteiro no Desktop, não só runbook. Grelha/Design/review/QA = needles de que o runbook as exige nos dois modos.

5. **Outros clientes — fora.**  
   Sem prova do mesmo bug de hospedagem. InstantiationService e Landlock/`uid_map` são Cursor. #822 não autoriza alargar.

## Apply contract

- Só após `Status=Pronto para Dev` no chat `#880`; pai `iniciar_apply` (T8) antes do spawn; filho Apply neste worktree. Zero produto. Este Design não aplica.
- `.cursor/skills/covenant-flow/SKILL.md`: os dois modos; cada etapa nos dois; Desktop+SSH Windows desta VM MUST NOT `move_agent_to_root`; bind por janela Remote-SSH nova no worktree, título `#<id>`; filhos `working_directory` = worktree e MUST NOT essa MCP; Shell do fluxo no worktree com `required_permissions: ["all"]` no primeiro attempt; `Task was interrupted` sem Stop visível ≠ sucesso; pai não substitui; operador não retoma cadáver; prova viva pasta+comando+filho; Grok/OpenCode/dsh fora.
- Prompts autocontidos do pai (grill / Design-autor / Apply / review / QA): as mesmas proibições. Sem fork da lei noutros clientes.
- Pytest `scripts/process-fsm/test_cursor_host_modes.py` (C1–C8 abaixo). Sem GitHub nos unitários. Sem `.cursor/process-fsm.yaml`. Sem `AGENTS.md` a crescer. Sem overlay `clients.*.auto`. Sem pin. Sem dual-write `.dsh/` / `.grok/`.
- P3 aceitos (resolver no Apply, não reabrir Design): URI exacta da janela nova; se `all` ainda pedir clique, `.cursor/cli.json` só com prova viva; helper de classificação de interrupt vs Stop.

### Golden cases (pytest `scripts/process-fsm`, sem GitHub)

| # | Caso | Esperado |
| --- | --- | --- |
| C1 | `covenant-flow` nomeia modo terminal e modo Desktop+SSH | needles dos dois; não manda abandonar um |
| C2 | Desktop+SSH Windows desta VM | needle MUST NOT `move_agent_to_root` |
| C3 | bind visível | needle janela Remote-SSH / worktree URI; não File > Open |
| C4 | Shell do fluxo no worktree | needle `required_permissions` / `["all"]` no primeiro attempt; não `workspace_readwrite` como contrato |
| C5 | payload `completed` + retorno do filho | classificado sucesso |
| C6 | `Task was interrupted by the user` sem Stop | classificado host kill; não sucesso |
| C7 | pai executar a etapa no Desktop / resume do cadáver | needles de recusa |
| C8 | `.dsh/` / `.grok/` / `.opencode/` skins | diff deste card não as exige; dual-write lei ausente |

## Prototype

N/A — `UI impact: none`. Harness Cursor only: modos de hospedagem, runbook, pytest. Sem HTML. Sem pasta `frontend/public/prototypes/`. Sem clonar rota de catálogo `/monitor` `/favorites` `/combo/*` `landing`. Sem superfície visual de produto.

## Prototype Validation

N/A — sem superfície visual. Sem URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica visual/audit/polish/browser de tela de produto. Snapshot Impeccable = N/A justificado.

## Risks / Trade-offs

- [Janela nova parece chat novo] → título permanece `#<id>`; recusa `#<id> Apply` (#729). Residual: o operador ainda olhar a janela antiga em `source` — aceite Q2 exige raiz visível = worktree; continuar Apply na janela antiga é falha.
- [`cursor --folder-uri` também dispose] → então o host ainda está partido; não voltar a `move_agent_to_root`; P3 Apply procura equivalente que crie InstantiationService **nova**.
- [`all` ainda pede clique neste Desktop] → Q3 falha até haver caminho sem clique; `.cursor/cli.json` só com prova viva, sem pin.
- [Interrupt do host usa a mesma string que Stop] → C6+prova viva: sem Stop visível no turno = kill. Residual aceite: o vendor não distingue.
- [Filho longo no Desktop] → ensaio, não card inteiro; filho curto o bastante para `completed`.
- [Guard `canonical_card_branch` / Landlock] → Guard fica; o furo é sandbox do Shell Cursor, não `decide()`.
- [Prova viva depende do par Windows desta VM] → Q6; outro PC não é aceite.

## Migration Plan

Aditivo no adapter Cursor (runbook + testes). Sem banco, sem rebuild, sem overlay pin. Rollback = reverter o skill e o pytest. Homologação deste card ≠ T15: é a prova viva pasta+comando+filho neste par + C1–C8 verdes.

## Open Questions

Nenhuma bloqueante. Q1–Q6 fechadas no issue. P3 acima são detalhe de Apply.

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Snapshot: `.impeccable/critique/880-card-880-fluxo-cursor-vm-desktop-ssh.md`. Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: sem rework (zero P0/P1).

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — URI exacta da janela Remote-SSH nova; se `required_permissions: ["all"]` ainda pedir clique, Q3 falha até haver caminho (`.cursor/cli.json` só com prova viva); helper interrupt vs Stop; diálogo de aceite da janela nova não conta como Q2 (bind continua do pai).
- **Disposition:** Q1–Q6 honradas; MUST NOT `move_agent_to_root` neste par; `all` à primeira; filho sucesso = `completed`; ensaio C1–C8 + prova viva pasta+comando+filho; Grok/OpenCode/dsh fora.
- **Riscos não bloqueantes:** `cursor --folder-uri` também pode dispose; operador na janela antiga em `source`; vendor não distingue interrupt vs Stop.

Design Agent verdict: PASS
