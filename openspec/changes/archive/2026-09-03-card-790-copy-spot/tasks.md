# Tasks — card-790-copy-spot

> Nota skills: usar skills canónicas em `.agents/skills` / `.cursor/skills` quando aplicável (ex.: `design-critic` já usada em Design; `impeccable` N/A com justificativa para este Design copy-only).
> Gate UI: **Design → Aprovação de Design (Alan, T7) → Pronto para Dev (T8)** antes de qualquer código/`/opsx:apply`. Este card permanece em `Design` até aprovação humana; não chamar `process_event`, não commitar.

## 1. Alinhamento e leitura fria (sem código)

- [x] 1.1 Re-ler issue 790 body inteiro (Q1–Q7, Entra/Não entra, Vocabulario/Avoid, critérios 1–7, Riscos) e `gh issue view 790 --json title,body`
- [x] 1.2 Conferir fatos em `develop`: `frontend/public/prototypes/cripto-farol-landing-v4/index.html:175,215,232,236`, `docs/landing-page.md`, `frontend/src/pages/HelpPage.tsx:49`, `frontend/src/pages/ProfilePage.tsx:113`, `frontend/src/components/binance/BinanceCredentialsForm.tsx:72,355`, `frontend/src/components/onboarding/OnboardingGuide.tsx` (check negativo hoje)

## 2. Landing pública v4 — copy Q3=A (Critério 1 e 2)

- [x] 2.1 Editar `frontend/public/prototypes/cripto-farol-landing-v4/index.html` — benefício carteira 04 (175): trocar “nunca envia ordem” por Spot opcional no Farol (confirmação, nunca saque, não é bot) — **Critério 1**
- [x] 2.2 Editar confiança (215): trocar “API apenas para consulta... nunca envia ordem” por leitura para Home/Carteira + Spot Trade opcional (sem saque) para enviar ordens no Farol — **Critério 1**
- [x] 2.3 Editar FAQ “É um robô que opera por mim?” (232): trocar “botão é na sua Binance” por “não é bot 24/7; com Spot você confirma no Farol” — **Critério 1**
- [x] 2.4 Editar FAQ “Vocês têm acesso ao meu dinheiro?” (236): trocar “API apenas para consulta / nunca enviamos ordem” por leitura + Spot opcional, nunca saque — **Critério 1**
- [x] 2.5 Espelhar mesma política em `docs/landing-page.md` (Hero apoio, Benefícios 04, Confiança e segurança) — **Critério 1**
- [x] 2.6 Verificar spec delta `landing-conversion-copy` deixa de exigir “não envia ordem / API só consulta” como verdade absoluta — **Critério 2**
- [x] 2.7 Validar que hero mantém CTA 6 meses grátis, hero message intacta, lead form `/api/leads` preservado (não regressão)

## 3. Help fora do OnboardingGuide — Q6=A (Critério 4)

- [x] 3.1 Editar `frontend/src/pages/HelpPage.tsx` header intro + `help-usage-grid` Carteira: corrigir “saldos read-only” para “leitura para Home/Carteira; Spot Trade (sem withdraw) opcional para comprar/stop/vender Spot no Farol (nunca saque; não é bot)” — **Critério 4**
- [x] 3.2 Garantir que quickActions/intro não contradizem Spot opcional e que guardrail segue “apoio à decisão” — **Critério 4**
- [x] 3.3 Confirmar que bloco `OnboardingGuide` embutido não foi alterado neste passo (boundary Q6 vs Q7)

## 4. Perfil — eliminar residual read-only-only (Critério 3)

- [x] 4.1 Editar `frontend/src/pages/ProfilePage.tsx:113` chrome: trocar “integração Binance read-only em um só lugar” por “Credenciais Binance: leitura para Home/Carteira; Spot Trade (sem saque) opcional para Operar no Monitor” — **Critério 3**
- [x] 4.2 Editar `frontend/src/components/binance/BinanceCredentialsForm.tsx:72` toast: remover “read-only” (“Crie uma chave API na Binance...”) — **Critério 3**
- [x] 4.3 Editar `frontend/src/components/binance/BinanceCredentialsForm.tsx:355` placeholder API Secret: trocar “API Secret da chave read-only” por “API Secret da mesma chave” — **Critério 3**
- [x] 4.4 Re-testar que helper texts mantêm “Spot Trading é necessário para proteger stop ou comprar/vender”, whitelist IP, “não habilite withdraw”, não pedir senha — **Critério 3**

## 5. OnboardingGuide — check negativo Q7=B (Critério 5)

- [x] 5.1 Verificar `frontend/src/components/onboarding/OnboardingGuide.tsx`: jornada permanece Favoritos → Selecionar estratégias → Monitor → Carteira opcional; **não** adiciona passo/frase Operar — **Critério 5**
- [x] 5.2 Grep negativo no componente e no Help embutido: **não** contém “nunca envia ordem”, “nunca movimenta dinheiro e nunca envia ordem”, “API apenas para consulta”, “somente leitura” absoluto — **Critério 5**
- [x] 5.3 Confirmar que guide não nomeia “comprar / stop / vender”, “Spot”, “Operar” — **Critério 5**

## 6. Ausências obrigatórias — testes negativos (Critérios 6 e 7)

- [x] 6.1 Grep em todo Entra: **não** há flag/toggle/indicador de ensaio, fail-closed, token, modo Ensaio/Mercado real — **Critério 6**
- [x] 6.2 Confirmar que #463, #637, #692 continuam issues próprias, não absorvidos neste card (sem arquivos deles alterados) — **Critério 7**
- [x] 6.3 Confirmar Não entra: sem saque/margem/futures/bot/webhook/grid/3Commas/copy-trading/ordem automática sem clique; sem remover Spot

## 7. Vocabulário, specs e validação Design

- [x] 7.1 Aplicar glossário com Avoid (Landing pública, Copy autenticada, Comprar/stop/vender, Opcional, Somente leitura, Sinais, Ensaio/flag) em proposal/design/specs sem sinónimos — critério transversal
- [x] 7.2 Criar/atualizar delta specs `specs/landing-conversion-copy/spec.md`, `specs/user-preferences-binance-credentials/spec.md`, `specs/user-onboarding/spec.md` com cenários Given/When/Then para critérios 1–7 (WHEN/THEN normativos; Given como pré-condição)
- [x] 7.3 Opcional: rascunho em `frontend/public/prototypes/card-790-copy-spot/**` para validar copy, **sem** alterar v4 vigente (residual PNG mantido)
- [x] 7.4 Rodar `openspec validate --all` ou `openspec validate card-790-copy-spot --type change` (sem --change; ver `openspec validate --help`) e corrigir até verde; não publicar Gist, não comentar issue, não editar `backend/`
- [x] 7.5 Registrar riscos residuais não-bloqueantes: redação exacta CTA/FAQ, PNG sinais vs painel Operar, fatia ensaio futura (Q4=A), boundary `/help` vs `OnboardingGuide`

## 8. Handoff Design → Aprovação de Design

- [ ] 8.1 Publicar change apenas em `openspec/changes/card-790-copy-spot/**` (e rascunho opcional `frontend/public/prototypes/card-790-copy-spot/**`); sem `git commit/push`, sem `gh project item-edit`, sem `process_event`, sem `CONTEXT.md`/`docs/adr/`
- [x] 8.2 Entregar ao pai: paths criados, resumo 10 linhas PT-BR, resultado do validate, riscos residuais; aguardar T7 (Alan) para `Pronto para Dev`
