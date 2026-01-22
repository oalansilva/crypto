# Proposta: Habilitar Edição de Templates de Estratégia

## Resumo
Permitir que usuários editem templates de estratégias combinadas através de uma UI dedicada, possibilitando modificação de parâmetros de otimização (valores min/max/step) e metadados da estratégia sem necessitar acesso direto ao banco de dados.

## Descrição do Problema
Atualmente, usuários não conseguem modificar os ranges padrão de otimização para templates de estratégia. Os valores exibidos na tela "Configure Backtest" vêm da coluna `optimization_schema` no banco de dados. Quando esses valores estão ausentes ou incorretos, usuários precisam:
- Aceitar valores calculados automaticamente (50%-150% dos defaults dos indicadores)
- Editar manualmente o banco de dados (requer conhecimento técnico)
- Criar workarounds ajustando valores por execução (mas não podem salvar mudanças permanentes)

Isso cria atrito no workflow de otimização e impede usuários de iterarem efetivamente em suas estratégias.

## Solução Proposta
Adicionar um "Editor de Templates de Estratégia" acessível pela página de seleção de templates (`/combo/select`) que permite aos usuários:
1. Visualizar todos os templates de estratégia existentes
2. Editar schema de otimização (ranges min/max/step dos parâmetros)
3. Modificar metadados do template (nome, descrição)
4. Salvar alterações de volta no banco de dados
5. Opcionalmente clonar templates para customização
6. **[Novo]** Modo de edição avançada com editor JSON para usuários técnicos

## Benefício ao Usuário
- **UX Melhorada**: Editar estratégias através de interface visual ao invés de SQL
- **Iteração Mais Rápida**: Ajustar rapidamente ranges de otimização baseado em resultados de backtest
- **Redução de Erros**: Validação de formulário previne configurações inválidas
- **Melhor Organização**: Clonar e customizar templates pré-construídos sem modificar originais
- **Flexibilidade para Power Users**: Editor JSON permite edições avançadas (modificar estrutura completa do schema, adicionar metadados customizados)

## Critérios de Sucesso
- Usuários conseguem editar parâmetros de otimização de qualquer template via UI
- Mudanças persistem corretamente no banco de dados
- Validação previne alterações problemáticas (ex: min > max)
- Templates pré-construídos originais podem ser marcados como "somente leitura" com fluxo clone-para-editar

## Mudanças Relacionadas
- Constrói sobre `database-driven-strategies` (completo)
- Pode melhorar `save-combo-favorites` (5/6 tarefas)

## Fora do Escopo
- Adicionar/remover indicadores dos templates (funcionalidade v2)
- Criar templates completamente novos do zero (mudança separada)
- Editar lógica da estratégia/condições de entrada-saída
