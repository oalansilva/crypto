# Review PT-BR — implementa-na-interface-inicial

## O que muda

**Mudar a interface inicial (`/`) de um hub de atalhos para um "cockpit diário"** que ajuda o usuário a entender o contexto atual, identificar a próxima ação e acessar os fluxos principais — tudo na primeira tela.

## Decisões de design

1. **Home como cockpit (não mais só hub)** —分层: orientação + ações primárias → cards de status/resumo → seções contextuais
2. **Dados reais ou fallbacks claros** — não exigir novos endpoints de backend; usar dados já acessíveis no frontend com estados de loading/fallback explícitos
3. **Mobile responsivo** — seções empilham por prioridade; labels legíveis e tappeáveis
4. **Sem analytics pesados** — escopo controlado: alinhamento visual e de conteúdo, sem novos endpoints

## Escopo de implementação (tasks)

- Alinhar `HomePage.tsx` com a hierarquia do design
- Consolidar blocos de saúde, snapshots e seções contextuais com fallbacks claros
- Cobertura de testes (unitários + E2E Playwright desktop/mobile)
- Validação visual via QA checklist

## Status do review

- Proposal ✅ | Design ✅ | Specs ✅ | Tasks ✅
- Aguardando aprovação do Alan para avançar para DEV
