# Snapshot — Design critic (pós Alan T6) · card #687 `card-687-remove-env-binance`

- Card: #687
- Change: `openspec/changes/card-687-remove-env-binance/`
- Critic: Assessment A isolada (sem transcript do pai); reavaliação após ajuste Alan T6
- Modelo: inherit
- UTC: 20260826T170042Z
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-687-remove-env-binance`
- Status observado: Design (artefatos OpenSpec; Apply ainda não executado)
- UI impact: **none** (ops/git/secrets; Prototype N/A; Impeccable N/A)
- Method: leitura proposal/design/tasks/spec + verificação read-only (`.gitignore`, `git ls-files`/`ls-tree` presença de path, `config.py` load paths, `ops/systemd` source/EnvironmentFile, `rg` por nome `.env.binance` / restos de rotação). Sem print de valores de secret.

Snapshots anteriores `687-...-A.md` / `687-...-A-r2.md` ficam **obsoletos** (avaliavam gate de rotação pré-T6).

---

## Decisão Alan T6 a verificar

| Expectativa | Artefatos |
|---|---|
| NÃO gerar / rotacionar / revogar chaves | Non-Goals + Decision 5 + tasks 4.x + Requirement “No Binance key rotation gate” |
| Rationale: repo privado + keys sem withdraw | proposal Why; design Context/D5/Risks; spec Requirement rotação |
| Done = tip develop limpo + gitignore + parar de usar `.env.binance` local (migrar vars existentes → `.env` raiz) | Goals/Done + Apply contract + tasks 1–4 + spec tip/gitignore/canonical home |
| Manter allowlist + `git rm --cached` | proposal What; design D1/D2; tasks 1–2; spec |

---

## Rubrica (UI none)

### 1. Fidelidade ao ajuste Alan T6
- Quatro artefatos coerentes: rotação saiu do Apply/Done; Done = higiene git + home canônica com chaves atuais.
- Menções a gerar/revogar/AC5/smoke/gate pré-merge aparecem **só** como Non-Goal / SHALL NOT / “não fazer” — sem gate positivo residual.
- Rationale (privado + sem withdraw) registado em proposal, design e spec.

### 2. Riscos de regressão
- Pré-Apply confirmado: `.env.binance` ainda no índice/HEAD; `.gitignore` **não** cobre o path (faltam `.env.*` + allowlist — esperado no Apply).
- `config.py`: só `backend/.env` + `.env` raiz (`override=False`); nenhum loader por nome `.env.binance` em produto/systemd.
- systemd: candle-writer source ambos; discovery/runtime-worker só `backend/.env` — Python ainda carrega raiz via dotenv; risco residual documentado (P3).
- History / `origin/main` com blob residual: aceite explícito sob T6; sem gate de revogação.

### 3. Superfície visual
- Nenhuma tela/rota/formulário. **UI impact: none** correto; Prototype/Impeccable N/A justificados; nada visual por classificar.

### 4. Gates de rotação / evidência / Apply contract
- Sem leftover de ordem gerar→gravar→revogar como requisito.
- Spec: Requirement dedicado “No Binance key rotation gate” + Done SHALL NOT exigir revoke.
- Tasks 4.3/4.5 proíbem revoke/AC5/gate de rotação.
- Evidência: proibido colar key/secret (Non-Goals, Apply contract, Risks, spec).
- Apply contract completo: gitignore+allowlist, `git rm --cached`, sem produto, sem secrets em evidência, ops migra vars existentes, verificação pós-merge `ls-tree` vazio.

### 5. Novos gaps bloqueantes
- Nenhum P0/P1.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: `.env.binance.example` pode sugerir home antiga (aceito Non-Goal / Decision 6).
- P3: Units que só `source backend/.env` dependem do `load_dotenv` raiz via Python para vars só na raiz — documentado em Risks; Apply não deve inventar loader.
- P3: Snapshots A / A-r2 pré-T6 descrevem rotação in-scope — ignorar; usar este snapshot no T7.

## Disposition
Aceitar P3. Escopo T6 refletido de ponta a ponta. Pronto para handoff T7 (Aprovação de Design) do ponto de vista desta crítica.

## Verdict
**PASS** (zero P0/P1 abertos)

## Snapshot
`.impeccable/critique/687-card-687-remove-env-binance-T6-20260826T170042Z.md`
