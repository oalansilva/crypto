# Dependência nucleus — histórico do primeiro handoff

Owner: repositório `oalansilva/covenant-flow`, separado de crypto#1080 e com seus próprios gates. Checkout inspecionado read-only `/srv/apps/dev/covenant-flow`, HEAD `de9004538232a1ee7aa8d681535bd1d6e3242a45`. `install.sh` atual não exige mapa legado nem chama codex_models/pin-map e não injeta pares: não há esses trechos a remover. Copia `.cursor/` por paths enumerados e não inclui model-policy.yaml; copia scripts/process-fsm inteiro, mas a fonte nucleus ainda precisa receber os novos mecanismos. Não contém o pacote Codex atual.

`nucleus-installer-proposed.patch` é proposta textual mínima contra esse HEAD, não aplicada: preflight de existência da política e cópia da política para consumidor. Não resolve sozinha transporte/integração Codex, publicação/pin e testes. Fonte deverá receber policy/resolver/adapters consumer e as mudanças de contrato, sob autorização/estado próprios. Não foram rodados testes externos nem alterado qualquer arquivo nucleus.

Nos worktrees nucleus de #1042, `install.sh` contém calls `--preflight-pin-codex-map` (linha 121) e `--pin-codex-map` (157). Referência inspecionada: `/srv/apps/dev/covenant-flow-worktrees/card-1042-review-parent-sandbox`, HEAD `4d5b9b5fd21f16255f798cb2b861499232fcea70`. Se esse trabalho vier a compor a próxima fonte, retirar calls antigas ou usar helper de compatibilidade sem escrita; não concluir que esses calls existem hoje no checkout principal. Merge/transporte deve preservar preflight de hooks/roles/bridges e não ler/gravar seleção da conta.

Consumer entrega facade compatível sem leitura/escrita, política versionada, mechanisms/adapters e testes instalador atualizados. Os quatro testes installer continuam skipped porque consumer não contém install.sh. Devem executar no nucleus após implementação: pin sem mapa/seleção local, pin com bytes locais existentes (até schema inválido deve ficar byte a byte intacto), colisões de hooks/bridges abortando antes de escrever, instalação política/resolver/roles/adapters, repetição idempotente e sem escolhas default. Os testes existentes de vendor/hooks/bridges foram mantidos.

3.4 permanece unchecked e sem marker de deferimento. `_check_tasks(..., phase="precommit")` retorna `tasks.md pending`. Nenhum review/commit é autorizado por este handoff. 4.4 conserva after-qa apenas para runtime real; cobertura OpenCode positiva indisponível deve permanecer residual explícito.

## Resolvido na retomada autorizada

O usuário pediu concluir pendências; Design#1080 abrange installer, sem gate/card extra por repo. Implementado no worktree nucleus do mesmo #1080 de de900453. Installer integra mecanismos/política/pacote Codex, preservando preflight e escolhas. 126 testes focados passaram, incluindo seis installer reais. Patch proposto anterior é histórico; alteração efetiva é o diff nucleus. 3.4 completa. Checkout principal e branches1042 não alterados. 4.4 permanece after-qa, sem P0 inferido.
