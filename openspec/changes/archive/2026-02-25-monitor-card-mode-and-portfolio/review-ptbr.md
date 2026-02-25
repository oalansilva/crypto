# Revisão (PT-BR) — monitor-card-mode-and-portfolio

## O que é
Melhorar o Monitor para ficar mais útil no dia a dia no celular, reduzindo ruído e permitindo alternar o conteúdo de cada card.

## Principais funcionalidades
1) **Em carteira (In Portfolio)**
- Marcar por **símbolo** quais ativos você realmente quer acompanhar.
- Por padrão, o Monitor mostra só os que estão **Em carteira**.
- Você consegue alternar para ver **Todos** quando quiser.

2) **Modo do card por símbolo (Preço vs Estratégia)**
- Cada card terá um ícone para alternar entre:
  - **Preço**: candles + métricas básicas
  - **Estratégia**: dados de estratégia/status (o que você já tem hoje)
- Essa escolha é **salva no backend**, então persiste entre celular/desktop.

## Persistência (backend)
- Preferências por símbolo:
  - `in_portfolio`: true/false
  - `card_mode`: price/strategy

## Como testar (manual rápido)
1) Abrir `/monitor`.
2) Ver que por padrão aparece só a lista "Em carteira".
3) Marcar/desmarcar um ativo como Em carteira e recarregar a página → deve persistir.
4) Em um card, alternar Preço/Estratégia e recarregar → deve persistir.
5) Trocar o filtro "Em carteira" ↔ "Todos".

## Observações
- Sem depender de localStorage: tudo persistido no backend.
- Mantém o dataset baseado em Favoritos.
