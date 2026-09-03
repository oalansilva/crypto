# Design — card 790 Copy alinhada ao Spot

## Context

Issue oalansilva/crypto#790 está em `Design` (T3, sem mover Status). É **story**, frente **Risco**, **P0 no-go do beta** (Q5=A). Estória: visitante/tester quer landing/Ajuda/Perfil admitindo comprar/stop/vender Spot **no Farol** (opcional; nunca saque; não é bot) e onboarding que comece por Favoritos sem promover Operar e sem mentir, para não contradizer o Monitor que já envia MARKET e coloca/cancela stop-limit.

Fatos verificados em `develop` 2026-08-29 (não reentrevistar):
- `frontend/public/prototypes/cripto-farol-landing-v4/index.html:175,215` “nunca envia ordem / API apenas consulta”; `docs/landing-page.md` idem; spec `landing-conversion-copy` exige “não envia ordem”.
- `frontend/src/pages/HelpPage.tsx:49` grelha Carteira “saldos read-only”.
- `frontend/src/pages/ProfilePage.tsx:113` chrome “integração Binance read-only”; `frontend/src/components/binance/BinanceCredentialsForm.tsx:72` toast “Crie uma chave API read-only”, `355` placeholder “API Secret da chave read-only”.
- `frontend/src/components/onboarding/OnboardingGuide.tsx` hoje **não** diz “nunca envia ordem” (check negativo OK).
- Parágrafo/spec `user-preferences-binance-credentials` já admite Spot Trade (sem withdraw) para Operar e leitura para Home/Carteira — residual é o chrome/placeholder/toast.
- Sem modo ensaio no produto; prints da landing são Monitor de **sinais** (lista Compra/Venda + gráfico), não painel Operar.

Decisões PO fechadas Q1–Q7 (não reabrir):
Q1=A só copy sem flag; Q2=B landing v4+docs+FAQ e help+Perfil+onboarding; Q3=A landing admite comprar/stop/vender Spot no Farol (opcional, nunca saque, não bot); Q4=A ensaio mais tarde sem irmã; Q5=A P0 no-go beta; Q6=A help admite Spot; Q7=B onboarding não nomeia Operar, só não mente.

Stakeholders: PO Alan (T1/T7/T15 único), visitantes/testers beta fechado, marca educacional (apoio à decisão, não recomendação financeira, não 3Commas).

## Goals / Non-Goals

**Goals:**

- Eliminar promessa absoluta “nunca envia ordem / API só consulta / botão é na sua Binance” da landing v4 (hero/confiança/FAQ/benefícios carteira), `docs/landing-page.md` e spec `landing-conversion-copy`, substituindo por política Q3=A (Spot opcional no Farol, nunca saque, não é bot 24/7).
- Corrigir `/help` (fora do `OnboardingGuide`) para Q6=A: admitir comprar/stop/vender Spot no Farol (opcional; nunca saque; não é bot) e remover “saldos read-only” como única verdade; grelha Carteira passa a distinguir leitura (Home/Carteira) vs Spot Trade (Monitor).
- Remover residual “só read-only” de Perfil/BinanceCredentialsForm que contradiz o parágrafo vigente, mantendo recomendação whitelist IP, sem withdraw, sem pedir senha.
- Garantir `OnboardingGuide` em check negativo Q7=B: mantém Favoritos → Monitor → carteira opcional, não adiciona passo/frase Operar, não introduz mentira (“nunca envia ordem”/“só consulta”).
- Alinhar spec deltas e critérios 1–7 como testes comportamentais, com vocabulário canónico e Avoid.
- Manter copy-only, sem backend, sem flag.

**Non-Goals (Não entra — não propor):**

- Flag/toggles/fail-closed de submit/place/cancel, indicador Ensaio vs Mercado real, token de ensaio, modo ensaio.
- Novo passo/frase Operar no onboarding (Q7=B).
- Paper trading com fill/PnL fictício; abrir issue irmã de ensaio agora.
- #463, #637, #692, #385 CLOSED; saque, margem, futures, bot/webhook/grid/3Commas, copy-trading, ordem automática sem clique; remover Spot.
- Frases pixel-perfect de CTA/FAQ como obrigação; substituir PNG do showcase por print do painel Operar (fica como residual de Design).
- Reabrir Q1–Q7.

## Decisions

**D1 — Landing v4 como superfície primária, copy como política (Q3=A).**  
Escolhido editar `frontend/public/prototypes/cripto-farol-landing-v4/index.html` (hero, confiança, benefícios carteira 04, FAQ “É um robô?/Vocês têm acesso ao meu dinheiro?”) para admitir Spot opcional no Farol; rationale HTML comenta que a figura continua sendo Monitor de sinais (lista+gráfico) e que a política vive no texto — troca de PNG é residual. `docs/landing-page.md` espelha mesma política. Alternativa rejeitada: manter “nunca envia ordem” e documentar Spot só no app — manteria contradição P0. Alternativa rejeitada: pixel-perfect de CTA como obrigação — fora do Entra.

**D2 — Spec `landing-conversion-copy` deixa de exigir “não envia ordem” como verdade.**  
MODIFICAR dois Requirements: “Landing explains requested product capabilities” (troca “read-only result tracking” por leitura para carteira/Home + Spot Trade opcional para comprar/stop/vender, nunca saque, não é bot) e “Landing explains product trust and risk” (remove “read-only” absoluto e “never send orders”, adiciona “pode enviar comprar/stop/vender Spot no Farol após confirmação, opcional, nunca saque, não é bot 24/7”). Alternativa rejeitada: criar nova capability — seria duplicar landing.

**D3 — HelpPage corrigido fora do OnboardingGuide (Q6=A vs Q7=B).**  
`frontend/src/pages/HelpPage.tsx` grelha Carteira/Benefícios/intro + quickActions: admitir Spot opcional, corrigir “saldos read-only” para “leitura basta para Home/Carteira; Spot Trade (sem saque) para comprar/stop/vender no Monitor”. O componente `OnboardingGuide` embutido permanece isolado com Q7=B (check negativo). Alternativa rejeitada: editar OnboardingGuide para promover Operar — violaria Q7=B.

**D4 — Perfil residual read-only-only removido (Fato Consequências).**  
Em `ProfilePage.tsx:113` trocar chrome “integração Binance read-only em um só lugar” por texto que distingue leitura vs Spot Trade; em `BinanceCredentialsForm.tsx:72` toast sem “read-only”, `355` placeholder sem “da chave read-only”, mantendo `BINANCE_API_KEY_HELP`/`SECRET_HELP` que já distingue. Não pedir withdraw, manter whitelist IP, rejeitar e-mail/senha. Alternativa rejeitada: manter residual e confiar no parágrafo — contradição permaneceria.

**D5 — OnboardingGuide check negativo, sem novo conteúdo.**  
Manter `journeySteps` Favoritos → Selecionar estratégias → Monitor → Carteira opcional; não adicionar step Operar; verificar que `OnboardingGuide.tsx` não contém “nunca envia ordem”, “só consulta”, “somente leitura” absoluto, nem nomes comprar/stop/vender. Se regressão futura inserir, teste falha. Alternativa rejeitada: adicionar frases Operar — fora do Entra Q7=B.

**D6 — Sem backend de ensaio.**  
Nenhuma flag/toggle/indicador. Q1=A e Q4=A fechadas. Ensaiar Spot real já existe no Monitor; copy apenas alinha verdade. Alternativa rejeitada: propor flag ensaio — inventaria escopo.

**D7 — Vocabulário canónico e Avoid como glossário normativo.**  
Reuso literal do bloco Vocabulário do issue (Landing pública, Copy autenticada, Comprar/stop/vender, Opcional, Somente leitura, Sinais Compra/Venda, Ensaio/Mercado real/flag) com Avoids (“cripto-farol-landing antigo”, “bot 24/7; saque”, “read-only como se nunca enviasse”, etc.). Não introduzir sinónimos. Usado em proposal/design/specs.

**D8 — Critérios 1–7 viram testes comportamentais em specs/tasks.**  
Cada critério gera um ou mais cenários WHEN/THEN nos delta specs e checklist em tasks.md. C6 e C7 são testes negativos (ausência de flag e de contaminação #463/#637/#692).

## Prototype

**UI impact explícito (copy-only, sem alteração fora de copy):**

| Superfície | Arquivo | Trecho atual | Após (política) | Evidência versionada |
|---|---|---|---|---|
| Landing v4 — benefícios carteira | `frontend/public/prototypes/cripto-farol-landing-v4/index.html:175` | “mas nunca movimenta dinheiro, nunca envia ordem e nunca faz saque.” | “...vê saldos/resultados; pode enviar comprar/stop/vender Spot **no Farol** quando você confirmar (opcional, nunca saque, não é bot 24/7).” | `index.html:175` |
| Landing v4 — confiança | `index.html:215` | “API apenas para consulta... nunca envia ordem.” | “Conexão usa API leitura para carteira/Home; com permissão Spot Trade (sem saque) você pode enviar ordens Spot no Farol após confirmação.” | `index.html:215` |
| Landing v4 — FAQ robô | `index.html:232` | “Quem aperta o botão ... é sempre você, na sua Binance.” | “Não é bot 24/7. Se habilitar Spot Trade, você confirma comprar/stop/vender **no Farol**; sem permissão, só acompanha sinais.” | `index.html:232` |
| Landing v4 — FAQ acesso dinheiro | `index.html:236` | “API apenas para consulta...nunca enviamos ordem.” | “Leitura para acompanhar; Spot opcional para operar no Farol; nunca pedimos senha, nunca sacamos.” | `index.html:236` |
| Docs | `docs/landing-page.md` (Benefícios, Confiança, Hero apoio) | “read-only / nunca envia ordem” | Mesmo texto da v4 (espelho). | `docs/landing-page.md` |
| Help (fora do guia) | `frontend/src/pages/HelpPage.tsx:49` | “saldos read-only. Ela não é pré-requisito” | “saldos (leitura) e, se quiser, comprar/stop/vender Spot no Farol após confirmação (opcional, nunca saque, não é bot)” | `HelpPage.tsx:49` |
| Perfil chrome | `frontend/src/pages/ProfilePage.tsx:113` | “integração Binance read-only em um só lugar.” | “Credenciais Binance: leitura para Home/Carteira; Spot Trade (sem saque) opcional para Operar no Monitor.” | `ProfilePage.tsx:113` |
| Form toast/placeholder | `frontend/src/components/binance/BinanceCredentialsForm.tsx:72,355` | “Crie uma chave API read-only” / “API Secret da chave read-only” | “Crie uma chave API na Binance” / “API Secret da mesma chave” (helper já distingue). | `BinanceCredentialsForm.tsx:72,355` |
| OnboardingGuide | `frontend/src/components/onboarding/OnboardingGuide.tsx` | (já não mente) | **Sem alteração** — verifica não conter “nunca envia ordem”/“só consulta”/nomes Operar. | `OnboardingGuide.tsx` |

Rascunho opcional permitido em `frontend/public/prototypes/card-790-copy-spot/**` (não altera v4 vigente). Prints continuam Monitor de sinais; troca por print do painel Operar é residual documentado, não obrigatório. Responsivo e guardrail “apoio à decisão” preservados.

## Design Critique

**Autocrítica do Designer (isolado, sem editar produto):**
- **Completude:** cobre todo Entra (landing v4+docs+FAQ, spec, help fora do guia, perfil residual, onboarding negativo) sem puxar Não entra. Superset do issue, não inventa flag/ensaio.
- **Consistência vocabular:** reusa termos canónicos e Avoids; não cria sinónimos; Q3/Q6/Q7 respeitados; “nunca saque; não é bot” sempre junto de Spot.
- **Riscos cobertos:** mitigação P0 (beta no-go) via alinhamento copy; residual de redação/PNG marcado como não-bloqueante; boundary Help vs OnboardingGuide explicitada.
- **Testabilidade:** critérios 1–7 mapeados em cenários comportamentais; testes negativos para flag e contaminação.
- **Proporção:** copy-only, sem backend; tasks granularizadas; nada fora de `frontend/public/prototypes/cripto-farol-landing-v4`, `docs/`, `frontend/src/pages|components`.

**Veredito do Designer:** **APTO para Aprovação de Design (Design → Aprovação de Design).** Passa para `Aprovação de Design` (Alan). **NÃO** aprova `Aprovação de Design → Pronto para Dev` (só humano em T7). Sem `process_event`, sem commit/push.

**Impeccable / DESIGN.md / Playwright desta coluna:**
- Impeccable: **N/A com justificativa não vazia** para esta entrega de Design (copy-only, sem componente novo além de delta textual; não requer shape/audit/polish). Gates de Design e aprovação humana permanecem integrais (não bypass). Auditoria automática futura não é bloqueada.
- `DESIGN.md` versionado e brand system continuam obrigatórios no Apply (seguir ao editar copy).
- Prototype validado em arquivo estático v4 + Help/Perfil; browser-gate será no Apply (confere copy renderizada).

## Prototype Validation

- URL final: `https://dev.criptofarol.com.br/prototypes/card-790-copy-spot/` (arquivo `frontend/public/prototypes/card-790-copy-spot/index.html`, 5770 bytes gerados, 0 copiados — antes/depois redigido, não clonado da v4).
- Comando: `playwright-core` chromium headless via `NODE_PATH=source/frontend/node_modules`, `page.goto` + asserts + `screenshot` em desktop 1280×800 e mobile 390×844 (evidência `/tmp/card790-desktop.png`, `/tmp/card790-mobile.png`).
- Asserts: `title="Protótipo 790 — Copy alinhada ao Spot"`, `h1` presente, `h2count=6` (6 superfícies), `DEPOIS=6` blocos, zero `pageerror`/`console.error` nos dois viewports.
- Resultado: PASS desktop + mobile, `ERRORS:[]`. Qualquer alteração posterior em HTML/CSS invalida esta validação.

## Risks / Trade-offs

- **[Risco] Landing ainda mostrar figuras de sinais, não do painel Operar → visitante pode não visualizar Operar.** → Mitigação: política textual Q3 resolve P0; troca de PNG fica residual pós-beta, sem bloquear. Alternativa (trocar PNG agora) rejeitada como obrigação.
- **[Risco] Redação exacta de CTAs/FAQ divergir do pixel-perfect desejado.** → Mitigação: critério 1 valida política (admite Spot, nunca saque, não é bot, não mente), não frase exacta; residual não bloqueia.
- **[Risco] Regressão de copy reintroduzir “read-only only” no Perfil/Help.** → Mitigação: specs com cenários negativos (“MUST NOT conter ‘integração read-only’/‘API read-only’/‘saldos read-only’ como única verdade”) + tasks de verificação textual.
- **[Risco] OnboardingGuide compartilhado em /help confundir Q6 vs Q7.** → Mitigação: boundary explícita (Q7 no componente, Q6 no resto da página); delta specs separam requisitos.
- **[Risco] Tentação de propor flag/ensaio/paper trading.** → Mitigação: Non-Goals e C6 bloqueiam; validate falhará se inventar escopo.
- **Trade-off:** copy admite Spot mas mantém “opcional; nunca saque; não é bot” → preserva confiança read-only para quem só quer acompanhar, sem prometer saque/automação.

## Vocabulário (Glossário com Avoid)

- **Landing pública:** `https://criptofarol.com.br/` = v4. FAQ vive nesse HTML. _Avoid:_ `cripto-farol-landing/` antigo como PROD.
- **Copy autenticada:** `/help` (Q6=A) e Perfil; onboarding só check negativo (Q7=B).
- **Comprar / stop / vender:** Spot MARKET e stop-limit **já no app**, no Farol, após confirmação. _Avoid:_ “o botão é na sua Binance”; bot 24/7; saque.
- **Opcional:** Favoritos/Monitor não exigem chave; enviar ordem exige chave com Spot Trade. _Avoid:_ modo ensaio/flag.
- **Somente leitura:** chave **sem** Spot Trade (Home/Carteira). _Avoid:_ “read-only” como se o produto nunca enviasse ordem.
- **Sinais Compra/Venda:** leitura da estratégia no Monitor. _Avoid:_ confundir com clique de enviar ordem.
- **Ensaio / Mercado real / flag / fail-closed / indicador:** fora deste card (Q1=A,Q4=A). _Avoid:_ voltar a metê-los no Entra.

## Migration Plan

Não há migração de dados. Apply após `Pronto para Dev`: editar copy nos 5 arquivos listados em Prototype + specs deltas. Rollback: reverter copy. Sem alteração de API/banco. Sem feature flag.

## Open Questions

Nenhuma aberta para este Design. Residuais não-bloqueantes: redação exacta de CTAs/FAQ, PNG do painel Operar, fatia ensaio (Q4=A) para card futuro.
