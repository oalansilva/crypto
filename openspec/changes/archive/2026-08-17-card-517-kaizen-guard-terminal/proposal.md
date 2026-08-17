## Why

O check `OpenSpec terminal changes` do `scripts/release-guard` produz falso negativo em dois casos comuns. Ele só associa uma change ao card quando o diretório começa com `card-<n>` ou `issue-<n>` e descarta a change antes de consultar o board quando existe qualquer task pendente. Na release de 2026-08-14, seis changes completas com nomes sem id e a change `card-509-*`, então ainda in-progress, não foram sinalizadas mesmo com seus cards em `Pronto`. O pacote terminou com sete changes fora do alcance efetivo do guard.

## What Changes

- Mapear change ativa para card por duas rotas determinísticas: id no nome e fallback por semelhança de título usando o snapshot único do board, priorizado pelos ids normalizados de `RELEASE_CARDS`.
- Avaliar toda change ativa mapeada cujo card esteja em `Pronto` ou `Cancelado`, sem usar conclusão das tasks como filtro de entrada.
- Informar no achado se a change está `complete` ou `in-progress`, além da fonte do mapeamento.
- Emitir warning em `audit` e blocker em `post`; uma change ativa de card terminal do pacote sempre bloqueia o closeout estrito.
- Cobrir o comportamento com testes determinísticos e `gh` falso, sem aumentar o número de snapshots remotos por execução.
- Após aprovação e autorização operacional, arquivar via `/opsx:bulk-archive` as dez changes terminais que continuam ativas no snapshot atual e confirmar que o audit não mantém warnings desse tipo.

## Capabilities

### Modified Capability

- `openspec-archive-hygiene`: ampliar o mapeamento change→card e a detecção do guard para changes completas e in-progress de cards terminais.

## Impact

- **Código afetado na implementação:** `scripts/release-guard` e `backend/tests/integration/test_release_guard.py`.
- **Operação afetada:** `release-guard audit|post` e o closeout/archive de OpenSpec.
- **UI impact: none** — trata-se de script operacional e higiene de artefatos; nenhuma tela, rota, componente, copy ou interação visual é criada ou alterada.
- **Sem impacto em runtime de produto:** nenhuma mudança de API, frontend, banco, migration ou serviço.
