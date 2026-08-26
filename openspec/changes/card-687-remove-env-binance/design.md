## Context

Card [#687](https://github.com/oalansilva/crypto/issues/687) (P0, Segurança). Issue grelhado: `.env.binance` está no índice Git e no tip de `origin/develop` (blob presente em `HEAD`; `git check-ignore` não cobre o path). O `.gitignore` lista `.env`, `.env.glassnode`, `.env.docker.local` e `backend/.env`, mas **não** um padrão que pegue `.env.binance`. Examples trackeados sem valores reais: `.env.binance.example`, `.env.docker.example`, `backend/.env.example`, `frontend/.env.example`.

Runtime: `backend/app/config.py` faz `load_dotenv` só de `backend/.env` e `.env` na raiz (`override=False`). Serviços Binance leem `BINANCE_API_KEY` / `BINANCE_API_SECRET` via `os.getenv` / env. Units systemd em `ops/systemd/` fazem `source` de `backend/.env` e/ou `.env` raiz; **nenhum** referencia `.env.binance` por nome. Não há loader explícito desse ficheiro no código de produto.

**Ajuste Alan T6 (2026-08-26) vs grelha original:** a grelha e o design anterior exigiam rotação/revogação Binance pré-merge. Alan devolveu o design e tirou rotação do escopo Apply/Done (ver Decisions + Risks). Motivo: repo privado; keys sem permissão de saque (withdraw).

**UI impact: none.** Trabalho de ops/git/secrets; nenhuma tela, rota UI ou superfície visual nova ou alterada. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Remover `.env.binance` do índice e do tip de `origin/develop` via PR deste card (`git rm --cached`; não recriar o ficheiro).
- Endurecer `.gitignore` com `.env.*` e allowlist dos quatro examples já trackeados.
- Home canônica do secret de operação: `.env` na raiz do checkout (já gitignored / já é o loader). DEV e PROD passam a viver aí; deixar de usar `.env.binance` local — migrar vars **existentes** para `.env` raiz se ainda só estiverem no ficheiro local (**sem** gerar par novo na Binance).
- Done com: tip `origin/develop` sem `.env.binance` + gitignore a impedir reincidência + ops deixa de usar `.env.binance` local (vars no `.env` raiz reutilizando chaves atuais). **Não** exige chaves antigas rejeitadas pela API.
- Confirmar (sem alterar loader) que runtime/systemd **não** carregam `.env.binance` por nome.

**Non-Goals:**

- Gerar chaves Binance novas; rotacionar ou revogar chaves; smoke AC5 ligado a chaves novas; evidência de rejeição pela API; gate pré-merge de rotação.
- Rewrite/purge de história (BFG, filter-repo, force-push).
- Limpar tip de `origin/main` neste card (main herda no release).
- Secret manager, `Environment=` no systemd, ou mudar loader para ler `.env.binance`.
- Cifrar `api_secret` (#692), fail-closed JWT (#684), rotas públicas (#685/#686), UX formulário credencial.
- Colar valores de chave/secret em issue/chat/evidência/log.
- Mudança de código backend/frontend de produto.

## Decisions

1. **Padrão `.env.*` + allowlist explícita dos examples trackeados.**  
   Alternativa: só adicionar `.env.binance` linha a linha. Rejeitada: o issue exige cobrir novos `.env.<nome>` e impedir reincidência genérica. Manter as entradas pontuais já existentes (`.env`, `backend/.env`, etc.) onde ainda forem úteis; `.env.*` cobre `.env.binance`, `.env.glassnode`, `.env.docker.local` e similares. Allowlist mínima: `!.env.binance.example`, `!.env.docker.example`, `!**/.env.example` (cobre `backend/.env.example` e `frontend/.env.example`) — ou paths explícitos equivalentes se o Apply preferir clareza.

2. **Remoção só do índice / tip (`git rm --cached`), sem purge de history.**  
   Alternativa: BFG/filter-repo + force-push. Fora do card (Não entra). Blobs antigos e `origin/main` podem ainda listar o path até o release; aceite neste card sob o racional T6 (repo privado; keys sem withdraw) — sem gate de revogação.

3. **Home canônica = `.env` raiz; não recriar `.env.binance`.**  
   Alternativa: documentar `.env.binance` como ficheiro local gitignored e manter o nome. Rejeitada pelo issue: home canônica é `.env` raiz; runtime já carrega esse path; não adicionar loader por nome `.env.binance`. Ops migra vars existentes para `.env` raiz se necessário e deixa de usar o ficheiro local.

4. **Apply não altera `config.py` nem units systemd** (salvo descoberta de referência explícita a `.env.binance` — exploração Design: nenhuma).  
   Tarefa de verificação read-only no Apply/closeout: `rg` / inspeção confirma ausência de load por nome; não inventar `EnvironmentFile=` novo.

5. **Sem rotação / revogação Binance neste card (ajuste Alan T6, 2026-08-26).**  
   A grelha original e o Decision 5 anterior exigiam ordem gerar → gravar → verify → revogar → merge. **Revogado por Alan:** NÃO gerar chaves novas; NÃO gravar novas no `.env` raiz por causa de rotação; NÃO smoke AC5 de chaves novas; NÃO revogar antigas nem evidenciar rejeição pela API; NÃO gate pré-merge de rotação. Rationale registado: (a) repositório é **privado** — não é vazamento público tipo clone anónimo de repo open; (b) as API keys **não têm permissão de saque** (withdraw). Done deste card **não** exige material antigo rejeitado pela API. Ops reutiliza as chaves atuais no `.env` raiz.

6. **Examples permanecem trackeados sem valores reais.**  
   `.env.binance.example` continua a documentar as variáveis com placeholders vazios (nome do ficheiro pode sugerir home antiga; aceite — Non-Goal não migrar docs neste card). Home canônica operacional continua a ser `.env` raiz (D3).

## Apply contract

- Editar `.gitignore` (padrão `.env.*` + allowlist).
- `git rm --cached .env.binance` (e garantir que o path não volta no tip da branch/PR).
- Não editar `backend/**` / `frontend/src/**` de produto; não adicionar loader `.env.binance`.
- Não commitar `.env` nem valores reais; não colar secrets em evidência.
- Ops (humano, sem rotação): se `BINANCE_*` ainda só estiverem em `.env.binance` local, copiar as **mesmas** vars para `.env` raiz DEV/PROD e deixar de usar `.env.binance` local — **sem** gerar par novo na Binance.
- Verificação pós-merge: `git ls-tree origin/develop -- .env.binance` vazio; examples ainda trackeados; check-ignore cobre `.env.foo` inventado.

## Risks / Trade-offs

- [History / `origin/main` ainda têm o blob] → aceito neste card. Rationale Alan T6: repo privado; keys sem withdraw. Limpeza de main no release, não neste card. **Não** há gate de revogação a tornar o blob “inútil” via API.
- [Material ainda válido em history/main] → risco residual aceite por Alan; fora do Done deste card. Mitigação futura opcional (outro card/release), não Apply #687.
- [Operador local ainda depende de `.env.binance` no disco] → após Apply, o ficheiro pode permanecer untracked no working tree até ser apagado; home canônica é `.env` raiz — task de ops para migrar vars existentes e apagar o local (**sem** gerar chaves novas).
- [Allowlist incompleta ignora um example] → listar os quatro paths conhecidos; validar `git check-ignore -v` nos examples (não ignorados) e num `.env.probe` (ignorado).
- [Vazar valores em evidência] → só presença/ausência de path/gitignore; proibido colar key/secret.
- [Candle-writer / workers sem `BINANCE_*` no env após migração] → garantir que as vars **atuais** estão no `.env` raiz (ou no path que o unit já faz `source`) **antes** de apagar o ficheiro local; services que só `source` `backend/.env` podem precisar das vars aí **ou** no path que já fazem source da raiz (candle-writer já faz ambos).

## Migration Plan

1. Após T7 / Pronto para Dev: Apply edita `.gitignore` e `git rm --cached .env.binance`; PR para develop.
2. Ops (sem rotação): se as vars ainda só estiverem em `.env.binance` local, migrar `BINANCE_API_KEY` / `BINANCE_API_SECRET` **existentes** para `.env` raiz DEV e PROD; deixar de usar `.env.binance` local; **não** gerar/revogar chaves na Binance.
3. Merge: tip `origin/develop` sem `.env.binance`.
4. `origin/main` pode ainda ter o path até o release — OK neste card (T6: sem gate de revogação).
5. Rollback de código: reverter o commit do gitignore/`rm --cached` **não** reintroduz o secret se o blob não for recommitado; **nunca** recommitar `.env.binance` com valores. Rollback operacional = manter `BINANCE_*` válidos (atuais) no `.env` raiz.

## Open Questions

Nenhuma bloqueante. Escopo e Done revisados pelo ajuste Alan T6 (2026-08-26): rotação saiu.

## UI impact

**none** — ops/git/secrets (gitignore, remoção do tip, migração de vars existentes para `.env` raiz). Nenhuma superfície visual nova ou alterada; nenhum formulário, dashboard ou rota UI no recorte.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; mudança é higiene de repositório e operação de secrets (sem rotação).

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`. Sem superfície visual; Impeccable/DESIGN.md/Playwright não se aplicam.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit pós Alan T6 (read-only, 1 spawn, sem transcript). Fontes: proposal/design/tasks/spec + decisão Alan (repo privado + keys sem withdraw → sem rotação). Card #687, change `card-687-remove-env-binance`, `Status=Design`. Prototype: N/A. Impeccable: N/A. Snapshot: `.impeccable/critique/687-card-687-remove-env-binance-T6-20260826T170042Z.md`.

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 — `.env.binance.example` sugere home antiga (aceito; D6).**
- **P3 — units só `source backend/.env` + `load_dotenv` raiz (aceito; Risks).**
- **P3 — snapshots A/A-r2 pré-T6 obsoletos (aceito; usar snapshot T6).**

Riscos não bloqueantes: blob/history e tip de `main` até o release; material antigo no Git permanece válido nas keys atuais — mitigação aceite por Alan (privado + sem saque).

**Design Agent verdict: PASS** — crítica isolada inherit. Prototype N/A. Impeccable N/A.
