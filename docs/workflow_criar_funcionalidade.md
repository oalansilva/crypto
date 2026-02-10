# Workflow: "Crie Funcionalidade" (atualizado com testes automatizados)

Este documento descreve o fluxo completo de desenvolvimento de novas funcionalidades no projeto Crypto Lab, incluindo testes automatizados obrigatórios.

## 📋 Fluxo Completo

### 1. Proposta da Funcionalidade
**Trigger:** Alan envia `"Crie Funcionalidade: <descrição>"`

**Ação:**
- Criar Change Proposal via OpenSpec em `openspec/changes/<change_id>/`
- Arquivos obrigatórios:
  - `proposal.md` — Problema, solução, escopo
  - `specs/<capability>/spec.md` — Requirements com Given/When/Then
  - `design.md` — Arquitetura e componentes
  - `tasks.md` — Breakdown de implementação

**Validação:**
```bash
openspec validate <change_id> --type change
```

**Output:** Link do viewer: `http://31.97.92.212:5173/openspec/changes/<change_id>/proposal`

---

### 2. Aprovação
**Trigger:** Alan envia `"Go"` ou `"implementar"`

---

### 3. Implementação
**Ação:**
```bash
./scripts/openspec_codex_task.sh <change_id>
```

**Guardrails:**
- Working tree limpa (commit antes)
- Validação OpenSpec passa
- Codex CLI implementa (escopo: `backend/`, `frontend/`, `src/`, `tests/`, `openspec/`)
- Limite de arquivos: default 10 (override: `MAX_FILES_CHANGED=<n>`)

---

### 4. Testes Automatizados (OBRIGATÓRIO)

#### 4.1. Testes Backend (pytest)
```bash
cd /root/.openclaw/workspace/crypto
./backend/.venv/bin/python -m pytest -q
```

**Esperado:** Todos os testes passam ✅

**Se falhar:**
- Revisar erros
- Corrigir código
- Rerun até passar

#### 4.2. Testes UI (E2E com Playwright)

**a) Criar script de teste:**
```bash
cp test_e2e_template.py test_e2e_<feature_name>.py
```

**b) Implementar steps do teste:**
- STEP 1: Navegar para página
- STEP 2-N: Interações (preencher forms, clicar botões)
- STEP N+1: Validar resultado (via API + UI)

**c) Rodar teste:**
```bash
./backend/.venv/bin/python test_e2e_<feature_name>.py
```

**Saída esperada:**
```
✅ TESTE <FEATURE> PASSOU!
📸 Screenshots gerados em /tmp/
```

**Screenshots gerados:**
- `/tmp/<feature>_step1_*.png`
- `/tmp/<feature>_step2_*.png`
- etc.

**Nota:** Screenshots são apenas para debug local. **NÃO enviar pro Telegram.**

#### 4.3. Reportar Resultado

**No chat, informar:**
```
✅ Testes backend: PASSOU (X testes)
✅ Teste E2E <feature>: PASSOU
   - Steps: [lista de steps testados]
   - Screenshots em /tmp/ (não enviados)
```

**OU, se falhou:**
```
❌ Teste E2E <feature>: FALHOU
   - Step que falhou: <número e descrição>
   - Erro: <mensagem>
   - Screenshot: /tmp/<feature>_error.png
```

---

### 5. Deploy na VPS

```bash
# Commit e push
git add .
git commit -m "feat: <descrição> [change:<change_id>]"
git push origin feature/long-change

# Restart services
systemctl restart crypto-backend.service
systemctl restart crypto-frontend.service

# Verificar status
systemctl status crypto-backend.service --no-pager | grep Active
systemctl status crypto-frontend.service --no-pager | grep Active
```

---

### 6. Validação Final

**Alan testa manualmente na UI:**
- URL: `http://31.97.92.212:5173/...`
- Verifica fluxo completo
- Manda feedback: `"ok"` ou ajustes necessários

---

### 7. Arquivamento

**Trigger:** Alan confirma que está ok

**Ação:**
```bash
openspec archive <change_id>
```

**Evidência a adicionar:**
- Commit hash
- URL testada
- Resultado dos testes (backend + E2E)

---

## 🧪 Checklist de Testes

Para cada nova funcionalidade:

- [ ] **Backend tests:** `pytest -q` passa
- [ ] **Script E2E criado:** `test_e2e_<feature>.py`
- [ ] **E2E executado:** Todos os steps passam
- [ ] **Screenshots gerados:** Salvos em `/tmp/` (não enviados)
- [ ] **Resultado reportado:** PASSOU/FALHOU + detalhes no chat
- [ ] **Deploy:** Services reiniciados na VPS
- [ ] **Validação manual:** Alan testa e aprova

---

## 📦 Ferramentas Instaladas

- **Playwright:** `./backend/.venv/bin/pip install playwright`
- **Chromium headless:** `python -m playwright install chromium`
- **Dependencies:** `python -m playwright install-deps chromium`

---

## 📝 Template de Teste E2E

Localização: `crypto/test_e2e_template.py`

**Como usar:**
1. Copiar: `cp test_e2e_template.py test_e2e_<feature>.py`
2. Ajustar constantes (`FEATURE_NAME`, etc.)
3. Implementar steps
4. Rodar e validar

**Estrutura:**
- Setup (navegação)
- Interações (forms, botões)
- Aguardar estados (polling API)
- Validar resultado (API + UI)
- Screenshots para debug

---

## 🔍 Seletores Úteis

**Lab home:**
- Textarea: `textarea[placeholder*="Ex.: Quero rodar"]`
- Botão Run: `button:has-text("Run Lab")`

**Lab run (upstream):**
- Textarea: `textarea` (primeiro)
- Botão Enviar: `button:has-text("Enviar")`
- Botão Aprovar: `button:has-text("Aprovar")`

**Helpers:**
- Polling API: função `wait_for_api_state()` no template
- Screenshots: `await page.screenshot(path="/tmp/step.png")`
- Aguardar elemento: `await element.wait_for(state="visible")`

---

## ⚠️ Regras Importantes

1. **Sempre rodar testes antes de marcar como "concluído"**
2. **Screenshots são apenas para debug local (NÃO enviar pro Telegram)**
3. **Reportar resultado dos testes no chat (PASSOU/FALHOU + resumo)**
4. **Se testes falharem, corrigir antes de fazer deploy**
5. **Documentar testes criados no commit message**

---

**Última atualização:** 2026-02-10 (inclusão de testes automatizados obrigatórios)
