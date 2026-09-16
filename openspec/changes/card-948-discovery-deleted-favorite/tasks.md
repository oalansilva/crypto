# Tasks — card-948-discovery-deleted-favorite

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Reclassificar no DELETE do favorito

- [x] 1.1 — Ao apagar um favorito N, resultados com `dedup_state` `duplicate_favorite` ou `already_promoted` e `dedup_reference` = N passam a current `unique` (reference limpo). Append-only em `discovery_dedup_evidence`. Sem nota histórica. Sem soft-delete do favorito.
- [x] 1.2 — A linha da varredura **não** é apagada neste caminho. `Excluir` da grelha continua a não apagar favorito.

## 2. Reler na hora (leaderboard e promoção)

- [x] 2.1 — GET de Decidir/parciais: se o estado gravado aponta para um N que já não existe, o payload corrente é `unique` (Promover), mesmo que o hook 1.1 ainda não tenha corrido.
- [x] 2.2 — `promote_result`: não recusar `duplicate` / não devolver `already_promoted` para N MISSING. Confirmar cria favorito **novo** (número novo). Relida da lista viva por reference e por `strategy_identity_key`.
- [x] 2.3 — Favorito **vivo**: `duplicate_favorite` + bloqueio **Já existe** / **Equivale ao favorito ativo N** permanecem (não regressão). Outros bloqueios reais (baixa amostra, insuficiente, discarded) intactos.

## 3. Grelha (reflectir o payload)

- [x] 3.1 — Decidir: órfão Já existe → **Promover**, sem **Equivale ao favorito ativo N**; órfão Favorito tier 3 → **Promover**; linha permanece. Fidelidade ao proto.
- [x] 3.2 — Acompanhar (se a mesma linha ainda visível): a mesma verdade que Decidir. Montar sem delta. Sem copy nova de «já foi favorito».

## 4. Fora e verificação

- [x] 4.1 — Fora: Excluir da grelha; nota histórica; sumir da grelha; só corrigir Já existe; equivalência; ranking/Preflight/worker/filtros/NO-GO/amostra; limpeza pontual PROD.
- [x] 4.2 — Testes: DELETE reclassifica; GET mente zero com N MISSING; POST promove órfão; N vivo ainda bloqueia; discard da grelha não apaga favorito. Playwright `/combo/discovery` contra o proto (desktop+mobile).
- [x] 4.3 — `openspec verify` desta change.
