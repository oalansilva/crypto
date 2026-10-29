# #1098 — Apply da onda inválida, 18/10/2026

Nova entrada Em desenvolvimento via T10 confirmada pelo pai. Único filho Apply dessa entrada. Pacote inativo `.cursor/tmp/card-1098-review-wave-fix/`; integração pelo pai após retorno, sem mudança de adapter ativo ou Design por este filho.

## Origem verificada

Tentativa produto `dedicated-review-508bcdce41382b390ddf5589.package.json`, coordenador `01a14c95-09d4-70d1-8642-42e0480969a4`. O trace original tem dois `CommandExecution` do mesmo preflight, ordinais 149/164, turno `01a14c98-94c6-7c83-90f6-7f09d9a1f939`, ambos ready/review/Code Review com o receipt `c6d0dc7c7904d4e8839cc27a5d073ed76c47c58b18cd6c37bbed614b5b93b2ce`. A coleta recusou `review_launch_source_unavailable`. O retorno plaintext 226 registra probe duplicado após truncamento e ausência de parecer; o retorno 273 traz os três achados confirmados contra o diff/base. Não constitui onda válida.

`inspect_review_metadata.py` extrai somente esses comandos e retornos finais plaintext, e metadata dos primeiros resultados dos dois filhos de produto. Seus `aggregated_output` têm 65275 caracteres e JSON inválido; o retorno nativo da ferramenta também está truncado. O extrator não abre planos de qualificação, expõe marcadores C/S ou decodifica blobs. `review-native-metadata.json` preserva paths, ordinais, hashes e limites das observações; fontes originais não foram editadas.

## Implementação candidata

- Preflight uma vez no coordenador; probe uma vez como primeiro comando de cada reviewer. Duplicatas continuam recusadas. Budgets explícitos e um resultado por saída.
- Probe curto com deny/readback; diff pequeno inline, grande em chunks de 4096 caracteres por helper `read` sem tentativa de escrita. Mesmo path/SHA/plano/child; todos os chunks necessários antes do payload.
- Verificação do `CommandExecution` e da chamada/retorno correspondente de ferramenta com JSON inteiro entregue. Stdout logado sem retorno completo não prova entrega. Cobertura nativa completa, reconstrução dos bytes/digest; manifesto, resumo, declaração, partes sintéticas/truncadas/omitidas ou posteriores ao payload falham.
- Perfis nomeados usam verificação inicial do helper. `verify-wave`/checklist somente no principal após ambos os payloads e coleta, sem dispensar nenhuma prova do filho.
- Restaurados `host_client()`/nomes de ancestral e registro Cursor/OpenCode, comparação do pai observado Claude versus captura claude/execucao em T16 (`--capture` e parâmetros internos), e tokens parseáveis de T5. Preservadas as mudanças Codex de preflight e I4; FSM e outros contratos não são ampliados.

## Verificação e limite

Regressão final **567 passed**, mais teste suplementar **1 passed** acrescentado durante a execução (total **568**). Quatro avisos pytest de configuração preexistentes no ambiente. Comandos exatos e resultados estão em `test-results.txt`, `test-command.txt`, `supplemental-test-results.txt`, `supplemental-test-command.txt` e `validation-results.txt` do pacote, ligados por hashes ao manifesto. OpenSpec strict e manifesto ativo PASS.

Casos incluem 700740 bytes, truncamento em cada camada, retorno entregue ausente/divergente, cobertura incompleta/sintética, unicode/read sem writes, dois perfis sobre mesmo artefato em partes, negativos dos três gates restaurados e suíte existente de settings/default/tier/fronteiras e preflight produto sob auditoria sem writes/cache/rede. O teste suplementar executa a função real do probe grande, lê depois todos os chunks e confirma uma única tentativa de escrita; a negação é uma fixture explícita. Fixtures T5 positivas agora têm os tokens obrigatórios.

São testes de contrato; nenhum reviewer/coordenador novo foi lançado. A nova versão exige integração pelo gerador do consumidor, revisão pertinente e novo bootstrap/contexto/probes/rota/review pelo pai. Pacotes e hashes históricos não são reescritos para reutilizar qualificação. O próximo preflight vivo e a onda de produto permanecem pendentes, incluindo eventual limitação de orçamento/contexto que deve recusar parecer em vez de afirmar leitura integral.

Progresso **23/35** preservado. Tasks 3.3/5.4/6.3 e aceites QA não foram marcados; 4.5/6.4 continuam parciais e a distribuição nucleus permanece negada por `target_outside_binding`, sem contorno. `internal_context_attestation=unavailable`. Sem process_event, commit/push, trust, alteração de conta/permissões, ou novos agentes/sessões por este filho.

Proxies: Design 4067 palavras; HTML gerado/copied N/A; spawns deste filho 0. proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol), esforço high da captura original `0826730d-d4e4-48a4-bc70-08236ea91625`; observado depende da coleta nativa do pai.
