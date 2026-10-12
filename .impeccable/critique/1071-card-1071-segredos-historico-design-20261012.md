# Crítica independente de Design — #1071

Data: 2026-10-12 UTC. Papel: design-critic; uma rodada sem tela.
Estado recebido do orquestrador: Design, T3 aplicado.
Branch observada: `card-1071-segredos-historico`.
Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1071-segredos-historico`.
Escopo: contrato observável, cobertura e consistência do pacote; sem implementação ou auditoria de credenciais.

## Metadados requested versus observed

- Cliente solicitado: Codex CLI; faixa: juizo.
- Captura: `/tmp/card-1071-design-critic-birth-20261012T0405.json`.
- Attempt ID: `267561a7-69a3-4512-ba7c-f861a2d9f145`.
- Requested model: `gpt-6-astra`; requested reasoning_effort: `medium`; rótulo: GPT-6 Astra.
- Observed model (confirmado pelo pai após retorno): `gpt-6-astra`.
- Observed reasoning_effort (confirmado pelo pai após retorno): `medium`.
- Observed host/version: Codex CLI `0.162.1`.
- Fonte nativa: registros `session_meta` e `turn_context` de `/home/ubuntu/.codex/sessions/2026/10/12/rollout-2026-10-12T04-04-58-01a12e49-006f-7221-86bb-c81576157e9a.jsonl`; child id `01a12e49-006f-7221-86bb-c81576157e9a`. O filho retornou esses metadados como indisponíveis; o pai os confirmou no trace, sem inferi-los da captura. Gate de modelo comprovado.
- Entrega: completed com payload. Nenhum processo iniciado permanece em execução.

## Materiais e limites

Lidos os quatro artefatos de `openspec/changes/card-1071-segredos-historico/`: proposal.md, design.md, specs/historical-secret-remediation/spec.md e tasks.md. Consultados os contratos canônicos design-critic, covenant-flow, covenant-flow-environments e docs/crypto-overlay.md.

O estado Git mostrou a branch esperada e o pacote OpenSpec não versionado. Não foram lidos código de produto, configuração protegida, conteúdo do backup, valores de segredos, logs privados ou história contaminada. Não houve operação de ambiente, contato com suporte, publicação, rewrite ou mudança de estado. OpenSpec strict PASS é informação do autor/orquestrador, não teste repetido nesta crítica. As 14 caixas pendentes são trabalho futuro apropriado ao Design.

## Rubrica e evidências

Referências abaixo relativas ao pacote OpenSpec.

| Critério | Resultado e referência |
| --- | --- |
| Gate sem tela | PASS: design.md:5-12 traz UI impact, live_route e surface em linhas próprias, justificativa e Prototype N/A. |
| Escopo aceito | PASS: proposal preserva Problema, História, Entra e Não entra; design.md:16-28 inclui limpeza histórica no mesmo card e separa Done DEV de Pronto. #684/#687 não são refeitos. |
| Inventário e dados | PASS: design.md:32-40, spec:5-32 e tasks:9-12 cobrem versões, fontes, aliases, limitações e conteúdo do backup. Schema e scanner limpo não bastam. |
| Invalidação verificável | PASS: design.md:44-52 e spec:36-50 exigem prova por segredo, teste antigo versus novo e configuração carregada. Falha de rede ou mera diferença de valor não encerra achado. |
| Evidência sanitizada | PASS: design.md:32-38, spec:16-18 e tasks:4-5 impõem armazenamento restrito, allowlist e fixtures para campos/erros. |
| Preservação e concorrência | PASS: design.md:56-66, spec:54-67 e tasks:18 preveem trabalho commitado e não commitado, recuperação testada, refs esperadas, congelamento e parada em divergência. |
| Limpeza controlada | PASS: design.md:60-70 e spec:69-80 incluem blobs, mensagens, refs, clone independente e resíduos do provedor, sem promessa sobre clones externos. |
| Recuperação segura | PASS: design.md:52,77,87 e spec:78-80,91-93 vedam restaurar credenciais ou história comprometidas; falha parcial permanece congelada para correção. |
| Ambientes e autorização | PASS: design.md:26,66,82-85 e spec:82-98 mantêm homologação, release explícita, autorização concreta e validação PROD. Design não autoriza execução. |
| Fechamento rastreável | PASS: tasks:27-41 mantém obrigações no mesmo card após Done/archive. Preparação não finge execução; pendências impeditivas bloqueiam Pronto. |

## Fontes primárias

Consultadas em 2026-10-12:

- [GitHub — Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository): confirma prioridade de revogação, alteração de SHAs, risco de recontaminação, refs de PR somente leitura, limites de suporte e de eliminação de clones externos. O Design registra eventual recusa como bloqueio, sem prometer resolução impossível.
- [git-filter-repo — manual oficial](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt): referência declarada para rewrite dedicado e conteúdo/mensagens. Comandos finais e versões efetivas serão validados no Apply/ensaio conforme o pacote.
- [Gitleaks — repositório oficial](https://github.com/gitleaks/gitleaks): referência de varredura local; o pacote exige fixture e exportação por allowlist, sem confiar somente em redaction.

Esta crítica não comprova revogação, classificação do backup ou limpeza remota. A dependência de suporte é risco operacional já explícito, não omissão de Design. Não houve achado que justificasse inspecionar dados protegidos ou implementação de produto.

## Achados e decisão

- P0: 0 achados.
- P1: 0 achados.
- P2: 0 achados.
- P3: 0 achados.
- disposition: aceitar para submissão à Aprovação de Design; nenhum rework necessário.
- verdict: PASS de Design, limitado ao contrato revisado; não é aprovação humana, autorização de operação nem confirmação de remediação.

Teto aplicado: um autor + este crítico; não é necessário consumir o rework único. Nenhum detalhe de Apply foi elevado a bloqueio de Design.
