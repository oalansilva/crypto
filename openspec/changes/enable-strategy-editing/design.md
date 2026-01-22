# Design: Editor de Templates de Estratégia

## Visão Geral da Arquitetura

### Camada de Armazenamento
- **Banco de Dados**: Tabela `combo_templates` (existente)
  - Colunas: `name`, `description`, `template_data`, `optimization_schema`, `is_prebuilt`, `is_example`
  - **Nova**: Adicionar coluna `is_readonly` BOOLEAN (default 0) para proteger templates pré-construídos
  
### Camada Backend
- **Novos Endpoints**:
  - `PUT /api/combos/meta/{template_name}` - Atualizar template
  - `POST /api/combos/meta/{template_name}/clone` - Clonar template
- **Lógica de Serviço**: `ComboService.update_template()`, `ComboService.clone_template()`
- **Validação**:  
  - Garantir `min < max` para cada parâmetro
  - Garantir `step > 0` e `step <= (max - min)`
  - Prevenir edição se `is_readonly = 1` (deve clonar primeiro)

### Camada Frontend
- **Nova Página**: `/combo/edit/:templateName`
  - Buscar metadados do template via `GET /api/combos/meta/{template_name}`
  - Exibir formulário com campos editáveis para cada parâmetro em `optimization_schema`
  - Submeter atualizações via `PUT /api/combos/meta/{template_name}`
- **Página Aprimorada**: `/combo/select`
  - Adicionar ícone/botão "Editar" próximo a cada card de template
  - Para templates somente-leitura, mostrar "Clonar & Editar"

## Decisões-Chave

### Decisão 1: Proteger Templates Pré-construídos
**Problema**: Usuários podem acidentalmente modificar templates do sistema, quebrando configurações padrão.

**Opções**:
1. Permitir todas as edições (arriscado)
2. Tornar templates pré-construídos somente-leitura, requer clonagem (mais seguro)
3. Adicionar histórico de versões/rollback (complexo)

**Escolha**: Opção 2 (Clone-para-Editar para pré-construídos)
- **Justificativa**: Equilibra segurança com flexibilidade. Usuários podem customizar sem quebrar originais.
- **Implementação**: Definir `is_readonly=1` para todos templates com `is_prebuilt=1`. UI força workflow de clonagem.

### Decisão 2: Estratégia de Validação
**Problema**: Ranges inválidos (ex: min > max) podem travar o otimizador.

**Opções**:
1. Validação apenas no frontend (rápido mas contornável)
2. Validação apenas no backend (seguro mas feedback lento)
3. Ambos frontend e backend (melhor UX + segurança)

**Escolha**: Opção 3 (Validação dupla)
- **Frontend**: Feedback instantâneo enquanto usuário digita (verificar min < max ao vivo)
- **Backend**: Portão final antes de escrever no banco (previne abuso de API)

### Decisão 3: Estrutura do Schema
**Problema**: `optimization_schema` pode ser dict plano ou aninhado com chave `parameters`.

**Opções**:
1. Forçar formato único (mudança quebrada)
2. Suportar ambos formatos (retrocompatível)

**Escolha**: Opção 2 (Suportar ambos)
- **Justificativa**: Templates existentes podem usar qualquer formato. Editor deve lidar com ambos graciosamente.
- **Implementação**: Frontend normaliza ao carregar, backend aceita ambos.

### Decisão 4: Modo de Edição Avançada (JSON)
**Problema**: Usuários técnicos podem querer editar diretamente o JSON completo do template para fazer mudanças estruturais ou adicionar metadados customizados.

**Opções**:
1. Apenas formulário visual (limitado mas seguro)
2. Toggle entre "Modo Simples (Formulário)" e "Modo Avançado (JSON)" (flexível)
3. Apenas editor JSON (poderoso mas intimidador para iniciantes)

**Escolha**: Opção 2 (Modo Dual com Toggle)
- **Justificativa**: Atende tanto usuários iniciantes (formulário) quanto avançados (JSON). Best of both worlds.
- **Implementação**: 
  - Toggle "Modo Avançado" no topo do editor
  - Quando ativado, substitui formulário por Monaco Editor (mesmo usado no VS Code)
  - Validação JSON em tempo real com syntax highlighting
  - Schema validation antes de salvar (prevenir JSON malformado)
- **Benefícios do JSON Editor**:
  - Editar toda estrutura do template de uma vez (incluindo `template_data`)
  - Copiar/colar configurações entre templates facilmente
  - Adicionar metadados customizados não suportados no formulário
  - Útil para importar/exportar templates

## Fluxo de UI

### Fluxo de Edição (Template Customizado)
```
/combo/select → Clicar "Editar" → /combo/edit/meu_template
  ↓
Carregar template → Exibir formulário (campos editáveis)
  ↓
Usuário modifica ranges → Salvar
  ↓
PUT /api/combos/meta/meu_template → Banco de dados atualizado
  ↓
Redirecionar para /combo/select com toast de sucesso
```

### Fluxo de Clonagem (Template Pré-construído)
```
/combo/select → Clicar "Clonar & Editar" em multi_ma_crossover
  ↓
POST /api/combos/meta/multi_ma_crossover/clone?new_name=minha_estrategia_ma
  ↓
Banco de dados cria nova linha (is_readonly=0, is_prebuilt=0)
  ↓
Redirecionar para /combo/edit/minha_estrategia_ma
  ↓
(Mesmo que Fluxo de Edição acima)
```

## Exemplo de Formato de Dados

### Antes (Banco de Dados)
```json
{
  "name": "multi_ma_crossover",
  "optimization_schema": {
    "parameters": {
      "sma_medium": {"min": 25, "max": 60, "step": 1},
      "sma_long": {"min": 50, "max": 200, "step": 1},
      "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002},
      "ema_short": {"min": 8, "max": 80, "step": 1}
    }
  },
  "is_readonly": 1
}
```

### Após Edição (Mudanças do Usuário)
```json
{
  "name": "minha_estrategia_ma",
  "optimization_schema": {
    "parameters": {
      "sma_medium": {"min": 10, "max": 50, "step": 2},
      "sma_long": {"min": 30, "max": 150, "step": 5},
      "stop_loss": {"min": 0.01, "max": 0.10, "step": 0.005},
      "ema_short": {"min": 5, "max": 60, "step": 2}
    }
  },
  "is_readonly": 0
}
```

## Mitigação de Riscos

1. **Perda de Dados**: Backup do banco antes do primeiro deploy
2. **Bypass de Validação**: Validação do backend é autoritativa
3. **Edições Concorrentes**: Usar locking otimista (verificar timestamp no update)
4. **Complexidade de UI**: Começar com formulário simples, iterar baseado em feedback
