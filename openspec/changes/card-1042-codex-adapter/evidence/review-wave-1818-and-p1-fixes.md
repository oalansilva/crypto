# Onda de review #1042 e correções dos P1

Data: 2026-09-25 UTC. A onda `card-1042-review-1818` usou o artefato imutável `.cursor/tmp/review-diff.patch`, SHA-256 `87ca32e0fb88449132d65cc0277d1503feeee8290465373ca1fe2cd91f29cccf` (200199 bytes). Verifiquei que o artefato ainda tem esse digest depois das correções; ele descreve o intervalo pré-correção e não é apresentado como review do código atualizado.

O pai registrou dois `codex exec` distintos, ambos Codex CLI `0.156.1`, sandbox `read-only`, status `completed`, payload retornado, execução observada `gpt-6-luna/max` e mesmo `review_diff_sha256`. `diff-reviewer`: child `01a0d9ca-2264-7410-90d6-6b8596eb91d5`; `code-reviewer`: child `01a0d9ca-2257-76e0-a3a5-51d63714fb8f`. Os pareceres vieram separados. `codex_review.py verify-wave --map-root <raiz do consumidor>` passou usando o mapa único do consumidor.

A revisão reportou quatro P1s, corrigidos nesta entrada Apply:

1. Cinco gravações temporárias usavam nome previsível, `write_bytes` e `replace`, permitindo que symlink preexistente desviasse a escrita. Os callsites agora usam `codex_fs.atomic_write_bytes()`, que cria um sibling aleatório e exclusivo com `mkstemp`; testes deixam um symlink no caminho antigo e verificam que o arquivo apontado permanece intacto em hooks, review diff, roles, skills e pin do mapa.
2. `codex_review.capture()` passava o `base` diretamente como argumento de `git diff`. Agora resolve e valida o commit com `git rev-parse --verify --end-of-options` antes do diff. Regressão com `base=--output=<sentinela>` confirma erro visível e bytes intactos.
3. `codex_adapter` convertia JSON inválido e payload não objeto em `{}`, e permitia tool desconhecida. Parsing inválido/shape inesperado agora gera deny visível em `PreToolUse`; tool desconhecida também recebe deny se o adapter for invocado. A documentação mantém o limite de que hosted routes podem não invocar o hook.
4. `codex_proxy.record()` agora resolve o par vigente da faixa no mapa do `repo_root`. `successful` exige que o pedido corresponda ao mapa válido atual além de pedido/observado coincidirem; mapa ausente, par obsoleto ou proibido fica registrado como falha com motivo. O mapa do consumidor não foi alterado.

Testes focados: `78 passed`. Suíte completa `scripts/process-fsm`: `586 passed`. Os P1s foram corrigidos após o intervalo revisado; a captura da versão atual fica para a segunda onda coordenada pelo pai.

## Prova complementar de juízo (não fecha 5.3)

Sessão CLI nova `01a0d9d3-8acc-7123-9ddf-9eed5411d1d9`, sandbox `read-only`, retornou payload `JUÍZO_1042_OK`; a orientação mostrou `Em desenvolvimento` e `turn_context` observou `gpt-6-sol/high`. Artefatos: `/tmp/card1042-juizo-session.jsonl` SHA-256 `8397c639e2ca449fd06b89c6d14c3cc151f926630978ed4a76cc945838b7b612` e `/tmp/card1042-juizo-final.txt` SHA-256 `c06f842713215706294fac3d3371a49d2d82de9e75b030cd05fbd9667cb10162`. Isto comprova apenas esta execução Juízo; isolamento/retorno de QA depende de T11 e checks, por isso 5.3 continua aberta `after-qa`.
