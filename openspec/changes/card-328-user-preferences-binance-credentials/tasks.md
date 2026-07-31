## 1. OpenSpec e card

- [x] 1.1 Publicar artifacts OpenSpec no issue #328 (Gist + comentário)
- [x] 1.2 Confirmar Status=In Progress e branch `change-328-user-preferences-binance-credentials`
- [x] 1.3 Republish OpenSpec do rework (credenciais no Perfil) mantendo Status=Done

## 2. Componente e página de preferências

- [x] 2.1 Extrair `BinanceCredentialsForm` a partir do bloco atual da Carteira (salvar/remover/status/máscara)
- [x] 2.2 Criar `UserPreferencesPage` em `/preferences` com o formulário completo e copy do card
- [x] 2.3 Registrar rota autenticada em `App.tsx` e título em `AppNav`
- [x] 2.4 Adicionar item Preferências na nav de conta; renomear admin para Preferências do sistema
- [x] 2.5 Mover formulário completo para `ProfilePage` (`/profile`)
- [x] 2.6 Remover item Preferências da nav de conta e redirecionar `/preferences` → `/profile`
- [x] 2.7 Atualizar CTA compacto da Carteira para Meu Perfil

## 3. Carteira

- [x] 3.1 Substituir formulário completo por status compacto + link/CTA para `/preferences`
- [x] 3.2 Manter carga de balances com a chave do usuário logado

## 4. Testes e QA

- [x] 4.1 Atualizar/criar E2E de preferências e ajustar `external-balances.spec.ts`
- [x] 4.2 Cobrir visual Playwright (preferences + wallet) e atualizar baselines se necessário
- [x] 4.3 Rodar testes focados backend de credentials + build frontend
- [x] 4.4 Code Review do diff, commit/push, PR para `develop`, QA gate e Done técnico
- [x] 4.5 Atualizar E2E/visual para perfil + wallet após rework
- [x] 4.6 Code Review, PR, QA e evidência no card (Status permanece Done)
- [x] 4.7 Rework visual do Perfil (seções, variant profile, ocultar onboarding) + baselines
