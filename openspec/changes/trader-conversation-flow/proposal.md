# Change Proposal: Trader Conversa Fluida (sem fixo)

**Status:** 🟡 draft  
**Created:** 2026-02-10  
**Author:** amigoalan (OpenClaw)  
**Priority:** high  
**Type:** enhancement

---

## Why

O Alan pediu explicitamente que o **Trader conduza uma conversa fluida**, podendo fazer **quantas perguntas forem necessárias** para montar a estratégia — sem ficar preso a um fluxo fixo ou travar por regras rígidas.

Hoje o upstream ainda pode parecer “travado” porque:
- há passos fixos (perguntar symbol/timeframe, depois aprovar) 
- o draft só é gerado após o contrato estar completo
- o Trader não tem liberdade para continuar perguntando quando julga necessário

Isso viola o objetivo de “conversa fluida” e gera fricção na experiência.

---

## 📋 Contexto

**Requisito do Alan:**
> “não quero algo fixo, mas uma conversa fluida; o Trader pode fazer quantas perguntas achar necessário para montar a estratégia.”

**Problema atual:**
- Conversa interrompida quando o contrato upstream é “tecnicamente aprovado”
- Perguntas adicionais do Trader não são tratadas como parte natural do fluxo
- A UI não diferencia entre “perguntas necessárias” e “perguntas opcionais do Trader”

---

## 🎯 Objetivo

Permitir que o Trader conduza a conversa **livremente**, sem limite rígido de perguntas, até se sentir pronto para entregar o draft da estratégia.

**Princípios:**
- **Fluidez**: o Trader pode perguntar N vezes
- **Controle**: o Trader decide quando o draft está pronto
- **Sem travar**: a UI deve aceitar perguntas adicionais sem bloquear

---

## 🚀 Mudanças Propostas

1. **Trader pode continuar perguntando após preencher symbol/timeframe**
2. **Draft só aparece quando o Trader sinaliza `ready_for_user_review=true`**
3. **Upstream permanece em modo chat** enquanto o Trader quiser perguntar
4. **UI trata perguntas adicionais como parte natural da conversa**

---

## ✅ Critérios de Aceite

1. Trader pode fazer múltiplas perguntas antes de gerar draft
2. Nenhum bloqueio automático por contrato “completo”
3. Draft só aparece quando `ready_for_user_review=true`
4. Fluxo funciona com input livre (sem exigir `symbol=` / `timeframe=`)

---

## 🔗 Relacionado

- Change anterior: `lab-trader-driven-flow`

---

## 📝 Notas de Implementação

Ver `design.md` e `tasks.md` para detalhes.
