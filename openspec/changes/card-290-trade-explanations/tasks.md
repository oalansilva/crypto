## 1. Contrato e transparência

- [x] 1.1 Adicionar schemas tipados para regras públicas, evidências e explicações de trades/sinais.
- [x] 1.2 Gerar resumos específicos de entrada, saída e risco para todo template ativo sem expor lógica bruta.
- [x] 1.3 Criar builder puro que alinha entrada/saída a séries históricas e trata `long`, `short`, stop e indisponibilidade.

## 2. Integração backend

- [x] 2.1 Enriquecer `GET /favorites/{id}/trades` com explicações por trade sem alterar campos existentes.
- [x] 2.2 Enriquecer o payload do Monitor e seu histórico de sinais com a mesma explicação pública.
- [x] 2.3 Preservar explicações allowlisted na redaction do usuário comum e bloquear segredos/diagnósticos.

## 3. Experiência Monitor

- [x] 3.1 Tipar o contrato no frontend e criar componente acessível “Entenda este trade”.
- [x] 3.2 Integrar o disclosure a trades abertos/fechados e o resumo contextual ao Monitor.
- [x] 3.3 Aplicar `DESIGN.md`, sem novas colunas horizontais, com semântica `long`/`short`, foco e mobile responsivo.

## 4. Testes e validação

- [x] 4.1 Adicionar testes backend de catálogo, valores históricos, saída lógica, stop, `long`/`short` e indisponibilidade.
- [x] 4.2 Adicionar testes frontend de renderização, disclosure, teclado e fallback seguro.
- [x] 4.3 Rodar testes focados, build, validação OpenSpec, checklist de acessibilidade e Playwright visual desktop/mobile.
- [x] 4.4 Registrar evidências de Code Review, QA, PR, integração em `develop`, restart e runtime no card #290.

Nota: usar as skills do projeto para arquitetura, testes, depuração, frontend, acessibilidade e Playwright quando aplicáveis.
