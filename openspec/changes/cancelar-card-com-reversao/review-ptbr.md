# Resumo - Cancelar card com reversão

## Problema
Cards podem ser excluídos permanentemente, sem possibilidade de recuperação.

## Solução
- Cards não podem mais ser excluídos
- Botão "Cancelar" move card para status "Canceled"
- Cards cancelados ficam ocultos do board ativo
- Botão "Reativar" permite trazer card de volta ao Pending

## Escopo
- Backend: endpoint de reativação de cards
- Frontend: botão Cancelar e Reativar na UI
- Testes automatizados

## Próximo passo
Aprovação → DEV → QA → Homologação
