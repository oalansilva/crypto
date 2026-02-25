# Revisão (PT-BR) — favorites-asset-type-filter

## O que é
Adicionar um filtro **Asset Type** na tela **Favorites** para separar rapidamente:
- **All** (padrão)
- **Crypto** (símbolos com `/`, ex: `BTC/USDT`)
- **Stocks/Ações** (símbolos sem `/`, ex: `NVDA`)

## Por que
Hoje a lista mistura cripto e ações. Isso deixa a leitura/organização mais lenta (principalmente no celular). O dropdown permite focar no que você quer ver.

## O que muda na prática
- Na barra de filtros do Favorites, aparece um novo dropdown **Asset Type**.
- Ao mudar o dropdown, a lista/tabela é filtrada imediatamente.
- Funciona tanto na visualização **desktop** (tabela) quanto no **mobile** (cards).

## Como testar (manual rápido)
1) Abrir: `http://72.60.150.140:5173/favorites`
2) Asset Type = **All** → deve mostrar ações + cripto.
3) Asset Type = **Crypto** → deve mostrar apenas símbolos com `/`.
4) Asset Type = **Stocks** → deve mostrar apenas símbolos sem `/`.

## Notas
- Não há mudança no backend.
- A regra de classificação é simples (contém `/` ou não). Se no futuro quiser algo mais robusto, dá pra evoluir para um campo explícito no favorito.
