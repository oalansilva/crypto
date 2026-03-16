# Proposal: Anexar imagem no card

## Problema / Necessidade

O usuário deseja ter a possibilidade de, ao criar um card, anexar uma imagem para deixar claro o problema ou necessidade. Atualmente, não há essa funcionalidade no sistema de criação de cards.

## Solução Proposta

Adicionar funcionalidade de upload de imagem no momento da criação de cards, permitindo:
- Upload de imagem durante a criação do card
- Armazenamento da imagem associada ao card
- Exibição da imagem na visualização do card

## Escopo

### Frontend
- Adicionar campo de upload de imagem no formulário de criação de cards
- Suporte a formatos comuns de imagem (JPG, PNG, GIF, WebP)
- Preview da imagem antes do envio
- Exibir imagem anexada na visualização do card

### Backend
- Endpoint para upload de imagem
- Armazenamento da imagem (local ou cloud)
- Associação da imagem ao card criado

## Critérios de Aceite
- [ ] Usuário pode selecionar e fazer upload de uma imagem ao criar card
- [ ] Imagem é exibida corretamente na visualização do card
- [ ] Upload limita tamanho máximo (ex: 5MB)
- [ ] Sistema rejeita formatos não suportados
- [ ] Interface é responsiva e funciona em mobile

## Dependências
- Sistema de storage (local ou cloud)
- Validação de tipo e tamanho de arquivo

## Estimativa
Média complexidade - requer adjustments no frontend e backend.

## Stage
PO

## Status
Aprovado

