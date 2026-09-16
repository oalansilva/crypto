## Why

Depois de excluir um favorito, a Descoberta continua a tratar o candidato como favorito ativo: a grelha mostra **Já existe** / **Equivale ao favorito ativo N** (ou **Favorito tier 3**) e a promoção recusa com «já duplica favorito ativo» para um N que já não existe. O administrador fica preso a uma mentira da lista.

## What Changes

- Depois de excluir o favorito, a linha que dizia **Já existe** / **Equivale ao favorito ativo N** volta a **Promover**, sem nota de favorito (Q1).
- A linha **Favorito tier 3** da mesma exclusão também volta a **Promover** (Q2).
- Tentar promover é aceite (cria um favorito novo); grelha e promoção dizem a mesma verdade.
- A linha permanece na varredura; não some só porque o favorito foi excluído.
- Decidir e Acompanhar (se a mesma linha ainda estiver visível) mostram a mesma verdade.
- Favorito **ainda** na lista: **Já existe** / **Equivale ao favorito ativo N** e o bloqueio permanecem (não regressão).
- **Excluir** na grelha continua a descartar só o candidato desta varredura; não apaga favorito.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-deduplication`: exclusão real de favorito deixa de ser match ativo; não há nota histórica visível; resultados gravados como `duplicate_favorite` / `already_promoted` apontando para um N inexistente passam a únicos e promovíveis.
- `discovery-leaderboard`: a grelha (Decidir e parciais do Acompanhar, quando visíveis) mostra **Promover** nesses órfãos — não **Já existe**, não **Equivale ao favorito ativo N**, não **Favorito tier 3**, não nota histórica; linha com favorito vivo permanece **Já existe**.
- `discovery-promotion`: promoção não recusa «já duplica favorito ativo» / `already_promoted` para um N que já não existe; confirmação cria um favorito novo.

## Impact

- Backend: reclassificar resultados que apontam para o favorito apagado **e** reler existência do favorito na hora do leaderboard e da promoção (os dois). Sem inventar soft-delete / arquivar na lista de favoritos.
- Frontend: `DiscoveryPage.tsx` só precisa reflectir o estado já verdadeiro do payload; sem copy nova de «já foi favorito».
- Specs canónicas: `openspec/specs/discovery-deduplication`, `discovery-leaderboard`, `discovery-promotion`.
- Protótipo: `frontend/public/prototypes/card-948-discovery-deleted-favorite/`.
- Fora: Excluir da grelha; nota histórica; sumir da grelha; só corrigir Já existe; bloqueio correcto se o favorito ainda existe; limpeza operacional pontual em PROD; ranking/Preflight/worker/filtros/selo/amostra; redefinir equivalência; redesign dos três modos.
