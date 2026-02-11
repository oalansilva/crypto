# Change Proposal: Lab Trader-Driven Flow

**Status:** 🟡 draft  
**Created:** 2026-02-10  
**Author:** amigoalan (OpenClaw)  
**Priority:** high  
**Type:** refactor

---

## Why

O fluxo atual do Strategy Lab tem uma **desconexão crítica** entre a proposta do Trader (aprovada pelo usuário) e a implementação que causa templates completamente não relacionados serem executados.

**Problema real observado (run 9a13692200ed):**
1. Trader propôs **RSI + EMA** (Momentum + Mean Reversion)
2. User aprovou explicitamente: "prossiga dessa forma aprovado"
3. Sistema escolheu **Bollinger_Breakout** alfabeticamente
4. Dev criou **EMA 50/200 + ADX** sem contexto da proposta
5. Resultado: 0% alinhamento com o que foi aprovado

**Impacto:**
- ❌ Perda de confiança do usuário (proposta ignorada)
- ❌ Desperdício de tokens/tempo (backtests irrelevantes)
- ❌ Iterações inúteis (Dev ajusta estratégia errada)
- ❌ 3 personas falando sem valor claro

Este refactor resolve o problema na raiz: fazer o Dev **implementar exatamente o que o Trader propôs** (e foi aprovado pelo usuário).

---

## 📋 Contexto

O fluxo atual do Strategy Lab tem uma **desconexão crítica** entre a proposta do Trader (aprovada pelo usuário) e a implementação:

**Problema observado (run 9a13692200ed):**
- ✅ Trader propôs: **RSI + EMA**
- ✅ User aprovou: "prossiga dessa forma aprovado"
- ❌ Sistema executou: **Bollinger_Breakout** (não relacionado!)
- ❌ Dev propôs: **EMA 50/200 + ADX** (ignorou proposta original!)

**Causa raiz:**
1. `_choose_seed_template()` escolhe template alfabeticamente (ignora `strategy_draft`)
2. Dev não recebe a proposta aprovada pelo Trader
3. Validator e Coordinator criam overhead sem valor claro
4. Fluxo atual: backtest → análise → proposta (invertido!)

---

## 🎯 Objetivo

Refatorar o fluxo do Lab para seguir a **arquitetura Trader-driven**:

```
Trader (propõe estratégia) 
   ↓
User aprova
   ↓
Dev (implementa + itera backtest)
   ↓
Trader (valida resultado)
   ↓
✅ Done ou 🔄 Loop

         Coordinator (Agile Coach)
              ↕
    Só intervém sob demanda
```

**Princípios:**
- Trader domina o **domínio financeiro** (propõe E valida)
- Dev domina a **implementação técnica** (cria template, itera, debugga)
- Coordinator é **facilitador opcional** (não gera resumos automáticos)

---

## 🚀 Mudanças Propostas

### 1. Remover Persona "Validator"
- **Antes:** Validator (Trader + PO) validava após Dev
- **Depois:** Trader faz validação final (mesmo que propôs)

### 2. Coordinator vira Agile Coach
- **Antes:** Resumia automaticamente tudo
- **Depois:** Só intervém sob demanda (dúvidas, impasses)

### 3. Reordenar fluxo do graph
- **Antes:** `upstream → backtest → coordinator → dev_senior → validator`
- **Depois:** `upstream → dev_senior → trader_validation`

### 4. Dev recebe `strategy_draft` completo
- Trader aprova upstream → `strategy_draft` vai direto pro Dev
- Dev cria template custom baseado na proposta (não escolhe aleatório)
- Dev itera: cria → backtest → analisa → ajusta → repete

### 5. Dev controla iteração de backtest
- Dev **chama o sistema** para rodar backtest
- Dev **analisa resultados**
- Dev **pode corrigir bugs no motor** entre iterações
- Dev **entrega resultado pronto** para Trader validar

---

## 📊 Impacto Esperado

**Antes:**
- ❌ Templates aleatórios (Bollinger quando pediu RSI)
- ❌ 3 personas falando sem valor claro
- ❌ Dev sem contexto da proposta original
- ⏱️ ~90s por run, ~75k tokens

**Depois:**
- ✅ Template criado exatamente da proposta aprovada
- ✅ 2 personas focadas (Trader + Dev)
- ✅ Dev com contexto completo + iteração controlada
- ⚡ Estimado: ~60s por run, ~50k tokens

---

## 🎭 Papéis Finais

| Persona | Papel | Responsabilidades |
|---------|-------|-------------------|
| **Trader** | Profissional de mercado financeiro | • Propõe estratégia upstream<br>• Conversa com User até aprovar<br>• **Valida resultado final** do Dev<br>• Decide: aprovar/ajustar/rejeitar |
| **Dev** | Engenheiro de software | • Recebe `strategy_draft` aprovado<br>• Cria template técnico<br>• Itera: backtest → análise → ajuste<br>• Corrige bugs no motor se necessário<br>• Entrega resultado validado tecnicamente |
| **Coordinator** | Agile Coach (opcional) | • **Não gera resumos automáticos**<br>• Intervém só sob demanda:<br>  - Dev ou Trader com dúvida?<br>  - Impasse técnico vs negócio?<br>  - Precisa facilitação? |

---

## 🔗 Relacionado

- Issue original: Run 9a13692200ed (templates não relacionados)
- Commit anterior: `39fa838` (AGENT_CHAT_ENABLED)
- Branch: `feature/long-change`

---

## ✅ Critérios de Aceite

1. **Template inicial criado do `strategy_draft`** (não escolha alfabética)
2. **Dev recebe proposta completa** no contexto
3. **Dev pode iterar** N vezes antes de entregar
4. **Trader valida resultado** (não Validator separado)
5. **Coordinator não gera resumos** (só sob demanda)
6. **Fluxo completo funciona** end-to-end com aprovação do User

---

## 🚧 Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Breaking changes em runs existentes | Média | Alto | Manter backward compatibility temporária |
| Dev itera infinitamente | Baixa | Médio | Limite de iterações (ex: 5 max) |
| Trader aprova strategy_draft ruim | Baixa | Baixo | User aprova antes (gate duplo) |

---

## 📝 Notas de Implementação

Ver `design.md` e `tasks.md` para detalhes técnicos.
