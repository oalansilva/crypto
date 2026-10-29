`proveniência: Assessment A (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/cf-assess-a-d2.json` (attempt `9423d8f8-76bc-4219-bb4b-2e2c58014564`, band `juizo`, role `assessment-a`, capture_sha256 `127ab1f7dfd80bd558c370dbecfafe41a24c36cac32d02c5ac79e526c0f0aff0`, arquivo sha256 `e3436bca2d20fcc6e1816fbba3942039613c70db9254110ce536a95bd7e97ca9`). Wave capture `cf-assess-a-d2w.json` (attempt `c0d6d1e0-b5f6-4492-b578-bf48ee0154dd`, arquivo sha256 `f0b24898df021ecee65f26c968e3c2cfeab0f4f3139752908646f38c38f847af`). Birth: `.cursor/tmp/claude-evidence/9423d8f8-76bc-4219-bb4b-2e2c58014564.birth.json`.

# Assessment A: card 1122, change card-1122-favoritos-alertas-acoes-etfs (rodada d2)

> Avaliador A isolado (produto, UX, acessibilidade e fidelidade do clone) da onda dupla com-tela da rodada d2. Não li o transcript do pai nem o snapshot do Assessment B. Não spawnei filho, não chamei `process_event`, não arrastei Status e não comentei no issue. Não editei `design.md`, OpenSpec, o protótipo, `backend/` nem `frontend/src/`. Única escrita: este arquivo (a versão d1 fica no git).

## Metadata

- card: 1122, "Acompanhar favoritos e receber alertas de ações e ETFs no horário correto"
- change: `card-1122-favoritos-alertas-acoes-etfs`, rodada d2 (mudança sobre o que já está em `develop`/DEV)
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1122-favoritos-alertas-acoes-etfs`
- branch / q_git: `card-1122-favoritos-alertas-acoes-etfs` @ `9b83d25e` (pacote modificado e não commitado; `configure.html` removido)
- tupla: `bound_card=1122` · Status = Design (dado no prompt; não arrastado)
- data: 2026-10-27
- cliente: Claude Code (adapter cooperativo, sem modo Auto), superfície claude-desktop
- Issue: REST `gh api repos/oalansilva/crypto/issues/1122` e `--paginate …/comments` (22 comentários). Fronteira: "Não homologar:" (27/10 17:45), "Decisões de Alan para a nova regra de alertas" (4 decisões, 17:51) e "Decisões de Alan no Design d2" (3 decisões, 18:42). Não reabri nenhuma.
- Decisão conhecida fora do meu achado: o Monitor do admin **continua abrindo em "Em portfólio"** (d2-3 de Alan); o `design.md` (decisão 21, Q3), o spec `monitor-multiclass` ("Carteira é só informação da tela" + cenário "Admin abre o Monitor"), as tasks 8.6/8.11, o Apply contract e o protótipo ainda dizem "Todos". Vai para o rework. Avalio só as consequências de UX (P1-1).
- sha256:
  - `design.md` `e79b20b0f943944a9a2ced1a620702743a5e4779be75d2856ee2bbfd1372ad36`
  - `proposal.md` `77f44347…d1a6` · `tasks.md` `98b9ae6a…a18b`
  - specs: `favorite-telegram-alerts` `fbae5287…139a`, `monitor-multiclass` `fa004fd1…e1d9`, `monitor-telegram-favorite-toggle` `be593711…6aa1`, `monitor-telegram-alerts` `72df4590…f89b`, `monitor-telegram-general-alerts` `8794081a…3da1`, `monitor-curated-fallback` `2db998fd…e500`, `discovery-promotion` `1cd2c8ff…4493`, `multiclass-batch` `0c77ab31…ffb0`, `favorite-configuration-identity` `e76631a3…3201`, `favorites-class-comparison` `7e12d11a…3172`, `market-session-awareness` `a4061042…4a52`, `favorite-backtest-refresh` `50a94132…3847`, `crypto-only-mvp` `9c0c2054…59de`, `favorites` `10d6a5d3…1ffc`
- Ignore list: `.impeccable/critique/ignore.md` não existe.
- Ferramentas: Playwright Python, Chromium headless shell 1243 (arm64, `executable_path` explícito), `pt-BR`, tema escuro, contexto novo por viewport: 1440×900, 1280×800, 1024×768 e 390×844 (`isMobile`, toque). **Servidor local** `python3 -m http.server 8791` na pasta `frontend/public` do worktree (a URL pública serve a d1; ver P2-1). Contraste pela cor computada contra o fundo efetivo (compondo os ancestrais), sem axe-core. A skill `impeccable` deste repo é ponte para `.agents/skills/impeccable/` (`.cursor/skills/impeccable/` não existe); segui `reference/critique.md` (Assessment A). Scripts, JSON e PNGs em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/6e575182-2e59-4ca3-aca7-4c1cc8d2f8a5/scratchpad/c1122A-d2/` (não versionados).

## Digest (disco == servido localmente; público ≠)

| Arquivo | sha256 disco (= local) | público (d1) |
|---|---|---|
| `index.html` | `ca632b32a2fb…` | `d0d7aa5a80af…` |
| `favorites.html` | `106ff36d9e92…` | `09880e120ada…` |
| `results.html` | `5159b303aa6c…` | `95909352c0c3…` |
| `discovery.html` | `0bb4e4e150e8…` | `f3720c4db2d7…` |
| `profile.html` | `2781744bf5fb…` | `9824fe0bc64d…` |
| `live.css` | `353ac045db2d…` | `8f4edf0aca9a…` |
| `delta.css` | `92fe48d60dc0…` | `9e34bd03b55b…` |
| `delta.js` | `7bfd0d9c90aa…` | `37794adfaaa2…` |
| `configure.html` | removido | ainda 200 |

`live.css` local é igual, byte a byte, a `https://dev.criptofarol.com.br/assets/index-DOHmvARO.css`, a folha que `/monitor` serve hoje (bundle `index-C9_PkDmo.js`). Nos fluxos clicados (5 páginas × 4 larguras, 6 cenários do Monitor, vitrine, detalhe, estrela em Favoritos) não houve `console.error`, `pageerror` nem resposta ≥ 400.

## Tokens parseáveis (rubrica 6, D4)

`design.md`, L1–L3, cada um em linha própria:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Bloco D4 em L5 idêntico ao da skill. `design_clone_gate` (HEAD): `design_token_gap` = None; `parse_live_route` = `/monitor`; `parse_surface` = `existing`; `classify(index.html, /monitor)` = PASS; `clone_gate_ok` = True; `copied_utf8_sum` = 120.281 (confere com o `design.md`). Marcadores pareados: index 55/55 COPIED e 59/59 DELTA; favorites 49/49 e 57/57; results 5/5 e 5/5; discovery 8/8 e 8/8; profile 5/5 e 5/5. Nenhuma página tem "ANTES"/"DEPOIS". As 4 URLs extras têm copy visível que muda; `configure.html` saiu com justificativa (o Combo não muda). **ok.**

## Decisões de Alan de 27/10 (rubrica 1)

| Decisão | design / spec / tasks | Tela (protótipo d2) |
|---|---|---|
| R1. Alerta = o que a pessoa monitora (estrela no Monitor), ligado por padrão, desliga no Monitor por estratégia; "Alertar" sai de Favoritos | d2, d3, d18, d19 · `favorite-telegram-alerts` R1/R2, `monitor-telegram-favorite-toggle`, `monitor-multiclass` "Controle de alerta…" · 8.2, 8.3, 8.6, 8.7 | Interruptor "Alerta ligado/desligado" nas 6 linhas (1440/1280 na célula de ações; 1024 na célula Status), nos 6 cartões (390) e no detalhe; Favoritos sem "Alertar" em nenhuma largura. **ok** |
| R2. A carteira não decide; cripto perde a exceção da Binance; mesma regra nas 3 classes | d6, d9 · `favorite-telegram-alerts` "Entrada e saída…" e "Carteira Binance fora da varredura", `monitor-telegram-alerts` (REMOVED) · 8.2 | Cenários "Entrada sem carteira" (NVDA fora), "Saída" (SPY), "Cripto com saldo" (BTC reentrada), ajuda "Entrada e saída saem com ou sem o ativo na carteira". **ok** |
| R3. O catálogo não alerta | d2, d16 · `monitor-curated-fallback`, `monitor-multiclass` "Faixa da vitrine" · 8.4, 8.6 | Vitrine com "Catálogo · sem alerta", sem interruptor, faixa nova. **ok** (copy da faixa de Favoritos: P2-2) |
| R4. Lote e Descoberta salvam sem estrela | d12 · `multiclass-batch`, `discovery-promotion`, `favorite-configuration-identity` · 8.3, 8.8 | QQQ (lote) e AAPL (Descoberta) "Fora do Monitor"; modal "Promover a favorito" · "Favoritos · sem estrela". **ok** |
| d2-1. Migração tira a estrela automática de lote/Descoberta; volta ligado ao dar a estrela | d20 Q1 · 8.1 | n/a (dados). O `design.md` ainda a trata como pergunta aberta (P3-2). |
| d2-2. Toda estratégia no Monitor fica com alerta ligado | d20 Q2 · 8.1 | n/a (dados). Idem P3-2. |
| d2-3. Monitor continua abrindo em "Em portfólio" | **não refletido** (decisão conhecida, rework) | Protótipo em "Todos". Consequência de UX: P1-1. |

Sem escopo furado: nada novo de canal, robô, ordem ou migração de fonte. O resto do card (calendário, estado do mercado, atraso, identidade) fica como implementado.

## Estados (rubrica 2)

- **Alerta ligado/desligado no Monitor:** ligado = sino + "Alerta" verde + "ligado" (borda sólida); desligado = sino cortado + cinza + "desligado" (borda **tracejada**). Medido nas 4 larguras: 6 interruptores visíveis por largura, um por linha/cartão, todos dentro da área visível (1440: x 1292–1399 com o Monitor até 1370 e a tabela até 1413; 1024: na célula Status, x 540–665, enquanto a tabela vai até 1257 e a área termina em 958). ETH/USDT desligado. **ok.**
- **Detalhe:** NVDA aberto com o interruptor "Alerta: ligado" (nome com ativo, tempo, estratégia e fonte) e a ajuda nova; sem a tag "Alerta". **ok.**
- **Favorito sem estrela fora do Monitor:** em Favoritos, "Fora do Monitor" em QQQ/AAPL, ajuda das estrelas, status ao dar a 1ª e tirar a última estrela ("AAPL 1d entrou no Monitor com o alerta ligado." / "…saiu do Monitor e não manda mais alerta."). **ok.** No Monitor, o estado "Sem estrela · sem alerta" do spec é inalcançável (P2-3).
- **Catálogo sem alerta:** vitrine com faixa `role=status`, frase datada opcional (caixa na Demonstração), "Ir para Favoritos" 44 px, "Catálogo · sem alerta" nas linhas, zero interruptor. **ok.**
- **Entrada sem carteira:** NVDA fora da carteira com alerta de Compra. **ok** na tela "Todos"; escondida no padrão "Em portfólio" (P1-1).
- **Cripto com saldo recebendo reentrada:** BTC/USDT, mensagem de Compra. **ok.**
- **Atraso real:** só a mensagem do Telegram. A linha de NVDA, destacada no cenário "Dados atrasados", continua "Aberto · fecha 17:00 (16:00 NY)" e sem "Sinal em espera"; não há tela de `stale_detail` (P1-2).
- **Mercado fechado:** não demonstrável na d2 (relógio fixo na seg. 15:00 BRT, só "Aberto"). Sem delta nesta rodada e já vivo no DEV; aceito (P3-4).

## Clareza para o usuário (rubrica 3)

- "Estrela = monitorar = alerta" está dito nos lugares certos: ajuda de Favoritos ("Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor)…"), legenda "No Monitor"/"Fora do Monitor", status ao dar/tirar estrela, nota do modal de Salvar, nota da Descoberta e Perfil ("Desligue por estratégia no Monitor.").
- "Onde desligar": o interruptor está em toda linha e cartão. Duas lacunas: (a) com o padrão "Em portfólio", as estratégias fora da carteira (que agora alertam) e os interruptores delas ficam escondidos ao abrir (P1-1); (b) a mensagem do Telegram não diz como parar (P2-5).
- Copy herdada que mudou de sentido: o resumo de Favoritos diz "Acompanhar · Monitorar quando fizer sentido" para 1 estrela, mas 1 estrela agora já é Monitor + alerta (P2-4).

## Fidelidade (rubrica 5)

- O canônico clona `/monitor` do DEV atual (com o #1122 anterior): AppNav, ajuda, topo, indicadores, filtros, seções e linhas vivas. Textos COPIED conferidos no bundle vivo (`Posição ativa com gestão…`, `Acompanhe as estrategias que voce selecionou em Favoritos`, `Monitorar quando fizer sentido`, `Catálogo operacional…`). `live.css` = CSS vivo servido.
- Linha a 1440: BTC 142 px, NVDA 178, SPY 178, SOL 141, ETH 138, NVDA antiga 177 (igual ao `design.md`). Cartão a 390: 927–972 px (vivo 845/913; +interruptor e ajuda, P2-7).
- 1440/1280/1024/390 sem rolagem horizontal em todas as páginas e na vitrine (`scrollWidth == clientWidth`).
- Desvio dentro do delta: o filtro está em "Todos" (decisão conhecida, rework).

## Acessibilidade (rubrica 4, medida)

- **`role=switch`:** `<button role="switch" aria-checked>` nas 4 larguras e no detalhe; o estado "ligado/desligado" visível fica `aria-hidden`. Nome acessível contém o texto visível "Alerta" (label-in-name) e distingue as duas NVDA ("… · Binance Ações" × "… · Stooq fonte antiga"). Space e Enter alternam; o `role=status` anuncia "Alerta de BTC/USDT 1d desligado: nada sai no Telegram para esta estratégia."; clicar não abre a linha (detalhes abertos 1 → 1). **ok.**
- **Foco:** contorno 2 px `#3b82f6` no desktop, `:focus-visible` verdadeiro. A 390, contorno 3 px `#0ecb81`, a mesma cor do "ligado" (P3-5).
- **Contraste (texto novo, menor razão):** "Alerta ligado" 5,74 (11 px); "Alerta desligado" 6,12 (11 px); ajuda da carteira 6,12 (12 px); "Catálogo · sem alerta" 6,12 (10 px); faixa da vitrine 14,49 e link 13,55; ajuda de Favoritos 5,56 (14 px); "Fora do Monitor" 6,81 e "No Monitor" 9,1 (10 px); faixa de Favoritos 11,36; nota do Salvar 10,24; nota da Descoberta 6,12 (11 px); Perfil 13,36. **Tudo ≥ 4,5:1.**
- **Estado só por cor:** não há. Ligado/desligado diferem por ícone (sino × sino cortado), texto e borda (sólida × tracejada).
- **Alvos:** interruptor 44 px de altura no cartão a 390 (127–130 × 44); 30 px no desktop (≥ 24 px, WCAG 2.5.8); "Ir para Favoritos" 44 px. Abaixo de 44 no celular: estrelas de Favoritos 28×28 (incumbente, mas agora são a porta do alerta: P2-8).
- **Diálogos:** Salvar `role=dialog aria-modal=true aria-labelledby=save-favorite-title`; Descoberta `aria-labelledby=modal-title`. Sem texto antigo ("Alertar", "tier 3", "No portfólio", "nasce sem alerta").

## Heurísticas Nielsen (0–4), só neste snapshot

| # | Heurística | Nota | Nota curta |
|---|---|---|---|
| 1 | Visibilidade do estado | 3 | Ligado/desligado em toda linha, cartão e detalhe. Atraso não aparece na linha do cenário (P1-2) |
| 2 | Linguagem do usuário | 3 | "Alerta ligado", "No Monitor", "Fora do Monitor". "Monitorar quando fizer sentido" ficou falso (P2-4) |
| 3 | Controle e liberdade | 3 | Desliga por estratégia, reversível, sem abrir a linha. Escondido no padrão "Em portfólio" (P1-1) |
| 4 | Consistência | 3 | Mesmo controle nas 4 larguras e no detalhe; mesma frase da carteira em todo lugar |
| 5 | Prevenção de erro | 3 | Lote/Descoberta sem estrela; vitrine sem alerta; status ao dar a 1ª estrela |
| 6 | Reconhecer em vez de lembrar | 3 | Nome acessível com ativo/tempo/estratégia; a ajuda da carteira repete em todo cartão (P2-7) |
| 7 | Flexibilidade | 3 | Filtros de carteira, estrela e tempo; sem desligar em lote (fora de escopo) |
| 8 | Estética e minimalismo | 3 | Interruptor no lugar da tag "Alerta" deixou a linha mais curta (BTC 158 → 142 px) |
| 9 | Recuperar de erros | 3 | Erro do PATCH volta o estado e avisa (só no texto, P3-3) |
| 10 | Ajuda | 3 | Favoritos, Perfil e modais explicam; Monitor e Telegram não dizem onde desligar (P2-5) |
| | **Total** | **30/40** | |

## Design specificity / cognitive load

A regra nova é simples de dizer ("estrela = Monitor = alerta; desliga na linha") e o protótipo a diz com o vocabulário da tela, sem jargão de banco. A carga cai em Favoritos (sai uma coluna e um aviso de carteira) e sobe pouco no Monitor (um botão por linha, que substitui a tag "Alerta"). O ponto de decisão mais pesado agora é "recebi um alerta de algo que não vejo": no Monitor do admin, que abre em "Em portfólio", metade das estratégias que alertam fica fora da vista.

## Emotional journey

Pico positivo: a compra de NVDA chega justamente quando Alan ainda não tem o ativo, e a reentrada de BTC deixa de sumir. Vale: o primeiro alerta de uma estratégia fora da carteira leva Alan a um Monitor que não a mostra (P1-1); e quem recebe alertas de tudo o que estrelou não encontra, na mensagem, como parar (P2-5).

## What's working

- As 7 decisões de Alan viraram texto testável (spec + task + cenário), sem reabrir nenhuma, e a transição ficou com marca segura em dry-run e `failed`.
- O interruptor é um `switch` de verdade: nome com ativo/tempo/estratégia, estado por ícone + texto + borda, 44 px no celular, não abre a linha, anuncia no status; a 1024 vai para a célula Status em vez de cair na parte cortada da tabela.
- Favoritos ficou mais limpo: a Estratégia ganhou largura (342 px a 1440, 296 a 1280) e a estrela virou a porta explícita do Monitor, com legenda e status.

## Findings

### P0: bloqueante (produto / escopo / contrato visível)

Nenhum.

### P1: deve corrigir antes de PASS

- **P1-1. Com "Em portfólio" ao abrir, a estratégia fora da carteira que mandou alerta, e o interruptor dela, ficam escondidos.**
  - Onde: consequência da decisão d2-3 de Alan; protótipo `index.html` (filtro), `monitor-multiclass` "Carteira é só informação da tela", tasks 8.6/8.11, cenário "Entrada sem carteira" da Demonstração.
  - Medido: no protótipo, 3 das 6 estratégias estão fora da carteira (NVDA Binance, ETH/USDT, NVDA fonte antiga; cartões "Fora do portfólio"). Em "Em portfólio" elas somem, inclusive NVDA, que é exatamente a compra que Alan disse querer receber, e ETH, a única desligada. O cenário "Entrada sem carteira" destaca uma linha que o padrão esconde. Não há contador nem aviso de que existem estratégias alertando fora da vista.
  - Correção: no rework, além de trocar o padrão para "Em portfólio" (decisão conhecida), clonar o canônico nesse estado e mostrar como chegar ao interruptor: recomendação, na barra de filtros, com "Em portfólio" ativo, "+N fora da carteira com alerta ligado · Ver todos" (um clique leva a "Todos"); a Demonstração passa a "Todos" ao abrir um cenário de linha fora da carteira. Atualizar spec, tasks 8.6/8.11 e Apply contract. Pergunta fechada abaixo, caso Alan não queira o aviso.
  - Disposition: rework (autor) + pergunta ao Alan.
- **P1-2. "Dados atrasados" não aparece na linha, e o delta `stale_detail` não tem tela.**
  - Onde: cenário "Dados atrasados" de `index.html`; decisão 8 (delta "o Monitor também lê `stale_detail`"); Apply contract ("linha retida por outro tempo gráfico com o horário e o rótulo da série atrasada"); `monitor-multiclass` cenário "1d em espera por causa do 15m"; task 8.5.
  - Medido: no cenário, a linha de NVDA destacada mostra "EM POSIÇÃO · Aberto · fecha 17:00 (16:00 NY)" nas 4 larguras, sem "Dados atrasados" nem "Sinal em espera", enquanto o painel diz "NVDA atrasada… sinais em espera". `grep "no 15m"` em `index.html` = 0. A d1 tinha essa tela; a d2 recapturou o vivo com mercado aberto e não pôs o estado.
  - Correção: no cenário "Dados atrasados", trocar o estado da linha e do cartão de NVDA para "Dados atrasados · falta seg. 26/10" + "Sinal em espera" (âmbar), e acrescentar a variante `stale_detail` ("Dados atrasados no 15m · falta 10:30" na linha; "Dados atrasados no 15m · último 09:30; esperado 10:30" no cartão).
  - Disposition: rework (autor).

### P2: residual visível, não bloqueia o teto 1+1+1

**Produto**

- **P2-1. A URL pública mostra a d1, que é a que Alan abre para aprovar.**
  - Onde: `design.md` Prototype (URL canônica) e Prototype Validation ("URL pública: não serve os arquivos novos").
  - Problema: os 8 arquivos públicos têm sha da d1 (tabela acima); `configure.html` ainda responde 200. Na URL, Favoritos tem "Alertar" e o Monitor tem a tag "Alerta".
  - Correção: antes de pedir a Aprovação de Design, fazer a URL pública servir a d2 (ou dar ao Alan a URL que serve) e conferir o sha. Não é tarefa do autor.
  - Disposition: pai, antes do T5.
- **P2-2. A faixa da vitrine de Favoritos manda quem não é admin usar Descoberta e lote.**
  - Onde: `favorites.html` faixa da vitrine; decisão 16 ("salve as suas no Combo, na Descoberta ou no lote e dê pelo menos 1 estrela aqui").
  - Problema: a vitrine só aparece para quem não é admin, e lote (`POST /backtest/batch`) e Descoberta (`discovery_routes`) exigem `get_current_admin`. A frase herdou o erro da d1, mas a d2 a reescreveu.
  - Correção: "…salve um resultado do Combo nos Favoritos e dê pelo menos 1 estrela aqui."
- **P2-3. "Sem estrela · sem alerta" no Monitor é um estado que não acontece.**
  - Onde: decisão 18 ("o filtro 'Estrelas' do Monitor deixa ver 'Sem estrela' e 'Todas'"), `monitor-multiclass` e `monitor-telegram-favorite-toggle` ("Unstarred own rows SHALL show…"), task 8.6/8.11.
  - Problema: o filtro vivo tem só "Estrelas: Todas / 3 / 2 / 1" e a lista corta em `isRatedOpportunity` (`MonitorStatusTab.tsx:166`, `:930`); `tierFilter` é fixo em `rated` (sem `setTierFilter` em uso). Quem não é admin e só tem favorito sem estrela vê a vitrine. O spec pede um estado sem caminho; o Apply teria de inventar um filtro.
  - Correção: tirar "Sem estrela · sem alerta" do Monitor (spec, decisão 18, tasks 8.6/8.11 e o P3 do protótipo); o estado sem estrela vive em Favoritos ("Fora do Monitor").
- **P2-4. "Acompanhar · Monitorar quando fizer sentido" contradiz 1 estrela = Monitor + alerta.**
  - Onde: resumo por estrelas de `/favorites` (COPIED; "Acompanhar 1★ · Monitorar quando fizer sentido", "Top picks · Fila principal do Monitor").
  - Problema: com a regra nova, 1 estrela já põe a estratégia no Monitor com alerta ligado; o texto sugere que 1 estrela ainda não monitora.
  - Correção: "Acompanhar · No Monitor, com alerta" (ou "Entra no Monitor"); as outras duas descrevem prioridade, não entrada.
- **P2-5. A mensagem do Telegram e o Monitor não dizem como parar de receber.**
  - Onde: mensagens de sinal e de atraso da Demonstração; ajuda "Como usar o Monitor" (COPIED).
  - Problema: o alerta agora vem ligado em tudo o que tem estrela, inclusive fora da carteira. Quem recebe não sabe, pela mensagem, que desliga na linha do Monitor. O Perfil diz, mas não é onde a pessoa está quando o alerta chega.
  - Correção: uma linha no fim da mensagem de sinal ("Para não receber desta estratégia, desligue o Alerta dela no Monitor.") e uma frase na ajuda do Monitor ("Toda estratégia aqui manda alerta no Telegram; desligue no botão Alerta da linha."). Texto exato da mensagem é P3 do autor.

**Mecânico**

- **P2-6. Status de Favoritos fica longe da estrela no celular.**
  - Onde: `favorites.html`, `[data-m22-status]` no topo (y = 613 px a 390, 360 a 1440).
  - Problema: ao dar a 1ª estrela num cartão mais abaixo, "…entrou no Monitor com o alerta ligado." sai fora da tela; só a legenda "No Monitor" muda perto do dedo, e ela não diz "com alerta".
  - Correção: legenda "No Monitor · alerta ligado" por 1 ciclo após a 1ª estrela, ou status perto do cartão. Leitor de tela já recebe pelo `role=status`.
- **P2-7. A ajuda da carteira repete em todo cartão a 390.**
  - Onde: cartões do Monitor (6 de 6 com "Entrada e saída saem com ou sem o ativo na carteira…"); `monitor-multiclass` exige no cartão e no detalhe.
  - Problema: +82 px por cartão (BTC 845 → 927); com 20 estratégias, ~1.600 px a mais de rolagem para a mesma frase.
  - Correção: no cartão, só o interruptor; a frase uma vez acima da lista (ou no detalhe, como na linha do desktop).
- **P2-8. Estrela de Favoritos com 28 px no celular, agora que é a porta do alerta.**
  - Onde: `[aria-label="Prioridade por estrelas"] button` (COPIED, incumbente; nome pelo `title` "1 estrela").
  - Problema: o toque errado põe ou tira uma estratégia do Monitor e do Telegram.
  - Correção: 44 px no cartão do celular e `aria-label` "1 estrela"/"2 estrelas"/"3 estrelas" além do `title`.

### P3: detalhe de Apply (aceito; não reabrir como P0/P1)

- Os itens da subseção "P3 aceitos" do autor.
- **P3-1.** Decisão conhecida "Em portfólio" (fora do meu achado): lugares a trocar no rework — `design.md` d21, Q3, Apply contract ("admin abre em 'Todos'"), Prototype ("visão do admin em 'Todos'"); `monitor-multiclass` "Carteira é só informação da tela" e cenário "Admin abre o Monitor"; tasks 8.6 e 8.11; `index.html` (segmento "Todos" ativo).
- **P3-2.** Q1 e Q2 seguem em Open Questions, mas Alan já respondeu as duas com a recomendada (d2-1, d2-2): passar para decisões e tirar "até a resposta" do Migration Plan e da task 8.1.
- **P3-3.** O erro do interruptor ("Não foi possível mudar o alerta. Tente de novo.") e o estado com o Telegram desligado no Perfil não têm tela; os textos estão no design.
- **P3-4.** Mercado fechado não aparece na d2 (sem delta; vivo no DEV e no protótipo d1 no git).
- **P3-5.** Foco a 390 em verde `#0ecb81` sobre o interruptor verde; usar o azul do desktop ou `outline-offset`.
- **P3-6.** No protótipo, o status "Alerta de … ligado" continua visível ao trocar para a vitrine; limpar ao trocar de vista.
- **P3-7.** Tirar todas as estrelas e dar de novo religa o alerta que a pessoa tinha desligado. É coerente com "estrela liga" (d3) e o status de Favoritos diz "com o alerta ligado"; só registrar no teste 8.9.
- **P3-8.** Faixa da vitrine do Monitor diz "Salve uma nos Favoritos" também a quem já tem favoritos sem estrela; "Dê pelo menos 1 estrela em Favoritos" cobre os dois casos.
- **P3-9.** Sino (ícone de alerta) na faixa que diz "sem alerta no Telegram" (incumbente da d1).

## Persona red flags

- **Alan, admin, abrindo o Monitor depois da compra de NVDA no Telegram:** a tela abre em "Em portfólio" e NVDA não está lá; para desligar, precisa saber que existe "Todos" (P1-1).
- **Alan, terça de atraso:** recebe "Dados atrasados" de NVDA, abre o Monitor e a linha está como se nada houvesse (no protótipo; P1-2).
- **Pessoa do beta sem favorito próprio:** a faixa de Favoritos manda usar Descoberta e lote, que ela não acessa (P2-2).
- **Pessoa que estrelou 12 estratégias:** recebe alerta de todas, inclusive fora da carteira, e a mensagem não diz onde parar (P2-5).
- **Celular:** rola ~80 px a mais por cartão pela mesma frase (P2-7); estrela de 28 px decide alerta (P2-8).

## Questions to consider

- O aviso de atraso vai a quem tem "o ativo no Monitor com alerta ligado". Com "Em portfólio" ao abrir, a linha atrasada também pode estar fora da vista; o mesmo contador de P1-1 resolve.
- A ajuda "Entrada e saída saem com ou sem o ativo na carteira" fica ao lado de "No portfólio" no cartão. Funciona como explicação, mas os dois botões lado a lado podem parecer ligados entre si; vale manter a frase perto dos dois (já está).

## Perguntas para Alan (rubrica 7)

- **Estratégia fora da carteira escondida ao abrir o Monitor.**
  - Conflito: o Monitor continua abrindo em "Em portfólio", e agora estratégia fora da carteira também manda alerta. Quando chega a compra de um ativo que você ainda não tem, a linha dela e o botão para desligar o alerta não aparecem até você clicar em "Todos".
  - **A (Recommended):** com "Em portfólio" ativo, mostrar na barra de filtros "+N fora da carteira com alerta ligado · Ver todos"; um clique leva a "Todos".
  - **B:** não mostrar nada; você troca para "Todos" quando precisar.
  - **C:** a mensagem do Telegram de ativo fora da carteira avisa "fora da carteira: no Monitor, veja em Todos".

## Disposition (resumo)

- Tokens L1–L3 ok; gate do clone passa (120.281 B copiados); `live.css` = CSS vivo servido; sem ANTES/DEPOIS; 4 URLs extras justificadas.
- As 4 decisões da regra nova e as 2 de dados do d2 estão em design, specs, tasks e tela; a d2-3 ("Em portfólio") é rework conhecido.
- A11y medida: `role=switch` com `aria-checked`, nome com ativo/tempo/estratégia, Space/Enter, status anunciado, contraste ≥ 4,5 em todo texto novo, 44 px no cartão, sem estado só por cor, sem rolagem horizontal a 1440/1280/1024/390.
- P0 = 0 · P1 = 2 · P2 = 8 (5 produto, 3 mecânico) · P3 = aceitos.
- **Verdict: PASS com rework.** P1-1 entra junto com a troca conhecida para "Em portfólio" (protótipo, spec, tasks); P1-2 é uma troca de estado no cenário "Dados atrasados" mais a variante `stale_detail`. Os P2 de produto cabem no mesmo rework; P2-1 é do pai antes do T5. A pergunta nova vai ao Alan.
