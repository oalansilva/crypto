# Tasks — card-954-discovery-acompanhar-stale

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Parciais e progresso no mesmo intervalo

- [x] 1.1 — Enquanto a run activa for não-terminal, o intervalo que já pede o sweep activo também relê as parciais top-5 desta `sweep_id`. Se o candidato já existe, a linha aparece; «Parciais ainda carregando» não permanece.
- [x] 1.2 — O contador do Acompanhar reflecte `processed`/`total` desta run. Não fica 0 de N se já processou.

## 2. Fecho desta run → Decidir desta

- [x] 2.1 — Quando o GET desta run vier terminal: aplicar state/contadores; `viewSweep` = esta run (não a do Histórico); hidratar o leaderboard desta `sweep_id`; modo visível = Decidir; Acompanhar deixa de estar ligado.
- [x] 2.2 — Sem ecrã «Acompanhar já concluída». Sem exigir clique ou F5. Abrir Histórico de outra run não conta como conserto.
- [x] 2.3 — Payload terminal desta `sweep_id` não é descartado (P3: skip `updated_at` / poll em voo).

## 3. Fora e verificação

- [x] 3.1 — Fora: ecrã Acompanhar concluída; unir a outra run; #952/#948/#949/#916/#664; worker; Combo/Favoritos/Monitor; modos novos.
- [x] 3.2 — Testes: a meio, parciais com linha + processed ≠ 0; no tick terminal, Decidir desta com o candidato e Acompanhar off. Playwright `/combo/discovery` contra o proto (desktop+mobile).
- [x] 3.3 — `openspec verify` desta change.
