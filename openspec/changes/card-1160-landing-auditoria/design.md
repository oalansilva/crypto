UI impact: affected
live_route: landing
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1160](https://github.com/oalansilva/crypto/issues/1160), Status Design (T1 do Alan com `/priorizar 1160`, 29/10/2026). O briefing é o body grelhado do issue, copiado em `proposal.md`. Decisões do Alan na grelha, fechadas: card único; o contador sai e vira frase fixa de beta fechado em levas; Política, Termos e aviso de risco redigidos pelo agente e aprovados pelo Alan no T7, revisão jurídica fora do card; rodapé sem responsável, CNPJ, contato ou redes; depois do envio, guardar tudo o que o formulário pede, avisar o Alan a cada lead e tela de sucesso honesta. Decisão do Alan durante este Design (29/10/2026): a landing de produção sai do `crypto` e passa a viver no repo `oalansilva/cripto-farol-landing`; `frontend/public/prototypes/` do `crypto` fica só com protótipos.

**Rodada d2 (devolução do Alan no T6, 29/10/2026, [recibo](https://github.com/oalansilva/crypto/issues/1160#issuecomment-6505701552)).** Motivo: atualizar a landing ao produto atual (prints novos do Monitor com "Em posição" / "Saída / cobertura", tempo gráfico por estratégia e sem alvo; alerta no Telegram por estratégia como benefício; backtest como análise pronta das estratégias acompanhadas; cripto, ações e ETFs da Binance no hero, nos benefícios, nos prints e no FAQ). O "novo posicionamento" sai do Não entra só para essa ampliação. Tudo o que a d1 e o r1 resolveram fica (fases F0–F7, Enter no passo 1, textos legais, fontes servidas pelo site, P3 aceitos, Open Questions 1–7); a d2 mexe só na copy, nos prints, nos specs de copy e de páginas legais e nesta documentação (D13).

**Rework r2 (último da rodada d2; dupla A/B da d2 e respostas do Alan pela ferramenta do host, 29/10/2026).** O Alan respondeu a Open Question 12 com "Frase honesta na landing (Recommended)": a landing mantém o Telegram, mas diz que o alerta vale para as estratégias que a pessoa acompanha com estrela; um card de produto separado (criado pelo pai) fará a vitrine alertar. Sobre a frequência do alerta, "Não citar frequência": a copy não diz quando o alerta sai, e também não pode sugerir tempo real. O r2 aplica isso no benefício 02, no chip do hero, na rotina 01, no FAQ 6, na descrição e no OG; troca a NVDA do print do Monitor pela SPY (os dois prints contavam histórias opostas da NVDA); refaz o recorte do gráfico para o celular com texto legível; e aplica os P3 baratos e visíveis da dupla (confiança 1 e 2, abertura do produto, `og:title`/`og:image:alt`, largura de linha dos avisos).

### Produto atual (conferido em 29/10/2026 nas changes arquivadas e no código do worktree)

- **Monitor:** estados "Em posição" e "Saída / cobertura" (`frontend/src/components/monitor/signalResolution.ts:8`, `MonitorStatusTab.tsx:1312-1317`; #718); tempo gráfico da estratégia em cada linha, 15m/1h/4h/1d (`types.ts:122`; #994, #1074); sem alvo (#803); risco = distância até a saída e até o stop, stop e entrada (#792); controle "Alerta" por estratégia, ligado por padrão (#1122).
- **Telegram:** cada pessoa recebe a entrada e a saída das estratégias próprias com estrela no Monitor, em cripto, ação e ETF, ligado por padrão e desligável por estratégia, depois de conectar o Telegram no Perfil (`users.telegram_chat_id`); mercado fechado aparece só na tela; o alerta nunca envia ordem (#747, #1122). O scan roda uma vez por dia, às 08:05 BRT (`ops/systemd/criptofarol-*-telegram-alert-scan.timer`); a copy não cita frequência (decisão do Alan, Open Question 13).
- **Quem entra pelo beta não recebe alerta hoje (Open Question 12, respondida):** a conta nova é comum (não admin) e não tem estratégia própria com estrela, então o Monitor dela mostra a vitrine do catálogo, com a faixa "só exibição, sem alerta no Telegram" e sem o controle de Alerta; a estrela que ela dá numa linha do catálogo também não alerta (#1122, decisão 3; spec `monitor-curated-fallback`). Ela também não consegue criar estratégia própria pela UI: o único caminho é "Salvar nos Favoritos" num resultado de otimização (`ComboResultsPage.tsx`, `isOptimization`), que é só do admin, e nada semeia favoritos na conta nova. Um card de produto separado (o pai cria) fará a vitrine alertar; até lá a landing usa a frase honesta (D13).
- **Análise** (`/combo/results`, aberta pelos Favoritos): o gráfico marca todas as operações no período com as linhas da estratégia (#917, #953). Não desenha linha de stop: as linhas "Compra" e "STOP" existem só no "Abrir Gráfico" do Monitor (`components/monitor/ChartModal.tsx:651-656`; `StrategyChartSurface` só recebe `priceLines` dali).
- **Quem roda backtest:** Combo, Descoberta e Otimização são só de admin (`frontend/src/App.tsx:68-74`, `requireAdmin`); quem não é admin e não tem favorito próprio com estrela vê a vitrine do catálogo no Monitor (#1122). Logo, para o visitante da landing o backtest é a análise pronta das estratégias que ele acompanha.
- **Ações e ETFs da Binance:** catálogo, histórico, backtest, lote, Descoberta, favoritos, Monitor, alertas, referência e exportação (#1117 a #1123), com o pregão de Nova York.
- **Operar é só cripto:** o botão aparece só para par Spot em USDT de classe cripto (`MonitorStatusTab.tsx:174-198`, `isSpotUsdtCandidate` exige `getOpportunityAssetType(...) === 'crypto'`); para ação e ETF o botão nem aparece. Comprar com USDT ou USDC (#637), proteger com stop e remover o stop antes de vender (#861), sempre com confirmação. Na copy: ação e ETF são acompanhados e alertados, não comprados nem vendidos pelo Farol.

### Como está hoje (conferido em 29/10/2026, `card-1160-landing-auditoria` @ 768467b8, host e PROD só leitura)

- **Página:** `https://criptofarol.com.br/` é `frontend/public/prototypes/cripto-farol-landing-v4/index.html` + `styles.css`, servidos pelo Caddy a partir de `/srv/apps/prod/criptofarol/source/frontend/dist/prototypes/cripto-farol-landing-v4` (`@prodLandingHome path / /styles.css`). O hero vem de `../cripto-farol-landing/assets/hero/cripto-farol-hero.png` (1.419.002 B) e o logo de `../cripto-farol-landing/assets/brand/`; os prints de `/prototypes/cripto-farol-landing-v4/assets/product/`. Qualquer outro caminho (`/robots.txt`, `/sitemap.xml`, `/privacidade`) cai no preview da SPA (`:5173`) e devolve o HTML do app; `/favicon.ico` dá 404. `www.criptofarol.com.br` está no mesmo bloco do apex e responde 200. A resposta não traz HSTS, `X-Content-Type-Options`, `Referrer-Policy` nem `frame-ancestors`; o HTML sai com `cache-control: no-cache` e os estáticos sem `Cache-Control`.
- **Envio do lead em PROD — achado que a grelha não tinha:** o `POST /api/leads` não vai direto ao backend. O Caddy manda `@prodLeadSubmit` para `127.0.0.1:5174`, o serviço Node `criptofarol-prod-leads.service` (`ops/landing-leads/server.js`, idêntico ao do repo). Esse serviço (a) **recusa o lead sem WhatsApp** (`400 whatsapp_required`, embora o formulário diga "WhatsApp opcional": quem deixa o campo vazio vê "Não foi possível enviar agora"); (b) repassa ao backend FastAPI (`backend/app/routes/leads.py`), que grava só o e-mail e marcas `has_whatsapp/has_profile/has_pain` em `beta_access_audit_logs` (desde #689); (c) grava nome, e-mail, WhatsApp, perfil, dificuldade e origem numa planilha `.xlsx` local (`ops/landing-leads/data/leads-cripto-farol.xlsx`, última escrita em 08/06/2026) e tenta, em "melhor esforço", subir para o Drive da Clara (`gog`), avisar um tópico de grupo no Telegram e mandar e-mail ao Alan (`gog gmail`). O token do Telegram fica num `.env.leads` só de root; não deu para confirmar se os avisos saem, e o journal não mostra erro nem envio. Ou seja: em PROD o dado completo existe numa planilha frágil fora do banco, e o caminho que o grava descarta quem não informa WhatsApp.
- **Contador:** `GET /api/leads/stats` (vai ao backend `:8003`) conta contas do app não banidas, com teto fixo de 50 (`BETA_TOTAL_SPOTS`).
- **Tela de sucesso:** "Cadastro recebido. Verifique seu e-mail para o acesso inicial." Nenhum e-mail sai desde #689.
- **PostHog — achado que a grelha não tinha:** o `posthog-config.js` servido em PROD tem `key: ''`, então a landing **não carrega o PostHog** hoje (nem grava no navegador). O app tem a chave (`frontend/.env.local` de PROD, `VITE_POSTHOG_KEY`). Os eventos já previstos (`landing_pageview`, `lead_form_submit_*`) não chegam.
- **Aviso por Telegram já existente no backend:** `send_telegram_message` (`backend/app/services/monitor_telegram_alerts.py:546`) com `MONITOR_TELEGRAM_BOT_TOKEN`, e `users.telegram_chat_id` vinculado pelo Perfil. É o canal que o Monitor usa todo dia em PROD. Não há caminho de e-mail confirmado (o SMTP do legado é opcional por variável de ambiente e a tela de hoje mostra que nada sai).
- **Repo `oalansilva/cripto-farol-landing`:** privado, `main`, último push 10/05/2026. Tem a primeira landing (`index.html`, `styles.css`, `assets/brand`, `assets/hero/cripto-farol-hero.png`), `server.js` antigo (planilha via `xlsx`), `scripts/create_beta_user.py` (criação de conta pela landing, aposentada no #689), `variants/` (skill-v2, v3 e uma v4 antiga), `assets/brand/concepts/` (logos aprovados, ~1,6 MB) e README "manter a landing separada do repositório principal". Não há checkout dele no host.
- **DNS:** só `criptofarol.com.br`, `www` e `dev` resolvem; não há curinga. Os hosts `*.163.176.208.0.sslip.io` já são usados pelo Caddy (dev, prod, clara-dev) e resolvem sem DNS.

### Regiões clonadas (só estas)

O protótipo clona o HTML vigente da landing v4 (`frontend/public/prototypes/cripto-farol-landing-v4/index.html`, o mesmo arquivo publicado em `https://criptofarol.com.br/`) e o `styles.css` inteiro. Regiões marcadas com `COPIED:start`/`COPIED:end` (28 pares no `index.html`) são substrings literais da v4; o delta fica só em `DELTA:start`/`DELTA:end`:

- **Cabeçalho do documento:** título e descrição com cripto, ações e ETFs, `canonical`, Open Graph, Twitter Card, ícone, `preload` do hero e da fonte, fontes (Inter + JetBrains Mono) servidas pela própria pasta (sem Google Fonts) e JSON-LD (Organization + FAQPage igual ao FAQ visível).
- **Topo:** logo sem caminho de protótipo; rótulo "Navegação principal" com acento; CTA "Entrar na lista" na navegação (`data-cta="nav"`, primeiro item e alvo de 44 px até 920 px).
- **Hero:** imagem em WebP responsivo; rótulo "Beta fechado · cripto, ações e ETFs da Binance"; abertura com cripto, ações e ETFs; `data-cta="hero"` no CTA; "Alerta no Telegram nas estratégias com estrela" no lugar de "Integração segura" na linha de confiança; frase de risco que cobre ações e ETFs; print do Monitor (layout de cartões do app, legível no desktop e no celular). O H1 fica igual (D13).
- **Rotina:** frase de abertura sem "cripto"; passos 01 (Monitor com cripto, ações e ETFs; alerta no Telegram nas estratégias com estrela) e 02 (análise pronta). O passo 03 é a v4.
- **Produto:** só a análise (gráfico com as operações marcadas), com recorte no celular; texto de abertura novo ("Além do Monitor que você viu acima…").
- **Benefícios:** 01 "Análise pronta de cada estratégia"; 02 "Alerta no Telegram por estratégia", com a frase honesta (estratégias com estrela, Telegram conectado no Perfil) (no lugar de "6 meses grátis", que já está no hero, no subtítulo da seção, no FAQ e no cadastro); 03 com a métrica explicada (`<dl>`); 04 sem nomes internos e com "compra e venda de cripto".
- **Sinais:** "Em posição" e "Saída / cobertura" no lugar de "Compra"/"Venda" (D13).
- **Confiança:** cartão 1 sem "grupo de Telegram" (r2), cartão 2 sem negar as médias que a análise mostra (r2), cartão 3 "Sem senha, sem saque" ("comprar e vender cripto").
- **FAQ:** três primeiras respostas (trader, robô, dinheiro) e a sexta, "Funciona com ações e ETFs?" no lugar de "outra exchange" (com a frase honesta do alerta e o Telegram conectado no Perfil).
- **Cadastro:** chamada "Entre na lista do beta"; frase de levas no lugar do contador; POL no lugar de MATIC e NVDA (ação), SPY e QQQ (ETF) nos exemplos; aviso de risco do cadastro com ações e ETFs; passo 1 que salva ("Entrar na lista do beta", também por Enter) com a linha de consentimento (link da Política em nova aba); passo 2 opcional (foco no título ao abrir) com "Pular esta etapa"; estado final "Recebemos seu cadastro."; mensagens de erro.
- **Rodapé** (novo, aviso de risco com ações e ETFs) e **script** do formulário (os trechos de atribuição da v4 seguem em COPIED; o resto é delta; envio simulado).
- **Páginas extras** `privacidade.html` e `termos.html`: clonam o `<head>` e o cabeçalho da v4 (COPIED) e trazem o texto legal e o mesmo rodapé (DELTA).

Tudo o que não está listado (passo 03 da rotina, títulos das seções, títulos da confiança, FAQ 4–5, textos do cadastro, campos do formulário, CSS da v4) é a v4 sem mudança.

## Goals / Non-Goals

**Goals:**

- Lead salvo no passo 1, passo 2 opcional que enriquece o mesmo lead, tudo guardado no banco do `crypto`, aviso ao Alan por lead e mensagens honestas (Entra 1, 11).
- Funil medido no PostHog, com a landing de fato carregando o PostHog em PROD (Entra 2).
- Rodapé, `/privacidade`, `/termos`, linha de consentimento e aviso de risco no hero, com textos para o Alan aprovar no T7 (Entra 3, 4).
- Copy enxuta, prints limpos e legíveis no celular (Entra 5, 6).
- SEO técnico, www → apex, performance e cabeçalhos de segurança (Entra 7–10).
- Landing de produção no repo `oalansilva/cripto-farol-landing`, com publicação e reversão próprias, e `frontend/public/prototypes/` do `crypto` só com protótipos (Entra 12).
- Landing com o produto atual: prints novos do Monitor e da análise, alerta no Telegram por estratégia, backtest como análise pronta, cripto, ações e ETFs da Binance, sem prometer operar ação ou ETF (Entra 13, T6).

**Non-Goals (do issue, não reabrir):**

- Redesenho visual ou troca de identidade; novo posicionamento ou promessa (#790 fechou), com a exceção do T6: a ampliação para cripto, ações e ETFs da Binance; blog, SEO de conteúdo, páginas por moeda, campanhas.
- Mudar os campos do formulário ("Nível com cripto", "Sua maior dificuldade hoje com cripto"): o T6 não pede (Open Question 11).
- Mudança no app autenticado (`/login` em diante). Os cabeçalhos de segurança valem para o domínio inteiro, mas não mudam código do app.
- Nome de responsável, CNPJ, contato ou redes no rodapé; revisão jurídica; dividir o card.
- Listagem de leads no app (não está no Entra; o Alan vê os leads pelo aviso do Telegram e o dado fica no banco).
- Prova social (aparece no Problema, mas não no Entra).

## Decisions

### D1 — Lead numa tabela própria do backend do `crypto`, salvo no passo 1

Nova tabela `landing_leads` (PostgreSQL, migração Alembic) com e-mail normalizado único, nome, WhatsApp, nível, dificuldade, origem, atribuição sanitizada (os mesmos campos que a v4 já manda), passo alcançado, criado/atualizado em. `POST /api/leads` passa a aceitar `step` (`1` ou `2`):

- passo 1: nome e e-mail obrigatórios; cria ou atualiza o lead do e-mail (upsert), sem apagar campos de um passo 2 anterior;
- passo 2: WhatsApp, nível e dificuldade, todos opcionais; enriquece o lead do mesmo e-mail (o formulário reenvia o e-mail do passo 1); sem lead do e-mail, cria;
- sem `step` (a v4 de hoje, repassada pelo Node até a fase F4, e o commit-base da landing, que é o alvo de rollback): trata como passo 1 + passo 2 juntos, para a release do backend não quebrar a página antiga.

A resposta continua o 202 neutro para todo envio aceito, e a auditoria do #689 (`record_lead_submission`, convite validado sem consumir, nenhuma conta criada) segue igual. A atribuição continua sanitizada como hoje (`_sanitize_attribution`).

Alternativas rejeitadas: (a) manter só e-mail + marcas na auditoria — não cumpre "tudo o que o formulário pede fica guardado"; (b) ficar com a planilha do serviço Node — fora do PostgreSQL (regra do overlay), reescreve o arquivo inteiro a cada lead, depende do `gog` e recusa quem não dá WhatsApp; (c) guardar os campos no `metadata_json` da auditoria — mistura log com cadastro e não deixa enriquecer sem duplicar.

### D2 — O serviço Node sai do caminho; o `POST /api/leads` vai direto ao backend

No corte, o Caddy de PROD deixa de mandar `@prodLeadSubmit` para `:5174`; `/api/leads` cai no `handle /api/*` do backend. `criptofarol-prod-leads.service` é parado e desabilitado, e `ops/landing-leads/` sai do repo `crypto`. A planilha local e a cópia no Drive ficam como histórico (ver Open Question 2).

Alternativa rejeitada: manter o Node na frente e só tirar a exigência de WhatsApp — seriam dois lugares gravando o mesmo lead, e o aviso continuaria dependendo de token num arquivo só de root.

### D3 — Aviso de lead por Telegram, no bot que já existe

O backend manda uma mensagem pelo bot do Cripto Farol (`MONITOR_TELEGRAM_BOT_TOKEN`, reaproveitando `send_telegram_message`) para cada admin com Telegram vinculado (`users.telegram_chat_id`, o vínculo que o Alan já usa para os alertas do Monitor):

- lead novo (passo 1): "Novo lead na landing" + nome, e-mail, origem e UTM de campanha quando houver;
- passo 2: "Lead completou o cadastro" + e-mail, WhatsApp, nível e dificuldade;
- reenvio do passo 1 de um e-mail que já existe: sem aviso (não é lead novo).

O envio roda depois do commit, fora do tempo da resposta, e uma falha só gera log sem dado pessoal; o lead e a tela de sucesso não dependem dele.

Alternativas rejeitadas: e-mail (não há envio confirmado em PROD; é exatamente a promessa que a página não cumpre hoje); tópico do grupo do serviço Node (token em arquivo só de root, serviço aposentado em D2).

### D4 — Formulário e mensagens

Textos (protótipo, região "Cadastro"):

| Onde | Antes | Depois |
|---|---|---|
| Chamada | "Garanta sua vaga no beta" | "Entre na lista do beta" |
| Contador | "Já são N cadastrados. Restam N vagas nesta leva." | "Beta fechado, com entrada em levas. Você entra na lista e a gente te chama quando abrir a próxima leva." |
| Botão do passo 1 | "Garantir minha vaga" (só mostrava o passo 2) | "Entrar na lista do beta" (salva o lead) |
| Abaixo do botão | — | "Ao enviar, você concorda com a Política de Privacidade." |
| Depois do passo 1 | "Primeira etapa pronta. Complete a qualificação para priorizar seu acesso." | "Pronto, seu cadastro está salvo." + título do passo 2 "Cadastro salvo. Quer contar um pouco sobre você? É opcional." |
| Campos do passo 2 | nível e dificuldade obrigatórios | "(opcional)" nos três; nível começa em "Prefiro não dizer" |
| Botões do passo 2 | "Enviar qualificação" | "Enviar respostas" e "Pular esta etapa" |
| Final | "Cadastro recebido. Verifique seu e-mail para o acesso inicial." | "Recebemos seu cadastro." / "Vamos te chamar quando abrir a próxima leva do beta." |
| Erro no passo 1 | "Não foi possível enviar agora. Tente novamente em alguns minutos." | "Não conseguimos salvar agora. Tente de novo em alguns minutos." (fica no passo 1) |
| Erro no passo 2 | — | "Seu cadastro já está salvo, mas estas respostas não foram. Tente de novo ou pule esta etapa." |
| Link da Política na linha de consentimento | — | abre em nova aba (`target="_blank" rel="noopener"`, "abre em nova aba" para leitor de tela), para não perder nome e e-mail digitados |

Teclado e foco:

- **Enter/"Ir" no passo 1 = "Entrar na lista do beta".** O botão do passo 1 é `type="button"` e o único `type="submit"` é o do passo 2, então o Enter num campo do passo 1 dispara o envio do formulário. O `submit` com o passo 1 ativo segue o caminho do botão do passo 1 (valida, salva com `step: 1` e nome, mostra o passo 2) e nunca manda o passo 2. Enter no passo 2 envia o passo 2.
- **Depois do passo 1, o foco vai para o título do passo 2** (`tabindex=-1`): o leitor de tela lê "Cadastro salvo… É opcional" e o teclado do celular não abre por cima de "Pular esta etapa".
- O estado final recebe o foco (`tabindex=-1`) e a mensagem fica no `role=status` que já existe. `GET /api/leads/stats` e `BETA_TOTAL_SPOTS` saem (com o teste que os cobre).

### D5 — Funil no PostHog e chave no deploy

Eventos novos, sem nome, e-mail, WhatsApp nem respostas: `lead_step1_completed`; `landing_cta_clicked` com `cta_location` = `hero` | `nav` | `footer`; `lead_step2_skipped`. Os `lead_form_submit_started/accepted/failed` que já existem passam a levar `step`. `origin` passa de `landing-v4` para `landing` (o nome da variante deixa de fazer sentido fora do `crypto`).

O `posthog.init` da landing desliga gravação de sessão e pesquisas (`disable_session_recording: true`, `disable_surveys: true`), além do `autocapture: false` e `persistence: "localStorage"` que a v4 já usa. Assim a Política não depende de uma chave do projeto do app (que é o mesmo projeto): se o app ligar replay ou surveys, a landing continua sem.

A chave do projeto é escrita no deploy da landing (D12) em `lp/posthog-config.js`, a partir da mesma chave do app; não entra no git. Sem a chave, os eventos continuam no-op, como hoje.

### D6 — Rodapé, páginas legais e aviso de risco

- Rodapé: marca, "Política de Privacidade", "Termos de Uso", "Já tenho acesso", CTA "Quero meus 6 meses grátis" (`data-cta="footer"`), aviso de risco e "© 2026 Cripto Farol". Sem responsável, CNPJ, contato ou redes. A identificação do controlador e o canal do titular ficam **dentro da Política** (item 7), não no rodapé.
- Navegação: CTA "Entrar na lista" (`data-cta="nav"`; mesma honestidade do botão do passo 1, que não promete vaga), primeiro item e com alvo de pelo menos 44 px até 920 px.
- Hero: "Apoio à decisão, não recomendação de investimento. Cripto tem risco e nenhuma análise garante resultado.", logo abaixo da linha de confiança (na primeira tela a 1440 px; logo depois dos CTAs a 390 px).
- `/privacidade` e `/termos` são HTML estático da landing, com o mesmo cabeçalho e rodapé (rascunhos abaixo, na seção "Textos para aprovação").
- O aviso de risco do cadastro (v4) fica como está.

### D7 — Copy enxuta

- Métricas: o `title` some e entra uma lista visível nome → explicação (Sharpe "retorno ajustado ao risco", Trades "quantas operações a estratégia fez", Win% "em quantas operações acertou", Return "quanto rendeu no período", Max DD "a maior queda no caminho", PF "quanto ganhou para cada 1 que perdeu", SQN "quão consistente é o resultado", Max L "a maior sequência de perdas", ATR "quanto o preço costuma oscilar"). Os nomes ficam como o app mostra (o spec já exige a lista).
- Benefício 04: "Veja saldo e resultado da sua Binance no Farol. Se quiser, libere também compra e venda de cripto à vista: cada ordem só sai depois que você confirma. Saque, nunca." ("de cripto" entrou na d2: Operar é só cripto, D13.)
- Confiança 1 (r2): "Você vê sinal, contexto e risco em linguagem simples, sem depender de opinião solta de influencer ou de grupo de sinais." (a v4 dizia "grupo de Telegram", ao lado do benefício do Telegram). Confiança 2 (r2): "A tela destaca o que importa para decidir. O Monitor diz em palavras se cada estratégia está em posição ou em saída; o gráfico fica para quando você quiser conferir." (a v4 dizia "não precisa interpretar gráfico, médias móveis…", e a análise mostra as médias).
- Confiança 3: título "Sem senha, sem saque" (o "Seu dinheiro nunca sai do lugar" não é verdade quando a pessoa compra pelo Farol); texto "O Farol nunca pede sua senha e nunca faz saque. Comprar e vender cripto pelo Farol é opcional, e cada ordem só sai depois que você confirma."
- FAQ: trader "Não. A leitura é em português claro, e cada métrica vem com uma explicação curta."; robô "Não. O Cripto Farol não opera sozinho: cada compra ou venda de cripto pede a sua confirmação. E ele nunca faz saque."; dinheiro "Não para sacar. O Farol lê seu saldo na Binance para acompanhar a carteira. Se você quiser, libera também compra e venda de cripto à vista, sempre com a sua confirmação. Nunca pedimos senha e nunca sacamos."; a sexta pergunta é a de D13.
- MATIC → POL. O print do Monitor aparece só no hero; o produto mostra só a análise, com a abertura (r2) "Além do Monitor que você viu acima, aqui está a análise pronta de uma estratégia que você acompanha: o gráfico marca todas as operações no período, com as linhas da estratégia, para você decidir com calma." A legenda mantém "02", que casa com o passo 02 da rotina, com o texto "Todas as compras e vendas da estratégia marcadas no gráfico, com o resultado de cada saída."

A política Q3=A do #790 continua (Spot opcional, confirmação a cada ordem, nunca saque, não opera sozinho); só saem os nomes internos. O spec `landing-conversion-copy` muda junto.

### D8 — Prints do produto atual, limpos e legíveis no celular

Rodada d2: os prints da d1 (tabela e gráfico da v4, maio/2026) saem; os novos mostram o produto atual. **Não há credencial do DEV no cofre de segredos, então nenhum print vem do DEV logado:** os dois saem de clones homologados que estão em `frontend/public/prototypes/`, capturados com Playwright (Chromium headless shell 1243, `pt-BR`), e ficam marcados como P3 "recapturar do DEV logado no Apply" (task 2.10; Open Question 8).

| Print | Arquivo (px) | Origem | Limpeza |
|---|---|---|---|
| Monitor (hero, desktop e celular) | `assets/monitor.webp` (680×1070, 2× de 340×535; r2) | `https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/` (clone do `/monitor` homologado no #1122), filtro "Todos", viewport de 438 px (layout de cartões do app; o board fica com 340 px), elemento `main.monitor-board` | No DOM, antes da captura: some tudo fora da lista (menu, cabeçalho com o nome da conta, "Como usar", faixa educacional, busca, KPIs, filtros, Demonstração); ficam só os cartões SPY (ETF, Em posição, 1d, "Alerta: ligado", "ETF · USD · Binance · NY · split", "Pregão aberto", bloco compra/stop) e ETH/USDT (Saída / cobertura, 4h, "Alerta: desligado"); somem BTC/USDT, as duas NVDA (r2: a análise mostra a NVDA fora de posição, então a NVDA sai do Monitor para os dois prints não se contradizerem), a descrição da estratégia (traz "stop de 5%", parâmetro), mensagem, notas, data do lote e botões que não são o Alerta; preços e percentuais em formato BR; contagens dos títulos = cartões visíveis |
| Análise (produto, desktop) | `assets/grafico-analise.webp` (848×569) | `nvda-chart-desk.png` do clone `card-1119-backtest-acoes-etfs/index.html` (captura viva de `/combo/results`, NVDA 1d, feita no Design do #1119 com a API simulada; o clone a mostra no lugar do canvas) | Corte da barra de controles ("Menos/Mais/Resetar", "180 velas", "Roda do mouse: zoom", "Lista 6 · Setas 12") e do painel "CANDLE"; título com parâmetros ("Média curta (20)", "Média longa (200)") trocado por um cabeçalho "NVDA · Ação · Diário · Médias: tendência · Último fechamento US$ 206,64"; rótulos das linhas sem parâmetro; eixo, etiquetas e percentuais em formato BR; "COMPRA" e "VENDA (-5,18%)" de 1º/jul., que o gráfico vivo sobrepõe, afastados sobre uma faixa escura (mesmas marcações); "PRA" e "v." cortados na borda esquerda apagados; logo do TradingView mantido (atribuição exigida) |
| Análise (produto, celular) | `assets/grafico-analise-recorte.webp` (348×573; r2) | o mesmo gráfico limpo | Período recente (ago.–out.: a COMPRA de agosto e a VENDA (11,16%) de setembro), 1:1 com o gráfico (eixo, marcadores e rótulos das médias em 12 px); cabeçalho redesenhado em duas linhas com texto ≥ 12 px ("NVDA · Ação · Diário", "Médias: tendência", "US$ 206,64", "Último fechamento"); o resto da faixa de "VENDA (-5,18%)" cortado na borda esquerda é apagado; logo do TradingView mantido (atribuição). A 390 px a figura tem ~341 px, ou seja 0,98 da escala: texto efetivo ≥ 11,7 px (o recorte da d2, 493 px, saía a 0,69, com 8,3 px) |
| Imagem OG | `assets/og-1200x630.jpg` (1200×630) | hero da v4 | Desenho da d1 com a frase (r2) "Cripto, ações e ETFs da Binance, com análise pronta e alerta no Telegram nas estratégias com estrela." |

- **Por que o Monitor no layout de cartões:** a tabela larga do Monitor (capturada a 1280 px, ~1050 px de largura) caberia na coluna do hero (~420–520 px) a menos de 0,5 da escala, com texto de ~6 px. O cartão é o próprio Monitor do app no celular; uma imagem só serve as duas larguras (sem `<picture>`).
- **Texto efetivo ≥ 11 px nos dois prints a 390 px (r2):** texto efetivo = menor fonte do print na origem × largura renderizada ÷ largura natural (em px CSS da origem). Monitor: menor fonte 10 px ("Compra / Stop"; rótulos 11 px), board de 340 px; a 390 px o print sai com 390 px (1,147×), menor texto 11,5 px; a 1440 px, na coluna do hero (~418 px), 12,3 px. Recorte da análise: menor fonte 12 px, 348 px naturais; a 390 px, ~341 px (0,98×), 11,7 px. O browser gate confere isso (Prototype Validation) e o Apply repete o assert (task 5.2).
- **Prints coerentes entre si (r2):** um ativo que aparece nos dois prints conta a mesma história (estado, entrada, último preço e tempo gráfico). Na d2 a NVDA 1d estava "Em posição" no Monitor (entrada US$ 182,40, preço US$ 186,10) e fora de posição na análise (última marca VENDA em set., fechamento US$ 206,64); no r2 o Monitor mostra a SPY (ETF) e a análise segue com a NVDA (ação). A regra vale para a recaptura (task 2.10).
- **Stop no gráfico:** a análise (`/combo/results`) não desenha linha de stop; só o "Abrir Gráfico" do Monitor desenha "Compra" e "STOP" (`ChartModal.tsx:651-656`), e nenhum clone homologado renderiza esse gráfico. O stop aparece no print do Monitor (stop, entrada e distâncias até a saída e até o stop); o gráfico mostra as operações marcadas, sem alvo. A recaptura do "Abrir Gráfico" no DEV fica para o Apply se o Alan quiser (Open Question 9).
- **Dados:** os do clone do #1122 (amostra de 26/10/2026; SPY em posição a US$ 668,12, entrada US$ 648,20) e da captura do #1119 (pregões até 12/10/2026). São amostra, não cotação; a legenda não promete preço atual.
- Scripts no scratchpad da sessão: `c1160-d2/capture_monitor.py` e `c1160-d2/build_imgs_d2.py` (d2; a análise de desktop continua a da d2); `c1160-r2/capture_monitor_r2.py` e `c1160-r2/build_imgs_r2.py` (r2: Monitor com SPY, recorte de 348 px e OG).

### D9 — SEO técnico

- Título (d2): "Cripto Farol: sinais para cripto, ações e ETFs da Binance". Descrição (r2): "O Cripto Farol mostra quando faz sentido comprar ou vender cripto, ações e ETFs da Binance, com a análise pronta de cada estratégia e alerta no Telegram nas que você acompanha com estrela. Beta fechado, grátis por 6 meses." `og:description`/`twitter:description` (r2): "Cripto, ações e ETFs da Binance, com análise pronta das estratégias e alerta no Telegram nas que você acompanha com estrela. Beta fechado, grátis por 6 meses." `og:title`/`twitter:title` (r2): "Comprar ou vender cripto, ações e ETFs? O Cripto Farol responde." (o H1 da página fica só com cripto, D13; a prévia do link pode falar das três classes). `og:image:alt` (r2) descreve a imagem: "Cripto Farol: comprar ou vender cripto? O Cripto Farol responde. Cripto, ações e ETFs da Binance, com análise pronta e alerta no Telegram nas estratégias com estrela. Beta fechado, 6 meses grátis."
- `canonical` `https://criptofarol.com.br/`; Open Graph e Twitter Card com o título acima, a imagem `og-1200x630.jpg` (gerada do hero, 87 KB, com a frase de cripto, ações e ETFs) e a descrição curta; JSON-LD com `Organization` (nome, URL, logo, sem contato) e `FAQPage` igual ao FAQ visível. `SoftwareApplication` fica de fora (o Entra pede Organization e FAQPage, e não há preço público).
- `robots.txt`: `Allow: /`, `Disallow: /api/`, `Disallow: /prototypes/`, `Sitemap: https://criptofarol.com.br/sitemap.xml`. `sitemap.xml` com `/`, `/privacidade`, `/termos`. `favicon.ico` (16/32/48) e `apple-touch-icon.png` (180) gerados do `cripto-farol-mark.svg`.

### D10 — Performance

- Hero em WebP com `srcset` 640/1024/1600 (9,6 KB / 20 KB / 36 KB, contra 1,4 MB do PNG), `fetchpriority="high"` e `preload`. AVIF fica opcional (o WebP já está muito abaixo dos 200 KB).
- Fontes: Inter (títulos e texto, 400 a 800) e JetBrains Mono (rótulos e números, 500/700). Sai o IBM Plex Sans (Open Question 4); `docs/brand-system.md` passa a dizer isso.
- As fontes saem do próprio site, não do Google Fonts: `woff2` variável com o subconjunto latino (Inter 48 KB, JetBrains Mono 31 KB, licença OFL) em `/lp/fonts/`, `@font-face` com `font-display: swap` e `preload` da Inter. Tira um terceiro da Política (o Google deixaria de receber o IP do visitante), tira duas conexões do caminho do H1 (o LCP do celular é o texto do H1) e deixa uma futura CSP mais simples. O protótipo já faz assim (`assets/fonts/`).
- Assets da landing em `/lp/` (caminho próprio, fora de `/prototypes/` e de `/assets/`, que é do bundle do app), com `?v=<commit curto>` no HTML e `Cache-Control: public, max-age=31536000, immutable`; HTML com `no-cache`.
- Logo e ícones com `width`/`height`; prints do produto com `loading="lazy"`.

### D11 — www → apex e cabeçalhos de segurança

- `www.criptofarol.com.br` vira um bloco próprio do Caddy: `redir https://criptofarol.com.br{uri} 308`.
- No bloco de PROD (`criptofarol_prod_routes`, vale para landing e app): `Strict-Transport-Security "max-age=31536000"` (sem `includeSubDomains` e sem `preload` nesta rodada), `X-Content-Type-Options "nosniff"`, `Referrer-Policy "strict-origin-when-cross-origin"`, `Content-Security-Policy "frame-ancestors 'none'"`. Uma CSP completa (scripts, estilos, conexões) fica fora: o app e o PostHog precisam de inventário próprio.

### D12 — A landing de produção vai para o repo `oalansilva/cripto-farol-landing` (decisão do Alan)

**Conteúdo do repo depois deste card** (branch `card-1160-landing-auditoria` → PR para `main`):

```
site/                      raiz publicada (tudo aqui é público)
  index.html               v4 + delta deste card (o index.html do protótipo, com caminhos de produção)
  privacidade/index.html
  termos/index.html
  robots.txt  sitemap.xml  favicon.ico  apple-touch-icon.png
  lp/                      styles.css, delta da v4 incorporado, script do formulário, imagens, og, svg
                           posthog-config.js é gerado no deploy (no .gitignore)
brand/                     logos aprovados (hoje em assets/brand/concepts), fora da raiz publicada
scripts/deploy.sh          publica um commit em DEV ou PROD (abaixo)
tests/                     checagens estáticas (node --test): textos proibidos, eventos sem dado pessoal,
                           links, metas, JSON-LD = FAQ, nenhum caminho /prototypes/
README.md                  como publicar, reverter e testar
```

**Dois commits que importam no repo da landing** (merge do PR **sem squash**, para os dois existirem no `main`):

1. **Commit-base = a v4 viva sem delta**, já com os caminhos de produção: `site/index.html` e `site/lp/styles.css` iguais à v4 publicada, só com os caminhos de assets trocados para `/lp/…` (hero PNG, logo, marca e prints da v4 copiados para `site/lp/`) e `lp/posthog-config.js` com a chave vazia (como em PROD hoje). Continua chamando `/api/leads/stats` e mandando o payload da v4 sem `step`. É o primeiro commit da branch e é o **alvo de rollback da landing independente do `crypto`**: funciona com o backend antigo atrás do Node e com o backend novo (payload sem `step` = passo 1 + 2, D1).
2. **Commit do delta** = este card (o `index.html` do protótipo com caminhos de produção, páginas legais, fontes, imagens, testes, `deploy.sh`).

Saem do `main`: a landing antiga de maio/2026 (`index.html`, `styles.css`, `assets/hero/cripto-farol-hero.png`), `server.js`, `package.json`/`package-lock.json` da planilha, `scripts/create_beta_user.py` (criação de conta pela landing, proibida desde #689) e `variants/` (ficam no histórico do git). O `styles.css` e o `delta.css` do protótipo viram um arquivo só.

**Checkouts no host:** PROD em `/srv/apps/prod/criptofarol/landing/` e DEV em `/srv/apps/dev/criptofarol/landing/`, cada um com `repo/` (clone), `releases/<commit>/` (export do `site/` de um commit) e o link `current` → release publicada. O Caddy serve sempre `.../landing/current/site`.

**Como o Caddy serve (PROD, depois do corte):** um snippet `criptofarol_landing_routes` antes do `handle /api/*`:
- `@landingPages path / /privacidade /termos /robots.txt /sitemap.xml /favicon.ico /apple-touch-icon.png` → `file_server` com `try_files {path} {path}/index.html`, `Cache-Control: no-cache`;
- `/lp/*` → `file_server` com cache longo (D10);
- `/cripto-farol-landing/assets/*` e `/prototypes/cripto-farol-landing-v4/assets/*` → `redir` 301 para o arquivo equivalente em `/lp/` (pelo menos uma release); `/prototypes/cripto-farol-landing-v4/` → `/` continua;
- `@prodLandingHome` sai na fase F2 e `@prodLeadSubmit` na fase F4 (D2). O resto (`/api/*`, `/ingest/*`, downloads, SPA) fica igual.

**DEV para QA e homologação:** novo bloco `landing-dev.163.176.208.0.sslip.io` (resolve sem DNS, como os `dev.`/`prod.`/`clara-dev.` que já existem) com o mesmo snippet apontando para `/srv/apps/dev/criptofarol/landing/current/site`, `/api/*` para o backend DEV (`:8004`), as rotas do PostHog e `X-Robots-Tag: noindex, nofollow`. O DEV publica o commit da branch do card; QA e o Alan homologam ali. `dev.criptofarol.com.br/` continua sendo o app.

**Publicação e reversão:** `scripts/deploy.sh <dev|prod> <commit>` busca o repo, exporta `site/` do commit para `releases/<commit>/`, escreve `lp/posthog-config.js` com a chave do ambiente (só em commit que tem `site/privacidade/index.html`; no commit-base a chave fica vazia, como hoje), troca o link `current` (troca atômica), registra commit, data e quem publicou em `deploys.log` e confere por HTTP `/`, `/privacidade`, `/termos`, `/robots.txt`, `/lp/styles.css?v=` e `/lp/og-1200x630.jpg` (`image/jpeg`, a imagem do Open Graph só existe depois do corte). Reverter = `deploy.sh prod <commit do log>` (só troca o link). Não precisa recarregar o Caddy nem reiniciar serviço do `crypto`. A landing fica fora do `release-guard` do `crypto`; os commits publicados da landing entram na nota da release do `crypto` quando os dois sobem juntos (este card).

**`crypto` em dois PRs: primeiro acrescenta, depois remove.**
- **PR-1 `card-1160-landing-auditoria` → `develop`** (Apply, QA, homologação): tabela e migração, `POST /api/leads` com `step`, aviso por Telegram, testes. Não remove nada que a página antiga ou o Node usam: `GET /api/leads/stats`, a v4 em `frontend/public/prototypes/` e `ops/landing-leads/` ficam. Sobe na fase F3.
- **PR-2 `card-1160-landing-remocoes` → `develop`** (aberto no Apply, revisado junto no Code Review, mesclado só depois da fase F5 conferida): saem `frontend/public/prototypes/cripto-farol-landing-v4/`, `frontend/public/prototypes/cripto-farol-landing/` (assets usados em PROD e a primeira variante), `cripto-farol-landing-v3/`, `cripto-farol-landing-skill-v2/`, `frontend/public/posthog-config.js` (só a landing usava), `ops/landing-leads/`, `GET /api/leads/stats` e `BETA_TOTAL_SPOTS` (com o teste que os cobre), o padrão `ops/landing-leads/.env.leads` de `backend/app/services/beta_access.py` (P3) e os testes do frontend que leem a v4 (vão para `tests/` do repo da landing). `docs/landing-page.md` passa a apontar para o repo novo e a descrever o fluxo real (lead no banco, aviso por Telegram, sem e-mail). Sobe na fase F6. O protótipo deste card fica em `frontend/public/prototypes/card-1160-landing-auditoria/` e é autossuficiente (CSS, fontes e imagens copiados para a pasta), então não quebra com a remoção.

Por que separar (e não remover a v4 e o Node no mesmo deploy do backend, como no primeiro rascunho): (a) o deploy de PROD do `crypto` reinicia `criptofarol-prod-leads.service` (nota da release de 12/10/2026), e a unit roda `ops/landing-leads/server.js` do checkout de PROD; tirar o arquivo no mesmo deploy derrubaria o caminho do lead antes de o Caddy trocar; (b) com a v4 ainda no `dist`, a volta do Caddy funciona em todas as fases até F6; (c) com `/api/leads/stats` vivo até F6, o commit-base continua mostrando o contador durante o corte e no rollback, sem "--". O custo é um segundo deploy do `crypto` (sem migração) no mesmo fecho; se ele escorregar para o lote seguinte, nada quebra: a v4 só fica parada no `dist` sem ser servida.

**Ordem do corte em PROD (fases F0–F7, detalhe no Migration Plan):** F0 contagem só leitura → F1 publicar o commit-base no checkout da landing (ainda não servido) → F2 Caddy serve `/` e `/lp/` do checkout novo, **mantendo** `@prodLeadSubmit` → Node (mudança invisível) → F3 deploy do `crypto` com o PR-1 (backend novo + migração) e POST de conferência → F4 Caddy manda `/api/leads` direto ao backend, www → apex, cabeçalhos, Node desligado → F5 `deploy.sh prod <commit do delta>` e conferência real do formulário → F6 deploy do `crypto` com o PR-2 (remoções) → F7 Lighthouse e prévia no WhatsApp. Em nenhuma fase o formulário no ar fala com um backend que não entende o payload dele: até F3 a v4 passa pelo Node (planilha + backend antigo, como hoje); de F3 em diante o backend novo aceita o payload sem `step`; o delta só vai ao ar em F5, quando o Node já saiu e o backend novo está conferido.

**Apply em dois repos:** branches `card-1160-landing-auditoria` no `crypto` (PR-1) e no `cripto-farol-landing`, mais `card-1160-landing-remocoes` no `crypto` (PR-2). O PR da landing fica aberto durante QA e homologação (o DEV publica o commit da branch) e é mesclado em `main` na release, na fase F1. As mudanças no `/etc/caddy/Caddyfile` são do host (não versionadas) e seguem o padrão de cópia `Caddyfile.before-<motivo>-<data>` antes de editar, uma cópia por fase.

Alternativas rejeitadas (pelo Alan): pasta própria dentro do `crypto`; manter a landing em `frontend/public/prototypes/`.

### D13 — Produto atual: cripto, ações e ETFs, análise pronta, sinais do Monitor e alerta no Telegram (T6 do Alan)

Textos novos (protótipo; todos em DELTA; "(r2)" marca o que o rework r2 mudou):

| Onde | Antes (v4 / d1) | Depois (d2) |
|---|---|---|
| Rótulo do hero | "Beta fechado para investidores em cripto" | "Beta fechado · cripto, ações e ETFs da Binance" |
| Abertura do hero | "Leitura simples do mercado, com base no histórico real da moeda. Acesso gratuito por 6 meses." | "Leitura simples do mercado de cripto, ações e ETFs, com base no histórico real de cada ativo na Binance. Acesso gratuito por 6 meses." |
| Linha de confiança | "Integração segura" | (r2) "Alerta no Telegram nas estratégias com estrela" ("6 meses grátis" e "Histórico real da Binance" ficam) |
| Risco no hero | "… Cripto tem risco e nenhuma análise garante resultado." | "Apoio à decisão, não recomendação de investimento. Cripto, ações e ETFs têm risco, e nenhuma análise garante resultado." |
| Rotina | "parar de comprar e vender cripto no chute"; 01 "O painel separa BTC, ETH, SOL…"; 02 "Rode um teste no histórico real…" | "parar de comprar e vender no chute"; 01 "O Monitor junta as estratégias que você acompanha, de BTC e ETH a ações como NVDA e ETFs como SPY, e mostra quais estão em posição e quais já deram sinal de saída. (r2) Nas que você acompanha com estrela, o alerta também vai para o Telegram."; 02 "Abra a análise pronta da estratégia: o gráfico marca cada compra e cada venda no histórico real da Binance, para você ver como ela se saiu antes de seguir o sinal de hoje." |
| Benefício 01 | "Backtest no histórico da Binance" / "Teste qualquer estratégia…" | "Análise pronta de cada estratégia" / "Para cada estratégia que você acompanha, o backtest no histórico real da Binance já está feito: o gráfico marca todas as operações e as métricas mostram como ela se saiu." |
| Benefício 02 | "6 meses grátis para os primeiros do beta" | "Alerta no Telegram por estratégia" / (r2) "Conecte o Telegram no Perfil, e cada estratégia que você acompanha com estrela no Monitor avisa as entradas e as saídas, em cripto, ações e ETFs. O alerta já vem ligado, e você desliga estratégia por estratégia." |
| Sinais | "Os dois sinais" / "Dois sinais simples…"; "Sinal de Compra · Compra · …já sugere um ponto de saída…"; "Sinal de Venda · Venda" | "Os dois sinais" / "Dois estados simples, com os mesmos nomes do Monitor."; "Sinal de entrada · Em posição · A estratégia entrou. O Monitor mostra a entrada, o stop e quanto falta até ele, para você saber o risco que está correndo."; "Sinal de saída · Saída / cobertura · A estratégia saiu. Pode ser hora de vender, reduzir ou proteger o que você já tem." |
| FAQ 6 | "Funciona com outra exchange além da Binance?" | "Funciona com ações e ETFs?" / (r2) "Sim. Você acompanha cripto, ações e ETFs da Binance no Monitor, com a análise de cada estratégia. O alerta no Telegram vale para as estratégias que você acompanha com estrela, depois que você conecta o Telegram no Perfil; as estratégias de exemplo do catálogo aparecem no Monitor sem alerta. Ações e ETFs seguem o pregão de Nova York: com o mercado fechado, o aviso aparece só na tela. Comprar e vender pelo Farol vale só para cripto; ações e ETFs você acompanha e recebe o alerta, e a decisão de operar é sua, fora do Farol." |
| Exemplos de ativos | BTC … AVAX, POL | os mesmos + "NVDA · ação", "SPY · ETF", "QQQ · ETF" (os exemplos de verificação do #1117) |
| Risco do cadastro e do rodapé | "Investir em cripto envolve risco…" | "Investir em cripto, ações e ETFs envolve risco…" |

Decisões:

- **H1 fica "Comprar ou vender cripto? O Cripto Farol responde."** É o gancho de conversão, a v4 viva e um marco do gate do clone (`route-landmarks.yaml`, chave `landing`, cópia pinada do covenant-flow que o `crypto` não edita). A ampliação entra no rótulo, na abertura, na linha de confiança e no aviso de risco, todos visíveis na primeira tela. Trocar o H1 pede um card de motor para o catálogo (Open Question 10). O `og:title`/`twitter:title` não é marco do gate e passa a citar ações e ETFs no r2 (D9).
- **Sinais com os nomes do Monitor.** "Em posição" e "Saída / cobertura" são os rótulos do app desde o #718; o cartão de sinal deixa de prometer "ponto de saída sugerido" (era o alvo, que saiu no #803) e fala de entrada, stop e distância (#792). O rótulo pequeno ("Sinal de entrada"/"Sinal de saída") mantém a palavra "sinal" que o resto da página usa. O nome grande, mais longo que "Compra"/"Venda", ganha um tamanho próprio em `delta.css` (quebra "Saída /" e "cobertura" em duas linhas).
- **Alerta no Telegram com a frase honesta (Open Question 12, respondida pelo Alan em 29/10/2026: "Frase honesta na landing (Recommended)").** A landing mantém o Telegram, mas diz que o alerta vale para as estratégias que a pessoa acompanha com estrela (benefício 02, chip do hero, rotina 01, FAQ 6, descrição, OG e imagem OG) e que depende de conectar o Telegram no Perfil (benefício 02 e FAQ 6). O FAQ 6 diz com todas as letras que as estratégias de exemplo do catálogo aparecem no Monitor sem alerta. A landing não promete que a vitrine alerta; um card de produto separado (o pai cria) fará isso. Se esse card sair antes do Apply deste, o Apply tira a frase do catálogo do FAQ 6 e mantém o resto.
- **Sem frequência do alerta (decisão do Alan em 29/10/2026: "Não citar frequência"; Open Question 13).** A copy não diz quando o alerta sai e não sugere tempo real: nada de "na hora", "assim que" ou "em tempo real"; o benefício diz "avisa as entradas e as saídas" (a d2 dizia "avisa quando entra e quando sai"). O teste estático do Apply proíbe essas expressões (task 2.7).
- **Benefício do Telegram no lugar de "6 meses grátis".** A grade tem 4 colunas; "6 meses grátis" já aparece no hero, na linha de confiança, no subtítulo da seção ("Tudo isso liberado durante os 6 meses gratuitos."), no FAQ e no cadastro.
- **Ação e ETF: acompanhar e receber alerta, não operar.** Toda frase de compra e venda pelo Farol diz "cripto" (benefício 04, confiança 3, FAQ 2, 3 e 6, Termos 1 e 5). O alerta nunca diz que envia ordem.
- **Termos:** item 1 descreve cripto, ações e ETFs da Binance (ação e ETF só acompanhados), item 3 o risco das três classes e que o alerta não envia ordem, item 5 "comprar e vender cripto à vista", item 6 o pregão de Nova York. **Política:** não muda; a ampliação não muda o que o formulário e o PostHog coletam.
- **Campos do formulário** ("Nível com cripto", "Sua maior dificuldade hoje com cripto") não mudam (Open Question 11).

## Risks / Trade-offs

- [O corte troca quem serve `/` e quem recebe o lead em PROD] → fases F0–F7 (D12 e Migration Plan): cada fase muda uma coisa, tem conferência e volta própria; o formulário no ar nunca fala com um backend que não entende o payload dele; a remoção da v4, do Node e de `/api/leads/stats` só vem em F6, com a página nova conferida.
- [F3–F4: Node e backend novo gravando o mesmo lead] → por alguns minutos o Node grava na planilha e repassa ao backend novo, que salva o lead e avisa o Alan; é o comportamento de hoje mais o banco. F4 vem logo depois do POST de conferência de F3.
- [Rollback da landing depois de F6] → o commit-base volta a v4, mas `/api/leads/stats` já saiu e o contador mostra "--". Aceito: é rollback de emergência, com a página nova já conferida em F5; se precisar durar, publica-se um commit de correção.
- [Dois deploys do `crypto` no mesmo fecho (F3 e F6)] → F6 é sem migração e só remove; pode ir no lote seguinte sem quebrar nada.
- [Cabeçalhos valem para o app também] → só `nosniff`, `Referrer-Policy`, `frame-ancestors` e HSTS sem subdomínios; nenhum deles muda comportamento do app; o QA confere `/login` e o Monitor depois do corte.
- [HSTS fixa HTTPS por 1 ano no navegador] → o domínio já é só HTTPS pelo Caddy; sem `includeSubDomains`, os outros hosts não são afetados.
- [Aviso só por Telegram] → se o Alan desvincular o Telegram, o lead continua salvo no banco; o log registra "sem destino". F0 confere que o admin tem `telegram_chat_id` em PROD.
- [Mais dado pessoal no banco (WhatsApp, texto livre)] → só os campos que o formulário pede, descritos na Política; prazo de guarda proposto na Política; nada disso vai para o PostHog.
- [Projeto do PostHog compartilhado com o app] → o init da landing desliga gravação de sessão e pesquisas (D5); a Política descreve só o que a landing manda.
- [Dois repos no mesmo card] → o Code Review e o QA do card precisam cobrir o diff dos três PRs (landing, PR-1 e PR-2 do `crypto`); o pai materializa os intervalos no patch da revisão (P3 de processo).
- [Catálogo do gate aponta para a v4] → `scripts/process-fsm/route-landmarks.yaml` (`landing.source`) é cópia pinada do covenant-flow e não pode ser editada no `crypto`. O gate só usa os textos e seletores da entrada (o H1, o CTA "Quero meus 6 meses grátis", `.faq-section`, `.button-primary`, que este card mantém); o campo `source` fica velho depois de F6. Precisa de um card de motor no covenant-flow para apontar para o repo da landing (fora deste card).
- [Prints de clones, não do DEV logado] → o Monitor vem do clone homologado do #1122 e a análise da captura viva guardada no clone do #1119; são amostra com a forma do produto de hoje. Recaptura do DEV logado no Apply (P3, task 2.10), se o Alan cadastrar a credencial (Open Question 8).
- [Limpeza feita no DOM e na imagem] → nada de dado é inventado: só some o que não é lista ou gráfico, os números passam para o formato BR, os rótulos de parâmetro perdem o número e dois rótulos sobrepostos são afastados. A lista das mudanças está em D8.
- [Gráfico sem linha de stop] → a análise do app não desenha stop; o stop aparece no print do Monitor. O "Abrir Gráfico" com "Compra" e "STOP" fica para o Apply se o Alan quiser (Open Question 9).
- [H1 continua falando só de cripto] → a primeira tela fala de cripto, ações e ETFs no rótulo, na abertura, na linha de confiança e no aviso; o H1 é marco do gate pinado (Open Question 10).
- [Ação e ETF acompanhados, não operados] → toda frase de compra e venda diz "cripto"; o FAQ 6 diz isso com todas as letras.
- [Quem entra pelo beta vê só a vitrine do catálogo, que não alerta, e não tem como criar estratégia própria (Produto atual; Open Question 12)] → frase honesta (D13): o alerta vale para as estratégias acompanhadas com estrela, depende do Telegram conectado no Perfil, e as estratégias de exemplo do catálogo aparecem sem alerta; nada promete que a vitrine alerta. Até o card de produto da vitrine sair, a pessoa da leva lê o benefício e não o recebe sem uma estratégia própria; o FAQ 6 deixa isso explícito. Se o card da vitrine sair antes do Apply, o Apply tira a frase do catálogo.
- [Print do Monitor com "Alerta: ligado"] → é o cartão de uma estratégia própria com estrela, como o app mostra; a copy ao redor diz "estratégias com estrela". O print não mostra a vitrine.
- [Frequência do alerta fora da copy (Open Question 13)] → o scan sai uma vez por dia (08:05 BRT); a copy não cita frequência e não sugere tempo real (sem "na hora", "assim que", "em tempo real"); o teste estático do Apply proíbe essas expressões.
- [Detector do Impeccable] → acusa Inter/JetBrains Mono (`overused-font`, `design-system-font`) e as cores da v4 (`#07121d`, `rgba(4, 28, 48, .58)`, `rgba(242, 201, 91, .24)`, `0.92rem`) como fora do `DESIGN.md`; o `DESIGN.md` é o sistema do app, e esses valores são da paleta e das fontes da landing (`docs/brand-system.md`), já na v4. Não é desvio novo. `side-tab` em `styles.css` (`.risk-note`) é da v4.
- [Detector Impeccable na d2: `design-system-font-size` em `.signal-card strong` (`clamp(2.4rem, 5vw, 4.4rem)` e `clamp(2rem, 10vw, 2.6rem)`)] → mesmo caso das fontes e cores da v4: o `DESIGN.md` é o sistema do app; a v4 usa `clamp(3rem, 8vw, 6.8rem)` nesse mesmo elemento. O tamanho novo só existe porque "Saída / cobertura" é mais longo que "Venda". Não é desvio novo.
- [`side-tab` novo em `.hero-risk` (`delta.css`, borda lateral dourada de 3 px)] → **aceito e mantido**: repete de propósito a `.risk-note` da v4, o aviso de risco do cadastro, para os dois avisos de risco da página terem a mesma marca visual. Trocar só o do hero criaria dois estilos para a mesma coisa; trocar os dois mexe na v4 sem pedido do card.

### P3 aceitos (detalhe de Apply)

Do primeiro autor:

- Nome da tabela e das colunas de `landing_leads`, índice único por e-mail normalizado, e se o passo 2 identifica o lead pelo e-mail ou por um `lead_ref` opaco devolvido no passo 1 (o protótipo manda os dois).
- Texto exato das mensagens do Telegram (os de D3 são a base) e como achar os admins (papel de admin no banco ou `ADMIN_EMAILS`).
- `BackgroundTasks` do FastAPI ou fila para o aviso; tempo limite do envio.
- Limite de tamanho e limpeza dos campos (os mesmos da `LeadAccessRequest` de hoje).
- Formato do `?v=` dos assets e do `deploys.log`; `try_files` e barra final em `/privacidade/` → 301 para `/privacidade`.
- Fonte da chave do PostHog no deploy (`VITE_POSTHOG_KEY` do `frontend/.env.local` de PROD ou um segredo próprio no bws).
- AVIF opcional do hero.
- Recaptura dos prints a partir do DEV, se o Apply preferir (mesmas regras de D8).
- Estilo do protótipo em dois arquivos (`styles.css` da v4 + `delta.css`) vira um só no repo da landing.
- Mapeamento arquivo a arquivo dos redirects dos caminhos antigos para `/lp/`.
- Achados do detector Impeccable em fontes e cores da v4 (Risks).

Da dupla (onda 1160-d1), aceitos neste rework:

- **Prototype Validation desatualizada** (A): resolvido neste rework; a URL pública responde 200 com o mesmo sha do worktree (seção Prototype Validation).
- **`og:image` só existe depois do corte** (B): `https://criptofarol.com.br/lp/og-1200x630.jpg` hoje cai no fallback da SPA; o `deploy.sh` confere `/lp/og-1200x630.jpg` como `image/jpeg` (somado à lista de URLs dele) e F7 passa o link num validador de prévia.
- **Protótipos antigos de landing depois de F6** (A): `/prototypes/cripto-farol-landing/`, `/prototypes/cripto-farol-landing-v3/` e `/prototypes/cripto-farol-landing-skill-v2/` virariam o shell da SPA (200); o Caddy de PROD responde 301 para `/` (ou 410) nesses caminhos, junto com o redirect que já existe para a v4.
- **`$pageview` manual** (A): com `capture_pageview: false`, a landing chama `posthog.capture("$pageview")` com o endereço sem parâmetros, para cumprir o spec `product-analytics`.
- **`role=alert` no erro** (A): a mensagem de erro passa a `role=alert` (ou o campo ganha `aria-describedby`); o sucesso fica no `role=status`.
- **Rótulos do eixo do gráfico** (A): o eixo mostra "2" entre "fev." e "abr." (deveria ser "mar.") e o recorte do celular corta "Venda"/"Compra" na borda esquerda; refazer na recaptura dos prints. (d2: o gráfico saiu; o print novo da análise tem o eixo e os rótulos inteiros.)
- **`data-cta` nas páginas legais** (A): o CTA da navegação e do rodapé de `/privacidade` e `/termos` tem `data-cta` sem script; o Apply carrega ali o mesmo script de eventos de CTA (sem formulário).
- **favicon e apple-touch-icon** (B): o protótipo tem só o SVG; o Apply gera `favicon.ico` (16/32/48) e `apple-touch-icon.png` (180) da marca (D9, task 2.5).
- **`landing.source` do catálogo** (A e B): card de motor no covenant-flow (Risks; task 4.5); `design_clone_gate.py` sem CLI também é do motor.
- **Mensagem "Pronto, seu cadastro está salvo."** repete o título do passo 2 e fica abaixo dos botões (A e B): o Apply pode deixar só o título (o foco já vai para ele).
- **Passo 2 enviado vazio** pode virar "pular" sem request (A).
- **Linha de consentimento acima do botão** (ler antes de enviar) (A): o Apply decide a posição sem mudar o texto.
- **Links da v4 na navegação com 36 px acima de 920 px** (A): fora do delta; até 920 px o CTA tem 44 px.
- **Commit-base na DEV**: a v4 manda o lead para `:5174` em host que não é `criptofarol.com.br`; o commit-base só é publicado em PROD (F1), a DEV homologa o commit do delta.
- **Unit do Node depois de F4**: apagar `criptofarol-prod-leads.service` (e drop-ins) do systemd e da lista de serviços que o deploy de PROD reinicia e confere, antes de F6.
- **`beta_access.py`** usa `ops/landing-leads/.env.leads` como padrão do `BETA_ACCESS_GOG_ENV_FILE`; o PR-2 troca o padrão ou exige a variável (spec `maintenance` muda junto, se for o caso).
- **Licença das fontes** (OFL) no `README` do repo da landing.

Do autor da d2 (devolução do T6):

- **Recapturar os prints do DEV logado no Apply** (task 2.10): Monitor em cartões e análise de uma estratégia acompanhada, com as regras de limpeza de D8; sem credencial do DEV no cofre, ficam os prints do protótipo (Open Question 8).
- **"Abrir Gráfico" do Monitor** com as linhas "Compra" e "STOP" como print extra ou no lugar da análise, se o Alan quiser (Open Question 9).
- **Faixa escura sob "COMPRA" e "VENDA (-5,18%)"** no gráfico encobre ~150 px da média curta; some na recaptura (o gráfico vivo sobrepõe os dois rótulos nesse dia).
- **Exemplos de ação e ETF** (NVDA, SPY, QQQ): o Apply confere que seguem no catálogo da Binance na data do corte.
- **`fetchpriority`/`loading`** do print do Monitor no hero (acima da dobra no desktop, abaixo dos CTAs no celular).

Da dupla (onda 1160-d2). Resolvidos no r2 (baratos e visíveis):

- **Textos herdados que destoavam** (A): confiança 1 dizia "grupo de Telegram" ao lado do benefício do Telegram (agora "grupo de sinais"); confiança 2 dizia "não precisa interpretar… médias móveis" com a análise mostrando médias (agora "O Monitor diz em palavras…; o gráfico fica para quando você quiser conferir"). A política Q3=A não muda (D7).
- **"O Monitor está lá no topo."** soava interno (A): agora "Além do Monitor que você viu acima, …" (D7).
- **`og:title` e `og:image:alt` só com cripto** (B): `og:title`/`twitter:title` citam ações e ETFs; `og:image:alt` descreve a frase da imagem (D9).
- **Linhas longas nos avisos do delta** (B, detector de navegador): `max-width: 62ch` em `.hero-risk` e `.form-consent` e `64ch` em `.footer-risk` (`delta.css`).
- **Borda direita dos cartões cortada no print do Monitor** (B): a recaptura do r2 (board de 340 px, elemento inteiro) já mostra a borda; a recaptura do Apply confere de novo.

Ficam para o Apply:

- **Imagem OG em Inter** (B): a OG foi desenhada em DejaVu; regerar com a fonte da marca junto da recaptura (task 2.10).
- **Análise de desktop com ≥ 1000 px** (A): a 1440 px a análise aparece a 978 px a partir de 848 px naturais (1,15×, levemente borrada); gerar a versão de desktop com ≥ 1000 px na recaptura ou limitar a largura da figura.
- **`loading`/`fetchpriority` do print do Monitor** (B): a 390 px ele carrega de saída abaixo da dobra (+32 KB no primeiro carregamento); já listado acima.
- **Recaptura da conta do Alan** (A): a conta é admin e o Monitor abre em "Em portfólio"; a recaptura usa o filtro "Todos" e só estratégias próprias, sem mostrar o que o beta não vê, e segue a regra de prints coerentes entre si (D8, task 2.10).
- **"split" na linha de configuração do print** (A): jargão do app; fica por fidelidade ao cartão; a recaptura pode cortar a linha.
- **Achados do detector herdados** (B): `overused-font` (`delta.css`), `side-tab` (`styles.css:637` da v4 e `.hero-risk`, aceito em Risks); os de navegador são da v4.
- **`/lp/og-1200x630.jpg` em PROD responde `text/html` até o corte** (B): já coberto (o `deploy.sh` confere `image/jpeg`).
- **Ferramentas do motor e do ambiente** (B): `detect.mjs` por URL sem `puppeteer` no host; `design_clone_gate.py` sem CLI e com `parse_live_route` que captura a linha seguinte como justificativa (o `\s+` atravessa a quebra de linha); card de motor, fora deste card.

## Migration Plan

1. **Apply (Em desenvolvimento):** no `cripto-farol-landing`, o commit-base (v4 sem delta, caminhos `/lp/`) e depois o delta, `deploy.sh` e testes; no `crypto`, o PR-1 (backend + migração + testes) e o PR-2 (remoções) abertos; no host DEV, clone em `/srv/apps/dev/criptofarol/landing/`, deploy da branch e bloco `landing-dev.163.176.208.0.sslip.io` no Caddy.
2. **QA e homologação no DEV:** `https://landing-dev.163.176.208.0.sslip.io/` com o backend DEV (`develop` com o PR-1).
3. **Corte no fecho da release (PROD), nesta ordem.** Cada fase só começa com a anterior conferida.

   | Fase | O que muda | Conferência | Rollback desta fase |
   |---|---|---|---|
   | F0 | Nada (só leitura): contar linhas da planilha do Node e leads auditados desde 08/06/2026; conferir `telegram_chat_id` do admin em PROD | números na nota da release | — |
   | F1 | Merge do PR da landing em `main` (sem squash); clone em `/srv/apps/prod/criptofarol/landing/repo`; `deploy.sh prod <commit-base>` (ainda não servido) | `releases/<commit-base>/site/index.html` igual à v4 a menos dos caminhos | apagar o link `current` (nada é servido dali) |
   | F2 | Cópia `Caddyfile.before-landing-f2-<data>`; Caddy serve `/`, `/lp/*` e as páginas raiz do checkout novo; redirects dos assets antigos para `/lp/`; sai `@prodLandingHome`; **`@prodLeadSubmit` → Node continua** | `/` = commit-base; assets `/lp/` 200; contador com número; `/login`, `/ingest` | voltar a cópia F2 e `caddy reload` (a v4 segue no `dist`) |
   | F3 | Deploy do `crypto` com o PR-1 (backend novo + migração; `docs/prod-migration-runbook.md`); o deploy reinicia o Node como sempre (os arquivos dele seguem no checkout) | health; **POST de conferência** pelo caminho público com o e-mail do Alan e o payload da v4 (sem `step`): 202, lead em `landing_leads` com todos os campos, aviso no Telegram | rollback do `crypto` de costume (commit anterior + downgrade da migração; a tabela nova some, nada antigo muda) |
   | F4 | Cópia `Caddyfile.before-landing-f4-<data>`; sai `@prodLeadSubmit` (`/api/leads` vai ao backend); `www` → apex 308; cabeçalhos de D11; `systemctl disable --now criptofarol-prod-leads.service` | POST sem `step` direto ao backend: 202, lead salvo, aviso; `www`; cabeçalhos; `/login`; `/ingest`; Monitor | voltar a cópia F4, `caddy reload` e `systemctl enable --now criptofarol-prod-leads.service` (o código do Node ainda está no checkout) |
   | F5 | `deploy.sh prod <commit do delta>` | páginas, `robots.txt`, `sitemap.xml`, ícones, `/lp/og-1200x630.jpg` `image/jpeg`; formulário real com o e-mail do Alan: passo 1 (lead + aviso "novo"), passo 2 (mesmo lead + aviso "completou"), Enter no passo 1; eventos no PostHog | `deploy.sh prod <commit-base>` (o backend novo aceita o payload sem `step`; o contador ainda funciona) |
   | F6 | Unit do Node apagada do systemd e da lista do deploy; merge do PR-2 e deploy do `crypto` (sem migração) | `/api/leads/stats` fora; caminhos antigos 301; `/`, `/login`, health | rollback do `crypto` para o commit de F3 (sem migração) |
   | F7 | Nada | Lighthouse móvel em `https://criptofarol.com.br/` (Performance ≥ 90, SEO ≥ 95); link colado no WhatsApp com imagem, título e descrição; commits da landing e do `crypto` na nota da release | — |

## Open Questions

Juízos do Alan para o T7. Nenhum bloqueia a submissão ao T7; as respostas entram com a aprovação, e o Apply não fecha a task 2.4 sem a resposta da 1.

1. **Controlador e canal do titular.** A Política precisa dizer quem trata os dados e por onde a pessoa pede acesso, correção ou exclusão (LGPD). O rascunho deixa os dois trechos do item 7 marcados como pendentes ("⟨controlador: …⟩", "⟨canal do titular: …⟩"). **Recomendação:** controlador identificado só dentro da Política (o rodapé segue sem nome nem contato, como o Alan decidiu); canal = um e-mail do domínio só para pedidos de titular, que o Alan escolhe.
2. **Leads antigos e quem dependia do Node.** A planilha local do Node e a cópia no Drive da Clara têm dado pessoal coletado sem Política; com o Node fora, somem também o aviso no tópico do grupo do Telegram e o e-mail ao Alan. **Recomendação:** não importar para `landing_leads`; contar em F0, arquivar a planilha fora do checkout com acesso só de root até o prazo de guarda e apagar a cópia do Drive da Clara; o Alan confirma que a Clara e o grupo não dependem da planilha nem do tópico.
3. **Prazo de guarda.** **Recomendação:** o do rascunho, "enquanto o beta fechado estiver aberto e por até 6 meses depois do fim dele, ou até a pessoa pedir para apagar".
4. **Qual família de fonte sai** (Entra 9: no máximo 2). Hoje são três: Inter (títulos), IBM Plex Sans (texto corrido) e JetBrains Mono (números). **Recomendação:** sai a IBM Plex Sans e o texto corrido passa a Inter (já carregada para os títulos); `docs/brand-system.md` muda junto. A alternativa é sair a Inter e os títulos virarem Plex.
5. **Regras novas nos textos legais.** "O beta é para maiores de 18 anos" (Política, item 9) e "se não assinar, o acesso termina" (Termos, item 4) não estão no issue. **Recomendação:** manter as duas; se a de 18 anos ficar, ela entra também nos Termos (item 4) no Apply.
6. **Linha do formulário.** Hoje: "Ao enviar, você concorda com a Política de Privacidade." (texto do issue). **Recomendação:** só a Política; os Termos passam a valer "ao usar" a página (rascunho já ajustado), sem aceite no formulário.
7. **Base legal do formulário.** O rascunho usa consentimento dado ao enviar (LGPD, art. 7º, I); a alternativa é procedimento preliminar a pedido do titular (art. 7º, V). **Recomendação:** manter consentimento; a revisão jurídica, fora do card, pode trocar.

Novas na d2 (devolução do T6):

8. **Credencial do DEV para os prints da conta real.** Não há credencial do DEV no cofre de segredos (bws), então os prints da d2 saem dos clones homologados (D8). **Recomendação:** cadastrar no bws a senha da conta do Alan no DEV (o DEV é usado com essa conta para QA) para o Apply recapturar o Monitor e a análise do DEV logado (task 2.10); sem isso, os prints do protótipo vão para produção como estão.
9. **Linha de stop no gráfico.** A análise do app não desenha stop; só o "Abrir Gráfico" do Monitor desenha "Compra" e "STOP". **Recomendação:** ficar com a análise (operações marcadas, que é o que o T6 pede para o backtest) e com o stop no print do Monitor; se o Alan quiser a linha de stop no gráfico, o Apply troca o print do produto pelo "Abrir Gráfico" recapturado do DEV.
10. **H1 só com cripto.** O H1 "Comprar ou vender cripto? O Cripto Farol responde." fica (é o gancho da v4 e marco do gate do clone). **Recomendação:** manter; a ampliação aparece no rótulo, na abertura, na linha de confiança e no aviso, na primeira tela. A alternativa ("Comprar ou vender? O Cripto Farol responde.") pede um card de motor no covenant-flow para o catálogo do gate.
11. **Campos do formulário com "cripto".** "Nível com cripto" e "Sua maior dificuldade hoje com cripto" seguem como estão. **Recomendação:** manter neste card (o T6 não pede e a Política descreve esses campos); trocar para "investimentos" pede um ajuste da Política junto.

Respondidas pelo Alan no r2 (ferramenta do host, 29/10/2026):

12. **Alerta para quem entra pelo beta.** *Respondida:* "Frase honesta na landing (Recommended)". A conta nova vê só a vitrine do catálogo, que não alerta, e não tem como criar estratégia própria (Produto atual). A landing mantém o Telegram e diz que o alerta vale para as estratégias que a pessoa acompanha com estrela, com o Telegram conectado no Perfil; um card de produto separado (o pai cria) fará a vitrine alertar. Aplicado em D13, D9, nos specs e no protótipo.
13. **Frequência do alerta na copy.** *Decidida:* "Não citar frequência". A copy não diz quando o alerta sai e não sugere tempo real (D13).

Abertas para o T7: 1 (controlador e canal do titular; o texto da Política tem as lacunas ⟨…⟩), 2 (precisa de resposta antes de F0/F4), 3 a 11 (padrão = recomendação).

## Apply contract

O Apply lê este `design.md`, os specs do change e os HTML de `frontend/public/prototypes/card-1160-landing-auditoria/` como spec de layout e texto. Os textos legais saem da aprovação do Alan no T7 (com a resposta das Open Questions); a faixa "Rascunho para o Alan aprovar" do protótipo não vai para produção.

**Contrato visível (não P3):**

- Hero: H1 e CTA como hoje; rótulo, abertura e linha de confiança de D13 (cripto, ações e ETFs; "Alerta no Telegram nas estratégias com estrela"); CTA com `data-cta="hero"`; frase de risco de D13 depois da linha de confiança; hero em WebP responsivo; print do Monitor em cartões (Em posição e Saída / cobertura, tempo gráfico, Alerta ligado e desligado, uma ação ou um ETF ao lado de cripto, stop e entrada, preço BR, sem nome de conta nem parâmetro de estratégia), legível a 1440 e 390 (de ponta a ponta até 560 px), com o texto alternativo do protótipo (r2: SPY e ETH/USDT).
- **Prints coerentes entre si:** um ativo que aparece no Monitor e na análise conta a mesma história (estado, entrada, último preço, tempo gráfico); no protótipo, SPY no Monitor e NVDA na análise (D8).
- **Texto efetivo ≥ 11 px nos dois prints a 390 px** (menor fonte do print × largura renderizada ÷ largura natural): assert do browser gate do Design (Prototype Validation) e do Playwright do Apply (task 5.2).
- Navegação: "Entrar na lista" (primeiro item e alvo de pelo menos 44 px até 920 px).
- Rotina 01 e 02 de D13 (01 com o alerta nas estratégias com estrela).
- Produto: só a análise (operações marcadas, sem alvo, sem controles de desenvolvedor, preço BR), com recorte até 560 px (o recorte de 348 px de D8, ou outro com texto efetivo ≥ 11 px a 390); abertura ("Além do Monitor que você viu acima…") e legenda de D7.
- Benefícios: 01 análise pronta e 02 alerta no Telegram por estratégia com a frase honesta (estratégias com estrela, Telegram conectado no Perfil, ligado por padrão, desligável por estratégia; D13); lista de métricas com explicação visível; benefício 04 com "cripto".
- Alerta: nenhuma promessa de que a vitrine do catálogo alerta; nenhuma frequência; nenhum "na hora", "assim que" ou "em tempo real" (Open Questions 12 e 13).
- Sinais: "Em posição" e "Saída / cobertura" com os textos de D13; nenhum "alvo".
- Confiança 1–3 e FAQ 1–3 com os textos de D7; FAQ 6 "Funciona com ações e ETFs?" de D13 (alerta nas estratégias com estrela, Telegram no Perfil, catálogo sem alerta); JSON-LD = FAQ visível; nenhum "Operar", "Home", "Spot Trade", "Teste qualquer estratégia" ou "outra exchange"; política Q3=A mantida; toda compra e venda pelo Farol dita como de cripto.
- Cadastro: chamada, frase de levas, POL e os exemplos NVDA · ação, SPY · ETF e QQQ · ETF, aviso de risco com ações e ETFs, botão e consentimento do passo 1 (link da Política em nova aba com `rel="noopener"`), passo 2 opcional com "Pular esta etapa", estado final e erros de D4; nenhum número de cadastrados ou vagas, nenhum "--".
- **Enter no passo 1 = "Entrar na lista do beta"**: valida, salva o passo 1 (com nome), mostra o passo 2; nunca envia o passo 2. Coberto por teste no repo da landing (task 2.7) e no Playwright do card (task 5.2).
- Foco depois do passo 1 no título do passo 2 (`tabindex=-1`); foco no estado final.
- Rodapé de D6 (aviso com ações e ETFs), nas três páginas; `/privacidade` e `/termos` com os textos aprovados (controlador e canal do titular dentro da Política; Termos com ação e ETF só acompanhados).
- Fontes servidas de `/lp/fonts/` (Inter + JetBrains Mono), nenhum pedido ao Google Fonts.
- Metadados de D9 (título, descrição, `og:title`, `og:description` e `og:image:alt` com cripto, ações e ETFs e a frase honesta do alerta), `robots.txt`, `sitemap.xml`, ícones, imagem OG da d2.
- Comportamentos dos specs: lead no passo 1, enriquecimento sem duplicar, campos guardados, resposta neutra, aviso por Telegram (novo e passo 2), `/api/leads/stats` fora (F6), eventos do funil sem dado pessoal, PostHog carregando em PROD sem gravação de sessão nem pesquisas, `$pageview`, www → apex, cache, fontes, cabeçalhos, Lighthouse, landing servida do repo novo, DEV com `noindex`, deploy e rollback próprios, corte por fases sem perder lead, caminhos antigos redirecionados.

**P3 aceito (Apply):** os itens da subseção "P3 aceitos" em Risks / Trade-offs.

## Textos para aprovação (T7)

Os textos completos estão nas páginas do protótipo (`privacidade.html`, `termos.html`) e são cópia do que segue. Descrevem só o que o formulário coleta, o que o PostHog grava e quem recebe dados (D1, D3, D5, D10); revisão jurídica fora do card. Os trechos entre ⟨ ⟩ são pendentes do Alan (Open Question 1); nenhum dado foi inventado.

### Aviso de risco

- **Hero (d2):** "Apoio à decisão, não recomendação de investimento. Cripto, ações e ETFs têm risco, e nenhuma análise garante resultado."
- **Rodapé (d2):** "O Cripto Farol é uma ferramenta de apoio à leitura de mercado e não faz recomendação de investimento. Investir em cripto, ações e ETFs envolve risco de perda. Resultados passados, inclusive de backtest, não garantem resultados futuros. Quem decide é sempre você."
- **Cadastro (v4, ampliado na d2):** "O Cripto Farol é uma ferramenta de apoio à leitura de mercado. Mostramos, sugerimos e organizamos; quem decide é sempre você. Investir em cripto, ações e ETFs envolve risco e nenhuma análise garante resultado."
- **Formulário:** "Ao enviar, você concorda com a Política de Privacidade." (link em nova aba; Open Question 6)

### Política de Privacidade (rascunho)

Atualizada em 29/10/2026. Esta política explica quais dados o Cripto Farol coleta nesta página (criptofarol.com.br), para que usa e como você pode pedir para ver, corrigir ou apagar seus dados. Ela cobre só a página pública e o formulário do beta.

1. **O que coletamos no formulário do beta.** Passo 1 (obrigatório): nome e e-mail. Passo 2 (opcional): WhatsApp, seu nível com cripto e sua maior dificuldade hoje com cripto (texto livre). De onde você veio: se o link tiver parâmetros de campanha (utm_source, utm_medium, utm_campaign, utm_content, utm_term), o endereço da página que trouxe você até aqui (sem parâmetros), o caminho da página em que você entrou e a data da primeira visita; esses dados ficam guardados no seu navegador (armazenamento local, chave `criptofarol_attribution`) e seguem junto com o cadastro. Não pedimos CPF, senha, dados bancários nem chaves da Binance nesta página.
2. **O que medimos sobre o uso da página.** Usamos o PostHog para entender quantas pessoas visitam a página e em que ponto do cadastro elas param. Quando a medição está ligada, o PostHog guarda um identificador aleatório no armazenamento local do seu navegador e registra: a visita à página, com o endereço sem parâmetros nem fragmentos; cliques nos botões de cadastro (no topo, na navegação e no rodapé); início, conclusão ou falha de cada passo do formulário; os parâmetros de campanha e só o domínio do site que trouxe você; dados técnicos do navegador e da conexão, como tipo de navegador, sistema, tamanho da tela e endereço IP. Esses eventos não levam seu nome, e-mail, WhatsApp nem as respostas do formulário. Nesta página, o PostHog fica sem gravação de sessão e sem pesquisas. O PostHog é uma empresa dos Estados Unidos, então esses dados são processados fora do Brasil.
3. **Para que usamos.** Chamar você quando abrir a próxima leva do beta fechado, por e-mail ou WhatsApp (se você informou); entender o perfil de quem se inscreve (nível e dificuldade) para decidir quem chamar em cada leva; medir onde o cadastro trava e melhorar esta página. Não vendemos seus dados e não os usamos para propaganda de terceiros.
4. **Com quem compartilhamos.** PostHog: só os dados de medição do item 2. Telegram: a cada cadastro, a equipe do Cripto Farol recebe um aviso interno pelo Telegram com os dados do formulário, para poder responder rápido; o Telegram é um serviço de fora do Brasil, então esse aviso também é uma transferência internacional de dados. As fontes, as imagens e os arquivos desta página vêm do próprio site do Cripto Farol, sem serviço de terceiros. Fora o que está acima, só compartilhamos dados se a lei ou uma autoridade exigir.
5. **Base legal.** Tratamos os dados do formulário com o seu consentimento, dado ao enviar o cadastro (LGPD, art. 7º, I). A medição de uso da página se apoia no nosso legítimo interesse de melhorar o site (LGPD, art. 7º, IX), sem identificar você pelo nome ou e-mail. (Open Question 7)
6. **Por quanto tempo guardamos.** Guardamos o cadastro enquanto o beta fechado estiver aberto e por até 6 meses depois do fim dele, ou até você pedir para apagar, o que vier primeiro. (Open Question 3)
7. **Quem cuida dos seus dados e seus direitos.** O responsável pelo tratamento dos seus dados (controlador, na LGPD) é ⟨controlador: nome e identificação, o Alan define no T7⟩. Você pode pedir a confirmação de que tratamos seus dados, o acesso a eles, a correção, a exclusão e a revogação do consentimento (LGPD, art. 18). Para isso, escreva para ⟨canal do titular: o Alan define no T7⟩. Respondemos em até 15 dias. Para limpar o que fica no seu navegador, apague os dados deste site nas configurações do navegador.
8. **Segurança.** Os dados do formulário ficam no servidor do Cripto Farol, com acesso restrito à equipe. A página só funciona por conexão segura (HTTPS).
9. **Menores de idade.** O beta é para maiores de 18 anos. Não coletamos dados de menores de propósito. (Open Question 5)
10. **Mudanças nesta política.** Se esta política mudar, a data no topo muda junto. Mudanças que afetem o uso dos seus dados serão avisadas nesta página.

### Termos de Uso (rascunho)

Atualizados em 29/10/2026. Estes termos valem para quem usa esta página e, para quem for chamado para o beta, para o uso do Cripto Farol. Ao usar, você concorda com eles. Leia com calma; são curtos de propósito.

1. **O que é o Cripto Farol.** Uma ferramenta de apoio à leitura do mercado de cripto e de ações e ETFs negociados na Binance. Ela mostra quando cada estratégia que você acompanha está em posição ou em saída, a análise dessas estratégias no histórico da Binance (backtest) com métricas, avisos no Telegram e, se você quiser, acompanha sua carteira na Binance. Ações e ETFs são só acompanhados: o Farol não compra nem vende ações e ETFs. (d2)
2. **Não é recomendação de investimento.** O Cripto Farol não é consultoria de investimentos e não faz recomendação personalizada. Os sinais e as métricas são informação para apoiar a sua decisão. Quem decide comprar, vender ou ficar parado é sempre você, e a decisão é sua responsabilidade.
3. **Risco.** Cripto, ações e ETFs têm risco, e a cripto tem alta volatilidade: você pode perder parte ou todo o valor investido. Resultados passados, inclusive os de backtest, não garantem resultados futuros. Nenhuma análise garante resultado. Um alerta é só informação: ele não envia ordem. (d2)
4. **Beta fechado.** O acesso é liberado em levas; entrar na lista não garante vaga nem data de entrada. Quem for chamado usa o Cripto Farol de graça por 6 meses, sem cartão e sem cobrança automática. Depois desse período, você decide se quer assinar; se não assinar, o acesso termina (Open Question 5). Por ser beta, o produto pode mudar, ter falhas ou ficar fora do ar.
5. **Sua conta na Binance.** O Cripto Farol nunca pede a senha da sua Binance e nunca faz saque. Para acompanhar a carteira, você cria uma chave de leitura na Binance. Se quiser comprar e vender cripto à vista pelo Farol, libera também essa permissão; cada ordem só sai depois que você confirma. Você é responsável pelas chaves que cria e pode apagá-las na Binance a qualquer momento.
6. **Dados de mercado.** Os preços e o histórico vêm de terceiros, como a Binance, e podem atrasar, falhar ou conter erros. Ações e ETFs seguem o horário do pregão de Nova York. Confira o preço na corretora antes de qualquer ordem.
7. **Uso aceitável.** Não tente acessar contas de outras pessoas, sobrecarregar o serviço, copiar o conteúdo em massa ou usar o Cripto Farol para algo ilegal. Se isso acontecer, o acesso pode ser encerrado.
8. **Limite de responsabilidade.** O Cripto Farol não responde por ganhos ou perdas das suas decisões de investimento, nem por falhas da Binance ou de outros terceiros.
9. **Privacidade.** O uso dos seus dados está na Política de Privacidade.
10. **Mudanças e lei aplicável.** Estes termos podem mudar; a data no topo mostra a versão em vigor. Eles seguem a lei brasileira.

## Prototype

- **Canônico:** `frontend/public/prototypes/card-1160-landing-auditoria/index.html`, clone da landing v4 viva (`https://criptofarol.com.br/`) com o delta deste card. URL: https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/
  - Página inteira como o visitante vê, sem painel de antes/depois. O formulário é simulado (nenhum envio real): o passo 1 "salva" em 0,45 s e mostra o passo 2, pelo botão ou por Enter num campo do passo 1; "Enviar respostas" (ou Enter no passo 2) e "Pular esta etapa" levam ao estado final.
  - **Gatilhos de falha:** no passo 1, um e-mail que começa com "erro" mostra a falha do passo 1 (fica no passo 1); no passo 2, uma dificuldade que começa com "erro" mostra a falha do passo 2 ("Seu cadastro já está salvo, mas estas respostas não foram…"), com "Enviar respostas" e "Pular esta etapa" de novo à mão.
  - Os eventos do funil ficam em `window.__eventosLanding` e no console (`[evento do funil]`); sem chave do PostHog.
  - Links de produção no protótipo: `./privacidade.html` e `./termos.html` (em produção, `/privacidade` e `/termos`); `/login` leva ao app do DEV.
- **Extras:** `privacidade.html` e `termos.html` (cabeçalho e rodapé da landing, texto da seção "Textos para aprovação", faixa de rascunho só no protótipo).
- **Apoio:** `styles.css` (v4 inteiro, idêntico byte a byte), `delta.css`, `assets/` (logo e marca copiados da v4; hero WebP 640/1024/1600 gerado na d1; análise de desktop gerada na d2; print do Monitor, recorte da análise e imagem OG refeitos no r2, D8; `assets/fonts/` com Inter e JetBrains Mono, subconjunto latino, baixados do Google Fonts uma vez e servidos pela pasta). A pasta não depende de `cripto-farol-landing-v4/` nem de `cripto-farol-landing/`, que saem do `crypto` em F6.

## Prototype Validation

Evidência de 30/10/2026 (autor do rework r2 da rodada d2). Qualquer mudança posterior nos arquivos abaixo a invalida.

- **`openspec validate card-1160-landing-auditoria --strict`:** válido.
- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py` rodado como módulo, catálogo do HEAD, chave `landing`): tokens L1–L3 = `affected` / `landing` / `existing`; `design_token_gap` = None; `requires_existing_clone` = True; `classify(index.html, landing)` = PASS; `evaluate_clone_gate` = True; `clone_gate_ok` = True; `copied_utf8_sum` = 8.602 B (d2: 9.100 B; a confiança 1 e 2 virou delta). `privacidade.html` e `termos.html` dão BLOCKED no `classify` (informativo: não têm os marcos da home, e o catálogo não tem entrada para elas), `copied_utf8_sum` = 231 B cada.
- **Regiões COPIED:** as 28 do `index.html` e as 3 de cada página extra são substrings literais da v4 publicada (`frontend/public/prototypes/cripto-farol-landing-v4/index.html`); 0 fora; nenhum marcador dentro de tag. `styles.css` = `styles.css` da v4 inteiro (13.878 B, sha `0014884b29cb…`). A v4, os clones de outros cards e o código do produto não foram tocados.
- **Bytes por arquivo** (copiado × gerado, sem os marcadores):

  | Arquivo | Bytes | sha256 | COPIED | DELTA |
  |---|---|---|---|---|
  | `index.html` (canônico) | 37.347 | `c59958eb8aea…` | 28 pares, 8.096 B | 28 pares, 24.038 B |
  | `privacidade.html` | 8.396 | `8d3647965bfb…` | 3 pares, 189 B | 3 pares, 7.761 B |
  | `termos.html` | 6.512 | `bba3d5cb720f…` | 3 pares, 189 B | 3 pares, 5.877 B |
  | `styles.css` | 13.878 | `0014884b29cb…` | clone inteiro | — |
  | `delta.css` | 6.193 | `42f1c9b4fb45…` | — | delta |
  | `assets/` (11 arquivos) | 323.477 | — | 2.945 B (logo e marca) | 320.532 B (hero WebP; Monitor 680×1070 `f44bb8cf0919…`, análise 848×569 `474b3f724596…` e recorte 348×573 `c715ff6477d9…`; OG `76e2dffb9947…`; 2 fontes de 79.688 B) |

  O delta do `index.html` cresceu no r2 porque a confiança 1 e 2 deixou de ser v4 (os pares continuam 28: a região COPIED antes da confiança encolheu e o delta da confiança 3 passou a cobrir os três cartões).
- **URL pública:** `https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/` responde 200 (`text/html`), sha256 `c59958eb8aea…` = `index.html` do worktree; `privacidade.html`, `termos.html`, `delta.css` (`text/css`), `assets/monitor.webp`, `assets/grafico-analise-recorte.webp` (`image/webp`) e `assets/og-1200x630.jpg` (`image/jpeg`) respondem 200 com o mesmo sha do worktree.
- **Browser gate** (Playwright Python, Chromium headless shell 1243, `pt-BR`, **na URL pública**; contexto novo por largura, 1440×900 DPR 1 e 390×844 DPR 3 com toque): **201/201 asserts PASS**, 0 `pageerror`, 0 `console.error`, 0 resposta ≥ 400, 0 request falho, **nenhum host de terceiro**, sem rolagem horizontal nas três páginas. Cobre tudo o que a d2 cobria (formulário inteiro: Enter no passo 1 vazio e preenchido, foco no título do passo 2, erro do passo 1 e do passo 2, pular, sucesso honesto, eventos sem dado pessoal, CTAs hero/nav/footer, consentimento em nova aba, CTA da nav com 44 px a 390, 2 famílias de fonte locais, páginas legais, JSON-LD FAQPage = FAQ visível, textos de cripto, ações e ETFs) e, do r2:
  - **texto efetivo ≥ 11 px nos dois prints** (menor fonte × largura renderizada ÷ largura natural): a 390, Monitor 390 px de 340 px CSS × 10 px = **11,47 px** e recorte da análise 341,2 px de 348 px × 12 px = **11,77 px**; a 1440, Monitor 418 px = 12,29 px e análise 978 px de 848 px = 13,84 px;
  - frase honesta do alerta: selo "Alerta no Telegram nas estratégias com estrela"; benefício 02 com "Conecte o Telegram no Perfil", "com estrela", "avisa as entradas e as saídas" e "desliga estratégia por estratégia"; rotina 01 com estrela; FAQ 6 com estrela, Perfil e "estratégias de exemplo do catálogo aparecem no Monitor sem alerta"; descrição, `og:description` e `og:image:alt` com estrela; `og:title` com ações e ETFs; nenhuma "vitrine";
  - nenhum "na hora", "assim que", "em tempo real", "quando entra e quando sai", "uma vez por dia", "08:05", "grupo de Telegram", "lá no topo", "médias móveis ou indicador" (além da lista da d2);
  - prints coerentes: alt do Monitor com SPY e sem NVDA, alt da análise com NVDA; abertura do produto "Além do Monitor que você viu acima"; confiança 1 e 2 novas; `max-width` em `ch` nos três avisos.
- **O que vi nas capturas:** a 1440, o hero tem o print do Monitor à direita (SPY em posição no 1d com alerta ligado, pregão aberto, stop, entrada e distâncias; ETH/USDT em saída / cobertura no 4h com alerta desligado), com a borda direita dos cartões inteira; o selo do alerta cabe numa linha. A 390, o selo quebra em duas linhas equilibradas ("Alerta no Telegram nas / estratégias com estrela"), o aviso de risco vem logo depois dos selos e o Monitor vem de ponta a ponta. O recorte da análise a 390 mostra ago.–out. com "COMPRA", "VENDA (11,16%)", "Média curta", "Média longa", o eixo em formato BR, o cabeçalho em duas linhas e o logo do TradingView, tudo legível.
- **Detector Impeccable (hook de escrita):** acusa só o que já está em Risks (fontes e cores da v4, `clamp` de `.signal-card strong`); nenhum achado novo.
- **Scripts e capturas:** `c1160-r2/` no scratchpad da sessão (`capture_monitor_r2.py`, `build_imgs_r2.py`, `regions.py`, `browser_gate_r2.py`, `shots/`, `shots-gate/`); d1, r1 e d2 em `c1160/`, `c1160-b/`, `c1160-r1/` e `c1160-d2/`.

## Design Critique

Rodada d2 (depois do T6 de 29/10/2026: "Atualizar a landing ao produto atual…"). Com tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r2) aplicou as decisões do Alan, os dois P1 e os P2 da dupla. Não houve segundo rework.

- Autor: `design-autor 1160 d2` (isolado). Rework: `design-autor 1160 r2` (isolado).
- Assessment A: `assessment-a 1160 d2` (isolado; produto, UX, acessibilidade e fidelidade). Assessment B: `assessment-b 1160 d2` (isolado; detector, gate e navegador).
- Verdict: **PASS**. A e B deram PASS com rework, e os dois reworks foram aplicados no r2. Tokens: `UI impact: affected` / `live_route: landing` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/ (clone da landing v4 viva). Páginas extras: `privacidade.html` e `termos.html`.
- Snapshots: `.impeccable/critique/1160-card-1160-landing-auditoria-A-d2.md` e `…-B-d2.md` (d2); `…-A.md` e `…-B.md` (d1). O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1, corrigidos no r2**:
  - O alerta no Telegram prometia o que a conta nova do beta não tem: ela vê só a vitrine do catálogo, que não alerta, e não consegue criar estratégia própria (A). O Alan escolheu "Frase honesta na landing": o alerta vale para as estratégias acompanhadas com estrela, depende do Telegram conectado no Perfil, e a vitrine aparece sem alerta. A vitrine alertar virou o card #1161, em Em Refinamento.
  - O recorte do gráfico de análise saía com texto de 8,3 px a 390 px (B). Novo recorte com 11,77 px, e o gate do Apply ganhou o assert de texto efetivo ≥ 11 px nos prints a 390 px.
- **P2, corrigidos no r2**: os prints contam a mesma história (Monitor com SPY, análise com NVDA, sem contradição de posição); o alerta depende do Telegram no Perfil; textos herdados que destoavam ("grupo de Telegram", "não precisa interpretar médias móveis") foram ajustados; títulos e alt da imagem de compartilhamento citam ações e ETFs; linhas longas dos avisos limitadas a ~62ch.
- **Decisão do Alan sobre a frequência:** "Não citar frequência". A copy não diz quando o alerta sai e não sugere tempo real.
- **P3 aceitos, para o Apply**: os itens da subseção de P3 aceitos em Risks / Trade-offs, incluindo os da onda 1160-d2 (OG em Inter, análise de desktop com 1000 px ou mais, `loading`/`fetchpriority`, recaptura dos prints do DEV logado com filtro "Todos"). Também entram os achados do detector em regiões COPIED da v4 e as fontes e cores da landing fora do `DESIGN.md` da raiz, que descreve o app.
- **Juízo do Alan no T7**: Open Question 1 (controlador e canal do titular) bloqueia a Política; a 2 (leads antigos) precisa de resposta antes do F0/F4; as 3 a 11 seguem a recomendação como padrão; a 12 e a 13 já estão respondidas. Mais a aprovação dos textos de `## Textos para aprovação (T7)`.
- **Disposition:** a landing é a v4 com o delta do card e atualizada ao produto atual: cobre cripto, ações e ETFs da Binance (ação e ETF acompanhados e alertados, não operados); sinais com o vocabulário do Monitor ("Em posição" e "Saída / cobertura", sem alvo); análise pronta das estratégias acompanhadas; alerta no Telegram nas estratégias com estrela; prints novos e legíveis; aviso de risco das três classes. Seguem da d1: formulário que salva no passo 1, rodapé com Política e Termos, contador trocado por frase de levas, SEO técnico, página ~89% mais leve e corte para o `oalansilva/cripto-farol-landing` em fases F0–F7.

### Rodada d1 (histórico)

Autor d1, dupla A/B d1 e rework r1, verdict PASS. Os P1 corrigidos no r1 foram a ordem do corte em PROD (fases F0–F7 com rollback por fase) e o Enter no passo 1 que enviava o passo 2. O Alan devolveu pelo T6 em 29/10/2026 para atualizar a página ao produto atual.

### Proxies

- `design.md` words: 14592 (antes desta seção)
- HTML generated vs copied (`index.html`): 24038 vs 8096
- Spawns: 4 nesta rodada (design-autor d2, assessment-a d2, assessment-b d2, design-autor r2); 8 no card
