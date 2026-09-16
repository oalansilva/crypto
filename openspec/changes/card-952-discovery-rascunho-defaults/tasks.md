# Tasks — card-952-discovery-rascunho-defaults

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Defaults do rascunho novo

- [x] 1.1 — Ao carregar o catálogo num rascunho que **não** é restore, **não** pré-escolher `flat.slice(0, 3)` nem `list.slice(0, 4)`. Templates e Símbolos ficam em 0, sem chips. Fidelidade ao proto.
- [x] 1.2 — Estado inicial de Time Frames = `['1d']` (só **1 dia**). **4 horas** desmarcado e marcável.

## 2. Novo rascunho e restore

- [x] 2.1 — `newDraft` aplica os mesmos defaults: limpa Templates/Símbolos/`committedSelection` e Time Frames só em 1 dia. Hoje o botão só libera o configurador.
- [x] 2.2 — `hydrateFromSweep` continua a reutilizar os eixos gravados. **Não** aplicar os defaults novos por cima. Se `axes.timeframes` vier vazio, **não** cair em `['4h', '1d']`.

## 3. Bloqueio e fora

- [x] 3.1 — Com Templates ou Símbolos vazios, «Falta fazer» e início bloqueado permanecem (já existem). Sem disparar varredura vazia. Direção, período e ranking intactos.
- [x] 3.2 — Fora: Combo; catálogo; preflight/limite/promoção; redesenho das três opções.
- [x] 3.3 — Testes: primeira abertura vazia + só 1 dia; «Novo rascunho» limpa; restore preserva eixos; restore sem TF não inventa 4h+1d; 4 horas ainda marcável; início bloqueado com vazio. Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 3.4 — `openspec verify` desta change.
