# Preflight de produto somente leitura — candidato, 18/10/2026

Nova entrada Em desenvolvimento via T10 `achar_bloqueante` confirmada pelo orquestrador; nenhum T8 executado nesta entrada. Apply único: captura `3e3a9801-4160-4f84-90e1-b143c08fc8a9`, papel `apply-coluna`, par solicitado `gpt-6.1-sol/high`; observação final e coleta deste filho pertencem ao pai. Não foram iniciados outros agentes, reviewers, coordenadores ou sessões externas.

## Falha real preservada

A [qualificação diagnóstica TUI → exec](dedicated-diagnostic-pass-20261018.md) permanece histórica e íntegra: coordenador `01a14c6d-8e42-79d3-bd0e-db78be7c3aca`, contexto próprio e ambos perfis/probes qualificados. Isso não prova revisão de produto.

Na tentativa produto `dedicated-review-0567e02596a31deef8edcf80.package.json`, o lançamento terminou exit0 e a coleta recusou `review_launch_source_invalid`. O evento nativo do coordenador ordinal133 registra o preflight exato, exit1, `review_session_unavailable` e ausência de diretório temporário utilizável. A consulta canônica de Status dependia de escrita/cache/rede dentro do coordenador somente leitura. Nenhum parecer foi aceito. O pai voltou a Em desenvolvimento via T10; não houve alternância de permissões nem alteração de fontes para fazer o gate passar.

## Candidato inativo

Pacote `.cursor/tmp/card-1098-readonly-preflight-fix/`, com três candidatos em `files/`: `codex_review_session.py`, sua suíte e `docs/codex-review-qualification.md`. Snapshots `before/`, patch, hashes, verificador e integração única pelo gerador preservado do consumidor. Adapter ativo, manifesto ativo, trust, conta, FSM, Design/digest aprovado e evidências runtime foram preservados.

O principal executa `stage_check_command` isolado após Code Review, consultando Status autoritativo pelo provider canônico. O launcher exige sua origem nativa completa ligada a pacote/wave/card/branch/principal/turno, revalida a rota e consulta Code Review novamente imediatamente antes do exec. Receipt de lançamento é exclusivo; não se copia/renova TTL. Falha de consulta fica específica (`review_stage_query_failed` ou `review_stage_status_unavailable`), e mudança de Status bloqueia antes do lançamento.

O pacote fixa também hashes do provider/dependências diretas de Status e do overlay de autoridade do board. A verificação RO lê esses bytes sem importar o provider ou interpretar o overlay; mudança de código/autoridade invalida a tentativa.

O preflight do coordenador somente lê pacote, fonte nativa da consulta, receipt, hashes e binding local. Esse caminho não importa Guard/GraphQL nem usa rede ou grava temporários/cache/receipts/bytecode. Confere janela fixa de 120s ao final dos demais pré-requisitos, antes de ready. Registra que verificou a prova; não alega ter consultado GitHub no filho. Atestação interna completa permanece unavailable.

A coleta posterior revalida fonte/digest/ordem da consulta, receipt e hash devolvido pelo launcher, mais os intervalos nativos de lançamento/preflight. Revalida a frescura no horário original; uma revisão longa não renova TTL nem invalida automaticamente evidência histórica. A falha estruturada nativa do preflight mantém seu código específico, em vez de ser mascarada por `review_launch_source_invalid`.

Outro obstáculo identificado: `principal_preflight` validava os bytes atuais de todos os pacotes históricos antes de selecionar o mais novo. O candidato seleciona o último header selado daquela sessão/root e depois valida integralmente somente o pacote selecionado. Preserva tentativas antigas que fixam código anterior; pacote atual divergente ou seleção ambígua continuam recusados.

## Verificação e limites

Há negativos para origem ausente/duplicada, JSON copiado, outro pacote/turno/card/branch, Status ausente/alterado, horários ausentes/futuros, expiração inclusive durante os demais pré-requisitos, receipt alterado e reuso de tentativa. Um subprocesso novo executou o preflight produto completo com importações frias e auditoria que nega toda escrita, mutação, temporário/cache/rede e subprocesso além de `git rev-parse` local. Exige SQLite `mode=ro`, zero tentativas de escrita mesmo se silenciadas e ausência de import Guard/GraphQL. O binding git usa repositório descartável apontando para objeto existente, sem criar commit.

Esse positivo e os demais são **testes de contrato**. Não qualificam o runtime novo, não produzem reviewers de produto e não substituem o próximo ensaio do pai. A regressão combinada final teve **316 passed**; o último ajuste de diagnóstico de falha nativa teve **2 passed** focados. Quatro avisos pytest são de opções de configuração já existentes no ambiente. OpenSpec strict, manifesto ativo e comparação dos arquivos ativos aos snapshots before passaram. Receita, logs e hashes ficam no pacote.

Pacote final verificado, ainda `integrated=false`, `trust=not_changed`; `git apply --check` PASS. Manifesto SHA-256 `c6f05581872903b0bf72fd26061c91c12950e985e7e7c9b815329693789076e3`; patch SHA-256 `c5ea71f96513d3be574e42a380d3cfe921646ddcc211163e1cb68f6630aed70c`. Três arquivos candidatos; pin-base v1.1.22. A integração única usa o gerador preservado do consumidor e nunca copia manifesto do nucleus.

Após coleta deste Apply, o pai verifica/integra com `verify_package.py --integrate`, revisa confiança pertinente e cria bootstrap/pacotes novos, repetindo contexto/probes/qualificação da rota com os hashes novos. Não editar pacotes/digests/traces históricos. Só depois preparar o diff final, T9 e stage-check/launch nativos. Tasks 3.3/5.4/6.3 e aceites restantes continuam pendentes; progresso conservado **23/35**. Distribuição 4.5/6.4 continua pendente por `target_outside_binding`, sem contorno.

Proxies: design 4067 palavras; HTML gerado/copiado N/A; spawns deste filho 0. Proxy modelo: apply-coluna → GPT-6.1 Sol (`gpt-6.1-sol`), esforço solicitado high. Observação runtime não foi inferida dessa captura.
