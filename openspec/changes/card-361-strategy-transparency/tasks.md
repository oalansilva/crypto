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

## 4. Rework após revisão de aceite

- [x] 4.1 Tornar a humanização de regras complexas completa, preservando condições, agrupamentos, comparadores e thresholds públicos sem fallback `partial` por quantidade.
- [x] 4.2 Resolver direção pelo parâmetro efetivo e, na ausência dele, pelo template executado; cobrir estratégias Short e texto de risco.
- [x] 4.3 Revisar nomes e descrições de todo o inventário visível com copy específica de tese, contexto, lado, timeframe e diferenciação, removendo fórmulas genéricas repetidas.
- [x] 4.4 Versionar inventário auditável de todos os templates ativos do PostgreSQL e testar identidade, direção, indicadores, parâmetros e regras completas para cada entrada.
- [x] 4.5 Atualizar testes backend/frontend/E2E necessários, executar validação focada, build, OpenSpec global, review do diff, QA visual e runtime DEV.

## 5. Correção de regressão na descrição de Favoritos

- [x] 5.1 Separar o comportamento visual do nome e da descrição em Favoritos, permitindo quebra integral da descrição sem alterar a compactação do nome.
- [x] 5.2 Cobrir desktop e mobile com teste E2E que prove texto completo, ausência de ellipsis/clipping e ausência de overflow horizontal.
- [ ] 5.3 Executar validação OpenSpec, testes focados, build, review do diff, QA visual e runtime DEV após integração.
