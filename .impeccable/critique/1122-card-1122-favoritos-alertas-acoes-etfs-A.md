`proveniência: Assessment A (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/cf-assess-a2-1122.json` (attempt `b0076cfb-0c68-4c7d-b7fc-c43868fc54b9`, band `juizo`, role `assessment-a`, capture_sha256 `6c905d79d8bc542e4872f30c2ab3a33000bba072a4b859024c3490de854ce9d0`, arquivo sha256 `b9a070a3f47dfac182293912f80ff1e5aebd7b6ba13834786a2dc0e85817b580`). Wave capture `cf-assess-a-1122.json` (attempt `47e4bb72-74fe-4263-840b-85837e1a323d`, arquivo sha256 `c1c41574feb4d5a83aa95f8f2d8705e2c3b7bf2879ae20ba4502ce20f0fd147a`). Birth: `.cursor/tmp/claude-evidence/b0076cfb-0c68-4c7d-b7fc-c43868fc54b9.birth.json`.

# Assessment A: card 1122, change card-1122-favoritos-alertas-acoes-etfs

> Avaliador A isolado (produto, UX, acessibilidade e fidelidade do clone). Onda dupla com-tela. Não li o transcript do pai nem o snapshot do Assessment B (os PNGs `card-1122-B-*` estão na pasta, mas não os abri). Não spawnei filho, não chamei `process_event`, não arrastei Status e não comentei no issue. Não editei `design.md`, OpenSpec, o protótipo, `backend/` nem `frontend/src/`. Única escrita: este arquivo.

## Metadata

- card: 1122, "Acompanhar favoritos e receber alertas de ações e ETFs no horário correto"
- change: `card-1122-favoritos-alertas-acoes-etfs`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1122-favoritos-alertas-acoes-etfs`
- branch / q_git: `card-1122-favoritos-alertas-acoes-etfs` @ `f093e2cc` (pacote untracked: as duas pastas `??`, mais os PNGs do B)
- tupla: `bound_card=1122` · Status = Design (dado no prompt; não arrastado)
- data: 2026-10-26
- cliente: Claude Code (adapter cooperativo, sem modo Auto), superfície claude-desktop
- Issue: REST `gh api repos/oalansilva/crypto/issues/1122` e `/comments` (2 comentários: "card nítido; sem grill" e "grill-card: fronteira vazia…"). A fronteira é o body grelhado (Problema / História / Entra / Não entra), com as 5 decisões de Alan de 26/10 dentro de Entra. Não reabri as decisões.
- sha256:
  - `design.md` `d4d64e7e8de504b40461d80f10b12b0a1bb1bd4e681fc817a3cb14833dd2e191`
  - `proposal.md` `294ae9b1…ce74` · `tasks.md` `115061c7…58b2`
  - specs: `favorite-telegram-alerts` `0e67ac45…bf9`, `market-session-awareness` `2b52b959…dec7`, `monitor-multiclass` `2bff58b3…3ea3e`, `favorite-configuration-identity` `f9a0176d…4f34`, `monitor-telegram-alerts` `d20c193d…b1e0`, `favorite-backtest-refresh` `50a94132…3847`, `monitor-curated-fallback` `31e15c2d…d98b`, `monitor-telegram-favorite-toggle` `f4c99ceb…3f68`, `monitor-telegram-general-alerts` `3353ca6c…aa10`, `crypto-only-mvp` `9c0c2054…59de`, `favorites-class-comparison` `d6cdd737…76cf`, `favorites` `10d6a5d3…ffc`, `discovery-promotion` `7d02c651…74e`, `multiclass-batch` `c9876f32…7fc7`
- Ignore list: `.impeccable/critique/ignore.md` não existe.
- Ferramentas: Playwright Python com Chromium headless shell 1243 (arm64, `executable_path` explícito), `pt-BR`, tema escuro, **na URL pública**, contexto novo por viewport: 1440×900 e 390×844 (`isMobile`, toque), mais 1280×800, 1180×800 e 1024×768 em Favoritos para a decisão d3. Contraste pela cor computada contra o fundo efetivo (compondo os ancestrais), sem axe-core. A skill `impeccable` deste repo é ponte para `.agents/skills/impeccable/` (`.cursor/skills/impeccable/` não existe); segui `reference/critique.md` (Assessment A). Scripts e PNGs em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122A/` (não versionados).

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP | servido |
|---|---|---|---|
| `index.html` (também a pasta `/`) | `b7a4971379428845d9f78717c41a0a072ccf74f760a6f8f5e8c308645126c9d7` | 200 | IDENTICAL |
| `favorites.html` | `99d0fdb1ac13811186db56a7479e85ce20f244fe44c765e20e3f0215cb796dea` | 200 | IDENTICAL |
| `results.html` | `5953caa17e29ceededc10ec31846577626cfca7c24e85e02fd52d0c3a9db2ca4` | 200 | IDENTICAL |
| `configure.html` | `d94216041b570e1168d4024b7ab81e758d7ff6df43ffae13637b38623215b3db` | 200 | IDENTICAL |
| `discovery.html` | `d1f32be145edd65ff863b0dc74ac9c26d2c64ae26520faca07c968596e79f3df` | 200 | IDENTICAL |
| `profile.html` | `9824fe0bc64d86c53263362da7b6afec029b9057b69df6a0c5eff9122cd7f30d` | 200 | IDENTICAL |
| `live.css` | `8f4edf0aca9aca6ff4414384993cab1adb18042e4443ee074fe5ee9a6d569183` | 200 | IDENTICAL |
| `delta.css` | `d83e8e504da566369683ed9b398d5600dd9267ea24aaac17bbcb375f71175f00` | 200 | IDENTICAL |
| `delta.js` | `9be14c630d273439eee7e4214492e606f69411db775d53fd500bf274e9358f18` | 200 | IDENTICAL |

`live.css` é igual, byte a byte, a `https://dev.criptofarol.com.br/assets/index-WJwiIv3A.css`, a folha que `/monitor` serve hoje (bundle `index-DUWqPrYj.js`). Nos fluxos clicados (6 páginas, 2 larguras) não houve `console.error`, `pageerror` nem resposta ≥ 400. O `design.md` ainda diz que a URL pública dá 404 (Risks, último item; Prototype Validation): está desatualizado, hoje é 200.

## Tokens parseáveis (rubrica 6, D4)

`design.md`, L1–L3, cada um em linha própria:

```
UI impact: affected
live_route: /monitor
surface: existing
```

O bloco D4 em L5 é idêntico ao da skill. `design_clone_gate` (HEAD): `design_token_gap` = None; `parse_live_route` = `/monitor`; `parse_surface` = `existing`; `classify(index.html, /monitor)` = PASS; `evaluate_clone_gate` = True; `clone_gate_ok` = True; `copied_utf8_sum` = 59.679. Marcadores pareados em todas as páginas: index 23/23 COPIED e 23/23 DELTA; favorites 19/19 e 23/23; results 6/6 e 6/6; configure 5/5 e 5/5; discovery 7/7 e 7/7; profile 5/5 e 5/5. Nenhuma página tem "ANTES"/"DEPOIS". A rota é página viva do catálogo, não emprestada; as outras 5 rotas com copy visível têm URL extra de clone, como a lei pede. **ok.**

## Cobertura do body (rubrica 1)

| Item do Entra | Decisão / spec | Protótipo (visível) |
|---|---|---|
| Favorito com fonte, sessão, ajuste; configurações distintas não colidem | d11 · `favorite-configuration-identity` | Monitor e Favoritos: NVDA "Binance Ações · NY · split" e NVDA "Stooq · fonte antiga · diário" lado a lado. Resultado: modal com a configuração longa; duplicata "Já está nos favoritos com esta configuração (fonte, sessão e ajuste). Nada foi salvo." (`role=alert`) |
| Calendário, sessões, candle fechado, dados insuficientes, sem falso stale | d7, d8, d14 · `market-session-awareness`, `favorite-backtest-refresh` | Sábado, feriado (26/11) e "fora do pregão" sem atraso; Favoritos: "Backtest atualizado: 24/10, 08:12 · último pregão 23/10" e "Aguardando dados: 40 de 200 candles". No Monitor, dado insuficiente não tem tela (P2-2) |
| Canais atendem ação/ETF e distinguem sinal, atraso e mercado fechado; restart não duplica | d5, d9 · `favorite-telegram-alerts` | Mensagens do Telegram por cenário: entrada (sáb.), aviso "Dados atrasados" (ter.), saída (qua.), nada no fim de semana e no feriado. Idempotência é comportamento sem tela (spec com 4 cenários) |
| Quem recebe: favoritos marcados de cada usuário, inclusive cripto | d2, d3 · `favorite-telegram-alerts` R1, `monitor-telegram-favorite-toggle` | Coluna "Alertar" do dono; vitrine "Catálogo · não alerta"; Perfil "favorito seu marcado 'Alertar' (cripto, ação ou ETF)" |
| Transição da cripto (aberta) | d16 · pergunta 1 | Cenário "Quem recebia pelo catálogo": faixa `role=status` + "Marcar em Favoritos" (44 px) + mensagem "Mudança nos alertas". O spec proíbe o Apply de ligar antes da decisão |
| Entrada e saída de ação/ETF na carteira | d6 · R4 | Detalhe "Ação/ETF na carteira recebe entrada e saída no Telegram."; alerta de entrada (sáb.) e de saída (qua.) |
| Um alerta por favorito, com estratégia e configuração | d4, d10 | Mensagem com "Estratégia:" e "Configuração:"; NVDA da fonte antiga não muda e não alerta |
| Atraso real: um aviso por ativo; mercado fechado só na tela | d8, d9 | Âmbar "Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out." + "Sinal em espera até o dado normalizar"; aviso único; recuperação sem mensagem. Cripto atrasada não tem tela (P2-1) |
| Alerta ≠ ordem | d10 | "Ordem: nenhuma enviada — o alerta é só o sinal da estratégia." (ver P2-6) |
| Validar ação, ETF, cripto, configurações distintas, atraso, fechado, recuperação | d17 · tasks 6.x | Demonstração com 6 momentos; teste por cenário em 6.1 |

Não entra: nenhum canal novo, nenhuma mensagem de mercado fechado/abertura/feriado, sem migração da fonte antiga (só coexistência), sem posição real (#1124). **Sem escopo furado.**

### Escopo das 6 telas (risco do autor)

Cabe no card. Cada tela muda por consequência direta do Entra, não por gosto:
- `/monitor`: centro do card.
- `/favorites`: "Alertar" do dono é o mecanismo de "Quem recebe"; estrelas e Revalidar de ação/ETF eram "ainda não… até o #1122".
- `/combo/results` e `/combo/configure`: a História é "favoritar e acompanhar ações/ETFs"; os textos "ainda não podem ser favoritados" ficariam falsos (confirmei os dois no bundle vivo `index-DUWqPrYj.js`).
- `/combo/discovery`: o modal do #1121 diz "Monitor, Telegram e Revalidar: ainda não para ações e ETFs" (5 ocorrências no bundle vivo), que ficaria falso.
- `/profile`: a frase viva "Receba DMs individuais quando um sinal mudar de forma relevante para a sua carteira Spot." contradiz a nova origem.

A única mudança que o issue não pede de forma literal é lote/Descoberta gravarem ação/ETF com 1 estrela (d12). É a regra que a cripto já segue e o motivo do "sem estrela" do #1121 era justamente o "ainda não"; aceito como P3 (observar volume no Monitor com lote grande).

## Decisões de Alan de 26/10 (rubrica 2)

1. **Quem recebe = favoritos marcados de cada usuário, inclusive cripto:** respeitada (d2; scan por usuário; catálogo só vitrine). **ok.**
2. **Transição da cripto decidida no Design com Alan:** respeitada como pergunta aberta, com recomendação e trava no spec. **ok.**
3. **Entrada e saída de ação/ETF na carteira, sem depender da Binance; seguir a posição quando o #1124 existir:** respeitada (d6, ponto de extensão nomeado). **ok.** Ver P2-3: a dependência da carteira não aparece onde o usuário marca "Alertar".
4. **Um alerta por favorito, com estratégia e configuração:** respeitada (estado por favorito, chave do evento por favorito). **ok.**
5. **Aviso único de atraso real; mercado fechado só na tela:** respeitada para ação/ETF. Ver P2-7 sobre a leitura de "durante o pregão" e P2-1 sobre a cripto.

## Estados (rubrica 3)

- **Sinal (entrada/saída):** sáb. (entrada de NVDA Binance) e qua. (saída, NVDA vai para "Saída / cobertura", contagens 3/3). ok.
- **Atraso real:** ter. 08:05, NVDA âmbar com último/esperado + "Sinal em espera"; SPY e fonte antiga "fora do pregão"; um aviso. ok para ação. **Cripto: sem estado na tela** (P2-1).
- **Mercado fechado:** fim de semana, feriado em NY, fora do pregão, cada um com próxima abertura em BRT e NY. ok.
- **Dados insuficientes:** só em Favoritos ("Aguardando dados: 40 de 200 candles"). **Monitor: sem estado** (P2-2).
- **Recuperação:** qua., episódio fecha sem mensagem e a leitura normal decide. ok.
- **Ação / ETF / cripto:** NVDA (Ação), SPY (ETF), BTC/SOL/ETH (cripto) nas mesmas seções. ok.
- **Mesmo ativo, configurações distintas:** NVDA Binance × NVDA Stooq, com estado, "Alerta" e estrelas próprios. ok, com inconsistência de estrelas entre páginas (P2-9) e detalhe errado da fonte antiga (P2-8).
- **Transição:** faixa + mensagem única (recomendação A). Copy datada para quem nunca recebeu (P2-4).

## Fidelidade (rubrica 5)

- O canônico `index.html` clona `/monitor` com as seções vivas ("Em posição", "Saída / cobertura"), filtros, ajuda e indicadores. As linhas de ação/ETF entram nas seções vivas; não há painel ANTES/DEPOIS nem grade de estados. A Demonstração fica no fim, no fluxo, e se declara "não é tela do produto".
- `live.css` é o CSS vivo inteiro e confere com o servido. `delta.css` usa só tokens do `monitor-theme` vivo (literais do vivo, já em P3 do autor).
- Textos removidos pelo delta existem no bundle vivo ("ainda não podem ser favoritados" ×2, "ainda não para ações e ETFs" ×5, "Receba DMs individuais quando um sinal mudar…"); os novos ("Pregão aberto", "Ação/ETF na carteira") não existem. O delta substitui copy real.
- Fora do delta, o clone se comporta como o vivo nas larguras medidas: 1440 e 390 sem rolagem horizontal em todas as páginas e cenários (`scrollWidth == clientWidth`).
- Desvio de fidelidade dentro do delta: o detalhe do NVDA da fonte antiga (P2-8).

## Acessibilidade (rubrica 4, medida)

- **Rolagem horizontal:** nenhuma a 1440 e a 390 (6 cenários do Monitor, Favoritos dono e vitrine, Resultado com modal, Descoberta, Combo, Perfil). Favoritos também sem rolagem a 1280, 1180 e 1024, mas a 1024 a coluna Estratégia some (P1-1).
- **Contraste (texto novo, menor razão):** identidade "Ação · USD · Binance Ações · NY · split" 14,7; "Pregão aberto" 6,1; "Mercado fechado" 9,2; "Dados atrasados" 8,3; "Sinal em espera" 9,7; tag "Alerta" 6,9 (10 px); faixa 14,5 e link 13,6; "Off"/"TG" do Alertar 5,6 (10 px); status de atualização 9,5; modal de Salvar 10,2. **Tudo ≥ 4,5:1.**
- **Estado só por cor:** não há. Aberto/fechado/atrasado têm ícone próprio (ponto, relógio, triângulo) + texto; "Alerta" tem sino + texto.
- **Nomes acessíveis:** Alertar das linhas novas com `aria-label` "Alertar no Telegram: ligado/desligado" + `aria-pressed`; ao clicar, o `role=status` anuncia "Alertar no Telegram desligado para NVDA." As linhas de cripto (101, 102, COPIED) ficam sem `aria-label` (P2-11). A faixa é `role=status`. O modal de Salvar é `role=dialog aria-modal=true aria-label`; o da Descoberta tem `aria-labelledby=modal-title`. Botões da fonte antiga a 1440: `aria-disabled=true` + `aria-label` com o motivo; a 390 só "Abrir Gráfico" tem `aria-disabled`, sem `aria-label`, e "Ver Trades" fica ativo (P2-8).
- **Foco:** contorno 2 px #3b82f6 nos controles novos; Tab percorre os botões da Demonstração em ordem. Modal de Salvar: foco inicial no campo Nome; Esc antes de salvar fecha e devolve o foco a `save-favorite-button`. Depois de salvar, o foco cai no `body` (o Salvar vira `disabled`) e Esc deixa de fechar (P2-12). Tab sai do modal para a página de trás (incumbente do `SaveFavoriteModal`, P3).
- **Alvos de toque:** faixa "Marcar em Favoritos" 44 px; botões da Demonstração 44 px; "Salvar nos Favoritos" 44 px. Abaixo de 44: Alertar 32 px (desktop) e 28×56 px (celular), "Ver em Favoritos" 15 px a 1440 (P2-11, P2-12); botões do cartão do Monitor 30–33 px e "Editar" 18 px (incumbentes, COPIED).

## Responsividade

- 390: o cartão do Monitor ganha o bloco classe · configuração · estado do mercado · "Alerta" abaixo da faixa de controle, legível; a faixa da transição quebra com botão de largura total. "Confirmar gestão" cortado no cartão (incumbente, já P3 do autor).
- 1440: Favoritos com a coluna Alertar cabe (tabela 1141 px no contêiner de 1141 px; Estratégia 271 px).
- 1280: Estratégia 252 px. 1180: 155 px. **1024: 4 px** (sem a coluna Alertar seriam 90 px). A linha de NVDA fica com ~685 px de altura e sem nome de estratégia, configuração e status (P1-1).

## Heurísticas Nielsen (0–4), só neste snapshot

| # | Heurística | Nota | Nota curta |
|---|---|---|---|
| 1 | Visibilidade do estado | 3 | Aberto/fechado/atrasado com próxima abertura e último/esperado. Falta cripto atrasada e dado insuficiente no Monitor |
| 2 | Linguagem do usuário | 3 | "Pregão", "feriado em Nova York", BRT com NY. "TG" no celular é jargão (P2-11) |
| 3 | Controle e liberdade | 3 | Alertar do dono, reversível. A segunda trava (carteira) é invisível onde se marca (P2-3) |
| 4 | Consistência | 3 | Rótulos de configuração iguais nas 4 telas. Estrelas da fonte antiga divergem entre Monitor e Favoritos (P2-9) |
| 5 | Prevenção de erro | 3 | Duplicata por configuração; lote nasce sem Alertar; fechado não vira atraso |
| 6 | Reconhecer em vez de lembrar | 2 | A linha de identidade distingue as duas NVDA, mas some em Favoritos a 1024 (P1-1) |
| 7 | Flexibilidade | 3 | Filtros de tempo e estrelas para todas as classes |
| 8 | Estética e minimalismo | 3 | A linha de ação/ETF empilha 4 blocos sob a estratégia; denso, mas ordenado |
| 9 | Recuperar de erros | 3 | Atraso diz último e esperado; duplicata diz o motivo; recuperação silenciosa |
| 10 | Ajuda | 3 | Perfil e notas explicam a origem; faltam a carteira e o limite de mensagens |
| | **Total** | **29/40** | |

## Design specificity / cognitive load

Específico do produto: o vocabulário é o do pregão de NY traduzido para o operador brasileiro (BRT primeiro, NY entre parênteses), e a cor âmbar do atraso é a mesma do `--wait` vivo. A carga cognitiva cresce na linha de ação/ETF (estratégia, descrição, identidade, estado do mercado, nota de espera), mas cada bloco responde uma pergunta distinta. O ponto de decisão mais pesado é "por que não recebi?": hoje são três travas invisíveis no mesmo lugar (Alertar, carteira, limite de mensagens).

## Emotional journey

O pico positivo é o sábado: alerta do pregão de sexta chega com "Ordem: nenhuma enviada", sem susto de "dados atrasados" no fim de semana. O vale é o usuário que marca "Alertar" num NVDA fora da carteira e não recebe nada, sem a tela dizer por quê (P2-3), e o usuário novo que lê "Até 26/10 você recebia…" sem nunca ter recebido (P2-4).

## What's working

- As 5 decisões viraram texto concreto e testável, e a transição ficou travada no spec até Alan decidir.
- A distinção sinal / atraso / fechado é visível na tela e no Telegram com o mesmo vocabulário, e o fechado nunca manda mensagem.
- Duas NVDA (Binance e fonte antiga) coexistem com estado, Alertar e estrelas próprios, e a duplicata explica que a configuração conta.

## Findings

### P0: bloqueante (produto / escopo / contrato visível)

Nenhum.

### P1: deve corrigir antes de PASS

- **P1-1. A coluna "Alertar" a partir de 1024 px apaga a coluna Estratégia em Favoritos.**
  - Onde: design d3 ("passa a aparecer a partir de 1024 px"), tasks 5.3, Apply contract (Favoritos), `favorites.html`.
  - Medido: Estratégia com a coluna Alertar = 4 px a 1024, 155 px a 1180, 252 px a 1280, 271 px a 1440. Sem a coluna, a 1024, seriam 90 px. A linha de NVDA fica com ~685 px de altura, sem nome da estratégia, configuração ("Binance Ações" × "Stooq · fonte antiga"), status de atualização e "Aguardando dados", que é justamente o que distingue os dois favoritos de NVDA.
  - Correção: mostrar a coluna a partir de 1280 px (o primeiro ponto medido em que a Estratégia fica com ≥ 250 px) e, entre 1024 e 1279, levar o controle "Alertar" para a célula Ações (ou esconder outra coluna, como TF ou Sharpe). Atualizar d3, tasks 5.3 e o protótipo com uma medida a 1024.
  - Disposition: rework (pai/autor, no rework único da dupla).

### P2: residual visível, não bloqueia o teto 1+1+1

**Produto**

- **P2-1. Cripto atrasada não tem tela e convive com "Sem candle válido" sem regra.**
  - Onde: d8 ("a cripto continua com a regra de hoje mais o `stale` do servidor"), `monitor-multiclass` ("A cripto MUST mostrar só 'Dados atrasados'"), Demonstração.
  - Problema: o aviso de atraso para cripto é comportamento novo (risco do autor), mas nenhum cenário mostra BTC/USDT atrasado nem a mensagem. A linha de cripto pode mostrar "Dados atrasados" e "Sem candle válido" ao mesmo tempo, ou um sem o outro.
  - Correção: um cenário na Demonstração com BTC/USDT atrasado (linha, cartão e aviso do Telegram) e uma regra de precedência em d8 (o `stale` do servidor substitui "Sem candle válido" quando os dois valem).
- **P2-2. Dado insuficiente não tem estado no Monitor.**
  - Onde: `market-session-awareness` "Dado insuficiente é estado próprio"; `monitor-multiclass` lista só aberto/fechado/atrasado.
  - Problema: um favorito com estrela e 40 de 200 candles entra no Monitor sem texto definido. Pode cair num status vazio ou parecer falha.
  - Correção: "Aguardando dados · 40 de 200 candles" em cinza na linha, sem sinal; ou declarar que favorito `INSUFFICIENT` não entra no Monitor. Pôr no spec `monitor-multiclass`.
- **P2-3. "Alertar" sem a carteira não alerta nada, e a tela não diz.**
  - Onde: nota do modal de Salvar ("Depois de salvar, marque 'Alertar' em Favoritos para receber os sinais no Telegram."), destino da Descoberta ("Para receber no Telegram, marque 'Alertar' lá."), controle Alertar em Favoritos. O spec R4 diz "Sem a marca na carteira, o favorito de ação ou ETF MUST NOT gerar alerta".
  - Problema: o usuário liga "Alertar no Telegram: ligado" num NVDA fora da carteira e nunca recebe. Só o Perfil fala da carteira.
  - Correção: completar as duas notas com "…e marque o ativo como 'No portfólio' no Monitor", e, em Favoritos, mostrar "fora da carteira: sem alerta" junto do Alertar ligado quando o ativo não está na carteira.
- **P2-4. A faixa da transição diz "Até 26/10 você recebia…" para quem nunca recebeu.**
  - Onde: `index.html` faixa; condição em d16/`monitor-multiclass` ("Telegram ligado e nenhum favorito marcado").
  - Problema: depois da migração, todo usuário com Telegram ligado e sem marca vê a frase, inclusive quem entrou depois de 26/10 ou nunca teve o ativo do catálogo na carteira.
  - Correção: mostrar a frase datada só a quem recebeu alerta do catálogo antes do deploy; aos outros, só "Os alertas do Telegram vêm dos seus favoritos marcados 'Alertar'. Você ainda não marcou nenhum."
- **P2-5. O limite de 5 mensagens por hora vira 5 alertas por dia.**
  - Onde: Risks ("Limite de 5 mensagens/60 min…", P3 rever); `monitor-telegram-alerts` anti-noise; default `MONITOR_TELEGRAM_RATE_LIMIT_COUNT=5` / janela 60 min no código.
  - Problema: com uma varredura por dia, o sexto alerta só sai no dia seguinte, já com o candle de ontem, ou some se a leitura mudou de novo. O volume sobe com este card: um alerta por favorito (antes era um por par), aviso de atraso e aviso de transição disputam o mesmo limite. É o "perder sinais" do Problema do issue.
  - Correção: ver a pergunta nova para Alan.
- **P2-6. "Ordem: nenhuma enviada" pode contradizer uma ordem real do Operar na cripto.**
  - Onde: d10, mensagem de sinal.
  - Problema: quem operou BTC/USDT pelo Operar recebe o alerta do mesmo favorito dizendo "Ordem: nenhuma enviada", o que pode ser lido como "não há ordem sua".
  - Correção: "Este alerta não envia ordem: é só o sinal da estratégia."
- **P2-7. A leitura de "durante o pregão" precisa estar escrita.**
  - Onde: issue ("quando há atraso real de dados durante o pregão, um único aviso por ativo"); d8/d9; cenário de terça às 08:05 ("antes da abertura de NY").
  - Problema: a varredura diária roda sempre fora do pregão de NY. Na leitura literal, ação/ETF nunca receberia aviso. O design usa outra leitura (falta o candle de um pregão que já fechou) sem dizer que é uma leitura.
  - Correção: uma frase em d8 ("atraso real = falta o candle de um pregão que o calendário diz que já fechou; ele é detectado na varredura seguinte, mesmo com o mercado fechado").

**Mecânico**

- **P2-8. O detalhe do NVDA da fonte antiga é cópia do BTC.**
  - Onde: `index.html`, `tr[data-m22-detail="nvda-s"]` a 1440; cartão `nvda-s` a 390.
  - Problema: a 1440 o detalhe diz "Em posição", entrada $105,134.49, stop $99,877.76, enquanto a linha diz "Saída / cobertura" e $182.31. "Abrir Gráfico" e "Ver Trades" do detalhe ficam ativos, contra o spec (indisponíveis na fonte antiga). A 390, "Ver Trades" do cartão também fica ativo, e "Abrir Gráfico" tem `aria-disabled` sem `aria-label`.
  - Correção: detalhe próprio da fonte antiga (Saída, valores de NVDA) e os dois botões indisponíveis na linha, no cartão e no detalhe.
- **P2-9. As estrelas da fonte antiga divergem entre as páginas.**
  - Onde: Monitor `nvda-s` mostra ★★; Favoritos 106 tem 0 estrelas ("Sem estrela 1") e o design diz "sem estrela".
  - Problema: o Monitor lista só favoritos com estrela, então ou a linha não deveria estar no Monitor, ou Favoritos deveria ter estrela.
  - Correção: alinhar as duas páginas (sugestão: 1 estrela nas duas).
- **P2-10. O motivo da indisponibilidade da fonte antiga está só em `title`.**
  - Onde: botões `[data-m22-off]`.
  - Problema: no toque não há tooltip; o botão fica esmaecido sem explicação visível.
  - Correção: texto visível curto abaixo dos botões ("Gráfico depois da migração para a Binance").
- **P2-11. O controle "Alertar" é pequeno e se chama "TG" no celular.**
  - Onde: `.telegram-toggle` em Favoritos (incumbente visual, agora para todo dono).
  - Problema: 32 px de altura no desktop e 28×56 px no celular, com o texto "TG". Antes só o admin via; agora é controle de todo usuário. As linhas de cripto (COPIED) ficam sem o `aria-label` que d3 promete.
  - Correção: rótulo visível "Alertar" no cartão, alvo de 44 px no celular, `aria-label` em todas as linhas.
- **P2-12. O modal de Salvar perde o foco depois do sucesso.**
  - Onde: `results.html`, depois de "Salvar".
  - Problema: o botão Salvar vira `disabled` com o foco nele, o foco cai no `body` e Esc deixa de fechar o modal. "Ver em Favoritos" tem 15 px de altura a 1440.
  - Correção: mover o foco para o status de sucesso ou para "Ver em Favoritos" (44 px), e manter Esc fechando.

### P3: detalhe de Apply (aceito; não reabrir como P0/P1)

- Os itens da subseção "P3 aceitos" do autor.
- **Telegram sem reenvio depois de queda no meio do envio (`unknown`):** coerente com "restart não duplica"; perda rara, visível no resumo do scan. Sugestão de Apply: contar `unknown` no resumo do admin com o favorito e o candle.
- **Aviso de atraso por (fonte, ativo):** NVDA em duas fontes pode gerar dois avisos; aceitável, porque são dados distintos e o texto diz a fonte.
- **Leitura que muda e volta enquanto o ativo está atrasado** não gera alerta na recuperação; aceitável (a leitura normal decide).
- **Migração que zera "Alertar" de quem não é admin:** coerente. A marca nunca teve efeito para essas pessoas (o `PATCH` recusava e o scan só lia o admin), e é coerente com as respostas possíveis das perguntas 1 e 2 (D cria favoritos já marcados, B de Q2 vale só daqui em diante).
- **Lote/Descoberta com 1 estrela** põem ação/ETF no Monitor, como a cripto já faz; observar o volume com lote de até 1.000 ativos.
- **Horário na mensagem:** "pregão fechou às 17:00 BRT" vale no horário de verão de NY; no inverno de NY o fechamento é 18:00 BRT (o protótipo acerta o feriado de novembro com 11:30). O Apply calcula.
- **Tab sai do modal de Salvar** (sem trap): incumbente do `SaveFavoriteModal`.
- **Vitrine com apelido e nota do admin** no protótipo: a redação é do servidor (incumbente, `monitor-curated-fallback`).
- **`design.md` diz 404 na URL pública:** hoje é 200; atualizar Risks e Prototype Validation.
- **"Tier 3" na Descoberta × "1 estrela"/"Acompanhar" em Favoritos:** vocabulário incumbente.

## Persona red flags

- **Alan com 8 favoritos marcados:** num dia de virada, o sexto alerta chega no dia seguinte (P2-5).
- **Pessoa do beta que marcou "Alertar" em NVDA:** não recebe nada porque NVDA não está na carteira, e nada na tela explica (P2-3).
- **Notebook de 1024–1180 px:** em Favoritos, não sabe qual NVDA está ligando (P1-1).
- **Celular:** vê "TG" em vez de "Alertar", com alvo de 28 px (P2-11); toca "Ver Trades" da fonte antiga e nada acontece (P2-8).
- **Usuário novo depois do deploy:** lê "Até 26/10 você recebia…" sem nunca ter recebido (P2-4).

## Questions to consider

- O Monitor mostra "Pregão aberto" para o NVDA da fonte antiga (Stooq, só diário). O estado do mercado vale para ela, mas "aberto" pode sugerir dado intradiário que essa fonte não tem.
- Com o aviso de atraso também na cripto, um atraso de 1 dia da Binance Spot segura todos os sinais de cripto da pessoa naquele dia. Vale um texto no aviso dizendo quantos favoritos ficaram em espera.

## Coerência com as 3 perguntas abertas (sem decidir)

- **Q1, transição:** A (recomendada) está no protótipo e no spec. B (14 dias de catálogo) pede o scan com duas origens por 14 dias e uma frase da faixa com prazo. C (corte seco) tira a faixa e a mensagem; o requisito "Faixa da transição" de `monitor-multiclass` passa a ser condicional. D (copiar já marcados) dispensa a faixa para essas pessoas e convive com a migração que zera as marcas antigas. O spec já trava o Apply até a decisão. Coerente com as quatro.
- **Q2, favorito novo nasce marcado?** Os specs já escrevem a resposta A como requisito (`favorite-configuration-identity`: "Todo favorito novo… MUST nascer com `notify_telegram = false`"; `discovery-promotion` e `multiclass-batch` idem). Com B, mudam esse requisito (separar "resultado" de "lote/Descoberta") e a nota do modal de Salvar ("O favorito nasce sem alerta"). A migração não muda.
- **Q3, horário:** A (só 08:05) é o que o protótipo mostra. Com B, a passada das 18:30 BRT fica antes do fechamento + tolerância no inverno de NY (fecha 18:00 BRT + 90 min = 19:30). Nesse caso o candle do dia ainda não chegou, não conta como atraso e o sinal sai só às 08:05, como hoje. Para B valer o ano todo, a passada precisa ser às 19:30 BRT ou depois. Ela também dobra a disputa pelo limite de mensagens (P2-5).

## Perguntas para Alan (rubrica 7)

- **Mais de 5 alertas no mesmo dia.**
  - Conflito: o limite é de 5 mensagens por hora por pessoa e a varredura roda uma vez por dia, então, na prática, são 5 alertas por dia. O que passar disso só sai na manhã seguinte, com o candle de ontem, ou some se a leitura mudar de novo. Com um alerta por favorito, o aviso de atraso e o aviso da transição, o volume cresce.
  - **A (Recommended):** o limite deixa de cortar alertas de sinal e avisos de atraso da varredura. A chave do evento já impede repetição. O limite continua só no aviso de falha da carteira Binance.
  - **B:** juntar numa mensagem só todos os alertas da pessoa naquela varredura.
  - **C:** manter o limite de 5 por hora; o excedente sai na varredura do dia seguinte, como está no design.

## Disposition (resumo)

- Tokens L1–L3 ok; o gate do clone passa; `live.css` = CSS vivo servido; sem ANTES/DEPOIS; 5 URLs extras justificadas pelo escopo.
- Os 10 itens do Entra têm decisão, spec e, onde há tela, estado visível. As 5 decisões de Alan foram respeitadas. Sem escopo furado; as 6 telas cabem no card.
- A11y medida: contraste ≥ 4,5 em todo texto novo, estado nunca só por cor, 1440/390 sem rolagem horizontal; falhas em alvos (Alertar, "Ver em Favoritos") e no foco depois de salvar.
- P0 = 0 · P1 = 1 · P2 = 12 (7 produto, 5 mecânico) · P3 = aceitos.
- **Verdict: PASS com rework.** O P1-1 cabe no rework único da dupla (d3 + tasks 5.3 + `delta.css`, com medida a 1024). Os P2 entram no mesmo rework, se o pai quiser; senão ficam como residual na seção de crítica do `design.md`. A pergunta nova vai para Alan junto das 3 abertas.
