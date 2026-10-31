# Assessment A — card 1160 · change card-1160-landing-auditoria · onda 1160-d2

## Metadata

- Papel: Assessment A (isolado), foco em produto, escopo, UX, acessibilidade e fidelidade ao card, ao produto atual e à página viva. O Assessment B (detector, gate, navegador) roda em paralelo.
- Rodada: d2 (devolução do Alan no T6, 29/10/2026, recibo issuecomment-6505701552).
- Model selection capture: `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/b7647ba9-4392-4616-a54f-e9ffed900257/scratchpad/capture-assessment-a-1160-d2.json`
- Worktree: `card-1160-landing-auditoria` @ 768467b8 + artefatos não commitados da d2.
- Material lido: `proposal.md`, `design.md` (inteiro), `tasks.md`, specs `landing-conversion-copy` e `landing-legal-pages`, protótipo (`index.html`, `privacidade.html`, `termos.html`, `assets/`), issue #1160 e comentários por REST, relatório A da d1, `openspec/changes/archive/2026-10-29-card-1122-*` (proposal e design), `openspec/specs/monitor-curated-fallback/spec.md`, `frontend/src/App.tsx`, `MonitorStatusTab.tsx`, `OpportunityCard.tsx`, `marketState.ts`, `ComboResultsPage.tsx`, `ops/systemd/*telegram-alert-scan.timer`, `docs/monitor-telegram-alerts.md`.
- Capturas próprias (URL pública do protótipo, Chromium headless shell 1243, pt-BR, 1440×900 DPR 1 e 390×844 DPR 3 com toque): scratchpad `a-d2/` (`d1440-top.png`, `m390-top.png`, `*-monitor.png`, `*-produto.png`, `*-sinais.png`, `*-benef.png`) e os prints convertidos para PNG.

## Rubrica

### Tokens do gate

`UI impact: affected` / `live_route: landing` / `surface: existing` em linhas próprias no topo de `design.md`. Regiões clonadas listadas em "Regiões clonadas (só estas)", com as regiões novas da d2 (hero, rotina, produto, benefícios, sinais, confiança, FAQ, cadastro, rodapé). OK.

### Cobertura do motivo do T6

| Ponto do T6 | Protótipo | design / specs / tasks |
|---|---|---|
| Prints novos do Monitor: Em posição / Saída-cobertura | `monitor.webp`: NVDA "EM POSIÇÃO", ETH/USDT "SAÍDA / COBERTURA" | D8, D13; spec "Clean and legible product prints"; task 2.10 |
| Tempo gráfico por estratégia | 1d e 4h no print; alt cita "gráfico diário" e "gráfico de 4 horas" | D8; spec exige "a timeframe on each item" |
| Sem alvo | print com distância até saída/stop, stop, entrada, preço; cartão "Em posição" fala de entrada, stop e distância | D13; spec "Signals use the Monitor vocabulary" (sem "alvo"); teste 2.7 |
| Alerta no Telegram por estratégia como benefício | benefício 02, chip "Alerta no Telegram", FAQ 6, OG | D13; spec "Telegram alert per strategy as a benefit" |
| Backtest como análise pronta | benefício 01, rotina 02, seção produto | D7/D13; spec "Landing explains requested product capabilities" |
| Cripto, ações e ETFs (hero, benefícios, prints, FAQ) | rótulo, abertura, risco do hero; benefício 02; NVDA no print e na análise; FAQ 6; chips NVDA/SPY/QQQ | D13; spec "Landing covers crypto, stocks and ETFs from Binance"; teste 2.7 |
| "Novo posicionamento" fora do Não entra só para essa ampliação | — | proposal Não entra com a exceção marcada; design Non-Goals igual |

Todos os pontos estão cobertos no texto. O problema está em parte do que o texto promete (P1-1).

### Produto descrito × app atual

- Estados "Em posição" e "Saída / cobertura" (#718): conferem com o app (`OpportunityCard.tsx`, "Compra / Stop", "distância até saída"; `marketState.ts`, "Ação · USD · Binance · NY · split"). O print é fiel ao cartão do app.
- Tempo gráfico por estratégia (#994/#1074): confere.
- Sem alvo (#803): confere.
- Alerta por estratégia ligado por padrão (#1122): confere **para estratégia própria com estrela**. Ver P1-1.
- Ação/ETF acompanhados e alertados, mas não operados: confere (`isSpotUsdtCandidate` exige cripto). Toda frase de compra e venda diz "cripto". OK.
- Combo, Descoberta e Otimização só para admin (`App.tsx:66-73`, `requireAdmin`); `/combo/results` é aberto: confere com "análise pronta".
- Mercado fechado só na tela (#1122): confere com FAQ 6.
- **Não confere:** (a) quem não é admin e não tem estratégia própria com estrela vê a vitrine do catálogo, e a vitrine nunca alerta, nem com a estrela da pessoa (`monitor-curated-fallback`, decisão 3 do #1122). O único caminho de UI para uma estratégia própria é "Salvar nos Favoritos" num resultado de otimização (`ComboResultsPage.tsx`, `isOptimization`), que é só do admin, e nada semeia favoritos para a conta nova. (b) O alerta sai uma vez por dia, às 08:05 BRT (`ops/systemd/criptofarol-*-telegram-alert-scan.timer`, `docs/monitor-telegram-alerts.md:166`).

### Prints

- Monitor (804×1070): legível nas duas larguras (1440: 418 px na coluna do hero; 390: largura total, ~0,97 da escala). Sem nome de conta, e-mail, descrição nem parâmetro da estratégia; preço BR. Fiel ao cartão do app.
- Análise (848×569): sem controles de desenvolvedor, rótulos sem parâmetro, eixo BR, logo do TradingView. A 1440 a imagem é esticada para 978 px (1,15×) e fica um pouco borrada (P3). O recorte a 390 está legível.
- Coerência entre os dois prints: falha (P2-1). NVDA aparece "Em posição" no 1d (entrada US$ 182,40, preço US$ 186,10) no Monitor. Na análise, NVDA 1d com último fechamento de US$ 206,64 e última marca "VENDA (11,16%)", ou seja, fora de posição e US$ 20 acima.
- OG: título com "cripto", descrição com ações e ETFs. Coberto pela Open Question 10.

### Aviso de risco

O aviso cobre as três classes no hero, no cadastro, no rodapé (nas três páginas) e no item 3 dos Termos ("o alerta não envia ordem"). OK.

### Não regressão d1/r1

- F0–F7 intactos no Migration Plan e nas tasks 6.1–6.8.
- Enter no passo 1: o script mantém o `submit` pelo caminho do passo 1; o foco vai ao título do passo 2 (`stepTwoTitle.focus()`); o cenário está no spec e nas tasks 2.7b e 5.2.
- Textos legais: abertura da Política "cobre só a página pública"; Termos "ao usar"; terceiros (Telegram, PostHog sem gravação de sessão, fontes locais) seguem corretos.
- Acessibilidade: nav "Entrar na lista" com 44 px a 390; link da Política em nova aba com aviso para leitor de tela; alts novos descritivos e coerentes com o que a imagem mostra nas duas larguras.
- Rodapé igual nas três páginas, só com a âncora e o `aria-current` próprios de cada página.

Nenhuma regressão.

### Acessibilidade d2

- O alt do Monitor é longo, mas descreve o que o print mostra.
- Os cartões de sinal quebram "Saída /" e "cobertura" em duas linhas sem estourar a 390.
- Os chips "NVDA · ação" são legíveis.
- O `role=alert` no erro continua P3 da d1.

## Achados

### P0

Nenhum.

### P1

- **P1-1 — O benefício do alerta no Telegram e o print do Monitor prometem ao beta o que a conta nova não tem.** Onde: benefício 02 ("Cada estratégia do seu Monitor avisa no Telegram… O alerta já vem ligado"), chip "Alerta no Telegram", FAQ 6 ("com a análise de cada estratégia e alerta no Telegram"), OG e descrição, rotina 01; print do hero com "Alerta: ligado"; `design.md` "Produto atual" (só tira da vitrine a conclusão do backtest, não a do alerta); spec "Telegram alert per strategy as a benefit".
  - Como é hoje: quem entra pelo beta é comum (não admin) e não tem estratégia própria com estrela. O Monitor dessa pessoa mostra a vitrine do catálogo, com a faixa "só exibição, sem alerta no Telegram" e sem o controle de Alerta. A estrela que ela dá numa linha do catálogo também não alerta (#1122, decisão 3). Ela não consegue criar estratégia própria pela UI: Combo e Otimização são só do admin, e nada semeia favoritos na conta nova.
  - Correção proposta: (a) registrar o fato em "Produto atual" e em Risks; (b) abrir a Open Question 12 para o Alan, bloqueante para o T7. Opções: "o Alan dá estratégias próprias com estrela a cada pessoa da leva (procedimento manual, documentado)", "card de produto à parte para a vitrine alertar ou para a pessoa adotar uma estratégia do catálogo" (fora deste card), ou "a landing condiciona o benefício" (por exemplo, "nas estratégias que você acompanha no Monitor" mais uma frase honesta de como elas chegam lá); (c) conforme a resposta, ajustar o benefício 02, o FAQ 6 e o spec. O Alan pediu o benefício no T6. O que precisa de resposta é como ele chega a quem entra.

### P2

- **P2-1 — Os dois prints da NVDA se contradizem.** Onde: `assets/monitor.webp` (NVDA 1d em posição, entrada US$ 182,40, preço US$ 186,10) × `assets/grafico-analise.webp` (NVDA 1d, último fechamento US$ 206,64, última marca VENDA em set., fora de posição). Correção: ativo diferente em um dos prints (por exemplo, a análise de SPY ou de BTC/USDT, ou o Monitor com outra ação), ou uma amostra coerente entre os dois. A regra vai para a recaptura da task 2.10: o mesmo ativo e tempo gráfico nos dois prints precisam contar a mesma história.
- **P2-2 — A frequência do alerta não aparece e a copy sugere aviso na hora.** Onde: benefício 02 ("avisa no Telegram quando entra e quando sai"), FAQ 6; o print mostra estratégias de 4h (e o app tem 1h e 15m). O alerta sai uma vez por dia, às 08:05 BRT. Correção: dizer a frequência ("um aviso por dia, de manhã, com o que entrou e o que saiu") ou registrar como juízo do Alan se a copy fica vaga. Nunca sugerir aviso em tempo real.
- **P2-3 — "Já vem ligado" omite o vínculo do Telegram.** Onde: benefício 02. O aviso só chega com o Telegram ligado no Perfil. Correção: "depois que você conecta o Telegram no Perfil, o alerta já vem ligado…".

### P3 (detalhe de Apply)

- A 1440 a análise aparece a 978 px, a partir de 848 px naturais (1,15×, levemente borrada): gerar a versão desktop com ≥ 1000 px na recaptura (task 2.10) ou limitar a largura da figura.
- Tensão de copy herdada da v4: confiança 1 ("sem depender de opinião… de grupo de Telegram") × benefício do Telegram; confiança 2 ("não precisa interpretar gráfico, médias móveis") × análise com "Média curta/longa". Ajuste fino no Apply, sem mudar a política Q3=A.
- "O Monitor está lá no topo." soa interno: no celular o Monitor vem depois dos CTAs. Ajuste fino sem mudar o contrato ("o Monitor que você viu acima").
- "split" na linha de configuração do print é jargão do app. Fica, porque é fiel ao app; se incomodar, a recaptura pode cortar a linha.
- A task 2.10 descreve a recaptura "da conta do Alan no DEV". A conta do Alan é admin e o Monitor dela abre em "Em portfólio": a recaptura deve usar o filtro "Todos" e só estratégias próprias, para não mostrar o que o beta não vê (depende da P1-1).

## Open Questions (1–11): o que bloqueia o T7

- **Bloqueiam o T7** (o texto aprovado depende da resposta, sem padrão possível): **1** (controlador e canal do titular: o texto tem lacunas ⟨…⟩) e a nova **12** (P1-1: como o alerta chega a quem entra pelo beta).
- **Vão como pergunta no T7, com a recomendação como padrão** (aprovar = aceitar a recomendação): 3, 4, 5, 6, 7, 8, 9, 10, 11.
- **Vai como pergunta, mas precisa de resposta antes de F0/F4** (não do T7): **2** (leads antigos, cópia no Drive da Clara, tópico do grupo; apagar não tem volta).
- Nota sobre a 8: a memória do operador diz que a senha do DEV fica no bws cadastrada pelo Alan. O design diz que não está lá. Fica como pergunta; os prints dos clones são aceitáveis.

## Juízos do Alan

- Open Question 12 (nova, P1-1): como a pessoa que entra pelo beta passa a ter estratégias próprias com alerta, ou como a landing fala do alerta até isso existir.
- Frequência do alerta na copy (P2-2): dizer "uma vez por dia" ou deixar sem frequência.
- Open Questions 1 (bloqueante), 2 (antes do corte) e 3–11 (padrão = recomendação).

## Disposition

A d2 cobre todos os pontos do T6 no protótipo, no design, nos specs e nas tasks. Os prints do Monitor e da análise são fiéis ao app atual, legíveis a 1440 e a 390, sem dado pessoal nem parâmetro. O aviso de risco cobre as três classes, e nada da d1/r1 regrediu. Falta registrar e decidir um fato de produto: a conta nova do beta só vê a vitrine, que não alerta, e não tem como criar estratégia própria. Do jeito que está, o benefício do Telegram e o print "Alerta: ligado" prometem o que essa pessoa não recebe. Há ainda dois ajustes de honestidade (frequência diária e vínculo do Telegram) e um de coerência entre os prints da NVDA.

## Verdict

**PASS com rework** (P1-1 vira Open Question 12 bloqueante para o T7, com "Produto atual", Risks e spec ajustados; P2-1 a P2-3 no mesmo rework).
