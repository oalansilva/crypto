## Context

#1098 está integrado por PR #1129 na base `1a06caec`. Seu registro final e `evidence/qa-cli-20261018.md`, apoiado por `evidence/ci-and-cli-acceptance-20261018.md` na change #1098, registram Review de produto, verify-wave/checklist e QA da rota CLI interativa no worktree → coordenador exec read-only, com 32/32 aceites desse recorte. Os resumos anteriores em `docs/codex-runtime-evidence.md` e `docs/codex-review-qualification.md` estão defasados quanto a esse fechamento. Essa prova histórica não cobre refinamento integral, principal exec independente ou toda a matriz de etapas/retomadas agora assumida por #1130. No #1117, `prepare` recusou `unverified` em `/source` por qualificação ausente no destino local. Na preparação deste Design, restaurar a referência íntegra e validar contexto resolveu essa camada, mas T3 recusou `unbound` em develop. Alan retomou nativamente o mesmo chat no worktree; o novo destino voltou a exigir diagnóstico. Esses diagnósticos de preparação não demonstram entrega CLI completa nem invalidam a rota já comprovada no #1098.

Base técnica: `codex_evidence.py` resolve qualificação em `destination(root)` e separa nomes por originator; relê fontes nativas e integridade. `codex_context.py` liga prova a sessão, contrato e binário observado pela ancestralidade do processo. `codex_review_session.py` já prepara coordenador exec read-only, continuidade e pacotes; sua prova não pode ser fabricada por shell. `process_event`, Guard e checklist são consumidores existentes. A implementação deve corrigir descoberta/orquestração sem substituir esses verificadores.

UI impact: none
live_route: N/A
surface: none

Não há tela ou rota do produto Cripto alterada. O contrato visível é operacional no terminal Codex CLI (TUI e exec); nenhuma URL de catálogo representa esta superfície.

## Goals / Non-Goals

**Goals:** todo o fluxo da criação até release autorizada, no terminal, com matriz real por etapa/rota; recuperação em sessões novas/retomadas; agentes nativos; Review automático sem alternância manual de permissões; atos humanos explícitos; procedência reproduzível.

**Non-Goals:** App/IDE, outros clientes, Auto, mudança da FSM, confiança automática, aprovação humana por agente, produção antecipadamente autorizada, fallback de etapa no pai. O briefing literal permanece em `proposal.md`.

## Decisions

### 1. Contrato de rotas do terminal

A rota principal é CLI interativa TUI: conversa, perguntas de refinamento, orquestração e handoffs permanecem no chat do card. Review lança exec automaticamente. A rota principal exec também pertence ao terminal e deve ser qualificada: exec → coordenador exec → dois filhos nativos. Não será transferida para #1128 nem declarada fora para fechar o card. Exec não inventa diálogo interativo: ao precisar resposta humana, retorna pergunta estruturada e checkpoint identificável, aguarda a resposta explícita do operador na mesma sessão nativa retomada e revalida estado antes de agir. O controle de execução do terminal pode retomar essa sessão; ausência dessa capacidade observada bloqueia essa célula da matriz. Não cria TUI/exec como novos clientes na FSM.

Cada rota exige suas próprias fontes de lançamento, seleção, contexto, sandbox, conclusão e retorno. Versão registrada é a do runtime, não a do PATH; mudança apenas de versão com schema compatível não obriga repetir qualificação de capacidade. App/IDE continuam unverified e fora deste card. A alternativa de anunciar apenas TUI ocultaria pendências CLI existentes.

### 2. Descoberta privada sem portabilidade falsa

Introduzir índice privado por conta para localizar qualificações de capacidade por superfície observada e schema do driver, com referências absolutas, digests e identidade de origem. O índice é localizador, jamais autoridade; registrar uma referência não qualifica nada. `prepare` consulta primeiro referência explícita válida, depois índice exato e descoberta dos destinos legados conhecidos. Conflitos de identidade/fontes recusam; não escolher arquivo mais recente por mtime. O verifier reabre proof, envelope, receipt e fontes originais antes de aceitar. Não copiar receipts para outra raiz como se tivessem nascido ali.

Qualificação de capacidade pode ser reutilizada entre worktrees quando a origem íntegra comprova a mesma superfície/schema. Qualificação operacional de contexto continua vinculada a chat/root/binário/contrato observado e não se transfere entre chats, raízes ou coordenadores. Probes de Review continuam vinculados a sessão/rota/perfis/diff conforme contrato. Births e snapshots imutáveis ficam associados à tentativa original. Nenhuma gravação global pode afrouxar `destination()` para permitir saída arbitrária ou symlinks: o armazenamento compartilhado terá validação própria de diretório privado da conta, escrita atômica e permissão restrita. Refs legadas são importadas somente depois da verificação, sem mover ou apagar a origem. Índice ausente/corrompido não significa sucesso; descoberta e diagnóstico autorizado produzem recuperação visível.

Alternativas rejeitadas: versionar proofs privados, copiar toda `.cursor/tmp` ou aceitar selo sem fontes. Todas confundem procedência com localização.

### 3. Preparação conduzida, com checkpoint e recuperação finita

Antes de evento dependente ou filho, o pai resolve `(q, bound_card, q_git)`, runtime, captura e provas. Se falta apenas capacidade/contexto, e o diagnóstico já está autorizado, prepara automaticamente o ensaio nativo sem produto/transição, coleta, qualifica e repete o preflight da operação original. Não pedir a Alan para executar sequência mecânica já autorizada. Cada tentativa de recuperação registra causa, escopo, etapa pendente e resultado; no máximo uma repetição automática por mesma causa e fontes inalteradas. Falha persistente retorna código e ação concreta, sem loop ou sucesso presumido. Fontes restauradas permitem recoleta da mesma tentativa; divergência exige novo nascimento.

`unverified` distingue referência ausente de fonte inacessível/inválida; `stage_capability_missing` aponta contexto atual; `worktree_mismatch` mostra raiz esperada e observada; schema incompatível identifica campo; trust/permissões incompatíveis apontam revisão/abertura necessária. Nenhuma recusa altera Status ou descarta arquivos. Handoff conserva failure original e sucesso posterior separado. Interrupção, payload vazio e modelo divergente nunca passam por completed nominal. Filhos divergentes não são retomados; artefatos podem ser insumo de filho novo, jamais sua prova.

### 4. Vínculo nativo e atos do operador

Em `/source`, criação/refinamento são possíveis com card identificado e estado apropriado; escrita de produto continua negada. Ao iniciar Design, o pai prepara worktree correto preservando alterações existentes. `workdir` do shell e `--root` não mudam o cwd do chat. Rebind automático só será usado se API nativa exposta e ensaio confirmar `turn_context` ativo no destino. Sem essa capacidade, o único ato inevitável é Alan retomar o UUID do mesmo chat com `codex resume <UUID> --cd <worktree>` no terminal; o pai fornece comando literal obtido do contexto e checkpoint, depois revalida cwd nativo, board e provas. Não promete API inexistente, não exige copiar arquivos privados, não trata novo chat como continuação do antigo.

Confiança R/A e `/hooks` continuam atos humanos, separados da distribuição; seleção local mantém capturas por nascimento. T1, T7, T15 e T18 continuam somente Alan. Silêncio ou frase genérica não move coluna. Exec pausado por uma decisão humana conserva checkpoint, nunca resume com resposta inventada. Ação já autorizada não ganha um novo pedido de permissão por recuperação mecânica.

### 5. Review e retornos do processo

O principal gravável materializa diff exato e SHA, prepara capturas da onda e pacotes; o launcher inicia/retoma coordenador exec read-only automaticamente. O coordenador apenas orquestra dois perfis nativos no mesmo turno com contexto isolado. Preservam-se consulta autoritativa de Status, receipt de lançamento e janela de 120 segundos do protocolo atual: expiração gera pacote novo, não renovação artificial de TTL. Dentro do coordenador preflight só lê fontes fixadas.

Cada reviewer faz probe deny/readback, leitura integral comprovada do mesmo diff (chunks quando necessário) e devolve parecer completo. SHA divergente, chunk ausente, write permitido, filho faltante ou retorno incompleto bloqueiam. O pai coleta, grava proxies, executa `verify-wave` e checklist antes de commit. Nem principal nem coordenador fazem review. Pré-commit e fechamento são ondas reais distintas sobre seus intervalos. O fluxo de correção conserva teto 1+1 e residual, P0 interrompe; não criar terceiro ciclo. Pós-T18, reabrir branch sobre develop atual e seguir correção sem repetir T8.

### 6. Matriz de aceitação e progressão da evidência

Publicar matriz em documentação de evidência do card e comentário/Gist sanitizados. Cada linha contém rota, sessão nova/retomada, card e estado vivo, SHA/pin, captura, IDs nativos, resultado do gate, referência verificável privada e resumo público, recusas, pendência e próxima ação. Estados de relatório: planejado, diagnóstico, comprovado, bloqueado, aguardando ato humano; não são estados novos da FSM. Resultado de fixture é coluna separada e não promove etapa.

| Etapa | Prova positiva real em TUI e principal exec | Recusa/retorno exigido |
| --- | --- | --- |
| Criação e refinamento | card em Em Refinamento; filho grill, pergunta/resposta no mesmo chat, body correto; #1117 se estado ainda permite | card/estado errado; falta de resposta; prepare sem qualificação |
| T1 e vínculo | ação humana registrada; sessão nova em /source e nova no worktree; retomada com cwd nativo validado | agente tentando T1; root de shell diferente do chat |
| Design e crítica | autor e crítico isolados, artefatos strict, tokens, publicação e T5 | sem contexto atual; filho sem payload; tokens ausentes |
| T7 e Apply | aprovação de Alan, T8 e único filho Apply com captura e artefatos | pedido implemente em Todo/Design; modelo divergente; interrupção preserva trabalho |
| Review pré-commit e fechamento | principal gravável → coordenador read-only → par nativo; verify-wave e checklist | diff/identidade trocados, status expirado, permissões incompatíveis, leitura parcial |
| Correção | caso real do retorno previsto; nova onda dentro do teto, residual rastreável | P0 interrompe; terceiro ciclo não é iniciado |
| QA e integração | filho QA, checks do SHA, PR, T14, restart DEV e validação da URL | pending/no_pr/dirty não viram Done; retry após causa resolvida |
| Homologação e não homologação | T15 humano e comentário; em caso real T18 com motivo e retorno ao mesmo card sem T8 | silêncio ou agente não substitui Alan; sem motivo não reabre |
| Fecho/release | pedido próprio, pai execução observado, fecho-lote, guards, archive, PR/merge, deploy, Kaizen, sync e T16 | sem pedido, sem homologação, trust inválido ou post falho não publica/não vira Pronto |

Sessões novas nas duas raízes e retomadas são cruzamentos obrigatórios das rotas; não basta uma sessão ancestral aquecida. Exercícios negativos usam alvos descartáveis/consultas sem mutação indevida, com readback. Não fabricar reprovação humana ou produzir defeito real para obter T18: se não ocorrer num card autorizado, a célula fica aguardando ato humano, explicitamente impedindo alegação integral. Acompanhamento prossegue neste compromisso, não migra para #1128.

O checklist não pode exigir a própria release antes do primeiro commit. Tasks de implementação, testes, matriz preparada e provas possíveis vencem em precommit; provas do SHA commitado em postcommit; instalação canônica em postpin; provas de QA disponíveis até postqa. As marcações existentes não são renomeadas para mascarar release como QA. Homologação/release e eventual T18 futuro são critérios da matriz de aceitação, fora das tasks executáveis pré-commit. Após QA, o pai atualiza evidências no card; após ato humano e pedido de release, o chat de lote coleta e anexa prova com a mesma rastreabilidade. Done técnico e Homologado podem ser atingidos pelo processo normal com indicação explícita das células ainda não exercidas; não significam entrega integral comprovada. Somente todas as células obrigatórias reais e gates finais permitem essa alegação. Essa separação evita dependência circular sem dispensar nenhuma etapa nem impedir publicar o suporte necessário para exercitá-lo.

### 7. Procedência e ambientes

Mudanças genéricas nascem no nucleus; implantação reproduzível traz arquivos ao consumidor por pin/manifest. O Apply deve identificar checkout/tag/SHA reais do nucleus, revisar também `install.sh` quando afetado e registrar hashes de origem e destino. Não inventar tag antes da entrega. Reconciliar histórico de #1098/#1128 com adendo datado: CLI pendente está em #1130; App/IDE permanece fora. Não reclassificar diagnósticos como produto concluído.

O overlay lido aponta DEV `/srv/apps/dev/criptofarol/source`, URL `https://dev.criptofarol.com.br`, PostgreSQL `crypto_app_dev`; PROD `/srv/apps/prod/criptofarol/source`, URL `https://criptofarol.com.br`, PostgreSQL `crypto_app`. `./restart`, migração Alembic, build e health são derivados do overlay no momento da operação. QA/Done validam DEV; release usa pedido próprio, inventário de services menos oneshots, migração conforme runbook, SHA publicado, saúde pública, higiene de branches e sync main → develop quando aplicável. Este Design mapeia contratos; não opera ambientes. Instalar pin não concede trust, e revisão humana nova não é automatizada pelo índice de provas.

## Risks / Trade-offs

- [Fontes privadas removidas] → índice detecta referência quebrada, conserva falha e conduz diagnóstico autorizado; documentação pública nunca vira prova substituta.
- [Exec sem retomada/retorno nativo suficiente] → célula CLI bloqueada com motivo e correção neste card; não substituir por subprocesso que apenas imita agente.
- [Mudança do binário invalida contexto] → nova qualificação contextual automática dentro da autorização, sem invalidar capacidade por número de versão apenas.
- [Gates humanos/release não ocorrerem nesta sessão] → matriz continua pendente e linguagem limitada ao estágio comprovado; nenhum fecho integral antecipado.
- [Legado de specs/docs divergente do runbook atual] → corrigir somente contrato necessário com rastreabilidade, preservar lei FSM e seleção local corrente; nenhuma restauração de model-map histórico.

## Migration Plan

Implementar e testar no nucleus autorizado; consumir por pin com revisão de procedência; importar somente referências legadas revalidadas; ensaiar destinos novos sem estado privado local, ambas as rotas e recuperação. Trust alterado exige ato humano e sessão adequada. Distribuição não inclui traces, controle ou sentinela. Rollback restaura pin/manifest anteriores conforme fluxo autorizado e preserva registro de evidências, mas não declara compatíveis contextos de outro binário. Nenhuma alteração de banco é prevista.

## Open Questions

Nenhuma decisão de produto reaberta. Capacidades reais de rebind e retomada do principal exec precisam ser medidas no Apply; ausência é bloqueio técnico da célula, não autorização para reduzir o escopo. A ocasião de T18 e release depende dos atos humanos reais; a matriz explicita essa dependência.

## Impeccable

N/A: sem alteração visual, tela ou rota de produto; experiência operacional descrita em contratos e matriz do terminal. Crítica independente sem-tela e aprovação humana continuam obrigatórias.

## Design Critique

- P0–P2: nenhum defeito de produto, escopo ou contrato visível identificado.
- P3: separar no Apply os registros pré-commit e de fechamento agrupados na task 6.1; `after-commit` não posterga verify-wave/checklist exigidos antes do commit.
- disposition: P3 aceito como detalhe de Apply; nenhum rework necessário.
- verdict: aprovado pela crítica documental sem-tela; capacidades e aceitação integral continuam dependentes das provas reais da matriz.
