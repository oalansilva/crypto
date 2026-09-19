# Snapshot Impeccable — #969 (T7)

Change: `card-969-discovery-selo-go-nogo`  
Rota: `/combo/discovery` · `UI impact: affected` · `surface: existing`

**Verdict da dupla: PASS.** Zero P0/P1. Sem rework.

- Assessment A: `.impeccable/critique/969-card-969-discovery-selo-go-nogo-assessment-A.md`
- Assessment B: `.impeccable/critique/969-card-969-discovery-selo-go-nogo-assessment-B.md`
- Proto: https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/
- Digest: `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` (50488 bytes, disco == HTTPS)

Contrato visível: o selo GO/NO-GO da Descoberta deixa o piso Combo (100 trades / Sharpe 0,8 / 20 holdout). BTC `RS-E0E30719CC` mostra **GO**; holdout mau mostra **NO-GO** com motivo Holdout; treino fraco mostra **NO-GO** com motivo Treino; Baixa amostra não leva chip. Promover no NO-GO elegível permanece. Mesma regra em 4h e short. Combo ao salvar favorito fora.

P3 aceites no Apply (não bloqueiam T7): Montar condensado; chip muted/full-width no mobile; mock incompleto (Amostra insuficiente / fail-closed / PF-only); Ação clipada; default Decidir ≠ vivo Montar.

Gist OpenSpec **não** é a crítica. Alan abre este arquivo no T7.
