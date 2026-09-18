# Snapshot Impeccable — #967 (T7)

Change: `card-967-discovery-recupera-varredura-ativa`  
Rota: `/combo/discovery` · `UI impact: affected` · `surface: existing`

**Verdict da dupla: PASS.** Zero P0/P1. Sem rework.

- Assessment A: `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa-assessment-A.md`
- Assessment B: `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa-assessment-B.md`
- Proto: https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/
- Digest: `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` (42186 bytes, disco == HTTPS)

Contrato visível: com varredura viva no servidor e sessão autenticada, a Descoberta reconstitui **sozinha** o Acompanhar (número verdadeiro, não «#—», e progresso). Banner «Não foi possível verificar a varredura ativa» ausente no caminho feliz. «Tentar novamente» só se a automática falhar de novo. Logout deixa de ser o conserto.

P3 aceites no Apply (não bloqueiam T7): Montar condensado; overflow 390; banner info de restore; markup `DELTA:end`; backoff/`hydrateFromSweep`.

Gist OpenSpec **não** é a crítica. Alan abre este arquivo no T7.
