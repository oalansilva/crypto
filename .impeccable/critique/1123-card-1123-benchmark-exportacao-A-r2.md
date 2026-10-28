`proveniência: Assessment A r2 (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/cf-assess-a-1123-r2.json` (attempt `9f92d08b-ee2e-4334-a9aa-ced51d073166`, band `juizo`, role `assessment-a`, capture_sha256 `1fdaeeecfccd1c31e4efdfba1e89dd0bef5e89594407011af1395bff42927a80`, arquivo sha256 `273e749c7e9b2f1ff6905a8d417aa6856e1f6275c9329372190dd0dd0dba73bf`). Wave capture: o mesmo arquivo. Birth: `.cursor/tmp/claude-evidence/9f92d08b-ee2e-4334-a9aa-ced51d073166.birth.json`.

# Assessment A r2: card 1123, change card-1123-benchmark-exportacao

> Avaliador A isolado, segunda onda (T4 `recriticar` depois do T6 de Alan). O foco é o delta do r3: coluna extra no Decidir. Não li o snapshot nem os arquivos do Assessment B nem o transcript do pai. Não spawnei filho, não chamei `process_event`, não movi Status e não comentei no issue. Não editei `design.md`, OpenSpec, protótipo nem código. Única escrita no repo: este arquivo.

## Metadata

- card: 1123 · change `card-1123-benchmark-exportacao` · Status = Design (dado no prompt)
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1123-benchmark-exportacao` · branch `card-1123-benchmark-exportacao` @ `9b83d25e` (change e protótipo não commitados)
- data: 2026-10-28 · cliente: Claude Code (cooperativo, sem modo Auto)
- Briefing: body do issue + decisão de Alan de 28/10 ([comentário 6462139347](https://github.com/oalansilva/crypto/issues/1123#issuecomment-6462139347)): coluna extra no Decidir, sem mudar a ordem nem a elegibilidade. As decisões de 27/10 e 28/10 e os 30 dias não foram reabertos.
- sha256 do change:
  - `design.md` `2f606e3a21e513813c19591b45db6f975086db45859c1801a1171c23ffadb1fe`
  - `proposal.md` `cf456e4b…96ae` · `tasks.md` `f07ac739…2604`
  - specs: `benchmark-reference-choice` `00e00597…2006`, `discovery-leaderboard` `b317a343…5f06`, `result-context-export` `2f875659…a616`
- Ignore list: `.impeccable/critique/ignore.md` não existe.
- Ferramentas: Playwright Python, Chromium headless shell 1243, `pt-BR`, tema escuro, fuso São Paulo, **na URL pública**, contexto novo por largura: 1440×900 e 390×844 (`isMobile`, `hasTouch`). O contraste foi medido pela cor computada contra o fundo efetivo, sem axe-core. Scripts (`a2.py`, `a2b.py`), saída (`a2.out`, `a2.json`) e 27 PNGs estão em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123A2/`.

## Digest e não regressão

- Os 7 arquivos têm o mesmo sha256 no disco e servidos, e batem com a tabela de `## Prototype Validation` do `design.md`: `index.html` `7a1dd22a…132f`, `favorite.html` `9ec8f65d…66ec`, `favorites.html` `84340678…7b33`, `discovery.html` `6c2af663…e740`, `live.css` `353ac045…32f6`, `delta.css` `ad738de2…0c3a` e `delta.js` `8578c21f…171c`.
- `index.html`, `favorite.html`, `favorites.html` e `live.css` são byte a byte iguais aos do r2 (comparei com a saída do r2, `c1123r2/out`). O `delta.js` mudou, porque o diálogo virou uma função usada pelas três páginas. Por isso conferi o comportamento nas duas larguras:
  - resultado e favorito: o diálogo abre com o foco na busca, o título é "Escolher referência", "Próprio ativo" aparece como Padrão e o Esc devolve o foco a "Trocar referência";
  - SPY no resultado: período comum 02 jan. 2019 – 31 dez. 2024, 0 trades de fora, "Retorno de preço, sem dividendos" e o aviso de USDT;
  - BTC/USDT no favorito NVDA: "2 trades fora", com o aviso de moeda;
  - Favoritos: "Ref.: SPY…" e "Ref.: BTC/USDT…" na linha e no cartão.
- O r2 não regrediu. Nos fluxos clicados não houve `console.error`, `pageerror`, resposta ≥ 400 nem rolagem horizontal (1440 = 1440; 390 = 390).

## Tokens parseáveis (rubrica, D4)

As linhas 1 a 3 do `design.md`, cada uma em linha própria: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`. **OK.** Manter `live_route` em `/combo/results` é coerente: o Decidir reaproveita o seletor, o contrato e o cálculo do resultado (decisão 1, parágrafo do r3), e as regiões clonadas estão declaradas na linha 7.

## O que verifiquei no delta do Decidir (medido)

| Item | 1440×900 | 390×844 (toque) |
|---|---|---|
| Padrão: "Coluna extra: Nenhuma", sem `<th>` nem célula visível | OK | OK |
| "Comparar com outra referência" / "Exportar planilha" | 44 px / 44 px | 44 px / 44 px |
| Diálogo: foco na busca; Tab e Shift+Tab presos; Esc devolve o foco ao gatilho | OK | OK (tela cheia, 390×844) |
| Filtros de classe | 36 px | 44 px |
| Primeira opção "Próprio ativo · Padrão · Sem coluna extra" | OK | OK |
| WAVES/USDT: `disabled`, `aria-describedby` → "Saiu da lista spot… Não pode ser escolhido como referência." | OK | OK |
| Aviso antes da escolha: CRCL "Sem período comum com nenhum candidato desta varredura"; SPY, QQQ e BTC "1 candidato com período comum curto (PENGU/USDT)" | OK | OK |
| SPY "Calculando…": `0 de 5`, nenhuma célula com dígito | OK | OK |
| "Contra SPY" nos 5; ordem e rank (1 BTC, 2 NVDA, 3 SOL, 4 SPY, — PENGU) iguais aos de antes | OK | OK |
| "Ordenar por" segue Calmar e "CAGR vs B&H"; trocar para Calmar não mexe na coluna | OK | OK |
| BTC +66.8 p.p. · SPY +15.25% a.a. · 02/01/2019 – 31/12/2024 · "USDT tratado como USD" (texto e ícone); NVDA e SPY sem aviso | OK | OK |
| PENGU: "Sem comparação · Período comum de 14 dias: o mínimo é 30.", sem número | OK | OK |
| Faixa: ativo, ETF, USD, "Retorno de preço, sem dividendos", "não muda a ordem…", "4 de 5…; 1 sem comparação (período comum curto)", aviso de moeda, linha de gravação | OK | OK |
| Recarregar: coluna gravada, sem cálculo | OK | OK |
| QQQ: "Coletando histórico de QQQ na Binance…", sem número, depois a coluna | OK | OK |
| BTC/USDT como referência: o aviso de moeda passa para NVDA e SPY | OK | OK |
| CRCL: "Sem comparação · Sem período comum com CRCL." nos 5, mais o resumo com as datas | OK | OK |
| Falha: alerta "Nada foi gravado: a coluna continua contra CRCL."; "Tentar de novo" com 44 px grava QQQ | OK | OK |
| "Próprio ativo": a coluna some, a planilha volta a 24 colunas (Rank, Candidato e os 22 campos), a ordem fica igual e recarregar mantém sem coluna | OK | OK |
| Planilha com SPY: 37 colunas = Rank + Candidato + 22 + as 13 " (extra)", na ordem do spec; o status do download cita "colunas (extra) contra SPY"; a Legenda tem "(extra)" | OK | OK |
| Celular: a célula ocupa a largura do cartão (326 px), com `::before` "Contra SPY" à esquerda | n/a | OK |
| Contraste: textos novos da faixa e do diálogo entre 5,56 e 19,35:1. Abaixo de 4,5: "Contra SPY" e a dica do `<th>`, 11/10 px, 4,01:1 (mesma cor e tamanho dos `<th>` do incumbente); "−3.2 p.p.", 14 px/600, 4,48:1 | ver P3 | ver P3 |
| Foco visível: contorno azul de 2 px no gatilho, na busca e no rótulo do rádio | OK | OK |

## Limitação registrada pelo autor: amostra do candidato vencida

O que está registrado: numa varredura com mais de 30 dias e sem nada que a fixe, cada candidato fica "Sem comparação · Amostra do candidato vencida em <data>.". O `design.md` (decisão 10 e Risks) e o spec descrevem esse estado.

A tela **não** deixa isso claro hoje:

- **Não há demonstração.** Nenhum candidato do protótipo está nesse estado, e o `delta.js` não tem o caso.
- **O resumo da faixa não conta vencidas.** Ele só conta `short_overlap` e `no_overlap`. Numa varredura antiga, sairia "0 de 5 candidatos com comparação." sem o motivo.
- **O seletor não avisa antes.** O aviso contado cobre período curto e falta de período comum, mas não amostra vencida. Alan escolheria SPY, esperaria o job inteiro e receberia uma coluna inteira de "Sem comparação".
- **A linha do candidato se contradiz.** Ela diz "amostra até 26 nov. 2026" (região COPIED). Com a coluna ativa, o design fixa essas amostras, mas a linha continua mostrando a data de vencimento. Também não aparece em lugar nenhum que escolher uma referência guarda as amostras. Esse é o único jeito de Alan evitar o problema antes do dia 30.

Como produto: Alan disse que usa mais a Descoberta. A limitação é coerente com o resto do produto, porque a promoção também depende da amostra congelada e já vence em 30 dias. Ela também respeita "sem recálculo escondido". Por isso é aceitável **se a tela disser isso**. Classifico a falta de clareza como **P2 (contrato visível incompleto)**. Aceitar a limitação ou trocá-la por outro comportamento é **decisão aberta de Alan** (ver abaixo). Não decido por ele.

## Heurísticas Nielsen (0–4), só para o delta do Decidir

| # | Heurística | Nota | Ponto-chave |
|---|---|---|---|
| 1 | Visibilidade do status | 3 | "k de 5", "Coletando…" e a linha de gravação estão bons; amostra vencida e exportação durante o cálculo não aparecem |
| 2 | Linguagem do mundo real | 3 | "p.p.", "a.a." e os motivos em português claro; formato numérico diferente do resto da linha |
| 3 | Controle e liberdade | 3 | "Próprio ativo" tira a coluna, reativar não recalcula, há Cancelar e Esc |
| 4 | Consistência | 3 | Mesmo diálogo do resultado; decimal com ponto e data dd/mm numa tabela em pt-BR |
| 5 | Prevenção de erro | 3 | Avisos contados antes da escolha; falta o de amostra vencida |
| 6 | Reconhecer em vez de lembrar | 2 | O Δ que ordena está escondido em "+ detalhes", e o único Δ visível é "Contra SPY", fora de ordem |
| 7 | Flexibilidade e eficiência | 3 | Uma escolha por varredura, gravada; planilha com "(extra)" |
| 8 | Estética e minimalismo | 3 | A faixa tem cinco blocos de texto mais a mensagem viva; no celular passa de uma tela |
| 9 | Recuperação de erro | 4 | "Nada foi gravado", coluna anterior mantida, "Tentar de novo" com 44 px |
| 10 | Ajuda e documentação | 3 | Legenda "(extra)", frase da referência do ranking; nada sobre vencimento |
| **Total** | | **30/40** | Bom, com ajustes |

## Especificidade, carga cognitiva e jornada

- **Especificidade:** a faixa, o `<th>` com a dica e a célula de três linhas usam a moldura, os tons de alta e queda, os chips de classe e o `td[data-label]` do Decidir vivo. É desenho do produto, não um componente genérico.
- **Carga cognitiva:** o diálogo tem 7 opções visíveis com 4 filtros; isso passa de 4 opções, mas a busca e os filtros compensam. A faixa tem frase do ranking, título, frase da coluna, resumo, aviso de moeda, linha de gravação e status. É denso, porém cada linha responde a uma pergunta real.
- **Jornada:** o pico é ver "Contra SPY" chegar sem a ordem se mexer, com a frase "A ordem do ranking não mudou.". O vale é ver uma coluna de "Sem comparação" (CRCL, ou uma varredura vencida) sem ter sido avisado; no CRCL o aviso existe, na varredura vencida não.

## What's working

- **A ordem fica intocada e isso aparece.** A frase do ranking, a faixa, o `aria-label` do `<th>` ("não muda a ordem"), a mensagem viva e a Legenda repetem a regra, e os testes mostram rank 1–4 e "—" iguais antes, durante, depois, ao recarregar e ao voltar ao Próprio ativo.
- **Os estados não mostram números falsos.** "Calculando…" não deixa dígito nenhum no DOM; insuficiente e sem período comum aparecem como "Sem comparação" com o motivo, nunca 0. A falha não grava e mantém a coluna anterior.
- **Reaproveitamento real.** É o mesmo diálogo, com título e primeira opção próprios, o mesmo WAVES/USDT desabilitado e os mesmos 44 px. A planilha usa os mesmos 22 campos mais 13 " (extra)", com nomes previsíveis.

## Findings

### P0
- nenhum.

### P1
- nenhum.

### P2 (produto e contrato visível, baratos)

1. **[P2 · produto/contrato] Amostra do candidato vencida não aparece na tela** (`discovery.html`, `delta.js` render/resumo; decisão 10). Correção:
   - na faixa padrão, uma frase: "Escolher uma referência guarda as amostras desta varredura enquanto a coluna existir.";
   - com a coluna ativa, a linha do candidato troca "amostra até …" por "amostra guardada pela coluna extra";
   - no seletor, um aviso contado: "N candidatos com amostra vencida: ficam sem comparação". Se forem todos, em tom de alerta: "As amostras desta varredura venceram em <data>. Rode a varredura de novo para comparar.";
   - o resumo da faixa conta "(amostra vencida)";
   - uma demonstração "Ver varredura com amostras vencidas".
   A decisão de produto fica com Alan (abaixo).
2. **[P2 · produto/UX] "Contra SPY" pode ser lido como a chave do ranking** (`discovery.html`, `<th>` e célula). Com "Ordenar por = CAGR vs B&H", o Δ do próprio ativo só aparece em "+ detalhes". O único Δ visível na tabela é "Contra SPY", com valores fora de ordem (+66.8, +49.8, +81.2, −3.2). O `aria-label` diz "não muda a ordem", mas o texto visível não diz. Correção:
   - na dica do cabeçalho: "Δ CAGR · período comum · não ordena";
   - opcional: na célula, uma linha discreta com o Δ gravado do próprio ativo ("vs próprio ativo +11.4 p.p."), sem recálculo, para os dois ficarem lado a lado.
3. **[P2 · contrato] Promover com a coluna extra ativa não tem regra.** Não está definido se o favorito promovido herda SPY. Na rodada nova, "Ao salvar nos Favoritos, a referência vai junto". O spec só cobre a troca depois de promover e o lote (regra 5). Correção: definir no `design.md`, no spec e nas tasks. A recomendação é herdar a comparação gravada da célula (mesmas amostras, com o ponteiro do favorito) e dizer isso na promoção ("Referência SPY vai junto"). A alternativa é escrever "o favorito nasce com o próprio ativo". É escolha de Design, não precisa de Alan.
4. **[P2 · contrato visível/consistência] Formato da célula diferente do da linha.** A linha COPIED do Decidir está em pt-BR: "+3.531,4%", "0,90", "1 jan. 2019 – 31 dez. 2024". A célula nova usa "+66.8 p.p.", "SPY +15.25% a.a." e "02/01/2019 – 31/12/2024". Correção: seguir o formato da tela do Decidir ("+66,8 p.p.", "+15,25% a.a.", "2 jan. 2019 – 31 dez. 2024") e ajustar o cenário "SPY column on a multiclass sweep" do spec. O resultado (`/combo/results`) já usa ponto no vivo e fica como está.

### P3 (detalhe de Apply; aceito, não reabrir)

- **[P3 · a11y]** `<th>` "Contra SPY" e a dica com 4,01:1 em 11 e 10 px: mesma cor e tamanho dos `<th>` do incumbente (`rgb(112,122,138)`). Herdado.
- **[P3 · a11y]** "−3.2 p.p." com 4,48:1 em 14 px/600 (`rgb(246,70,93)`). No Apply, usar o token de queda do componente vivo.
- **[P3 · a11y]** Alerta de falha (`role=alert`) dentro da região `role=status` da faixa: o mesmo P3 aceito no r2, agora repetido no Decidir.
- **[P3 · detalhe de Apply]** O resumo "4 de 5 candidatos" conta a varredura inteira, e com filtro de classe a tabela mostra menos linhas. Escrever "desta varredura".
- **[P3 · detalhe de Apply]** Exportar com a coluna em cálculo (planilha sem as "(extra)" e o status dizendo isso), falha no cálculo (não na coleta) e "Sem amostra" (`insufficient_sample`) estão no design, mas não no protótipo.
- **[P3 · detalhe de Apply]** Na mesma linha da planilha, o retorno da estratégia de BTC aparece como +3531.39% (22 campos, derivado do CAGR gravado) e +3532.61% (extra, dos trades regenerados), e o CAGR como +82.00% e +82.06%. Falta uma linha na Legenda "(extra)" explicando a origem.
- **[P3 · dados do protótipo]** SPY dá +134.20% no Decidir e +134.26% no resultado para o mesmo período comum 02/01/2019 – 31/12/2024. Alinhar no mock (a task 4A.6 já exige igualdade no produto).
- **[P3 · incumbente, fora do escopo]** `Leaderboard · CAGR vs Buy &amp; Hold` aparece assim na tela (região COPIED, defeito do vivo). Pede card próprio.
- **[P3 · incumbente]** A 1440, "Promover"/"Excluir" seguem cortados no Decidir: o contêiner tem `overflow-x: auto`, 1240 px contra 1175. Com a coluna extra, a tabela continua com 1240 px e as colunas apertam. Já era P3 aceito no r2.

## Persona red flags

- **Alan (pesquisador, usa mais a Descoberta):**
  - abre uma varredura de mais de um mês, escolhe SPY, espera o job e recebe 5 × "Sem comparação" sem ter sido avisado (P2-1);
  - lê "Contra SPY" como se fosse a ordem do ranking (P2-2);
  - promove o BTC achando que o SPY vai junto (P2-3).
- **Leitor de tela:** fluxo bom (foco preso, `aria-describedby`, "Período comum" em `sr-only`, mensagens `polite`). O alerta dentro do status pode ser anunciado duas vezes (P3).
- **Celular a uma mão:** os alvos têm 44 px, o diálogo ocupa a tela e a célula vira linha do cartão. A faixa com SPY passa de uma tela de 844 px antes da tabela.

## Questions to consider

- Se a amostra vence em 30 dias, por que não fixar automaticamente as amostras da varredura mais recente de cada tipo, que é a que Alan mais usa?
- A célula deveria mostrar os dois Δ (próprio ativo e SPY) lado a lado, já que comparar os dois é o motivo da coluna?
- "Contra SPY" no lugar de "vs SPY": o rótulo curto pesa menos na tabela, mas deixa claro que é Δ?

## Decisões para Alan

- **Mínimo de 30 dias** (já aberta, não reaberta aqui).
- **Amostra vencida na coluna extra.** Opções:
  - aceitar "Sem comparação · Amostra do candidato vencida", com o aviso prévio e o caminho "rode a varredura de novo" (o Design recomenda isto, com o P2-1 aplicado);
  - permitir um cálculo **explícito** com dado novo, rotulado como amostra nova e data nova (não é recálculo escondido, mas muda números já vistos na varredura);
  - fixar as amostras de toda varredura concluída por mais tempo, com custo de armazenamento.

## Disposition

O delta do r3 cumpre a decisão de Alan de 28/10: há coluna extra em todos os candidatos, a ordem, o rank, "Ordenar por" e a elegibilidade não mudam, o seletor é reaproveitado e os estados aparecem sem número falso, com planilha e Legenda "(extra)" gravadas e lidas sem recálculo. As páginas do r2 não regrediram. Os tokens estão OK. Não há P0 nem P1. Os quatro P2 são de clareza e contrato e são baratos: amostra vencida, "não ordena", herança na promoção e formato pt-BR. Verdict: **PASS com rework**.
