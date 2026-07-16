## 1. Contrato frontend

- [x] 1.1 Preservar metadados tipados de `logic_blocks` no normalizador de transparência.
- [x] 1.2 Criar helper direcional que sempre produz “Quando compra” e “Quando vende”, com fallback seguro.

## 2. Experiência do usuário

- [x] 2.1 Criar overview reutilizável das regras permanentes conforme tokens e densidade do `DESIGN.md`.
- [x] 2.2 Integrar o overview ao card expandido do Monitor, independente do sinal/posição atual.
- [x] 2.3 Integrar o overview ao disclosure de trades abertos/fechados em Monitor e Favoritos.
- [x] 2.4 Preservar teclado, foco, ordem de leitura, alvo de 44px e layout sem overflow em desktop/mobile.

## 3. Testes e fechamento

- [x] 3.1 Cobrir normalização, `long`, `short`, posições distintas e fallback legado em testes frontend.
- [x] 3.2 Validar build, lint, OpenSpec e checklist básico de acessibilidade.
- [x] 3.3 Validar Playwright funcional e visual em desktop/mobile.
- [x] 3.4 Registrar evidências de Code Review, QA, PR, integração em `develop`, restart e runtime no card #293.

Nota: usar as skills do projeto em `.codex/skills` para frontend, testes, depuração, acessibilidade e Playwright quando aplicáveis.
