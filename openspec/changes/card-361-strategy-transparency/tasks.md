## 1. Contrato seguro e catálogo de estratégias

- [x] 1.1 Separar autorização de detalhe funcional autenticado da autorização de segredos administrativos, preservando os gates de autenticação/ownership e a allowlist de campos.
- [x] 1.2 Revisar `PUBLIC_STRATEGY_DISPLAY_NAMES` e `PUBLIC_STRATEGY_DESCRIPTIONS` para eliminar duplicidades, copy genérica e referências não executadas, mantendo direção, timeframe e comportamento distinguíveis.
- [x] 1.3 Garantir que o manifesto canônico serialize indicadores, parâmetros efetivos, regras de entrada/saída e risco apenas quando comprovados, com estados explícitos de indisponibilidade/mismatch.
- [x] 1.4 Atualizar testes backend do redactor, catálogo, identidade, allowlist e cobertura de explicações para todos os templates ativos.

## 2. Superfície compartilhada de transparência

- [x] 2.1 Criar/ajustar o adaptador e componente reutilizável de transparência para exibir identidade, tese, direção/timeframe, regras, indicadores, risco e parâmetros efetivos com rótulos de trader.
- [x] 2.2 Integrar a variante compacta no card expandido do Monitor, removendo a experiência `Protegido/Oculto` para usuários autenticados e mantendo controles fora do escopo de detalhe funcional.
- [x] 2.3 Integrar a variante completa em Favoritos/Resultados e no gráfico/modal, garantindo paridade de manifesto com o Monitor e mensagens explícitas para indisponibilidade.
- [x] 2.4 Atualizar tipos, formatadores e testes frontend/E2E para estados disponível, recolhido, indisponível, mismatch, long/short e conteúdo responsivo.

## 3. Validação e integração

- [x] 3.1 Executar testes focados de backend/frontend, build e `openspec validate --all`, corrigindo qualquer falha antes de avançar.
- [x] 3.2 Executar revisão read-only do diff exato, mover o card por Code Review/QA e registrar evidências de aceite.
- [x] 3.3 Executar `/opsx:verify`, QA visual Playwright desktop/mobile e validação da URL DEV após restart.
- [x] 3.4 Integrar a branch em `develop`, confirmar o bundle/resultado novo no DEV e mover o card para `Done` técnico.
