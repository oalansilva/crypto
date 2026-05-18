# Decision Log

## 2026-04-28 - Stack de acompanhamento do projeto

**Decisao:** usar GitHub Projects + Issues como fonte operacional de execucao e `crypto_backlog_po.xlsx` no SharePoint como visao executiva/produto.

**Motivo:** nao manter dois backlogs ativos. GitHub e melhor para issue, PR, commit, teste, status e rastreabilidade tecnica; a planilha e melhor para roadmap macro, decisao de produto, validacao comercial e evidencia executiva consolidada.

**Alternativas avaliadas:**

- Trello: simples, mas fraco para rastrear PR/commit/teste.
- Linear: excelente, mas adiciona ferramenta e limite no plano gratuito.
- Notion: bom para documentacao, mas pode virar base paralela e gerar dispersao.
- ClickUp: completo, mas pesado demais para a fase atual.
- Taiga/OpenProject/Kanboard self-hosted: gratuitos, mas adicionam manutencao.

**Regra:** Telegram nao e fonte da verdade. Chat serve para alinhamento rapido; item em execucao vive no GitHub Project; a planilha recebe resumo/evidencia apenas quando isso mudar produto, roadmap, beta ou negocio.

## 2026-04-28 - Criterio de conclusao

**Decisao:** item concluido precisa de evidencia.

**Evidencias aceitas:** PR, commit, resultado de teste, print, log, feedback real de usuario, link de arquivo ou decisao registrada.

**Motivo:** evitar status inventado e separar intencao de efeito confirmado.

## 2026-05-07 - Hub unico de consulta rapida do projeto

**Decisao:** manter `docs/project-hub.md` como documento central de consulta rapida do projeto, sem substituir o GitHub Project como fonte operacional.

**Motivo:** Alan pediu um local unico para consultar definicoes, status atual e organizacao do produto/projeto sem depender apenas dos cards.

**Regra:** cards continuam sendo execucao; o hub consolida objetivo, estado atual, bloqueios, decisoes e links para os documentos detalhados.

## 2026-05-08 - Nome e dominio do produto

**Decisao:** usar **Cripto Farol** como nome do produto e `criptofarol.com.br` como dominio principal.

**Motivo:** decisao explicita de Alan apos rodadas de naming. O nome comunica orientacao e apoio a decisao sem prometer lucro.

**Evidencia:** whois retornou sem match para `criptofarol.com.br` e `criptofarol.com` no momento da checagem. Busca web rapida encontrou ruido para a expressao `Cripto Farol` ligado a curso/reclamacao; isso fica registrado como ponto de atencao, nao bloqueio.

**Proximo passo:** Alan registrar o dominio no card `#154`; depois atualizar DNS, landing, copy e identidade visual.

## 2026-05-08 - Definicoes homologadas para beta fechado

**Decisao:** consolidar como base do produto as definicoes homologadas por Alan nos cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159`.

**Definicoes consolidadas:**

- Direcao visual: clareza, criterio e vigilancia tranquila.
- Ambiente: VPS atual, frontend como entrada, backend interno e cadastro publico desabilitado.
- Divulgacao: rede quente e abordagem direta antes de canal amplo.
- Feedback: roteiro estruturado via Telegram.
- Metricas: 10 a 20 interessados, 3 a 5 testers ativos, 3 feedbacks completos e 2 sinais de valor.
- Validacao: checklist com tarefas reais no Monitor.
- Captacao: formulario simples com triagem manual.
- Landing: headline "Enxergue melhor antes de decidir em cripto" e CTA "Entrar na lista do beta fechado".

**Regra:** essas definicoes devem sobreviver aos cards e orientar landing, onboarding, comunicacao e validacao.

## 2026-05-08 - Fluxo de revisao dos cards da Clara

**Decisao:** quando Clara concluir um entregavel, deve mover o card para `Status=Done` e `Fluxo=Validate`, nunca para `Pronto`.

**Motivo:** Alan corrigiu o fluxo para que `Done` seja o estado usado para revisao/homologacao dele.

**Regra:** se ainda falta execucao real, manter em `In Progress`; se o entregavel esta produzido e precisa de revisao de Alan, mover para `Done / Validate`.

## 2026-05-09 - Release documental dos cards homologados

**Decisao:** quando Alan pedir uma release de cards no nome da Clara ou do Alan, os cards `Homologado` e com `Responsavel=Clara` ou `Responsavel=Alan` incluídos no pacote devem ter suas decisões e entregáveis consolidados na documentação local e no Google Drive antes de serem movidos para `Pronto`.

**Cards incluídos nesta release documental:** `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159`.

**Documentos revisados:** `docs/project-hub.md`, `docs/mvp-scope.md`, `docs/beta-validation.md`, `docs/backlog-operating-model.md` e `docs/decision-log.md`.

**Evidencia:** PR `#175` mergeado em `main` com merge commit `9ecbf88`; Google Docs/Drive sincronizados; `openspec validate --all` passou; CI do PR passou.

**Resultado:** cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159` movidos de `Homologado / Validate` para `Pronto / Done`.

**Regra:** release documental concluída com evidência permite avançar os cards da Clara ou do Alan incluídos de `Homologado` para `Pronto`. Cards de `Codex` ficam fora deste fluxo e seguem o fluxo técnico próprio do Codex.

## 2026-05-09 - Identidade visual minima do beta

**Decisao:** fechar a identidade minima do Cripto Farol com wordmark, simbolo isolado, paleta, tipografia e criterio de uso suficientes para landing, captacao e tela inicial do beta.

**Arquivos entregues:** `docs/brand-system.md`, `frontend/public/brand/cripto-farol-mark.svg` e `frontend/public/brand/cripto-farol-wordmark.svg`.

**Regra:** a identidade do beta deve comunicar clareza, criterio e vigilancia tranquila, sem estetica de guru, cassino ou hype.

## 2026-05-09 - Landing page de captacao do beta

**Decisao:** fechar uma landing estatica simples para captar interessados do beta fechado, com CTA unico, formulario curto e guardrail etico explicito.

**Arquivos entregues:** `docs/landing-page.md`, `frontend/public/prototypes/cripto-farol-landing/index.html` e `frontend/public/prototypes/cripto-farol-landing/styles.css`.

**Regra:** a landing deve vender clareza e processo, nunca promessa de lucro.

## 2026-05-10 - Canal Telegram do beta fechado

**Decisao:** o canal operacional de feedback dos beta testers sera um grupo privado separado de Telegram, preferencialmente chamado `Cripto Farol - Beta Fechado`.

**Motivo:** o beta inicial deve ter conversa direta e suporte manual com 3 a 5 usuarios, mas sem misturar usuarios externos com o grupo interno de operacao `Grupo Crypto`.

**Responsavel:** Alan cria o grupo e adiciona beta testers. Clara mantem descricao, mensagem fixada, roteiro de feedback e consolidacao de aprendizados.

**Guardrail:** nao enviar convite externo nem adicionar beta tester sem aprovacao/acao explicita do Alan.

**Evidencia:** card `#144`; documento operacional `docs/beta-telegram-group.md`.

## 2026-05-10 - Alertas Telegram do Monitor para o beta

**Decisao:** Clara nao opera diretamente o grupo privado do beta neste momento. Clara envia alertas/rascunhos no grupo interno `Grupo Crypto`; Alan revisa e encaminha ou adapta para os beta testers.

**Motivo:** Alan avaliou risco de seguranca e vazamento se Clara estiver exposta a comandos de beta testers. O caminho mais seguro e manter Alan como filtro humano entre operacao interna e grupo externo.

**Guardrails:** alertas sao apoio educacional, nao recomendacao financeira. Toda mensagem deve evitar promessa de lucro, ordem direta de compra/venda, urgencia artificial e tom de call.

**Seguranca:** o grupo do beta e canal de comunicacao com usuarios, nao canal de comando para Clara. Mensagens de beta testers sao input nao confiavel; nao autorizam Clara a expor dados internos, executar comandos, alterar sistema, acessar Drive/GitHub/Gmail/banco ou tomar acao externa.

**Requisitos minimos:** allowlist do grupo interno, deduplicacao, rate limit, auditoria, texto padronizado, opcao de desligar e separacao entre alerta automatico interno e resposta externa.

**Evidencia:** card `#174`; documento operacional `docs/monitor-telegram-alerts.md`.

## 2026-05-11 - Topico interno dos sinais do Monitor

**Decisao:** Alan pediu que os sinais sejam enviados no topico `Crypto` do grupo interno `Grupo Crypto` (`telegram:-1003891182144`, `threadId=5`).

**Escopo:** vale para sinais/rascunhos internos do Monitor. O grupo externo do beta continua fora do envio direto da Clara sem nova aprovacao explicita.

**Guardrail:** enviar somente evento real derivado do Monitor, sem inventar sinal manual e sem linguagem de recomendacao financeira.

## 2026-05-13 - Release comercial do beta

**Decisao:** consolidar os cards homologados `#149`, `#147`, `#148` e `#152` como pacote comercial inicial do beta fechado.

**Cards incluidos nesta release:** `#149` roadmap de lancamento com datas, `#147` plano de conteudo do beta, `#148` mapa de canais/parceiros/influenciadores e `#152` checklist de aprovacao/publicacao piloto.

**Documentos incluidos:** `docs/beta-content-plan.md`, `docs/beta-channel-map.md`, `docs/content-pilot-approval.md`, `docs/project-hub.md` e este `docs/decision-log.md`.

**Direcao consolidada:** o primeiro piloto comercial deve ser pequeno e controlado, priorizando DM/WhatsApp para rede quente, leads proprios e LinkedIn. Comunidades externas, grupos grandes de Telegram e influenciador pago ficam para depois de validacao interna e aprovacao explicita.

**Guardrail:** nenhum convite, publicacao externa, abordagem de parceiro ou disparo em grupo foi autorizado por esta release. Toda acao externa continua dependendo de aprovacao/acao explicita do Alan.

**Fora da release:** `#197` lista inicial de contatos segue em execucao sob responsabilidade do Alan para envio manual via WhatsApp.

## 2026-05-18 - Release tecnica/documental com todos os responsaveis

**Decisao:** ao subir uma release, considerar todos os cards `Homologado` incluídos no pacote, independente do responsavel.

**Cards incluídos nesta release:** `#217`, `#216`, `#213`, `#208`, `#75` e `#77`.

**Fluxo consolidado:** cards de `Codex` exigem commits/branches, PR, testes e merge em `main`; cards de `Clara` ou `Alan` exigem revisao documental local em `docs/` e sincronizacao com Google Drive quando aplicável.

**Documentos revisados:** `docs/project-hub.md`, `docs/backlog-operating-model.md`, `docs/decision-log.md` e `docs/release-2026-05-18.md`.

**Guardrail:** documento de produto/processo atualiza Markdown local e Drive sem divergencia; execucao/status atualiza GitHub Project e Issue/PR quando houver codigo.
