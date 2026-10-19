# Correção do pin v1.1.23 — pacote para o núcleo

Delta canônico sobre `v1.1.23`, commit `c10fb7cf50bb09c87f7da8734f92688df8b1b789`, árvore `740ca48994b452c642807cc87eb166261ba688e1`. Não é uma versão publicada. O código reconciliado está em `nucleus.patch`; `manifest.json` contém o inventário exato, hashes de origem/destino e árvore Git equivalente. Nenhuma árvore completa é duplicada neste pacote.

O pré-pin do consumidor é `cfaa6d949614b8d9b43b906e6b758530a5ef1287`. Restaurações exatas desse commit são identificadas individualmente no manifesto. `guard.py` combina o hardening anterior com o provider atual de autoridade externa. `process_event.py`, `process_authority.py`, índice/controller #1130 e seus contratos permanecem os da tag; não há overlay do Cripto no delta. A distribuição existente por `install.sh` continua copiando todos os helpers/testes e gerando o manifesto por último; a correção acrescenta a documentação Claude ao conjunto distribuído e à proteção contra colisão com `overlay_doc`.

## Conteúdo

- `nucleus.patch`: única alteração aplicável ao núcleo.
- `manifest.json`: hashes SHA-256 por arquivo, procedência, SHA do patch e árvores base/destino.
- `package.py`: reempacotamento determinístico; lê Git de origem e pré-pin sem editá-los, verifica a tag/base, faz apply-check e aplicação real numa cópia, comparando toda a árvore resultante com o candidato testado. Ignora caches/logs pelos paths rastreados da tag e pela lista explícita de arquivo novo.
- `README.md`: procedimento e limites.
- `validation.json`: comandos/resultados e hashes dos logs finais. Reexecuções sobrepostas ficam identificadas e não são somadas.
- `validation-logs/*.log`: saídas das execuções e inventários, incluindo falhas iniciais e suas rechecagens.
- `SHA256SUMS`: inventário/hash de todos os arquivos deste pacote, exceto ele próprio; verificar com `sha256sum -c SHA256SUMS` neste diretório.

O relatório de achados e provas está em `../../evidence/pin-correction-20261019.md`.

## Aplicar e conferir

O pai conduz a operação no núcleo sob seu próprio binding nativo/FSM. Exigir árvore limpa e a árvore base indicada; nenhuma instrução deste arquivo grava trust ou concede transição. O checkout dirty #1098 não participa.

```bash
git apply --check /caminho/absoluto/correction-v1.1.23/nucleus.patch
git apply /caminho/absoluto/correction-v1.1.23/nucleus.patch
```

Para reprodução descartável, extraia a tag com `git archive v1.1.23` para `<scratch>/base`, copie-a para `<scratch>/candidate` e aplique o patch no candidato. Ao usar uma pasta dentro de outro repositório, execute apply com `GIT_CEILING_DIRECTORIES=<scratch>` para impedir que Git descubra o consumidor ancestral e ignore paths por prefixo. Não aplique o patch nos adapters ativos do consumidor. Após validar/publicar uma revisão real do núcleo, o pai executa o pin pelo instalador; R/A e `/hooks` continuam atos humanos separados.

Reempacotar a árvore já testada, a partir deste worktree consumidor:

```bash
python3 openspec/changes/card-1130-codex-cli-fluxo-completo/implementation/correction-v1.1.23/package.py \
  --nucleus /srv/apps/dev/covenant-flow-worktrees/card-1130-codex-cli-fluxo-completo \
  --consumer . \
  --base .cursor/tmp/card-1130-pin-correction/base \
  --candidate .cursor/tmp/card-1130-pin-correction/candidate
```

Executar as invocações pytest de `validation.json` no candidato reproduz as verificações. Os testes usam contas, consumidores, traces e repositórios descartáveis. Eles não são Review/QA de produto nem aceitação nativa.

## Nova leitura dos reviewers

O probe permanece primeiro e único. Para diff grande, o helper retorna `next_read_command`; cada resposta de chunk retorna o comando seguinte, ou `null` na última. O reviewer copia o comando literalmente, com `workdir` igual ao cwd nativo indicado no prompt. Os comandos usam paths relativos curtos e não fazem escrita. O template permanece informativo. Não reconstruir path, inserir `./`/`../`, concatenar comandos ou repetir o probe. O coletor exige ordem consecutiva, argv literal, cwd/thread/turno/SHA, saída integral nas duas camadas nativas e deny/readback. O preflight bem-sucedido deve preceder os nascimentos em context/probe/review, com fontes/ordinais no mesmo turno. TTL, isolamento, autoridade externa e `verify-wave` permanecem obrigatórios.

As duas ondas históricas que falharam continuam falhas. A aplicação/publicação/pin/revisão humana e um ensaio nativo novo desse suporte ainda cabem ao pai. As sete tasks after-pin/after-commit/after-qa da change permanecem abertas; fixture não as satisfaz.
