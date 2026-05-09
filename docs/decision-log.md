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

**Decisao:** quando Alan pedir uma release de cards no nome da Clara, os cards `Homologado` e com `Responsavel=Clara` incluídos no pacote devem ter suas decisões e entregáveis consolidados na documentação local e no Google Drive antes de serem movidos para `Pronto`.

**Cards incluídos nesta release documental:** `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159`.

**Documentos revisados:** `docs/project-hub.md`, `docs/mvp-scope.md`, `docs/beta-validation.md`, `docs/backlog-operating-model.md` e `docs/decision-log.md`.

**Evidencia:** PR `#175` mergeado em `main` com merge commit `9ecbf88`; Google Docs/Drive sincronizados; `openspec validate --all` passou; CI do PR passou.

**Resultado:** cards `#156`, `#136`, `#146`, `#138`, `#145`, `#137`, `#160` e `#159` movidos de `Homologado / Validate` para `Pronto / Done`.

**Regra:** release documental concluída com evidência permite avançar os cards da Clara incluídos de `Homologado` para `Pronto`. Cards de `Codex` ou `Alan` seguem seus fluxos próprios.
