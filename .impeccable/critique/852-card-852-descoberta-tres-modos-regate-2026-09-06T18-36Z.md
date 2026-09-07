# Re-gate isolado — card 852 · change card-852-descoberta-tres-modos (2026-09-06T18-36Z)

> Re-gate isolado, sem transcript, sem contato com autor/A/B. Sessão distinta.
> Sem troca de branch, sem mover Status, sem process_event. Leitura + browser real apenas.
> Única escrita deste re-gate: este arquivo em `.impeccable/critique/**`.
> design.md, protótipo, produto e Gist NÃO editados (verificado: só leitura + grep).
> Referências lidas (não editadas): fix snapshot `852-card-852-descoberta-tres-modos-fix-2026-09-06T18-35Z.md`,
> assessments A (`...-assessment-A-2026-09-06T18-16Z.md`) e B (`...-assessment-B-2026-09-06T18-19Z.md`).
> Sem HTML neste retorno, conforme pedido.

## 1. Servido vs local — CONFIRMADO (==)

- Servido: `https://dev.criptofarol.com.br/prototypes/card-852-descoberta-tres-modos/` → HTTP 200,
  `text/html; charset=utf-8`, 32946 bytes,
  sha256 `0a2bc5727c2a372ba13a14a0622f99536a7304534536fe67cad4c7f1a1a7b1f7`.
- Local: `frontend/public/prototypes/card-852-descoberta-tres-modos/index.html` → 32946 bytes,
  sha256 `0a2bc5727c2a372ba13a14a0622f99536a7304534536fe67cad4c7f1a1a7b1f7`.
- Veredito: servido == local, idêntico ao digest alegado no fix. PASS.
- Markup local (grep, sem edição): `✕</button></header>` nas linhas 247 (#m-promote) e 271 (#m-adv);
  `Pronto para iniciar` (l.167 + JS l.315), chip `EM CURSO` (l.188), vazio com `#lb-empty-clear`
  (l.370-371), nota de parciais top-5 (l.206). Contrato do apply confirmado por leitura:
  design.md l.34 (preservação fora do switch), l.43 (digest novo), l.46 (fluxos + PT);
  tasks 1.1/5.1 e spec req 8 com cláusula anti-typo e anti-regressão.

## 2. Browser real (matriz ação→resultado, 62/62 PASS)

Playwright Python + Chromium headless 1243 (`chrome-linux-arm64`), executado DIRETAMENTE
contra o servido remoto (byte-idêntico ao local, item 1). Desktop 1440×900 + mobile 390×844.
Script próprio e independente: `/tmp/card852-regate.py`; resultados em `/tmp/card852-regate-results.json`.
Nota de transparência: 1ª execução teve 3 falhas DO MEU SCRIPT (não do protótipo — seletores
`#tbl-lb`, "Página" com maiúscula, `.exp` sem escopo); corrigidos no script sem tocar o protótipo.
Asserts EM ESCOPO DE DIALOG marcados com [D].

Desktop 1440 (31/31):
- R-title: "Descoberta — 3 modos (protótipo card 852)" PASS
- R-landmarks 3/3 (h1 "Descoberta de estratégias swing", Preflight, Rascunho) PASS
- R-1-modo-visível (active=1), R-preflight contém "combinações" PASS
- R-CTA estável ("Iniciar varredura — 24, ~48min") PASS
- R-pfstate "Pronto para iniciar", R-chip "EM CURSO" PASS
- R-lb 6 th exatos, 12 linhas + "24 de 24 candidatos · página 1 de 2", expansão aria-expanded PASS
- [D] promote visível; .risk DENTRO; .dest+Tier 3 DENTRO ("Destino obrigatório / Tier 3 · observação /
  Onde ver depois: Favoritos → Tier 3"); #m-promote-ok DENTRO; nome "multi trend v1" DENTRO PASS
- [D] geometria: dialog 520px / corpo 518px / padding 20px, bodyInsideX=true, bodyBelowHeader=true
  (corpo dentro do dialog, abaixo do header, sem lado-a-lado) PASS
- [D] confirmação cita Favoritos ("Candidato promovido a favorito tier 3. Veja em Favoritos → Tier 3.") PASS
- [D] Escape fecha (#m-promote-bg sem .open); foco retorna ao gatilho (data-promote=1);
  trap Tab mantém foco no modal (activeElement BUTTON.btn dentro) PASS
- [D] #m-adv .body DENTRO + 2 ações (#m-adv-select, #m-adv-ok); Escape fecha PASS
- R-vazio: filtro SOL+1d → "0 de 24 candidatos · página 1 de 1" + "Nenhum candidato neste filtro.
  Limpar filtros"; Limpar filtros restaura 12 linhas + "24 de 24 · página 1 de 2" PASS
- R-acomp 5 parciais; zero console errors; zero pageerrors; zero recursos >=400 PASS

Mobile 390 (31/31): mesma matriz, mesmos resultados; geometria do dialog 350px / corpo 348px /
padding 20px, dentro e abaixo do header. TOTAL 62/62 PASS.

## 3. Console / rede / screenshots

- Console errors: 0 · pageerrors: 0 · responses ≥400: 0 (desktop + mobile).
- Fix-round `/tmp/card852-desktop-*.png`: 4× IHDR 1440×900 reais (montar a8776875…, acomp cbbf954d…,
  decidir 10e0df26…, promote af43f809…); promote ≠ decidir (sha distintos). Mobile 4× 390×844,
  todos sha distintos. Conferido por bytes — P1-A1/A2 do assessment A RESOLVIDOS.
- Re-gate recapturou `/tmp/card852-regate-{desktop,mobile}-{montar,acomp,decidir,promote}.png`:
  desktop 4× 1440×900 byte-idênticos aos do fix (re-render determinístico); mobile 4× 390×844
  com bytes diferentes dos do fix (ver P3-R3, não-bloqueante).
- SEM VISÃO neste modelo: `read_image` rejeitado pelo runtime
  ("model does not declare image input"). Nenhuma revisão de pixels alegada — passada visual
  humana nos PNGs segue pendente (P3-R1).

## 4. Residuais P0–P3 com disposition

- P0 — nenhum. Landmarks 3/3, sem toggle cosmético, sem chrome-só. (disposition: n/a)
- P1 — nenhum residual. P1-B (dialog) corrigido e re-gatado em escopo nas 2 viewports;
  P1-A1/A2 (evidência) resolvidos com PNGs reais + modal distinto; P1-F1 blindado no contrato
  (design.md l.34, tasks 1.1/5.1, spec req 8 — confirmado por leitura). (disposition: n/a;
  F1 vira checklist do apply, sem re-gate adicional possível neste escopo)
- P2 — nenhum residual. PT ("Pronto para iniciar", "EM CURSO"), vazio com "Limpar filtros",
  parciais top-5 definidas — todos re-gatados acima. (disposition: n/a)
- P3-R1 — Sem revisão de pixels (modelo sem visão). (disposition: passada visual humana nos
  `/tmp/card852-*.png` + `/tmp/card852-regate-*.png` antes/como condição da Aprovação de Design;
  inclui contraste)
- P3-R2 — Rota viva `/combo/discovery` avaliada só via fonte (sem sessão autenticada), como em A/B.
  (disposition: verificação autenticada fica para T6/verificação do apply)
- P3-R3 — Mobile re-renderiza com bytes diferentes entre fix e re-gate (desktop determinístico).
  (disposition: informativo; sem impacto funcional — 31/31 PASS nas duas rodadas; se o apply
  alegar estabilidade de screenshot, comparar mesma sessão)
- P3-R4 — `data-testid="start-sweep"`, simulador "só protótipo", `href="#"` com preventDefault —
  artefatos de mock já aceitos em A/B. (disposition: aceitar; apply deriva modo do sweep)

## Veredito: PASS

P1-B corrigido e re-gatado em escopo de dialog nas 2 viewports (62/62, servido remoto);
servido == local == digest alegado; evidência desktop 1440 real + modal distinto; pequenos
incorporados e re-testados; contrato do apply verificado por leitura. Nada foi movido
(branch, Status, process_event intactos). Resta passada visual humana nos PNGs (P3-R1, fora do
meu alcance) antes da Aprovação de Design. Snapshot: este arquivo,
`.impeccable/critique/852-card-852-descoberta-tres-modos-regate-2026-09-06T18-36Z.md`.
