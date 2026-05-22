# Hub do Projeto Cripto

## Objetivo

Este documento e o ponto unico de consulta rapida do projeto.

Aqui deve ficar:

- o objetivo do produto;
- o status atual;
- as decisoes principais;
- os bloqueios e proximos passos;
- o mapa para os documentos detalhados.

## Regra de Uso

- GitHub Project continua sendo a fonte operacional de execucao.
- Este hub e a fonte rapida de contexto e status consolidado.
- Documentos detalhados ficam nos arquivos tematicos de `docs/`.
- Telegram e chat nao sao fonte da verdade.

## Produto

- Nome do projeto: **Cripto Farol**.
- Dominio definido por Alan: `criptofarol.com.br`.
- Objetivo do produto: ajudar investidores em cripto com clareza, contexto e apoio a decisao.
- Proposta do MVP: usar o Monitor como tela principal do beta fechado.
- Guardrail comercial: sem promessa de lucro, sem sinal milagroso, sem hype vazio.

## Status Atual

- Fase atual: fechamento do beta fechado.
- Fonte operacional: GitHub Project `MVP Cripto - Beta Fechado`.
- Status consolidado em 2026-05-08: Alan homologou definicoes de marca, beta, metricas, captacao, copy, divulgacao e feedback.
- Release documental 2026-05-09 concluida: cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159` consolidados na documentacao, publicados em `main` pelo PR `#175` e movidos para `Pronto / Done` no GitHub Project.
- Entregaveis da Clara em 2026-05-09 para revisao: `#143` com brand system, wordmark, mark e ativos minimos; `#140` com landing page estatica para captacao e documento de copy/estrutura.
- Ambiente do beta: VPS atual, frontend como entrada, backend restrito, cadastro publico desabilitado.
- Canal de feedback do beta: definido no `#144` como grupo privado separado de Telegram, com Alan responsavel pela criacao e Clara responsavel por descricao, mensagem fixada, roteiro e consolidacao dos feedbacks.
- Alertas do Monitor no beta: definido no `#174` que Clara envia alertas/rascunhos no grupo interno `Grupo Crypto`, topico `Crypto` (`telegram:-1003891182144`, `threadId=5`); Alan revisa e encaminha/adapta para o grupo privado do beta. Envio direto por Clara ao grupo externo fica fora do MVP atual.
- Implementacao tecnica dos alertas: criada no card `#183`, com envio apenas ao grupo interno allowlistado, deduplicacao, rate limit, auditoria e opcao de desligar.
- Release comercial 2026-05-13 preparada: cards `#149`, `#147`, `#148` e `#152` consolidados na documentacao, com roadmap, plano de conteudo, mapa de canais e checklist de publicacao piloto. Publicacao externa continua dependente de aprovacao explicita do Alan.
- Release tecnica/documental 2026-05-18 preparada: cards `#217`, `#216`, `#213`, `#208`, `#75` e `#77` incluídos no pacote, com melhorias de Favoritos, Carteira, Monitor e revisao documental de Clara/Alan.
- Pacote inicial de conteudo do card `#151` recuperado e versionado em `docs/social/card-151-content-package.md`, com 2 textos de LinkedIn, 2 pecas de Instagram, 1 texto para Telegram/grupos e 1 abordagem WhatsApp/DM. Publicacao externa continua dependendo de aprovacao explicita do Alan.
- Lista inicial de contatos do beta: card `#197` segue em execucao com Alan, com canal WhatsApp definido para os nomes iniciais. Nenhum convite externo foi enviado automaticamente.
- Redis runtime: correcao aplicada localmente e card `#170` em `Pronto / Validate`.
- Arquitetura runtime/candles: modelo operacional documentado em `docs/runtime-architecture.md`; boot padrao leve, candle writer dedicado opt-in e endpoint `/api/runtime/status`.
- Nome, marca e dominio: decidido como **Cripto Farol** / `criptofarol.com.br`; registro do dominio em andamento com Alan no `#154`.

## Gates Atuais

Antes de liberar usuarios beta reais:

1. Alan confirmar registro de `criptofarol.com.br`.
2. Fechar publicacao controlada da VPS.
3. Validar fluxo ponta a ponta.
4. Validar os documentos e definicoes homologadas no Drive.

## Decisoes Ja Tomadas

- GitHub Project = execucao.
- SharePoint Excel = visao executiva/produto.
- Monitor = home operacional do MVP.
- Beta fechado com 3 a 5 usuarios.
- Acesso manual e controlado no inicio.
- Feedback inicial via grupo privado de Telegram.
- Captacao inicial por formulario simples com triagem manual.
- Posicionamento do Cripto Farol: ferramenta educacional de apoio a decisao, nao recomendacao financeira.

## Definicoes Homologadas em 2026-05-08

Alan homologou os seguintes cards e estas definicoes passam a ser base do produto:

- `#156` direcao visual minima: clareza, criterio e vigilancia tranquila; paleta com azul petroleo/navy, verde/teal e acento amarelo-farol.
- `#136` ambiente de publicacao: VPS atual, frontend como entrada, backend interno, cadastro publico desabilitado e usuarios beta autorizados manualmente.
- `#146` estrategia de divulgacao: rede quente e abordagem direta primeiro; LinkedIn controlado depois; Instagram como apoio; grupos/comunidades somente apos validar fluxo e mensagem.
- `#138` roteiro de feedback: mensagem inicial, perguntas apos primeiro acesso, perguntas apos uso real do Monitor e nota final por tester.
- `#145` metricas do beta: 10 a 20 interessados, 3 a 5 testers ativos, ativacao do Monitor, minimo de 3 feedbacks completos e pelo menos 2 sinais de valor.
- `#137` checklist de validacao: 3 a 5 perfis reais, roteiro minimo de uso e registro de travas/valor percebido.
- `#160` canal de captacao: formulario simples com triagem manual; lista manual como contingencia.
- `#159` copy/CTA: headline "Enxergue melhor antes de decidir em cripto" e CTA "Entrar na lista do beta fechado".

## Itens Publicados na Release 2026-05-09

Cards com definicoes homologadas por Alan, consolidadas na documentacao e movidas para `Pronto / Done`:

- `#136` ambiente de publicacao do beta fechado.
- `#137` checklist de validacao com 3 a 5 usuarios.
- `#145` metricas de sucesso do beta e divulgacao.
- `#159` copy e CTA da landing.
- `#160` formulario ou canal de captacao.
- `#146` estrategia de divulgacao e canais.
- `#138` roteiro de feedback no Telegram.
- `#156` direcao visual minima.

## Itens Publicados na Release 2026-05-13

Cards homologados por Alan, sob responsabilidade da Clara, consolidados na documentacao e prontos para mover para `Pronto / Done`:

- `#149` roadmap de lancamento com datas, dependencias, responsaveis e gates.
- `#147` plano de conteudo para divulgar o beta, com CTA, canais, guardrails e rascunhos.
- `#148` mapa de parceiros, grupos e influenciadores, com recomendacao de priorizar rede quente, leads e LinkedIn.
- `#152` checklist de aprovacao e publicacao piloto, com pre-gates, textos e evidencias a registrar.

Decisao da release: piloto comercial pequeno e controlado, com DM/WhatsApp para rede quente e LinkedIn como primeira validacao publica leve. Telegram/grupos externos e influenciador pago ficam para depois de validacao interna e aprovacao explicita.

## Itens Entregues e Aguardando Homologacao

- `#143` identidade visual minima do beta:
  - `docs/brand-system.md`
  - `frontend/public/brand/cripto-farol-mark.svg`
  - `frontend/public/brand/cripto-farol-wordmark.svg`
- `#140` landing page para captacao:
  - `docs/landing-page.md`
  - `frontend/public/prototypes/cripto-farol-landing/index.html`
  - `frontend/public/prototypes/cripto-farol-landing/styles.css`

## Itens Ainda em Execucao Real

Estes cards ainda nao sao apenas planejamento:

- `#154` registrar dominio aprovado `criptofarol.com.br`.
- `#171` configurar publicacao beta na VPS atual com acesso controlado.
- `#75` validar fluxo ponta a ponta do beta fechado.
- `#157` criar logo ou wordmark inicial da marca aprovada.
- `#158` exportar assets de marca para landing e produto.
- `#155` preparar DNS inicial do dominio aprovado.
- `#183` implementar alertas Telegram internos do Monitor.
- `#197` montar lista inicial de contatos para convite beta, sob responsabilidade do Alan para envio manual via WhatsApp.

## Proximos Passos Recomendados

1. Alan concluir o registro de `criptofarol.com.br` no `#154`.
2. Clara preparar o plano DNS no `#155` apos confirmacao do registro.
3. Codex executar `#171` para publicacao controlada na VPS atual.
4. Clara/Codex avancarem landing e identidade com base em `#156`, `#159` e `#160`.
5. Rodar validacao interna ponta a ponta no `#75`.
6. Abrir beta controlado com 3 a 5 usuarios usando `#137`, `#138` e `#145`.

## Mapa de Documentos

- Pasta do projeto no Google Drive: `https://drive.google.com/drive/folders/1OE0D_nsb7BAMQ_ntZXUonnsfX9MtXhT9`
- Escopo do MVP: [mvp-scope.md](/root/.openclaw/workspace/crypto/docs/mvp-scope.md)
- Validacao do beta: [beta-validation.md](/root/.openclaw/workspace/crypto/docs/beta-validation.md)
- Grupo Telegram do beta: [beta-telegram-group.md](/root/.openclaw/workspace/crypto/docs/beta-telegram-group.md) / Drive `https://docs.google.com/document/d/1HFO-cpFeGzGnDvH8pz5JjpekMU6192I93TwEgzJ3tgU/edit?usp=drivesdk`
- Alertas Telegram do Monitor: [monitor-telegram-alerts.md](/root/.openclaw/workspace/crypto/docs/monitor-telegram-alerts.md) / Drive `https://docs.google.com/document/d/1mSOQGGVY7OnnrDaQN6rDB_Q6Qp8fh-Xt-JHe39r6gqs/edit?usp=drivesdk`
- Plano de conteudo do beta: [beta-content-plan.md](/root/.openclaw/workspace/crypto/docs/beta-content-plan.md)
- Mapa de canais e parceiros do beta: [beta-channel-map.md](/root/.openclaw/workspace/crypto/docs/beta-channel-map.md)
- Checklist de aprovacao/publicacao piloto: [content-pilot-approval.md](/root/.openclaw/workspace/crypto/docs/content-pilot-approval.md)
- Release comercial do beta 2026-05-13: [release-2026-05-13-commercial-beta.md](/root/.openclaw/workspace/crypto/docs/release-2026-05-13-commercial-beta.md)
- Release tecnica/documental 2026-05-18: [release-2026-05-18.md](/root/.openclaw/workspace/crypto/docs/release-2026-05-18.md)
- Pacote inicial de conteudo do card #151: [card-151-content-package.md](/root/.openclaw/workspace/crypto/docs/social/card-151-content-package.md) / Drive `https://docs.google.com/document/d/1klZyP4IezZTOIq0xPWAz0k7o4gSjb8X0IQ_Vi_vcdVs/edit?usp=drivesdk`
- Lista inicial de contatos para convite do beta: [beta-invite-contacts.md](/root/.openclaw/workspace/crypto/docs/beta-invite-contacts.md)
- Arquitetura runtime/candles: [runtime-architecture.md](/root/.openclaw/workspace/crypto/docs/runtime-architecture.md)
- Modelo operacional do backlog: [backlog-operating-model.md](/root/.openclaw/workspace/crypto/docs/backlog-operating-model.md)
- Log de decisoes: [decision-log.md](/root/.openclaw/workspace/crypto/docs/decision-log.md)
- Sistema de marca: [brand-system.md](/root/.openclaw/workspace/crypto/docs/brand-system.md)
- Estrutura da landing: [landing-page.md](/root/.openclaw/workspace/crypto/docs/landing-page.md)

## Regra de Atualizacao

Atualizar este hub quando houver mudanca em pelo menos um destes pontos:

- decisao de produto;
- mudanca de status do beta;
- novo bloqueio relevante;
- mudanca de ambiente/publicacao;
- definicao de marca/dominio;
- alteracao do proximo passo principal.

## Regra de Release

Quando Alan pedir uma release para cards no nome da Clara ou do Alan, levantar os cards `Homologado` e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos no pacote, revisar se as decisões e entregáveis estão refletidos nos Markdown locais e nos Google Docs/Drive correspondentes, publicar/encerrar a release com evidência e então mover esses cards para `Pronto`.

Cards de `Codex` ficam fora deste fluxo e seguem o fluxo técnico próprio do Codex.
