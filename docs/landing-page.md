# Landing Page - Cripto Farol

## Onde a landing mora

Desde o card [#1160](https://github.com/oalansilva/crypto/issues/1160) (decisão do Alan no Design, 29/10/2026), a landing pública de `https://criptofarol.com.br/` **não mora mais neste repo**. A fonte de produção é o repo **`oalansilva/cripto-farol-landing`**:

- `site/index.html`: a landing (v4 do #790 + delta do #1160);
- `site/privacidade/index.html` e `site/termos/index.html`: Política de Privacidade (`/privacidade`) e Termos de Uso (`/termos`);
- `site/robots.txt`, `site/sitemap.xml`, `site/favicon.ico`, `site/apple-touch-icon.png`;
- `site/lp/`: CSS único, `landing.js` (medição, CTAs e formulário), imagens WebP, imagem de compartilhamento `og-1200x630.jpg`, logo, marca e fontes (Inter e JetBrains Mono, servidas pelo próprio site);
- `scripts/deploy.sh`, `tests/` e `README.md` (como testar, publicar e reverter).

`frontend/public/prototypes/` deste repo guarda **só protótipos** de Design. A v4 (`cripto-farol-landing-v4/`), os assets antigos (`cripto-farol-landing/`), as variantes `-v3` e `-skill-v2` e `frontend/public/posthog-config.js` saíram no PR de remoções do #1160. O protótipo aprovado do card fica em `frontend/public/prototypes/card-1160-landing-auditoria/` e é autossuficiente.

Mudança de copy, layout ou SEO da landing = PR no `oalansilva/cripto-farol-landing`, não neste repo.

## Fluxo real do formulário

O formulário tem 2 passos e posta em `/api/leads` (caminho relativo), que é servido pelo backend **deste** repo (`backend/app/routes/leads.py`):

1. **Passo 1** (obrigatório): nome e e-mail. O botão "Entrar na lista do beta" (ou Enter num campo do passo 1) manda `step: 1` e o lead **já fica salvo** na tabela `landing_leads` do PostgreSQL (um lead por e-mail normalizado).
2. **Passo 2** (opcional): WhatsApp, nível com cripto e maior dificuldade. Manda `step: 2` com o mesmo e-mail e **enriquece o mesmo lead**, sem duplicar. "Pular esta etapa" (ou passo 2 vazio) não envia nada.
3. Payload sem `step` (a v4, que é o commit-base de rollback da landing) = passo 1 + passo 2 juntos.

Regras que seguem do #689: resposta `202` neutra para todo envio aceito, auditoria em `beta_access_audit_logs` (`record_lead_submission`, agora com o `step`), convite validado mas nunca consumido, nenhuma conta criada.

**Aviso ao Alan:** depois do commit, fora do tempo da resposta, o backend manda uma mensagem pelo bot do Cripto Farol (`MONITOR_TELEGRAM_BOT_TOKEN`) para cada admin com Telegram vinculado (`users.telegram_chat_id`): "Novo lead na landing" (nome, e-mail, origem, campanha) no passo 1 e "Lead completou o cadastro" (WhatsApp, nível, dificuldade) no passo 2. Reenvio do passo 1 do mesmo e-mail não avisa. Falha do Telegram só gera log, sem dado pessoal; o lead e a tela de sucesso não dependem dele.

**O que não existe mais:**

- e-mail ao lead ou ao Alan (a tela final diz só "Recebemos seu cadastro. Vamos te chamar quando abrir a próxima leva do beta.");
- contador de vagas e `GET /api/leads/stats` / `BETA_TOTAL_SPOTS` (no lugar, a frase fixa de beta fechado em levas);
- o serviço Node `ops/landing-leads/` (`criptofarol-prod-leads.service`), a planilha `.xlsx`, o tópico do grupo no Telegram e a criação de conta pela landing.

## Medição (PostHog)

A landing carrega o PostHog pelo caminho próprio `/ingest` (mesmo projeto do app), com gravação de sessão, pesquisas e autocapture desligados. Eventos, sem nome, e-mail, WhatsApp nem respostas: `$pageview` (manual, endereço sem parâmetros), `landing_pageview`, `landing_cta_clicked` (`cta_location` = `hero` | `nav` | `footer`), `lead_form_submit_started` / `lead_form_submit_accepted` / `lead_form_submit_failed` (com `step`), `lead_step1_completed` e `lead_step2_skipped`. A chave é escrita no deploy da landing em `lp/posthog-config.js` (fora do git).

## Publicação e reversão (próprias, fora da release do `crypto`)

Cada ambiente tem um checkout da landing com `repo/`, `releases/<commit>/site` e o link `current`; o Caddy serve sempre `<raiz>/current/site`:

| Ambiente | Raiz | URL |
|---|---|---|
| DEV (QA e homologação) | `/srv/apps/dev/criptofarol/landing` | `https://landing-dev.163.176.208.0.sslip.io/` (`X-Robots-Tag: noindex, nofollow`; `/api/*` vai ao backend DEV) |
| PROD | `/srv/apps/prod/criptofarol/landing` | `https://criptofarol.com.br/` |

- Publicar: `scripts/deploy.sh <dev|prod> <commit>` no repo da landing (exporta `site/` do commit, troca `?v=` dos assets, escreve a config do PostHog, troca o link `current` de forma atômica, registra em `deploys.log` e confere por HTTP).
- Reverter: `scripts/deploy.sh prod <commit anterior do deploys.log>` (só troca o link; sem reload do Caddy e sem restart do `crypto`). O alvo de rollback de emergência é o **commit-base** (a v4 com caminhos `/lp/`).
- O Caddy serve `/`, `/privacidade`, `/termos`, `/robots.txt`, `/sitemap.xml` e os ícones com `no-cache` e `/lp/*` com cache longo (`immutable`); os caminhos antigos (`/cripto-farol-landing/assets/*`, `/prototypes/cripto-farol-landing-v4/assets/*`) redirecionam para `/lp/*` e os protótipos antigos de landing para `/`.
- `www.criptofarol.com.br` redireciona (308) para o domínio sem www, e o domínio sai com HSTS, `X-Content-Type-Options`, `Referrer-Policy` e `frame-ancestors 'none'`.

O corte em PROD seguiu as fases F0–F7 do `design.md` do #1160 (`openspec/changes/archive/*-card-1160-landing-auditoria/`).

## Guardrails de copy

- Apoio à decisão, não recomendação de investimento; aviso de risco visível desde o hero, no cadastro e no rodapé, cobrindo cripto, ações e ETFs.
- Cripto, ações e ETFs da Binance são acompanhados e alertados; comprar e vender pelo Farol é **só cripto** (Spot opcional, confirmação a cada ordem, nunca saque, nunca senha).
- Sinais com os nomes do Monitor: "Em posição" e "Saída / cobertura"; sem alvo.
- Alerta no Telegram só nas estratégias que a pessoa acompanha com estrela, com o Telegram conectado no Perfil; sem frequência e sem "na hora", "assim que" ou "em tempo real".
- Prints do produto limpos (sem controles de desenvolvedor, preço em formato BR, sem parâmetros internos) e legíveis no celular (texto efetivo ≥ 11 px a 390 px).
- Rodapé sem responsável, CNPJ, contato ou redes; o canal do titular (`contato@criptofarol.com.br`) fica dentro da Política.
