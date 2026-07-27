## Context

Home e Carteira já consomem a chave Binance do usuário logado via `GET/PUT/DELETE /api/user/binance-credentials`. O formulário completo (API Key, API Secret, salvar/remover) vive em `ExternalBalancesPage`. Preferências do sistema (`/system/preferences`) são admin-only e não cobrem credenciais por usuário. Perfil (`/profile`) cuida só de nome/e-mail.

## Goals / Non-Goals

**Goals:**
- Oferecer tela autenticada de preferências do usuário com o bloco Credenciais Binance.
- Extrair o formulário para um componente reutilizável e usá-lo nessa tela.
- Na Carteira, trocar o formulário completo por status + link para preferências.
- Manter o mesmo contrato de API e as regras de segurança (read-only, secret não retornado em claro).

**Non-Goals:**
- Alterar endpoints de balances ou lógica de PnL.
- Pedir senha da conta Binance.
- Mudar Preferências do sistema (admin).
- Trocar provider de exchange.

## Decisions

1. **Rota `/preferences` (UserPreferencesPage)**  
   - Em vez de sobrecarregar `/profile` (identidade) ou `/system/preferences` (admin).  
   - Alternativa rejeitada: só Profile — mistura identidade com segredos de exchange.

2. **Componente `BinanceCredentialsForm`**  
   - Extrair da Carteira para `frontend/src/components/binance/BinanceCredentialsForm.tsx`.  
   - Preferências usam o formulário completo; Carteira usa modo compacto (status + CTA `Configurar em Preferências`).

3. **Navegação**  
   - Item `Preferências` na seção de conta (todos os usuários logados), ícone Settings.  
   - Admin mantém `Preferências` do sistema com label distinto (`Preferências do sistema`) para evitar colisão.

4. **Backend**  
   - Sem mudança de contrato; reutilizar rotas e testes existentes.

5. **DESIGN.md**  
   - Tokens existentes (`page-card`, `section-title`, inputs/borders do app); manter copy e hierarquia do bloco atual.

## Risks / Trade-offs

- [Usuário procura form na Carteira] → Status + link claro para `/preferences`; empty/erro de balances continua orientando configuração.
- [Colisão de label "Preferências" no nav admin] → Labels distintos: usuário vs sistema.
- [Regressão visual da Carteira] → Atualizar baseline Playwright `wallet-*` e cobrir nova tela `preferences-*`.

## Migration Plan

1. Ship front com nova rota + componente + ajuste Carteira.
2. Sem migração de dados (credenciais já por usuário no DB).
3. Rollback: reverter front; API permanece compatível.

## Open Questions

- Nenhum bloqueante: preferência é mover form completo (não duplicar).
