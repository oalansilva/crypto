## Why

`.env.binance` está trackeado em `origin/develop` (e ainda em `origin/main`) com `BINANCE_API_KEY` / `BINANCE_API_SECRET` de operação, enquanto o `.gitignore` não cobre esse ficheiro. P0: tirar o ficheiro do tip de develop, impedir reincidência via gitignore, e deixar de usar `.env.binance` local como fonte de verdade (vars no `.env` raiz, **reutilizando as chaves atuais**).

**Ajuste Alan T6 (2026-08-26):** NÃO gerar chaves novas e NÃO rotacionar/revogar neste card. Rationale: repositório privado (não é vazamento público tipo clone anónimo de repo open); as API keys **não têm permissão de saque** (withdraw).

## What Changes

- Adicionar ao `.gitignore` o padrão `.env.*` com allowlist dos examples já trackeados: `.env.binance.example`, `.env.docker.example`, `backend/.env.example`, `frontend/.env.example` (exceções `!**/.env.example` se necessário para cobrir os examples sob pacotes).
- Remover `.env.binance` do índice Git (`git rm --cached`) e do tip de `origin/develop` via PR deste card. **Não** recriar `.env.binance`.
- Home canônica do secret de operação: `.env` na raiz do checkout (já gitignored / já é o loader). Runtime já lê via env (`config.py` carrega `backend/.env` e `.env` raiz; serviços não carregam `.env.binance` por nome) — **não** acrescentar loader para `.env.binance`.
- Ops: se as vars ainda só estiverem em `.env.binance` local, migrar `BINANCE_API_KEY` / `BINANCE_API_SECRET` **existentes** para `.env` raiz DEV/PROD e deixar de usar `.env.binance` local — **sem** gerar par novo na Binance.
- Done com: tip `origin/develop` sem `.env.binance` + gitignore impede reincidência + ops deixa de usar `.env.binance` local (vars no `.env` raiz reutilizando chaves atuais). **Não** exige chaves antigas rejeitadas pela API.

Não entra: gerar chaves novas; gravar novas no `.env` raiz por causa de rotação; smoke AC5 ligado a chaves novas; revogar antigas + evidência de rejeição pela API Binance; qualquer gate pré-merge de rotação; rewrite/purge de história (BFG, filter-repo, force-push); limpar tip de `origin/main` neste card (main herda no release); secret manager; `Environment=` no systemd; mudar loader para ler `.env.binance`; cifrar `api_secret` (#692); fail-closed JWT (#684); rotas públicas (#685/#686); UX formulário credencial; colar valores de chave/secret em issue/chat/evidência/log.

**UI impact: none.** Ops/git/secrets; nenhuma superfície visual. Prototype N/A.

## Capabilities

### New Capabilities

- `env-binance-git-hygiene`: remoção de `.env.binance` do tip de develop, padrão `.env.*` no `.gitignore` com allowlist de examples, e home canônica operacional em `.env` raiz (reuso das chaves atuais; sem gate de rotação).

### Modified Capabilities

- (nenhuma) — specs de runtime Binance / balances continuam a ler `BINANCE_API_KEY` / `BINANCE_API_SECRET` do ambiente; este card só remove o ficheiro trackeado e endurece o gitignore.

## Impact

- Git: `.gitignore`; `git rm --cached .env.binance`; tip de `origin/develop` após merge.
- Ops: migrar vars existentes para `.env` raiz em DEV e PROD se ainda só estiverem no ficheiro local; deixar de usar `.env.binance` local; **sem** rotação Binance.
- Runtime: sem mudança de código de produto; confirmar que nenhum unit/systemd/loader referencia `.env.binance` por nome (já é o caso: `config.py` só `backend/.env` + `.env` raiz; candle-writer faz `source` desses dois).
- History: blobs antigos e `origin/main` podem ainda ter o path até o release — aceito neste card (repo privado; keys sem withdraw; sem gate de revogação).
- Frontend/UI: nenhum.
