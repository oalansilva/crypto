## Why

Landing v4 (`frontend/public/prototypes/cripto-farol-landing-v4/index.html:175,215`), `docs/landing-page.md`, spec `landing-conversion-copy`, `/help` e chrome do Perfil prometem “nunca envia ordem” / API apenas consulta / “saldos read-only” / “integração Binance read-only”. O Monitor já envia ordens Spot MARKET e coloca/cancela stop-limit no Farol após confirmação. A contradição confunde visitante/tester do beta e fere confiança educacional (não recomendação financeira, não 3Commas disfarçado). Classificação **story**, frente **Risco**, **P0 no-go do beta** (Q5=A). Card sem ensaio (Q1=A, Q4=A). Implementação só após `Pronto para Dev`.

## What Changes

**Entra (copy-only, sem backend):**

- Landing pública v4 (`frontend/public/prototypes/cripto-farol-landing-v4/index.html` + FAQ no HTML) com política **Q3=A**: admite comprar / stop / vender Spot **no Farol** (opcional; nunca saque; não é bot 24/7); cai “nunca envia ordem” e “o botão é na sua Binance” como verdade absoluta.
- `docs/landing-page.md` alinhado à mesma política Q3=A (API somente leitura deixa de ser verdade absoluta; leitura basta para carteira/Home, Spot Trade opcional para Operar).
- Spec `landing-conversion-copy` deixa de exigir “não envia ordem” / API só consulta como verdade do produto.
- `/help` fora do bloco `OnboardingGuide` (grelha de uso, intro, acções) com **Q6=A**: admite comprar/stop/vender Spot no Farol (opcional; nunca saque; não é bot) e corrige “saldos read-only”.
- Perfil (`frontend/src/pages/ProfilePage.tsx:113` + `frontend/src/components/binance/BinanceCredentialsForm.tsx:72,355`): eliminar residual “integração Binance read-only”, toast “Crie uma chave API read-only”, placeholder “API Secret da chave read-only”. Parágrafo vigente já admite Spot Trade (sem withdraw) para Operar e leitura para Home/Carteira (`user-preferences-binance-credentials`).
- `OnboardingGuide` (`frontend/src/components/onboarding/OnboardingGuide.tsx`, também embutido em `/help`): **check negativo Q7=B** — mantém Favoritos → Monitor → carteira opcional, não nomeia comprar/stop/vender, não introduz “nunca envia ordem” nem “só consulta”. Sem novo passo/frase Operar.

**Fora de forma (não reabrir):** decisões Q1–Q7 fechadas; prints da landing (sinais vs painel Operar) e frases pixel-perfect de CTA/FAQ são residuais de Design, não obrigação deste card.

## Capabilities

### New Capabilities
- (nenhuma) — copy-only sobre capacidades existentes; não cria produto novo.

### Modified Capabilities
- `landing-conversion-copy`: política Q3=A na trust/risk e capabilities; cai exigência “nunca envia ordem” / “API apenas consulta” como verdade; admite comprar/stop/vender Spot no Farol (opcional; nunca saque; não é bot).
- `user-preferences-binance-credentials`: remove copy residual read-only-only no chrome/placeholder/toast do Perfil; mantém leitura para Home/Carteira e Spot Trade (sem withdraw) para Operar, sem pedir senha e com whitelist IP.
- `user-onboarding`: `/help` (fora do `OnboardingGuide`) admite Spot Q6=A e corrige Carteira read-only; `OnboardingGuide` mantém check negativo Q7=B (não nomear Operar, não mentir).

## Impact

- **Afeta (copy):** `frontend/public/prototypes/cripto-farol-landing-v4/index.html` (hero/confiança/FAQ/benefícios carteira), `docs/landing-page.md`, `frontend/src/pages/HelpPage.tsx` (grelha Carteira/intro/acções, não o bloco `OnboardingGuide`), `frontend/src/pages/ProfilePage.tsx`, `frontend/src/components/binance/BinanceCredentialsForm.tsx`, `frontend/src/components/onboarding/OnboardingGuide.tsx` (verificação negativa apenas).
- **Não afeta:** backend (`backend/`), modo ensaio, flag/toggle/fail-closed/indicador/token de ensaio, paper trading, #463/#637/#692, saque/margem/futures/bot/webhook/grid/3Commas, rotas fora de copy. Sem alteração fora de copy.
- **Specs:** delta em `landing-conversion-copy`, `user-preferences-binance-credentials`, `user-onboarding`.
- **Rastro:** HTML v4 publicada + rationale em `design.md` + `docs/landing-page.md`; sem alteração da v4 vigente além de copy (PNG do painel Operar fica como residual).
- **Origem:** issue oalansilva/crypto#790. Status `Design` via T3; sem mover coluna, sem commit/push.
