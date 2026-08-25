## Context

Card [#684](https://github.com/oalansilva/crypto/issues/684) (P0, Segurança). Issue grelhado: fallback `JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")` em `app.routes.auth`, `app.middleware.authMiddleware` e `app.services.oos_promotion_proof`. O literal está no Git; units DEV/PROD fazem `source` do `.env` do backend e **não** expõem `JWT_SECRET` em `Environment=`. O exemplo de env do backend não documenta a variável.

HS256 access 15 min + refresh 7 dias. Quem conhece o default forja `sub` e passa em `get_current_user` / `get_current_admin`.

**UI impact: none.** Nenhuma tela nova ou alterada. Sessão cair após a rotação é efeito operacional. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Fail-closed no runtime DEV e PROD que assina ou valida JWT.
- Recusar ausente, vazio/whitespace, igual ao `default conhecido`, ou comprimento menor que 32.
- Um critério único nos três caminhos de runtime.
- Pytest com secret de teste explícito; cobertura do fail-closed e 401 para token assinado com o default.
- Exemplo de env com placeholder, sem valor real.
- Rotação: DEV no Done/restart; PROD no release. Valor nunca em git, systemd `Environment=`, chat, issue ou evidência.
- Scripts one-off `card_262` / `card_277` sem fallback do default.

**Non-Goals:**

- RS256, 2FA, cookie HttpOnly / revogar ao trocar senha (#694).
- Cifrar `api_secret` Binance (#692), rate limit (#690), `.env.binance` (#687), rotas públicas P0 (#685/#686).
- UI/frontend, `Environment=` no systemd, log do valor, checagem de entropia além de 32 + denylist.
- Workers que não importam JWT não precisam da variável.

## Decisions

1. **Um resolver único, fail-closed no import, no estilo `resolve_db_url`.**  
   Alternativa: `pydantic-settings` em `Settings` com validator. Rejeitada neste card: auth/middleware já leem `os.getenv` no import, antes de um ponto único de Settings; espalhar `Settings.jwt_secret` sem matar os três `os.getenv` deixa o furo.  
   Função `resolve_jwt_secret()` (módulo pequeno, p.ex. `app.jwt_secret`) lê `os.getenv("JWT_SECRET")` **sem** default, faz `strip`, recusa `None`/vazio, igualdade com o `default conhecido`, e `len < 32`. Levanta `RuntimeError` cujo texto cita `JWT_SECRET` e **não** inclui o valor (nem o candidato rejeitado). Auth, middleware e `oos_promotion_proof` **MUST** atribuir `JWT_SECRET = resolve_jwt_secret()` no import. Chamada só no request deixaria `/health` verde com JWT ainda inválido — fora do aceite.

2. **Denylist do literal `dev-secret-change-in-production` mesmo se setado no env.**  
   Alternativa: só recusar ausente. Insuficiente: o issue exige recusar “igual ao default”. O literal permanece no código **apenas** como denylist; não é fallback.

3. **Limiar de “fraco” = comprimento menor que 32; sem entropia.**  
   Fechado na grelha (Q2). Sem zxcvbn, sem exigência de charset.

4. **Pytest: forçar `os.environ["JWT_SECRET"]` (não `setdefault`) antes de `import app.config`.**  
   `app.config` faz `load_dotenv` do `.env` do backend com `override=False`. `setdefault` herdaria o secret live de DEV (ou o default conhecido, e a collection fail-closed). Assignment absoluto de um secret de teste ≥ 32 e ≠ default, **antes** de `from app.config import get_settings`. Testes do resolver usam monkeypatch de env. Auth que hoje usa `unit-test-secret` (16 chars) e helpers OOS `_expired_proof` / `_proof_with_purpose` (ainda com fallback do default) MUST passar a um secret de teste ≥ 32 e a `os.getenv("JWT_SECRET")` sem fallback.

5. **Token assinado com o default → 401 porque o runtime já não usa essa chave.**  
   Não precisa de denylist na `jwt.decode`: com o secret rotacionado/valid, a assinatura do default falha (`InvalidTokenError` → 401 já existente). O teste de aceite constrói um JWT com o default conhecido e chama `get_current_user` / `get_current_admin` contra um processo que subiu com secret válido.

6. **Scripts one-off: remover o segundo argumento do `getenv`; falhar se ausente.**  
   Não importar o resolver de runtime se isso puxar FastAPI no script; basta `os.getenv("JWT_SECRET")` sem default (ou abort explícito). Não são systemd.

7. **Rotação operacional fora do Git.**  
   DEV: no Done/restart, garantir `JWT_SECRET` forte no `.env` do backend DEV (gerar se ausente/inválido) **sem** imprimir o valor. PROD: o mesmo no release, não neste Done. Evidência: “chave presente e backend subiu”; nunca o valor. Units permanecem com `source` do `.env`.

8. **Workers.**  
   Só herdam o fail-closed se importarem o módulo de JWT. Discovery/candle-writer que não importam auth não exigem a variável. Não alargar o card para “todo unit systemd tem JWT_SECRET”.

9. **Mensagem de erro e evidência nunca vazam o secret.**  
   `RuntimeError` genérico. Logs, journal, comentário de Done e chat registram só presença/ausência da chave.

## Apply contract

- Implementar o resolver e trocar os três caminhos de runtime + scripts one-off + testes + exemplo de env.
- Não editar frontend.
- Não commitar `.env` nem o valor do secret.
- Rotação DEV é tarefa de Done/restart; PROD é tarefa de release.
- Não imprimir `JWT_SECRET` em evidência.

## Risks / Trade-offs

- [`.env` DEV/PROD ainda sem secret forte] → restart fail-closed derruba o serviço. Mitigação: tarefa de rotação **antes** do restart de Done/release; não é “depois”.
- [Import-time explode pytest] → `conftest` seta o secret antes dos imports de auth.
- [Constante de módulo vs env reload] → restart é a rotação; sem reload a quente.
- [Literal do default continua no Git como denylist + history] → aceito; a mitigação real é o fail-closed + rotação. Não reescrever history neste card.
- [Vazar o valor em journal/`set -a`] → evidência só de presença; não `cat`/não `systemctl show Environment`.
- [Scripts one-off quebram se alguém rodá-los sem env] → desejado; não assinar com o default.

## Migration Plan

1. Código fail-closed na branch do card (após T7).
2. Antes do `./restart` de Done em DEV: escrever/rodar `JWT_SECRET` forte no `.env` DEV se ainda inválido.
3. Restart DEV; sessões DEV caem; login volta a emitir tokens com o secret novo.
4. PROD: no release, mesmo passo no `.env` PROD + restart do backend PROD.
5. Rollback de código sozinho **não** reabre o default se o apply removeu o fallback; rollback completo exigiria revert do commit (não desejado). Rollback operacional = restaurar um secret válido no `.env`, não o default conhecido.

## Open Questions

Nenhuma bloqueante. Q1–Q4 da grelha fechadas (2026-08-25).

## UI impact

**none** — autenticação/boot. Nenhuma superfície visual nova ou alterada. Logout de fato após rotação não é UI deste card.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`. Fail-closed de secret, sem superfície visual.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit (read-only, 1 spawn, sem transcript). Fontes: `proposal.md`, `design.md` (D1–D9), `tasks.md`, `specs/jwt-secret-fail-closed/spec.md`, código atual de auth/middleware/OOS/conftest. Card #684, change `card-684-jwt-secret-fail-closed`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

- **P0:** nenhum
- **P1:** nenhum
- **P2 — pytest vs `load_dotenv` (corrigido no design/tasks):** assignment `os.environ["JWT_SECRET"]` antes de `app.config`, não `setdefault`.
- **P2 — helpers OOS ainda com fallback (corrigido no tasks 2.4):** `_expired_proof` / `_proof_with_purpose`.
- **P2 — asserção de leakage incompleta (corrigido no spec/tasks 2.2):** `RuntimeError` não contém o candidato em todos os casos inválidos.
- **P3 — denylist é necessária porque o default tem 32 chars (aceito).**
- **P3 — resolver no import, não só no request (aceito; D1 apertado).**
- **P3 — `scripts/card_261_*` fora do recorte grelhado (aceito).**
- **P3 — compose / `.env.docker.example` fora (aceito; exemplo canônico é o do backend).**

Riscos não bloqueantes: PROD permanece forjável até a rotação no release; rotação derruba sessões e provas OOS em voo; evidência nunca `printenv`/`cat .env`; literal denylist fica no history.

**Design Agent verdict: PASS** — crítica isolada inherit. Prototype N/A. Impeccable N/A.
