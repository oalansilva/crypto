# #1098 — distribuição concluída e reconciliação documental, 18/10/2026

Continuação documental do mesmo Apply-coluna, ainda Em desenvolvimento. Captura original `0826730d-d4e4-48a4-bc70-08236ea91625`, gpt-6.1-sol/high preservados; o pai informou a coleta/revalidação completed/payload da continuação anterior. Nenhum novo nascimento, sessão, transição, commit/push ou retuning por este filho.

## Distribuição real e integridade

O operador executou `deliver.py --apply` em terminal comum. O receipt real em `.cursor/tmp/card-1098-consolidated-delivery/distribution-receipt.json` registra `result=distributed`, `published=false`, pin-base `v1.1.22`, aplicação canônica seguida de redistribuição ao consumidor e hashes reais por payload. Este filho leu o receipt e executou, **antes das mudanças documentais**, `python3 -B .cursor/tmp/card-1098-consolidated-delivery/deliver.py --applied`, que retornou `verified`, `applied=true`, `writes=false`.

| Artefato | SHA-256 |
|---|---|
| Pacote/manifest.json | `83d27a47eed4f91966d92acf2785f9dbb120a0cefe7233bce829f318cfe2678b` |
| Receipt real | `e3bdbf77d5cca469c34317efe79e32fbf2c430c6bcbc50245cc9ce67a9298456` |
| Manifesto consumidor gerado localmente | `bfcf715275cb5e7be42df69c2d9db6ca6b4a8d6419331dbe997ba7b13888f15b` |
| Design aprovado preservado | `685305bec5e7664246b6304cfb9b24ee0f930ab53db45a7c171fc4124677d9b3` |

Raízes verificadas: nucleus `/srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos`, consumidor `/srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos`. As 25 relações do receipt foram conferidas pelo verificador contra bytes reais: 18 exatas, seis com mapeamento explícito de links de prova em docs e uma por `CODEX_CLIENT_CONTEXT`, preservando as demais partes do paging de cada destino. O mapeamento documental pode ser identidade quando o link não está presente; não se afirma igualdade de arquivos inteiros onde há transformação/componente.

O instalador canônico e particulares de cada árvore foram preservados; a dependência `design_token_gap` foi entregue. O manifesto do consumidor foi produzido por seu gerador local; nenhum adapters.json foi copiado do consumidor ao nucleus. Não se criou overlay no nucleus, mudou conta/FSM/gates humanos ou publicou novo pin. A recusa anterior `target_outside_binding` foi resolvida pela ação legítima do operador, sem contorno pela sessão agente. Os snapshots/manifestos selados continuam descrevendo a entrega executada.

## Trust separado e aceites 4.5/6.4

O campo `trust=not_changed_operator_review_still_required` do receipt descreve corretamente o helper: ele não registra confiança. **Depois da entrega**, o operador executou `trust --record` separadamente. O pai confirmou `trust --status` Codex com `reviewed=true`, `manifest=true`, listas missing/divergent vazias e adapter `d174776e2c16a162b949a392fd56c4e9c73aea5ce235fa2be01856bb3a7b8d6c`. O prefixo R informado pelo pai é `978b249ffe49`; não se inventa o restante do digest. Este filho não executou nem editou trust.

| Task | Aceites satisfeitos |
|---|---|
| 4.5 | Critério revisado implementado após os gates canônicos já registrados; runbook/docs/matriz e preflight/proxy/verify-wave separam contrato, chamada/ensaio empírico e atestação interna unavailable. Testes reexecutados para as alterações; novo delta distribuído realmente nucleus→consumidor, com hashes, manifesto local e revisão de trust pelo operador. Não se reutilizou 4.4 como prova dessa distribuição. |
| 6.4 | Runbook/docs/matriz/testes atualizados para a coordenação e coleta novas; OpenSpec validado; distribuição/mapeamentos/manifesto conferidos nos destinos reais e trust pertinente confirmado. Conta, FSM, gates humanos, Design e evidências históricas preservados; internal_context_attestation unavailable. |

Logs selados da entrega: 66 testes de protocolo/probes, oito de integração de onda/perfis/preflight read-only/settings e 40 dos gates Cursor/OpenCode/Claude/T5/I4 passaram. A correção específica de serialização DEL recebeu seis casos focados, incluindo casos repetidos; o helper de entrega recebeu 16 testes em destinos descartáveis. Não se somam repetições como casos únicos. Auditoria prospectiva de imports canônicos e OpenSpec strict/manifesto ativo passaram. São testes de contrato/documentação; não equivalem à nova onda viva. Não foi necessário reexecutar código ou centenas de testes nesta reconciliação documental.

O benchmark local do pacote preservou o SHA do diff informado e reduziu 170→52 leituras por reviewer com limites JSON/retorno. Essa medição e os diagnósticos anteriores não qualificam runtime do código final nem dispensam provas reais de contexto, permissões, probes, payloads e verify-wave.

## Estado e desvio documental intencional

Somente 4.5 e 6.4 avançam, de 23 para **25/35 tasks concluídas**. Permanecem **dez pendentes**: 3.3, 6.3 e 5.1–5.8. O pai conduz novo bootstrap diagnóstico com código estável; esta nota não antecipa seu resultado, Review de produto, QA, App/IDE, interfaces/controles não observados ou substituição integral. `internal_context_attestation=unavailable` permanece.

A verificação `deliver --applied` ocorreu antes desta reconciliação. O tasks.md entregue tinha SHA `da313347beb6b0e6be48f4ff2382a7445cad85021337f8207fbee6af85466c63`; evidence.md tinha SHA `17e322723e15dba0f87787f520e2978c48f8d469ac9645fbac516aa477dd97fa`. As edições posteriores em tasks/evidence são um **desvio documental intencional**, e este novo arquivo não integra o pacote original. Não se reescrevem manifestos/before para esconder esse desvio e não se repete a aplicação. Uma nova comparação estrita do tasks.md ao payload entregue pode apontar essa diferença esperada; isso não revoga a comprovação já feita dos bytes compartilhados.

Esta continuação tem ownership apenas de tasks.md, evidence.md e desta nota. Código, docs compartilhados, skills, perfis, manifesto, pacote/receipt, Design/digest, nucleus/source, trust, conta e permissões não foram alterados por ela. Verificação documental final: 213 paths protegidos comparados por SHA-256, **zero alterações**, incluindo Design e pacote/receipt; exatamente os checkboxes 4.5/6.4 mudaram, contagem **25/35**. OpenSpec strict e git diff --check PASS. Não foram repetidos testes de código nem a aplicação/checagem estrita de payload após o desvio documental intencional.
