# #1098 — entrega consolidada inativa, 18/10/2026

Continuação do mesmo Apply-coluna, Status Em desenvolvimento confirmado pelo pai às 01:52 UTC, sem novo T8. Captura 0826730d-d4e4-48a4-bc70-08236ea91625 preservada; o pai informou proxy revalidado completed/payload/observed gpt-6.1-sol/high successful=true. Nenhum novo agente, reviewer ou sessão foi lançado por este filho.

## Distribuição preparada, ainda não executada

Nucleus: /srv/apps/dev/covenant-flow-worktrees/card-1098-codex-agentes-nativos, HEAD 14aa9d6f046219b6a00a5f89333c50a68b3103ef. Consumidor: worktree homônima de crypto, HEAD bf7cd24595f3216f91dcf3eb576f91780252e86b. Foram registrados dirty inicial, snapshots e hashes por destino. Dos 24 payloads iniciais, 3 já eram iguais, 8 estavam ausentes no nucleus e 13 divergiam; acrescentou-se a dependência mínima design_clone_gate.design_token_gap ausente no nucleus. A auditoria prospectiva de imports contra libs reais do nucleus passou, sem writes externos.

Install.sh canônico conserva sua alteração anterior (preflight de codex_binding); geradores, cf_shim, resolve, manifestos de origem, overlays, FSM, AGENTS e Design ficam protegidos por hashes. No paging canônico só se transfere CODEX_CLIENT_CONTEXT; o comportamento Claude/app_folder_note próprio do consumidor é preservado. Links novos de prova em docs canônicos são mapeados a cópia sanitizada em docs/evidence, sem transportar OpenSpec/Design ao nucleus.

O helper deliver.py do pacote só ativa em terminal comum do operador, na raiz real do nucleus; recusa env/ancestral de agente e não oferece bypass. Confere os dois destinos completos antes de escrever. Aplica o candidato canônico e então lê a fonte real para redistribuir ao consumidor, com mapeamentos explícitos e verificação de bytes. Regenera apenas o manifesto local do consumidor por seu gerador preservado, no pin-base v1.1.22; não copia adapters.json, cria overlay, instala hooks, registra trust ou publica pin. Produz receipt apenas após sucesso real. Foi testado somente com destinos descartáveis dentro do pacote; target_outside_binding não foi contornado. Nenhuma procedência canônica concluída é alegada agora.

## Diff real e páginas limitadas

Ensaio local no SHA-256 226eb571d1d5883ac5171e006101ead3da32b4b755efe93fa1fa669865042c95: 700740 bytes, 693766 caracteres e 7994 linhas, sem excluir arquivos/bytes. Resultado: 170→52 leituras por reviewer, 340→104 no par (-69,41%). Maior JSON nativo medido 14494 bytes; maior envelope limitado 16689 bytes. O código limita JSON UTF-8 a 16000 e o retorno externo serializado com escapes a 28000, com reservas de metadata e budgets 20000/32000. Aspas, barras, controles (incluindo DEL), BMP e emojis foram reconstruídos byte a byte; Unicode extremo pode exigir mais páginas para manter os limites. Não é qualificação nativa da rota ou uma promessa do tamanho do próximo diff rematerializado.

As provas continuam completas em CommandExecution e chamada/retorno nativo entregue ao modelo. Mesmo path/SHA/plan/child, um probe/deny/readback por reviewer, todas as páginas anteriores ao payload, cobertura e digest integral, duplicatas/truncamentos/omissões recusados. Perfis, prompts e documentação são candidatos inativos coerentes com v2. O materializador não foi alterado; a próxima revisão deve incluir install.sh canônico pela opção existente --nucleus/--nucleus-base.

## Verificação e pendências

Logs/comandos/checksums estão no pacote consolidado: testes focados de probe, integração da onda/preflight read-only/default settings, gates restaurados Cursor/OpenCode/Claude/T5, serialização adversa e integração de dois destinos em fixtures. README/manifestos registram contagens e resultados finais. Não se reexecutou a regressão de centenas de casos já aprovada sem motivo.

Tasks 3.3/4.5/6.3/6.4 e aceites vivos permanecem pendentes, progresso 23/35. O próximo fato necessário é aplicação legítima do pacote pelo operador/contexto de origem e verificação do receipt; depois, trust pertinente separado e novo ciclo real pelo pai para os hashes finais. Nenhum contexto/interface não observado foi marcado; internal_context_attestation=unavailable. Sem process_event, commit/push, writes em adapter/perfis/skills/manifesto ativos, Design/digest, seleção, conta, permissões, FSM ou fontes runtime por este filho.

Proxies: Design 4067 palavras; HTML gerado/copied N/A; spawns deste filho 0. proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol), esforço high original; observado revalidado pelo pai, sem retuning.
