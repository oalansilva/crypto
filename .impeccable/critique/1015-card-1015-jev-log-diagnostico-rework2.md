# Relatório do Design-autor em rework #2 — #1015 · card-1015-jev-log-diagnostico

Filho **Design-autor em rework #2** (spawn isolado, cliente dsh). Worktree `crypto-worktrees/card-1015-jev-log-diagnostico`, branch `card-1015-jev-log-diagnostico`. Escrita só em `openspec/changes/card-1015-jev-log-diagnostico/**` e neste relatório. Sem `process_event`, issue, board, Gist, comentário, commit/push, filhos nem `move_agent_to_root`; `backend/**` e `frontend/src/**` intocados (só leitura para conferir a convenção de constantes de bytes).

## Motivo (δ)

O card já foi submetido (T5) e o **Alan devolveu-o com `devolver_design` (T6)**, fixando a decisão de produto que faltava: **a justificação do segundo rework é a decisão do dono (T6) que fecha o tecto do ficheiro de log, que estava em P3.** Não há P0 novo de produto; o que se crava é o valor do tecto e o mecanismo, que passam de P3 para o contrato visível. Diff mínimo: o Design não foi reescrito.

## Valor fixado (bytes)

- **200 MB = `200 * 1024 * 1024` = 209 715 200 bytes** (200 MiB).
- Convenção do próprio repo, verificada por leitura: `backend/app/routes/logs.py` → `MAX_INCREMENTAL_BYTES = 256 * 1024` (produto de 1024, sufixo `_BYTES`). Segue-se a mesma forma: produto `200 * 1024 * 1024`.
- Escreve-se sempre as duas formas: «200 MB» **e** «209 715 200 bytes».

## Mecanismo fixado (não é produto, é mecanismo)

- **Um só ficheiro de log**, truncagem de cauda: ao encher, o registo mais antigo cai **dentro do próprio ficheiro**; sem prazo fixo.
- **Nada** de `RotatingFileHandler` com backups `.1`/`.2`, **nada** de `backupCount` — em Python `backupCount=0` não roda nada (fica sem tecto); registado como alternativa rejeitada. **Nada** de rotação por tempo.
- **Fronteira de linha** (decisão/risco, com a implementação fina em P3): a truncagem corta pela cabeça e tem de cair em fronteira de linha (descartar a linha parcial do início), senão o primeiro registo do ficheiro fica corrompido/ilegível.

## Diff conceptual

### 1. `design.md`

- **Decisão 4** — de «Ficheiro de log dedicado com rotação por tamanho — cai o mais antigo, sem prazo» (tecto indefinido «com tecto de bytes») para **«Ficheiro de log único com tecto de 200 MB (209 715 200 bytes) e truncagem de cauda — cai o mais antigo, sem prazo»**: ficheiro único, tecto explícito `200 * 1024 * 1024 = 209 715 200` (com a convenção do repo citada), truncagem de cauda no mesmo ficheiro, corte pela cabeça em fronteira de linha, nunca por tempo. Acrescentada a alternativa rejeitada **`RotatingFileHandler` com backups (`.1`, `.2`, `backupCount`)**, com a razão: o tecto seria o par `maxBytes` × `backupCount` e `backupCount=0` não capa; o dono fixou ficheiro único. Mantidas as rejeitadas `TimedRotatingFileHandler`/prazo, crescer sem tecto em `full_execution_log.txt` e só stderr/journald.
- **Vocabulário** — «Rotação por tamanho» → **«Ficheiro único com tecto de 200 MB (truncagem de cauda)»**, nomeando o tecto de 200 MB (209 715 200 bytes), o ficheiro único, a fronteira de linha e a ausência de backups `.1`/`.2` e de prazo.
- **Goals** — a linha do ficheiro de log passou a «Ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)** … truncagem de cauda em fronteira de linha … sem prazo fixo».
- **Apply contract (contrato visível)** — a linha do nível/ficheiro passou a «ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)**, truncagem de cauda (cai o mais antigo no mesmo ficheiro, em fronteira de linha), sem prazo fixo».
- **P3 (`Apply contract` e secção `## P3`)** — removido «Mecanismo concreto de rotação por tamanho (`RotatingFileHandler` vs truncagem de cauda) e valores de tecto/`backupCount`» → fica só **implementação fina da truncagem** (onde/como corta: seek/trim, bytes por escrita), porque tecto e mecanismo passaram a contrato. Removido «rotação/`backupCnt`» da lista de restantes detalhes → «implementação fina da truncagem». A linha de injecção de handler nos testes passou a «forçam o tecto/truncagem (ficheiro temporário com tecto minúsculo)» (mesma matéria P3, wording coerente com o mecanismo).
- **Risks / Trade-offs** — o risco de flood mantém-se, com a mitigação actualizada de «rotação por tamanho» para «tecto de 200 MB com truncagem de cauda (decisão 4)». Acrescentado o risco **[Risco] A truncagem corta a meio de uma linha e o primeiro registo do ficheiro fica corrompido/ilegível → Mitigação: cortar sempre em fronteira de linha (descartar a linha parcial do início); teste prova que a primeira linha do ficheiro truncado continua legível.**
- **Intocados:** secção `## Design Critique` (P0/P1/P2/P3/Disposition/Spawns/proxy modelo — incluindo a linha do crítico que ainda diz «rotação/`backupCnt`», l.149), tokens do gate (`UI impact: none` · `live_route: N/A registo de diagnóstico em ficheiro de log; sem tela de produto` · `surface: new`), bloco D4, decisões 1–3 e 5–7, fronteira do P2 (ciclo recusado por gate com `skip_reason` não nulo), `proposal.md`, checkboxes, escopo do «Não entra».

### 2. `specs/scalp-jev-diagnostic-log/spec.md`

- Requisito **«The log file rotates by size and drops the oldest records»** → **«The log file is a single file with a 200 MB ceiling and drops the oldest records»**: ficheiro **único**, tecto fixo de **200 MB (209 715 200 bytes = 200 × 1024 × 1024)**, cai o mais antigo **dentro do mesmo ficheiro** (tail truncation) mantendo os mais novos; corte em **fronteira de linha** (linha parcial do início descartada) para que os registos ficam legíveis; **sem** backups `.1`/`.2`, **sem** `RotatingFileHandler`/`backupCount` e **sem** expiração por tempo.
- Cenário «Full file drops the oldest records»: `WHEN` o ficheiro atinge o tecto de 200 MB e chegam registos novos → cai o mais antigo e o ficheiro fica **dentro do tecto de 200 MB**, mantendo os mais novos.
- Cenário **novo** «Truncation preserves readable records at the line boundary»: o corte cai em fronteira de linha, descarta a linha parcial do início e a primeira linha do ficheiro truncado continua legível.
- Cenário «No time-based rotation» intacto (continua **sem** rotação por tempo).
- Nenhum requisito novo fora disto (7 requisitos, 1 cenário acrescentado).

### 3. `tasks.md`

- **3.2** — de «Ficheiro de log dedicado com rotação por tamanho…» para «Ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)**: ao encher, o registo mais antigo cai no próprio ficheiro (truncagem de cauda em fronteira de linha, descartando a linha parcial do início); sem prazo fixo (nada de rotação por tempo, nada de `RotatingFileHandler`/`backupCount`/backups `.1`); o ficheiro não cresce sem tecto.»
- **7.1** — de «…rotação por tamanho cai o mais antigo» para «…tecto forçado num ficheiro temporário com tecto minúsculo prova que o registo mais antigo caiu, que o ficheiro ficou dentro do tecto e que a primeira linha do ficheiro truncado continua legível (fronteira de linha)».
- Checkboxes mantidas `- [ ]` (15); o resto do `tasks.md` intacto (o cabeçalho da secção 3 continua «Nível e rotação do ficheiro» — não estava na lista de edições pedida; assinalo aqui para o pai decidir se quer ajustar).

## Evidência e validação

`/usr/bin/openspec validate card-1015-jev-log-diagnostico --type change --strict` (worktree) →

```
Change 'card-1015-jev-log-diagnostico' is valid
[exit code: 0]
```

Conferência de intocáveis: `UI impact: none` / `live_route: N/A registo de diagnóstico em ficheiro de log; sem tela de produto` / `surface: new` presentes em linha própria (design.md l.15–17); secção `## Design Critique` inalterada; `proposal.md` não tocado; `backend/**` e `frontend/src/**` sem escrita.

## Ficheiros alterados

- `openspec/changes/card-1015-jev-log-diagnostico/design.md`
- `openspec/changes/card-1015-jev-log-diagnostico/specs/scalp-jev-diagnostic-log/spec.md`
- `openspec/changes/card-1015-jev-log-diagnostico/tasks.md`
- `.impeccable/critique/1015-card-1015-jev-log-diagnostico-rework2.md` (este relatório)

Este relatório não submete Design, Gist nem T5; a submissão fica com o pai.
