## 1. Frontend — tabela de saldos

- [x] 1.1 Aplicar zebra striping nas linhas da tabela desktop em `ExternalBalancesPage.tsx` usando `even:` com opacidade sutil, preservando `hover`, cores semânticas e barra de participação
- [x] 1.2 Confirmar que os cards mobile não recebem zebra e permanecem inalterados

## 2. Frontend — remoção de textos

- [x] 2.1 Remover o subtítulo "Saldos lidos da Binance Spot por chave API read-only. O Cripto Farol não solicita e-mail nem senha da Binance." do header
- [x] 2.2 Remover a nota "Layout responsivo: tabela no desktop e cards no mobile." sob o título Balances
- [x] 2.3 Remover o chip "Binance · read-only" do header da página (decisão de Alan registrada no card e no design.md)

## 3. Validação visual e QA

- [x] 3.1 Atualizar baseline do Playwright visual da tela Carteira e revisar o `diff.png` (subagent vision) — veredito EXPECTED (zebra visível, chip/textos ausentes, PnL/participação preservados, mobile inalterado)
- [x] 3.2 Validar aderência ao `DESIGN.md` (contraste, hover, densidade) em desktop e mobile — zebra `rgba(255,255,255,0.03)` sobre `#101c2a`, hover `0.05` distinto em ambas as paridades; teste funcional de computed styles na página real
- [ ] 3.3 Integrar em `develop`, rodar `./restart` e validar a URL DEV servindo o resultado novo
