# Fix snapshot — card 852 · change card-852-descoberta-tres-modos (rodada de fix, 2026-09-06T18-35Z)

> Filho Design-autor isolado, sem transcript. Escopo: `openspec/changes/card-852-descoberta-tres-modos/**`,
> `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html`, este snapshot. Sem troca de branch,
> sem mover Status, sem `process_event`, sem T5, sem edição de produto (`frontend/src/**`, `backend/**` intactos —
> `git status` mostra só os diretórios novos permitidos). Sem visão neste modelo (sem revisão de pixels);
> geometria via DOM/getBoundingClientRect + forense de bytes dos PNGs (IHDR + sha256).

## 1. P1-B BLOCKED — corrigido (2 linhas, StrReplace, sem reemitir HTML)

- `index.html:246` (`#m-promote`) e `index.html:270` (`#m-adv`): `</button></div>` → `</button></header>`.
- Verificado por grep: 2× `✕</button></header>`, 0× `✕</button></div>`; `</header>` fecha 2×.
- `design.md` (Apply contract) passa a descrever dialog íntegro: header + corpo DENTRO do `role=dialog`;
  tasks 5.1 proíbe o apply de copiar o typo.

## 2. Pequenos — todos feitos no protótipo + contrato (sem reescopo)

- `Snapshot válido` (fora do `<details>`, `#pf-state` + JS `sync()`) → `Pronto para iniciar`; `snapshot`
  mantido SÓ no `<details>` técnico (linhas 174/316). Chip `RUNNING` → `EM CURSO` (Acompanhar).
- Vazio de filtro: `renderLb()` com 0 linhas renderiza `Nenhum candidato neste filtro. [Limpar filtros]`
  (colspan 6 + `#lb-empty-clear` que limpa e re-renderiza).
- Parciais do Acompanhar definidas: top-5 travadas do sweep em curso, sem paginação (tasks 1.1 +
  nota no protótipo + Apply contract no `design.md`).
- P1-F1 no contrato: tasks 1.1/5.1 + req 8 listam explicitamente a preservação fora do switch de modos
  (Descartar por linha + copy destrutiva, dedup `duplicate`/`already_promoted`, bloco 409, nota de
  revalidação sob lock, painel 403, bloco stale, sessão expirada).

## 3. Re-gate — browser real, asserts EM ESCOPO DE DIALOG (48/48 PASS)

- Playwright Python + Chromium headless (cache 1243, `executable_path` explícito), servido via
  `http.server` local do diretório do protótipo. Desktop 1440×900 + mobile 390×844.
- Servido == local: `0a2bc5727c2a372ba13a14a0622f99536a7304534536fe67cad4c7f1a1a7b1f7`, 32946 bytes,
  idêntico nas duas pontas (digest novo pós-fix; anterior `9b298054…` pré-fix).
- Matriz (24 asserts/viewport, ação→resultado): título/landmarks/CTA OK; `pf-state`=`Pronto para iniciar`;
  chip Acompanhar=`EM CURSO`; `#m-promote` visível com `.risk` DENTRO, `.dest`+Tier 3 DENTRO, `#m-promote-ok`
  DENTRO, nome do candidato DENTRO; geometria desktop dialog 520px/corpo 518px dentro/padding 20px/corpo
  abaixo do header (`bodyInsideX`+`bodyBelowHeader` true), mobile dialog 350px/corpo 348px/padding 20px;
  confirmação cita Favoritos; Escape fecha + foco retorna ao gatilho; trap Tab mantém foco no modal;
  `#m-adv` com `.body` DENTRO + 2 ações; filtro SOL+1d → `0 de 24` + mensagem de vazio + `Limpar filtros`
  restaura 12 linhas/`Página 1 de 2`; Acompanhar com 5 parciais; **0 console errors, 0 pageerrors,
  0 recursos ≥400** nas duas viewports. TOTAL 48/48 PASS (script: `/tmp/card852-gate.py`).
- Nota: 1ª execução teve 2 falhas do SCRIPT (não do protótipo): seletor de chip fora do painel Acompanhar
  e clique em Promover com tbody vazio filtrado — ambos corrigidos no script, sem tocar o protótipo.

## 4. Screenshots recapturados (P1-A1/A2) — `/tmp/card852-*`, dimensões reais

- `card852-desktop-montar.png` 1440×900 (82677 B, `a8776875…`), `card852-desktop-acomp.png` 1440×900
  (96083 B, `cbbf954d…`), `card852-desktop-decidir.png` 1440×900 (94112 B, `10e0df26…`),
  `card852-desktop-promote.png` 1440×900 (108402 B, `af43f809…`) — **distinta** de decidir (sha ≠).
- `card852-mobile-montar/acomp/decidir/promote.png` 390×844, todos sha distintos entre si.
- Pendência humana declarada: sem revisão de pixels neste modelo — aprovação deve incluir passada visual
  nos 8 PNGs (contraste incluso). Sem sessão autenticada: rota viva avaliada só via fonte (inalterada).

## 5. Arquivos + patches

1. `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` — `</div>`→`</header>` ×2;
   `Snapshot válido`→`Pronto para iniciar` ×2; `RUNNING`→`EM CURSO`; vazio com `#lb-empty-clear`;
   nota de parciais top-5.
2. `openspec/changes/card-852-descoberta-tres-modos/design.md` — dialog íntegro + preservação fora do
   switch + parciais no Apply contract; Fluxos com PT + vazio; digest novo `0a2bc572…`/32946 B;
   seção Prototype Validation reescrita com o re-gate.
3. `openspec/changes/card-852-descoberta-tres-modos/tasks.md` — 1.1 (parciais + preservação), 5.1 (dialog íntegro + preservação).
4. `openspec/changes/card-852-descoberta-tres-modos/specs/discovery-three-modes/spec.md` — req 8 com
   cláusula de preservação fora do switch.
5. Este snapshot: `.impeccable/critique/852-card-852-descoberta-tres-modos-fix-2026-09-06T18-35Z.md`.

## Veredito próprio: PASS

P1-B corrigido e re-gatado em escopo de dialog nas 2 viewports; A1/A2 com evidência dimensional real +
modal distinto; pequenos incorporados; contrato do apply blindado contra o typo e contra regressão de
estados do vivo. Resta passada visual humana nos PNGs (fora do meu alcance) antes da Aprovação de Design.
Sem HTML neste retorno, conforme pedido.
