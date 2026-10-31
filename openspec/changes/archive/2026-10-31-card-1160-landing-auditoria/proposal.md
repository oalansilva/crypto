## Why

A landing pública (https://criptofarol.com.br/, v4) perde leads e confiança em pontos que um webmaster pegaria de cara: o lead só é salvo no fim do passo 2, a tela de sucesso promete um e-mail que não sai, não há Política de Privacidade, Termos nem aviso de risco visível, e a página falha em SEO técnico, performance e cabeçalhos de segurança. O tráfego do beta fechado chega por link no WhatsApp e pela busca; cada visita perdida no formulário é um lead que não volta. Origem: issue oalansilva/crypto#1160 (grelhado; Alan priorizou com `/priorizar 1160` em 29/10/2026).

O texto abaixo (Problema, História, Entra, Não entra) é cópia do body do issue #1160, com duas adições do Alan durante o Design, marcadas como tal: o item 12 de Entra (29/10/2026) e a devolução do Design pelo T6 de 29/10/2026 ([recibo](https://github.com/oalansilva/crypto/issues/1160#issuecomment-6505701552)), que acrescenta o bloco "Produto desatualizado" em Problema, o item 13 de Entra e a ressalva do "novo posicionamento" em Não entra. Motivo literal do Alan no T6: "Atualizar a landing ao produto atual: prints novos do Monitor (Em posição / Saída-cobertura, tempo gráfico por estratégia, sem alvo); alerta no Telegram por estratégia como benefício; backtest como análise pronta das estratégias acompanhadas (não 'teste qualquer estratégia'); a página passa a cobrir cripto, ações e ETFs da Binance (hero, benefícios, prints e FAQ). Sai do Não entra o 'novo posicionamento' só para essa ampliação."

### Problema (do issue #1160)

A landing pública (https://criptofarol.com.br/, v4) tem visual sólido, mas perde leads e confiança em pontos que um webmaster pegaria de cara. Avaliação feita em 2026-10-29 na página publicada (desktop 1440px e celular 390px, Playwright):

**Conversão**
- O formulário tem 2 passos, mas o lead só é salvo no passo 2, e lá o campo "Sua maior dificuldade" é obrigatório. Quem preenche nome e e-mail e desiste no passo 2 se perde. O botão do passo 1 diz "Garantir minha vaga", mas não garante nada.
- Quando o formulário é enviado, só o e-mail fica guardado (com marcas de sim/não sobre o resto). Nome, WhatsApp, nível e dificuldade são descartados, o Alan não é avisado e a tela diz "Verifique seu e-mail para o acesso inicial", mas nenhum e-mail sai.
- O PostHog não registra a conclusão do passo 1 nem os cliques nos CTAs, então não dá para medir onde o funil quebra.
- O contador mostra "Já são 5 cadastrados. Restam 45 vagas". O número conta contas do app, não quem se inscreveu na landing. Com número baixo, isso enfraquece a prova social. Se a API falha, aparece "--".
- Não há prova social (depoimento, número de backtests, quem está por trás).

**Confiança e LGPD**
- Não há rodapé: faltam política de privacidade, termos de uso e aviso de risco. O formulário coleta nome, e-mail e WhatsApp sem link de privacidade nem aviso de uso dos dados. O PostHog grava no localStorage sem aviso.
- O aviso de risco aparece só no fim da página, ao lado do formulário. O hero promete "O Cripto Farol responde", e a página fala em "Sinal de Compra / Venda". O aviso de que não é recomendação financeira precisa estar visível desde o hero.

**Clareza da copy**
- O FAQ diz "quem nunca comprou cripto entende na primeira tela", mas o card de métricas mostra Sharpe, SQN, PF, Max DD e ATR sem explicação visível (só no `title`, que não aparece no celular).
- Os textos de Spot usam nomes internos ("Operar", "Home", "Spot Trade") e frases longas, como no benefício 04 e em "Seu dinheiro nunca sai do lugar".
- A lista de ativos ainda mostra MATIC, que a rede renomeou para POL.
- A mesma imagem da tabela aparece duas vezes (no hero e no produto 01).
- O print do gráfico mostra controles de desenvolvedor ("Mouse wheel: zoom", "307 candles", "Zoom Out/In/Reset"), mistura inglês ("LAST PRICE") e usa preço no formato americano ($80,819.25).
- No celular, os dois prints do produto ficam ilegíveis (texto de ~4px).

**SEO e compartilhamento**
- `/robots.txt` e `/sitemap.xml` devolvem o HTML da SPA (200 text/html), e `/favicon.ico` dá 404.
- Faltam Open Graph e Twitter Card: o link compartilhado no WhatsApp ou no X sai sem imagem nem título bom. Faltam também `canonical`, dados estruturados (Organization/SoftwareApplication/FAQPage) e `apple-touch-icon`.
- `www.criptofarol.com.br` responde 200 em vez de redirecionar para o domínio sem www (conteúdo duplicado).
- A meta description está sem acentos ("historico", "comparacao"). O título "Cripto Farol | Beta" não diz o que o produto faz.

**Produto desatualizado (devolução do Alan no T6, 29/10/2026, [recibo](https://github.com/oalansilva/crypto/issues/1160#issuecomment-6505701552))**
- Os prints e a seção dos sinais mostram o Monitor antigo ("Compra"/"Venda" e ponto de saída sugerido). Hoje o Monitor mostra "Em posição" e "Saída / cobertura" (#718), o tempo gráfico de cada estratégia (#994, #1074), o risco até o stop sem alvo (#792, #803) e o controle "Alerta" por estratégia (#1122).
- O alerta no Telegram por estratégia, ligado por padrão e desligável no Monitor (#747, #1122), não aparece como benefício.
- O benefício do backtest diz "Teste qualquer estratégia", mas quem não é admin não roda backtest: vê a análise pronta das estratégias que acompanha (#917, #953).
- A página fala só de cripto, e o Farol já acompanha ações e ETFs da Binance (#1117 a #1123).

**Performance e infraestrutura**
- A imagem do hero é um PNG de 1,4 MB, quase 90% dos ~1,56 MB da página. O LCP no celular ficou em ~1,26 s.
- CSS e imagens saem sem `Cache-Control`.
- São 3 famílias do Google Fonts (IBM Plex Sans, Inter e JetBrains Mono, 9 pesos).
- A página de produção carrega assets de `/prototypes/...` e `../cripto-farol-landing/...`, caminhos de protótipo que ficam frágeis.
- Faltam cabeçalhos de segurança (HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`/CSP).

### História (do issue #1160)

Como visitante que chega à landing por um link no WhatsApp ou pela busca, quero entender rápido o que o Cripto Farol faz, confiar em quem está por trás e deixar meu contato sem atrito, para entrar no beta sem medo de golpe nem de uso indevido dos meus dados.

Como Alan, quero que cada visita que chega ao formulário vire um lead medido, e que a página passe numa checagem básica de SEO, LGPD e performance, para que o tráfego do beta não se perca.

## What Changes

### Entra (do issue #1160; itens 12 e 13 são decisões do Alan no Design)

1. **Lead no passo 1:** nome e e-mail salvam o lead na hora. O passo 2 (WhatsApp, nível, dificuldade) só enriquece o lead e é opcional.
   - Critério: quem sai depois do passo 1 fica registrado como lead; quem completa o passo 2 enriquece o mesmo lead, sem duplicar.
   - Tudo o que o formulário pede (nome, e-mail, WhatsApp, nível, dificuldade) fica guardado, não só o e-mail.
   - O Alan recebe um aviso a cada lead novo.
   - A tela de sucesso diz a verdade: algo como "Recebemos seu cadastro. Vamos te chamar quando abrir a próxima leva." Nada de prometer e-mail que não sai. O botão do passo 1 deixa de dizer "Garantir minha vaga".
2. **Funil medido:** eventos de conclusão do passo 1 e de clique em cada CTA (hero, nav, rodapé).
3. **Rodapé com confiança:** links para Política de Privacidade e Termos (páginas reais, não a SPA) e aviso de risco curto. Sem nome de responsável, CNPJ, contato nem redes (decisão do Alan). O formulário ganha uma linha "Ao enviar, você concorda com a Política de Privacidade".
   - Política e Termos são redigidos pelo agente a partir do que o formulário e o PostHog de fato coletam, e o Alan aprova o texto antes de publicar.
   - Critério: `/privacidade` e `/termos` mostram o conteúdo real.
4. **Aviso de risco visível desde o hero** (frase curta), com texto redigido pelo agente e aprovado pelo Alan.
5. **Copy enxuta:** o jargão das métricas ganha explicação visível no celular, os textos de Spot saem dos nomes internos, MATIC vira POL e a imagem duplicada sai.
6. **Prints do produto limpos e legíveis:** sem controles de desenvolvedor, em português e com preço em formato BR. No celular, um recorte legível em vez da tela inteira.
7. **SEO técnico:** `robots.txt` e `sitemap.xml` reais, `favicon.ico` e `apple-touch-icon`, Open Graph e Twitter Card com imagem 1200×630, `canonical`, meta description com acentos, um título que diga o que o produto faz, e JSON-LD de Organization e FAQPage.
   - Critério: o link colado no WhatsApp mostra imagem, título e descrição.
8. **www → apex** com redirect 301/308.
9. **Performance:** o hero vira WebP/AVIF responsivo (`srcset`), com meta de ≤ 200 KB no celular. Assets estáticos ganham `Cache-Control` longo, as famílias de fonte caem para no máximo 2 e os assets saem de `/prototypes/`.
   - Critério: Lighthouse no celular com Performance ≥ 90 e SEO ≥ 95.
10. **Cabeçalhos de segurança** no Caddy: HSTS, `X-Content-Type-Options`, `Referrer-Policy` e `frame-ancestors`.
11. **Sem contador de vagas:** sai "Já são N cadastrados. Restam N vagas". Fica uma frase fixa de beta fechado em levas.
    - Critério: a página não mostra número de cadastrados nem de vagas, nem "--".
12. **(Decisão do Alan no Design, 29/10/2026) A landing de produção sai do repo `crypto` e passa a viver no repo `oalansilva/cripto-farol-landing`.** O Alan escolheu "Repo cripto-farol-landing" contra "pasta própria no crypto" e confirmou que `frontend/public/prototypes/` do `crypto` deve ter somente protótipos.
    - A v4 com o delta deste card substitui a versão antiga do repo; a landing ganha checkout, publicação e reversão próprios, fora da release do `crypto`.
    - Depois do corte, a v4 e os assets de landing saem de `frontend/public/prototypes/` do `crypto`, e `docs/landing-page.md` aponta para o repo novo.
    - O envio de leads continua no backend do `crypto`.
13. **(Devolução do Alan no T6, 29/10/2026, [recibo](https://github.com/oalansilva/crypto/issues/1160#issuecomment-6505701552)) A landing passa a mostrar o produto atual.**
    - Prints novos do Monitor: "Em posição" e "Saída / cobertura", tempo gráfico de cada estratégia, controle de alerta, sem alvo; e da análise com as operações marcadas.
    - Alerta no Telegram por estratégia como benefício.
    - Backtest como análise pronta das estratégias acompanhadas, não "teste qualquer estratégia".
    - A página cobre cripto, ações e ETFs da Binance no hero, nos benefícios, nos prints e no FAQ, e deixa claro que ação e ETF são acompanhados e alertados, mas não comprados nem vendidos pelo Farol (comprar e vender pelo Farol é só cripto, na Binance Spot).
    - O posicionamento de apoio à decisão e o aviso de risco ficam; o aviso passa a cobrir ações e ETFs.
    - Critério: a página não mostra "Compra"/"Venda" como estado, alvo, "Teste qualquer estratégia" nem a pergunta sobre outra exchange; os prints mostram ação ou ETF ao lado de cripto.

### Não entra (do issue #1160; ressalva do T6 marcada)

- Redesenho visual ou troca de identidade da marca.
- Novo posicionamento ou nova promessa do produto (#790 já fechou o posicionamento educacional). **Exceção (T6 do Alan, 29/10/2026):** a ampliação para cripto, ações e ETFs da Binance (item 13) entra; o resto do posicionamento do #790 continua.
- Blog, conteúdo de SEO, páginas por moeda ou campanhas pagas.
- Mudança no app autenticado (`/login` em diante).
- Nome de responsável, CNPJ, contato ou redes no rodapé (decisão do Alan).
- Revisão jurídica da Política, dos Termos e do aviso de risco: fica para depois, fora deste card.
- Dividir o card: o Alan decidiu manter um card só.

## Capabilities

### New Capabilities

- `landing-lead-capture`: lead salvo no passo 1 com tudo o que o formulário pede, passo 2 opcional que enriquece o mesmo lead, aviso ao Alan a cada lead, resposta neutra e tela de sucesso honesta.
- `landing-legal-pages`: rodapé com Política de Privacidade, Termos e aviso de risco; páginas `/privacidade` e `/termos` reais; aviso de risco no hero; linha de consentimento no formulário. Pelo T6, os avisos de risco e os Termos cobrem ações e ETFs (só acompanhados e alertados).
- `landing-seo-performance`: `robots.txt`, `sitemap.xml`, ícones, Open Graph/Twitter Card, `canonical`, título e descrição, JSON-LD, www → apex, hero responsivo, `Cache-Control`, no máximo 2 famílias de fonte, cabeçalhos de segurança e metas de Lighthouse.
- `landing-publication`: a landing de produção vive no repo `oalansilva/cripto-farol-landing`, com checkout próprio em DEV e PROD, publicação e reversão fora da release do `crypto`, assets fora de `/prototypes/` e `frontend/public/prototypes/` do `crypto` só com protótipos.

### Modified Capabilities

- `landing-conversion-copy`: o formulário passa a salvar no passo 1 com passo 2 opcional (o requisito "Landing keeps closed-beta lead capture intact" deixa de mandar enviar só no submit final); os textos de carteira, confiança e FAQ deixam de exigir os nomes internos "Operar", "Home" e "Spot Trade"; a métrica ganha explicação visível; sai o contador; MATIC vira POL; o print do Monitor aparece uma vez; prints do produto atual, limpos e legíveis no celular; e, pelo T6, cripto, ações e ETFs da Binance (comprar e vender pelo Farol só cripto), backtest como análise pronta, sinais com os nomes do Monitor e alerta no Telegram por estratégia como benefício.
- `product-analytics`: novos eventos `lead_step1_completed` e `landing_cta_clicked`, e os eventos de envio passam a dizer o passo, sem dado pessoal.

`beta-lead-access-hardening` não muda: a auditoria do lead, a resposta neutra e a regra de não criar conta nem consumir convite (#689) seguem valendo; os campos guardados vivem em `landing-lead-capture`.

## Impact

- **Repo `oalansilva/cripto-farol-landing` (novo destino da landing de produção):** branch e PR próprios; recebe a v4 com o delta deste card, as páginas `/privacidade` e `/termos`, `robots.txt`, `sitemap.xml`, ícones, imagem OG, assets otimizados e o script de publicação; saem a versão antiga, `server.js`, `scripts/create_beta_user.py` e `variants/`.
- **Repo `crypto`:**
  - `backend/app/routes/leads.py` e `backend/app/services/beta_access.py`: passo 1 salva, passo 2 enriquece sem duplicar, campos guardados, aviso por Telegram, `/api/leads/stats` sai; modelo e migração Alembic de uma tabela de leads.
  - `ops/landing-leads/` (serviço Node que hoje recebe o `POST /api/leads` em PROD e exige WhatsApp) sai do caminho e do repo; `criptofarol-prod-leads.service` é desligado no corte.
  - `frontend/public/prototypes/cripto-farol-landing-v4/` e os assets de landing em `frontend/public/prototypes/cripto-farol-landing/` saem depois do corte; testes que leem a v4 (`frontend/tests/landing-posthog-legacy.test.mjs`, `frontend/tests/card-1075-no-scalp-copy.test.mjs`) passam a ler o repo da landing ou saem.
  - `docs/landing-page.md` aponta para o repo novo e descreve o fluxo real; `docs/brand-system.md` registra as 2 famílias de fonte.
- **Infra (host):** `/etc/caddy/Caddyfile` passa a servir a landing do checkout do repo novo, com redirect www → apex, `Cache-Control` e cabeçalhos de segurança; host de DEV para a landing.
- **Specs:** delta em `landing-conversion-copy` e `product-analytics`; novos `landing-lead-capture`, `landing-legal-pages`, `landing-seo-performance`, `landing-publication`.
- **Não afeta:** app autenticado (`/login` em diante), convite de uso único (#689), identidade visual.
