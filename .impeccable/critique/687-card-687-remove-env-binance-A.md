# Snapshot — Assessment A · card #687 `card-687-remove-env-binance`

- Card: #687 P0 Remover `.env.binance` do Git e rotacionar chaves
- Change: `card-687-remove-env-binance`
- Critic: Assessment A (crítica isolada, sem transcript do pai)
- Modelo: inherit
- UTC: 20260826T164423Z
- Status observado: Design
- UI impact: **none** (ops/git/secrets; Prototype N/A; Impeccable N/A)
- Method: leitura proposal/design/tasks/spec + verificação read-only (`.gitignore`, `git ls-files`/`ls-tree`, `config.py`, `ops/systemd`, refs por nome). Sem print de valores de secret (só nomes de chaves / presença de path).

---

## Rubrica (UI none)

### 1. Fidelidade ao #687 grelhado
- Entra/não entra alinhados (gitignore `.env.*`+allowlist, `git rm --cached`, home `.env` raiz, rotação pré-merge, sem purge/main/secret-manager/systemd Environment/loader `.env.binance`/UI).
- AC 1–7 cobertos em spec + tasks (tip develop, ignore, examples, rotação sem valores, `.env` raiz DEV/PROD, sem load por nome, main residual OK).

### 2. Regressão produto/ops
- Confirmado: `.env.binance` trackeado em HEAD/`origin/develop`/`origin/main`; **não** coberto por `.gitignore` atual.
- Confirmado: `config.py` só `backend/.env` + `.env` raiz (`override=False`); binance_* chama `get_settings()` antes de `os.getenv`.
- Confirmado: nenhum unit `ops/systemd` referencia `.env.binance` por nome; candle-writer source ambos; discovery/runtime só `backend/.env` (mitigado por dotenv no Python — risco já notado no design).
- Risco residual: workers/shell sem import de `config` + vars só na raiz — documentado; não exige mudança de produto neste card.

### 3. Superfície visual
- Nenhuma tela/rota/formulário no recorte. Classificação **none** correta; Prototype/Impeccable N/A justificados.

### 4. Ordem de rotação / evidência
- **P1:** Decision 5 e tasks 4.1→4.2 ordenam *revogar antigas / evidência de rejeição* **antes** de *gravar novas no `.env` raiz* → janela de outagem Spot/wallet se chaves antigas morrerem sem as novas instaladas em DEV/PROD.
- Ordem segura exigida: gerar novas → gravar `.env` raiz DEV+PROD → (smoke presença/uso) → revogar antigas → evidência sem valores → merge.
- Gate “revogadas antes do merge” permanece; só a sub-ordem install↔revoke precisa inverter.
- Evidência sem leakage: contrato OK (presença/rejeição API; proibido cat/printenv).

### 5. Gaps / contradições / Apply contract
- Apply contract curto e adequado (gitignore, `rm --cached`, sem produto, sem secrets em evidência, gate humano).
- Spec não fixa sub-ordem install→revoke (lacuna).
- Tasks sem smoke explícito pós-gravação vs AC5 (P2).

### 6. Spec/tasks vs AC
- Spec `env-binance-git-hygiene` cobre os quatro requisitos do issue.
- Tasks 1–4 mapeiam Apply + closeout; falha só na ordenação 4.1/4.2 e smoke fraco.

---

## Achados

- P0: (nenhum)
- P1: Ordem de rotação invertida em `design.md` Decision 5 e `tasks.md` 4.1→4.2 (revogar antes de instalar novas no `.env` raiz DEV/PROD).
- P2: Sem task de verificação pós-gravação de que runtime/ Spot|wallet lê `BINANCE_*` do `.env` raiz (AC5) antes de revogar.
- P3: `.env.binance.example` pode continuar a sugerir home antiga (aceito Non-Goal / Decision 6).
- P3: Units que só `source backend/.env` dependem do `load_dotenv` raiz via Python — OK se documentado; não expandir loader.

## Disposition
Corrigir Decision 5 + Migration/tasks para: gerar → escrever DEV/PROD → evidência presença → revogar → evidência rejeição → merge; acrescentar smoke/check AC5 sem valores. Depois reavaliar.

## Verdict
**BLOCKED** (P1 aberto)

## Snapshot
`.impeccable/critique/687-card-687-remove-env-binance-A.md`
