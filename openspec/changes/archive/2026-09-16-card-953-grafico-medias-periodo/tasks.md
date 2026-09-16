# Tasks — card-953-grafico-medias-periodo

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Linhas no recorte das velas carregadas

- [x] 1.1 — Em `/combo/results`, calcular as linhas da estratégia (SMA/EMA de preço **e** as outras que o gráfico já desenha) sobre as velas já carregadas; não só no extremo recente.
- [x] 1.2 — No gráfico do Monitor, o mesmo recorte velas↔linhas; não esconder as linhas.
- [x] 1.3 — Painel de baixo da estratégia (quando o manifesto o declara) cobre o mesmo histórico. Não inventar linha.

## 2. 6 meses / 2 anos e zoom

- [x] 2.1 — Favorito 6 meses / 2 anos **não** alarga para todo o mercado só para completar linhas.
- [x] 2.2 — Zoom inicial ~180 permanece; recorte visível ao abrir já tem linha após aquecimento.
- [x] 2.3 — Menos / afastar / arrastar: velas antigas da série carregada também têm linha. Resetar volta ao recorte recente sem apagar as linhas da série.

## 3. Clip, 1:1 e período do favorito

- [x] 3.1 — Linha **não** avança à frente da última vela (#921). Aquecimento (N−1) não conta como furo.
- [x] 3.2 — 1:1 lista↔setas do #917 continua a passar.
- [x] 3.3 — Período operacional do favorito (#949) não muda.
- [x] 3.4 — Vale noutro ativo / intervalo dessas telas.

## 4. Contrato e evidência

- [x] 4.1 — UI alinhada ao proto `frontend/public/prototypes/card-953-grafico-medias-periodo/` (`index.html` análise + `monitor.html`).
- [x] 4.2 — Playwright desktop+mobile: 2 anos ≠ todo o mercado; zoom 180 com linha; Menos com linhas nas velas antigas; clip #921; Monitor com painel de baixo no mesmo recorte.
- [x] 4.3 — `openspec verify` desta change.
