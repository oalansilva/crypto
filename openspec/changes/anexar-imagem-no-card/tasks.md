# Tasks: Anexar imagem no card

## Change ID
b1aaddbd-7a3b-4408-ab63-83131813ab47

## Stage
PO → Alan approval

## Tasks

### 1. Backend - API de Upload
- [ ] 1.1 Criar endpoint POST para upload de imagem
- [ ] 1.2 Definir storage (local/cloud)
- [ ] 1.3 Implementar validação de tipo (jpg, png, gif, webp)
- [ ] 1.4 Implementar limitação de tamanho (5MB)
- [ ] 1.5 Associar imagem ao card no banco

### 2. Frontend - Formulário de Criação
- [ ] 2.1 Adicionar componente de upload no formulário de criação de card
- [ ] 2.2 Implementar preview da imagem selecionada
- [ ] 2.3 Integrar com endpoint de upload
- [ ] 2.4 Tratar erros de upload (tipo inválido, tamanho excedido)

### 3. Frontend - Visualização do Card
- [ ] 3.1 Exibir imagem anexada na visualização do card
- [ ] 3.2 Layout responsivo para imagem

### 4. QA
- [ ] 4.1 Testar upload de imagem válida
- [ ] 4.2 Testar rejeição de tipo inválido
- [ ] 4.3 Testar rejeição de arquivo muito grande
- [ ] 4.4 Validar exibição em diferentes dispositivos

## Dependências
- Task 1.1-1.5 devem ser concluídas antes de 2.1-2.4
- Task 2.1-2.4 devem ser concluídas antes de 3.1-3.2

## Status
Planejamento PO concluído. Aguardando Alan approval para iniciar DEV.

