# Revisão (PT-BR) — monitor-asset-type-filter

## Objetivo
Adicionar no `/monitor` um filtro simples de **Asset Type** para visualizar apenas:
- **All** (padrão)
- **Crypto**
- **Stocks**

## Onde fica
No topo do `/monitor`, junto dos filtros existentes (Symbol/Tier/List etc.).

## Persistência
Não precisa salvar preferência. É um filtro temporário (por sessão/estado da página).

## Critérios de aceite
- Filtro aparece no topo.
- Trocar o filtro atualiza a lista imediatamente.
- “Crypto” mostra apenas símbolos com formato `AAA/BBB`.
- “Stocks” mostra apenas símbolos sem `/`.
- “All” mostra tudo.

## Próximo passo
Alan aprovar a change pra eu implementar.
