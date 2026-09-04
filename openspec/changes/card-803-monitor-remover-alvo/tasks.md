# Tasks: Monitor — remover alvo derivado (card #803)

> Fonte: proposal + design § Apply contract. Só após `Status=Pronto para Dev` (T7). Proto já fechado em Design.

## 1. Spec canónica

- [x] 1.1 Aplicar o delta `openspec/changes/card-803-monitor-remover-alvo/specs/opportunity-monitor/spec.md` em `openspec/specs/opportunity-monitor/spec.md`: HOLD sem `alvo`, ordem aceite, card+modal iguais, sem cálculo derivado; cenário stale sem linha `alvo`; EXIT sem `alvo`.

## 2. Frontend — card HOLD (aceite 1, 3, 5)

- [x] 2.1 `OpportunityCard.tsx`: remover `alvoPrice` / `alvoStr` e o par `<dt>alvo</dt><dd>`. Ordem visível HOLD: `distância até saída` → `distância até stop` → `stop` → `entrada` → `preço atual`. Sem placeholder, tooltip ou número equivalente.
- [x] 2.2 Stale/null: campos afetados continuam `indisponível — dado não confiável`; não renderizar “alvo indisponível”. Manter frase de cenário e copy EXIT.

## 3. Frontend — modal (aceite 2, 4)

- [x] 3.1 `ChartModal.tsx`: remover `chartAlvoPrice` e a row `Alvo`. Mesmo recorte e ordem do card no HOLD; EXIT permanece preço atual + `Risco residual`, sem `alvo`.

## 4. Testes (aceite 1–5)

- [x] 4.1 Grep `alvo` / `Alvo` / `alvoPrice` / `chartAlvoPrice` em `frontend/tests` e unitários; atualizar asserts que ainda esperam a linha (Design-time: nenhum e2e; só os dois componentes).
- [x] 4.2 Cobrir HOLD confiável (ordem sem alvo), HOLD stale (indisponível, sem linha alvo), EXIT (residual, sem alvo), coerência card↔modal.

## 5. Proto (já em Design)

- [x] 5.1 Protótipo clone+delta em `frontend/public/prototypes/card-803-monitor-remover-alvo/index.html` (URL DEV). Apply não reescreve o HTML.
