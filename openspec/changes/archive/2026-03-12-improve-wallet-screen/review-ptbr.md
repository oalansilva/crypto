# Revisão (PT-BR) — improve-wallet-screen

## Objetivo
Melhorar a tela **Carteira** (`/external/balances`) pra ficar:
- mais rápida de entender (resumo + formatação)
- usável no celular (sem tabela gigante com scroll horizontal)
- com filtros/pesquisa (achar ativo rápido)

## O que vai ter

### UI (frontend)
- Resumo no topo (Total USD + info de atualização)
- Campo de busca por ativo (ex: BTC, ETH)
- Filtros:
  - "Só locked"
  - controle de "dust" (limite mínimo em USD — padrão continua $0.02)
- Ordenação (por valor, PnL, ativo)
- Layout responsivo (desktop tabela / mobile cards)

### API (backend)
- Resposta passa a incluir `as_of` (timestamp do snapshot)
- Query param `min_usd` pra ajustar o filtro de dust (padrão $0.02)

## Critérios de aceite
- Consigo achar um ativo usando busca em poucos segundos.
- No mobile a tela fica legível sem scroll horizontal.
- Fica claro quando o PnL não está disponível (avg cost não calculado pra todos).
- Default continua seguro: read-only + dust escondido.

## Como revisar
1. Abrir `/external/balances`
2. Conferir topo: Total USD + horário (`as_of` / last updated)
3. Testar busca (ex: digitar "BTC")
4. Testar filtro "Só locked"
5. Alternar presets do dust (0 / 0.02 / 1 / 10) e ver a lista mudar
6. Em celular (ou devtools mobile), ver se virou lista de cards

## Status QA — 2026-03-12
- **Resultado:** falhou na revalidação de fidelidade visual.
- **Protótipo publicado:** agora abre corretamente em `/prototypes/improve-wallet-screen/` (blocker anterior encerrado).
- **Diferenças principais encontradas em `/external/balances`:**
  - shell/header ainda é do app **Crypto Backtester**, não a composição aprovada **Crypto Lab** do protótipo;
  - cards, labels, espaçamentos e hierarquia visual divergem materialmente em desktop e mobile;
  - conteúdo renderizado também não bate com a referência capturada (implementação mostrou ~US$174.80 / 4 ativos vs protótipo ~US$31,231.06 / 8 ativos).
- **Evidências:** `qa_artifacts/playwright/improve-wallet-screen/revalidation-2026-03-12/{proto-desktop,impl-desktop,proto-mobile,impl-mobile}.png`

## Status DEV — 2026-03-12 (rodadas pós-falha visual)
- Shell da rota `/external/balances` foi alinhado para um header dedicado no estilo **Crypto Lab**, removendo da carteira a nav/header global **Crypto Backtester** que aparecia na evidência anterior.
- A hierarquia visual da página foi reaproximada do protótipo aprovado: KPI total no cabeçalho, cards-resumo, controles/meta line, callout de PnL e painel `Balances` ajustados em desktop e mobile.
- Follow-up DEV desta rodada: o painel `Balances` foi refinado com proporções mais próximas do protótipo aprovado — no desktop a tabela voltou para uma coluna de ativo mais estreita e espaçamento/row density menos comprimidos; no mobile os cards foram relaxados (ícone, paddings, gaps e mini-cards) para reduzir a sensação de layout apertado.
- Evidências DEV locais atualizadas: `frontend/qa_artifacts/playwright/improve-wallet-screen/dev-check-desktop.png`, `frontend/qa_artifacts/playwright/improve-wallet-screen/dev-check-mobile.png`, `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-desktop.png` e `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-mobile.png`.

## Próximo gate
Gate atual: **QA reexecutar a validação visual de `/external/balances` vs protótipo aprovado**. A homologação final do Alan só acontece depois do QA visual passar.
