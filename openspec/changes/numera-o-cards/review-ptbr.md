# Revisão PT-BR — numera-o-cards

## Resumo

Esta change adiciona uma **numeração automática e estável** para os cards do Kanban, para facilitar referência rápida no dia a dia.

Exemplo:
- `#1`
- `#2`
- `#3`

## O que entra
- gerar um número sequencial automático para cada card
- mostrar esse número no card e no detalhe
- manter o número estável após reload/reabertura
- entregar o número também no runtime/API usado pelo board
- novos cards recebem automaticamente o próximo número livre

## O que não entra
- renumerar cards antigos manualmente
- mudar a ordem dos cards por causa da numeração
- numeração por coluna
- substituir slug/id técnico atual

## Decisão de PO
- a numeração deve ser **simples, visível e estável**
- o número serve como identificador humano, não como driver de workflow
- a primeira versão deve evitar regras complexas de renumeração
- não precisa gate de DESIGN separado; a UI é um ajuste pequeno sobre o card já existente

## Próximo gate
- Alan approval do pacote de planning para DEV implementar persistência + exibição da numeração
