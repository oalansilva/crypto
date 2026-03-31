## 1. Frontend surface removal

- [x] 1.1 Remover as rotas `/lab` e `/lab/runs/:runId` do roteador frontend
- [x] 1.2 Remover links, atalhos e labels do Lab da navegação global e da Home
- [x] 1.3 Remover páginas, componentes, hooks e tipos exclusivos do fluxo Lab no frontend

## 2. Backend surface removal

- [x] 2.1 Remover o registro das rotas e superfícies runtime exclusivas do Lab no backend
- [x] 2.2 Remover endpoints, SSE de logs, trace viewer e serviços exclusivos do Lab
- [x] 2.3 Limpar imports, referências e código morto deixados pela remoção do Lab

## 3. Testes, docs e reconciliação

- [x] 3.1 Remover ou ajustar testes que dependem das rotas, páginas ou APIs do Lab
- [x] 3.2 Atualizar documentação ativa e referências internas para não instruírem uso do Lab como capability suportada
- [x] 3.3 Validar que frontend e backend continuam coerentes sem referências ativas ao Lab

## 4. Verificação final

- [x] 4.1 Rodar os checks relevantes de build/test para confirmar ausência de imports órfãos e rotas quebradas
- [x] 4.2 Verificar manualmente que Home e navegação não expõem mais o Lab
- [x] 4.3 Usar skills do projeto quando aplicável durante a implementação e validação, especialmente para frontend, testes e debugging
