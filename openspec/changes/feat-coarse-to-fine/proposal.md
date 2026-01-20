---
title: Otimização 4D Grosso-para-Fino
status: proposed
type: feature
---

# Otimização 4D Grosso-para-Fino

## Summary
Implementar uma Otimização Adaptativa (Coarse-to-Fine) que utiliza uma Grade Combinatória de 4 rodadas com passos decrescentes para encontrar estratégias sinérgicas (N parâmetros + Stop Loss) de forma 194x mais rápida que a força bruta.

## Why
A lógica de otimização atual falha em descobrir "Estratégias Sinérgicas" como a **Antiga** (EMA 3 / Stop 2.7%), que requerem Médias Móveis curtas específicas E Stop Losses curtos específicos para funcionar.
- Se testada com Stop Loss Padrão (1.5%), EMA 3 falha no Estágio 1.
- Se testada sem Stop Loss (0.0%), EMA 3 falha no Estágio 1 (whipsaws).
- Ela só funciona quando EMA 3 e Stop 2.7% são testados **juntos**.

Além disso, a busca exaustiva (Força Bruta) é inviável computacionalmente (42+ horas). Precisamos de uma abordagem inteligente (15 min) que garanta cobertura matemática.

## What Changes
### 1. Busca Adaptativa em 4 Estágios (Zoom-In)

Vamos implementar uma lógica de "Funil de Refinamento", onde cada passo reduz a área de busca e refina a precisão.

### Lógica da Otimização Genérica (4 Rodadas)
Esta lógica será aplicada automaticamente para **QUALQUER estratégia**, independentemente do número de parâmetros. O sistema detectará o tipo do parâmetro (Inteiro ou Decimal) e aplicará a redução de passo apropriada.

1.  **Rodada 1 (Exploração Global):**
    *   **Range:** 100% do espaço definido (Min/Max do template).
    *   **Passo (Inteiros):** 5 (ex: Periodos 10, 15, 20...).
    *   **Passo (Decimais):** 0.50 (ex: Stop Loss 1.0%, 1.5%...).
    *   *Objetivo:* Mapear o terreno e achar os "Top 3 Candidatos".

2.  **Rodada 2 (Foco):**
    *   **Range:** `[Melhor - 5, Melhor + 5]` (Inteiros) ou `[Melhor - 0.5, Melhor + 0.5]` (Decimais).
    *   **Passo (Inteiros):** 3.
    *   **Passo (Decimais):** 0.30.

3.  **Rodada 3 (Detalhe):**
    *   **Range:** `[Melhor - 3, Melhor + 3]` (Inteiros) ou `[Melhor - 0.3, Melhor + 0.3]` (Decimais).
    *   **Passo (Inteiros):** 2.
    *   **Passo (Decimais):** 0.20.

4.  **Rodada 4 (Precisão Final):**
    *   **Range:** `[Melhor - 2, Melhor + 2]` (Inteiros) ou `[Melhor - 0.2, Melhor + 0.2]` (Decimais).
    *   **Passo (Inteiros):** 1 (Precisão Máxima).
    *   **Passo (Decimais):** 0.10.

*Nota: O sistema identificará automaticamente quais parâmetros são da estratégia (N) e qual é o Stop Loss, aplicando essa lógica recursivamente para todas as dimensões.*

### Análise de Performance: Comparação Matemática

Você perguntou se "ficaria mais rápido". A resposta é: **Sim, absurdamente mais rápido.**

Vamos comparar usando o exemplo da sua imagem:
*   Média Curta (3-20), Média Média (10-40), Média Longa (20-100), Stop (0.5% - 13%).

#### Modelo Antigo (Força Bruta com Passo 1 e Stop 0.2%)
*   Combinações: 17 * 30 * 80 * 62 = **2,529,600 testes**.
*   Tempo Estimado: **~42 horas** (Inviável).

#### Novo Modelo (Tudo com Tudo - 4 Rodadas)
*   **Rodada 1 (Passo 5):** 4 * 6 * 16 * 25 = **9,600 testes**.
*   **Rodada 2 (Passo 3):** 4 * 4 * 4 * 4 = **256 testes**. (Multiplicado por 3 candidatos = 768).
*   **Rodada 3 (Passo 2):** 4 * 4 * 4 * 4 = **256 testes**. (x3 = 768).
*   **Rodada 4 (Passo 1):** 5 * 5 * 5 * 5 = **625 testes**. (x3 = 1,875).

**Total de Testes:** ~13,000.
**Redução:** De 2.5 milhões para 13 mil testes.
**Velocidade:** **194x mais rápido**.
**Resultado:** O mesmo (garantido pela matemática dos limites inteligentes).

### Integração com a Interface (UI) - "Input Simplificado"
Como sugerido, **não solicitaremos o `step` ao usuário**. O campo deve ser **REMOVIDO DA TELA** (`ComboConfigurePage.tsx` e `ParameterConfigScreen.tsx`).

*   **UI Envia:** Apenas `Min` e `Max`.
*   **Backend Decide:**
    *   Constrói a pirâmide de passos (5 -> 3 -> 2 -> 1) sozinho.

Isso simplifica a tela de otimização e evita que o usuário escolha um passo "errado" ou ineficiente. O sistema é uma "Caixa Preta" inteligente.

### Princípio Fundamental: Grade Combinatória ("Tudo com Tudo")
É importante esclarecer que em **CADA RODADA**, o sistema executa uma **Grade Combinatória Completa** (Plano Cartesiano) dentro do Range e Passo definido.

*   Isso significa que **TUDO é testado contra TUDO**.
*   Exemplo Rodada 1: Se temos 4 opções de Média (5,10,15,20) e 4 opções de Stop (1,2,3,4), o sistema fará 16 testes (4x4).
*   Não existem "atalhos" dentro da rodada. Isso garante que se uma estratégia depende da **combinação exata** de Média 5 com Stop 4, ela será encontrada porque essa intersecção é testada.

### Melhorias Sugeridas (Para garantir o Ótimo Global)

A proposta de "Zoom" tem um risco: Se a grade inicial for muito larga, podemos cair em um "máximo local" e perder a verdadeira melhor estratégia (que poderia estar entre dois pontos da grade). Para corrigir isso, sugiro duas melhorias:

1.  **Multi-Foco (Top 3 Candidatos):**
    *   Não dar zoom apenas no resultado #1.
    *   Pegar os **Top 3 resultados distantes entre si** da Rodada 1.
    *   Rodar o processo de refinamento para cada um desses 3 "candidatos".
    *   *Por que?* Isso previne que a gente ignore uma estratégia excelente só porque a grade inicial não caiu exatamente nela.

2.  **Limites Inteligentes (Smart Bounds):**
    *   Em vez de reduzir arbitrariamente para "50%" ou "25%".
    *   O novo Range deve ser calculado matematicamente: `[Melhor_Valor - Passo_Anterior, Melhor_Valor + Passo_Anterior]`.
    *   *Exemplo:* Se testamos Médias 10, 15, 20 (Passo 5) e a melhor foi 15.
    *   O próximo range deve ser exatamente **10 até 20** (Cobrir o buraco deixado pelo passo anterior).
    *   Isso garante cobertura **matemática de 100%** do espaço útil, sem desperdício.

### Mudanças no Código (`combo_optimizer.py`)
Precisamos evoluir a função `generate_stages` e o loop de otimização para suportar **"Adaptive Sizing"**:
- Calcular dinamicamente o `min`, `max` e `step` de cada rodada com base no vencedor da anterior.
- Isso substituirá a lógica simples de "Grade Única" por uma "Grade Adaptativa Recursiva".

## Passos de Implementação
1.  Criar `scripts/update_schema_coarse_4d.py` para atualizar o esquema do banco de dados.
2.  Modificar `backend/app/services/combo_optimizer.py` para permitir rodadas de refinamento após a busca em grade.
3.  Verificar rodando uma otimização completa que descobre com sucesso a "Antiga".
