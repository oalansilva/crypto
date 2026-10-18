# #1098 — correção consolidada da retomada, 18/10/2026

Continuação do mesmo Apply, captura/birth da tentativa `7139a39e-952e-4f36-9d67-3d2414742c6b`, sem retuning ou novo agente. O pai informou integração/revisão humana do adapter `662cefb9ded9e00bf89259949fec5583e58cee2a1a9fe860e077a451f907e7fb`, novo bootstrap com binding PASS e recusa `review_route_unqualified` esperada. A continuação context saiu exit0, mas a qualificação permaneceu recusada.

## Fonte inspecionada e obstáculos consolidados

Fonte `/home/ubuntu/.codex/sessions/2026/10/18/rollout-2026-10-18T00-22-28-01a14c63-737e-7802-8620-2f8b343cfd0e.jsonl`, coordenador `01a14c63-737e-7802-8620-2f8b343cfd0e`. Inspeção restrita a metadata/ordem/códigos de falha, sem expor conteúdo de S/C/prompts ou argumentos contendo marcadores. O trace, pacotes e digests não foram modificados.

1. Ordem real: contexto7/settings8, terminal25, settings26/27, started28/context31. Settings8/26/27 integralmente idênticos. Ambos os turnos registram v2, mesmo modelo/esforço/cwd e readonly efetivo managed/restricted/root-read/network-restricted. O coletor tratava os settings do intervalo como alteração tardia do turno anterior.
2. Comando49 chamou **inspect com context-package**, falhando `review_coordinator_identity_mismatch` antes do filho. O prompt context não fornecia o comando exato de preflight, ao contrário das ondas de probe/produto.
3. Os custom_tool_call exec14/39/47 eram chamadas de shell; nenhuma chamada nativa de spawn foi registrada. Portanto não existe origem de filho a adaptar/promover a partir dessa tentativa. Runtime v2 foi observado; configuração/listagem CLI não substitui essa observação nem comprova ferramenta/chamada disponível.

`native-resume-metadata.json` registra somente projeção permitida e hashes das linhas. `check_native_projection.py` validou permissões/ordem e a atribuição dos refs: bootstrap `{7,8}`, continuação `{26,27,31}`. Retorno explicita binding/context_qualification/route_qualification `not_evaluated`, zero spawns nativos observados e trace intacto. Não é uma nova sessão nem uma qualificação positiva.

## Implementação candidata

Pacote inativo `.cursor/tmp/card-1098-coordinator-resume-fix/`, três arquivos candidatos, snapshots before, patch/manifesto/hashes, verificador/integrador e receita. Adapter ativo/manifesto/trust/conta/FSM/Design preservados durante o filho.

Settings idênticos após terminal vinculado podem ficar pendentes entre turnos. São validados imediatamente contra o baseline seguro e novamente contra o próximo contexto efetivo; não autorizam trabalho/nascimento sem esse contexto. Mudança/ampliação/unknown/divergência mesmo transitória, terminal errado, evento tardio em turno ainda ativo ou ferramentas no intervalo sem novo turno recusam. Refs pendentes passam à próxima continuação e não mudam as fontes do bootstrap encerrado. Append futuro válido não retuna tentativas históricas.

O prompt context agora fornece comando exato `preflight --package <context-package>`, exige result ready/phase context/work_release diagnostic_only e solicita diretamente `collaboration.spawn_agent` com argumentos capturados. Falha de preflight ou ferramenta indisponível impede o filho; não se executa seu diagnóstico no coordenador ou shell. O preflight exige v2 observado no turno ativo. `inspect` permanece bootstrap-only e uso em outra fase recebe `review_action_phase_mismatch`.

O extrator nativo permanece rígido: custom exec/JavaScript/texto não substituem nascimento, retorno, filiação, modelo/esforço, fork none, completude/payload ou contexto. Novo formato requer fonte real; não foi inventada adaptação sem spawn observado. Gates humanos, Guard, dois reviewers/probes/mesmo diff, readonly contínuo e internal_context_attestation unavailable preservados.

## Testes, integração e limites

Os primeiros 19 testes focados passaram, cobrindo ordem real e negativos entre turnos, ancoragem histórica, preflight exato, runtime ausente e erro de fase. A regressão combinada terminou com **288 passed**, sem falhas/skips e quatro avisos pytest de configuração; inclui 20 casos novos e a recusa de custom exec como origem. Saída em `test-results.txt`, comando em `test-command.txt`. Validação de projeção, manifesto ativo, verificação do pacote e git apply --check: PASS. OpenSpec strict foi repetido após este registro.

Após coletar/verificar este retorno com o adapter ainda confiado, o pai pode integrar com `python3 .cursor/tmp/card-1098-coordinator-resume-fix/verify_package.py --integrate`, regenerando o manifesto pelo gerador preservado do consumidor, sem copiar adapters.json do nucleus ou gravar confiança. Preparar **novo bootstrap/pacotes** depois da revisão pertinente: os hashes de código/prompt antigos não devem ser editados para reuso.

Permanece pendente observar o filho nativo real, qualificar C/S da própria sessão e executar perfis/probes/rota/onda produto com todas as fontes. Exit0 do coordenador e metadata válida não encerram esses aceites. Nenhum novo agente/sessão externa, process_event, commit/push, alteração de conta/trust/modelo/Design ou promoção de qualificação foi executado por este filho.
