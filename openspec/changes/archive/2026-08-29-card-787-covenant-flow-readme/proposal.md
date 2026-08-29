## Why

Quem abre o GitHub privado [`oalansilva/covenant-flow`](https://github.com/oalansilva/covenant-flow) (visitante convidado ou Alan daqui a meses) não consegue dizer o que o Covenant Flow *é*: o README actual (~37 linhas, inglês, tag `v1.1.1`) começa em clone / `install.sh --init` / `--pin` / Layout. Card [#787](https://github.com/oalansilva/crypto/issues/787).

## What Changes

- Reescrita de **um** `README.md` na raiz do produto `oalansilva/covenant-flow`, **em PT-BR**. Ordem: **estranho primeiro** (o que o produto resolve; quem usa; núcleo vs consumidor vs overlay; canal v1 = copiar + commitar; primeiro consumidor = Cripto `oalansilva/crypto`; quatro clientes por nome e Auto vs cooperativo), **depois** walkthrough das 12 colunas (uma linha cada + uma frase dos 3 gates humanos, sem IDs T0–T17), **depois** Install / Pin / Layout em PT-BR. O clone **não** é o primeiro parágrafo.
- Description do GitHub no **mesmo entregável**, exactamente: `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)` (substitui o texto EN actual).
- Exemplo `--pin` no README = **tag do próprio entregável**. Hoje o pin live é `v1.1.1`; este card recomenda patch `v1.1.2` no produto após o commit do README, e o exemplo passa a `v1.1.2`. Consumidor Cripto só re-pin depois desse bump.
- `install.sh --pin` continua a **não** copiar o README para o consumidor. Sem segundo ficheiro. Sem reescrita de skills/hooks/yaml/`install.sh`/`AGENTS.md`/adapters. Sem código de produto Cripto. Sem reabrir #773 (Pronto) ou #784 (Done).
- Não é **BREAKING**: overlay schema, canal v1, payload do pin e lei T0–T17 permanecem.

## Capabilities

### New Capabilities

- (nenhuma) — o produto já existe (#773); este card só orienta o estranho no README e na description do GitHub.

### Modified Capabilities

- `covenant-flow`: README do produto orienta o estranho em PT-BR **antes** de Install; description GitHub congelada na frase PT-BR; exemplo `--pin` = tag do entregável; o cenário existente «Product README does not require host backup paths» permanece; `--pin` continua a **não** copiar `README.md` para o consumidor.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — `README.md` na raiz + `gh repo edit --description` com a frase congelada; tag patch `v1.1.2` nesse commit; depois `implantar --pin v1.1.2` no Cripto só para alinhar overlay `pin` (payload do pin **não** inclui README).
- Não toca `backend/` / `frontend/src/` de produto, skills, hooks, yaml, `install.sh`, `AGENTS.md` gerado, adapters, LICENSE, homepage, overlay no repo do produto, `CONTRIBUTING.md` / segundo ficheiro.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A. Sem HTML.
- Origem: issue #787 (DoD grelhado; Q1–Q8 congeladas). Relacionado e **não** reaberto: #773, #784, #608.
