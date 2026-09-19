# Snapshot Impeccable — #970 (T7)

Change: `card-970-favoritos-carga-nao-vazio`  
Rota: `/favorites` · `UI impact: affected` · `surface: existing`

**Verdict da dupla: PASS.** Zero P0/P1. Sem rework.

- Assessment A: `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio-assessment-A.md`
- Assessment B: `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio-assessment-B.md`
- Proto: https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/
- Digest: `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` (43492 bytes, disco == HTTPS)

Contrato visível: com sessão válida e favoritos crypto gravados, `/favorites` lista os pares (não 0 / «Nenhuma estratégia favorita encontrada»). Erro de carga mostra falha + «Tentar de novo» e permanece na tela. Filtro sem resultado ≠ catálogo vazio. Monitor deixa de tratar falha como «Nenhum ativo disponível no monitor». Início não muda copy.

P3 aceites no Apply (não bloqueiam T7): `side-tab`; truncagem; alvos do retry; strip de velas na lista; header «Todas N» no erro.

P2 residual: clip 390 no extra Monitor (scroll; sem redesenhar).

Gist OpenSpec **não** é a crítica. Alan abre este arquivo no T7.
