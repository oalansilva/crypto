# Snapshot — Assessment A re-avaliação · card #687 `card-687-remove-env-binance`

- Card: #687 P0 Remover `.env.binance` do Git e rotacionar chaves
- Change: `card-687-remove-env-binance`
- Critic: Assessment A re-assessment (após fix do autor; isolado, sem transcript do pai)
- Modelo: inherit
- UTC: 20260826T164741Z
- Status observado: Design (artefatos OpenSpec; Apply ainda não executado)
- UI impact: **none** (ops/git/secrets; Prototype N/A; Impeccable N/A)
- Method: releitura proposal/design/tasks/spec + verificação read-only (`.gitignore`, `git ls-files`/`ls-tree` presença de path, `config.py` load paths, `ops/systemd` source/EnvironmentFile, `rg` por nome `.env.binance` em código). Sem print de valores de secret.

---

## Re-check dos achados anteriores

### P1 (ordem de rotação invertida) — FECHADO
- `proposal.md`: gerar → gravar `.env` raiz DEV+PROD → verificar presença → revogar → evidência → merge.
- `design.md` Decision 5: mesma ordem; alternativa “revogar antes de gravar” explicitamente rejeitada (critic P1).
- `tasks.md` 4.1→4.4: generate → write → smoke AC5 → revoke → evidence/merge gate.
- `specs/.../spec.md` Requirement rotação: SHALL generate → write → verify presence → revoke → evidence → merge; cenário “New keys installed and verified before revoke”.

### P2 (smoke AC5) — FECHADO
- Task 4.3: smoke/verify presença `BINANCE_*` no runtime que carrega `.env` raiz (só presença/sucesso) **antes** de revogar.
- Design D5 passo (3) + Migration + Risks mitigation alinhados.
- Spec cenário exige confirmação presença/sucesso antes do revoke.

---

## Rubrica (UI none)

### 1. Fidelidade ao #687
- Entra/não entra intactos; AC tip develop, gitignore+allowlist, home `.env` raiz, sem load por nome, rotação sem valores, main residual OK — cobertos.

### 2. Regressão produto/ops
- `.env.binance` ainda trackeado em HEAD/`origin/develop` (esperado pré-Apply); **não** coberto por `.gitignore` atual (Apply fará `.env.*` + allowlist).
- `config.py`: só `backend/.env` + `.env` raiz (`override=False`); nenhum loader `.env.binance` em `*.py`/`*.service`/`*.sh` de produto.
- systemd: candle-writer source ambos; discovery/runtime-worker só `backend/.env` — risco residual P3 já documentado; Apply contract não adiciona loader.

### 3. Superfície visual
- Nenhuma tela/rota/formulário. **UI impact: none** continua correto; Prototype/Impeccable N/A justificados.

### 4. Ordem / evidência / Apply contract
- Ordem segura consistente em proposal/design/tasks/spec.
- Evidência: presença/rejeição API; proibido colar valores — OK.
- Apply contract adequado; sem mudança de produto.

### 5. Novos gaps bloqueantes
- Nenhum P0/P1 novo.

---

## Achados

- P0: (nenhum)
- P1: (nenhum — P1 anterior fechado)
- P2: (nenhum — P2 anterior fechado)
- P3: `.env.binance.example` pode sugerir home antiga (aceito Non-Goal / Decision 6).
- P3: Units que só `source backend/.env` dependem do `load_dotenv` raiz via Python para vars só na raiz — documentado; smoke 4.3 deve cobrir o runtime relevante antes do revoke.

## Disposition
P1/P2 fechados com evidência nos quatro artefatos. Aceitar P3. Pronto para handoff T7 (Aprovação de Design) do ponto de vista desta crítica.

## Verdict
**PASS** (zero P0/P1 abertos)

## Snapshot
`.impeccable/critique/687-card-687-remove-env-binance-A-r2.md`
