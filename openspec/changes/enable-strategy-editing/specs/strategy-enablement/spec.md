# Spec Delta: Strategy Enablement

## ADDED Requirements

### Requirement: Template Editing via API
**ID**: REQ-STRAT-EDIT-001

O sistema SHALL permitir que usuários atualizem templates de estratégia existentes através de uma API REST.

#### Scenario: Editar ranges de otimização de um template customizado
**Given** um template de estratégia customizado existe no banco com `is_readonly = 0`  
**And** o usuário tem permissão para editar templates  
**When** o usuário envia `PUT /api/combos/meta/{template_name}` com novo `optimization_schema`  
**Then** o banco de dados é atualizado com os novos valores  
**And** uma resposta 200 OK é retornada com o template atualizado  

#### Scenario: Rejeitar edição de template somente-leitura
**Given** um template pré-construído existe com `is_readonly = 1`  
**When** o usuário tenta enviar `PUT /api/combos/meta/{template_name}`  
**Then** uma resposta 403 Forbidden é retornada  
**And** uma mensagem é exibida: "Este template é somente-leitura. Clone-o para editar."  
**And** o banco de dados permanece inalterado

#### Scenario: Validar ranges inválidos
**Given** um usuário está editando um template  
**When** o usuário envia ranges onde `min >= max` para qualquer parâmetro  
**Then** uma resposta 400 Bad Request é retornada  
**And** uma mensagem de erro específica indica qual parâmetro é inválido  
**And** o banco de dados permanece inalterado

---

### Requirement: Template Clonagem
**ID**: REQ-STRAT-CLONE-001

O sistema SHALL permitir que usuários clonem templates existentes para criar versões editáveis.

#### Scenario: Clonar template pré-construído
**Given** um template pré-construído "multi_ma_crossover" existe com `is_readonly = 1`  
**When** o usuário envia `POST /api/combos/meta/multi_ma_crossover/clone?new_name=minha_estrategia`  
**Then** um novo template "minha_estrategia" é criado no banco  
**And** o novo template tem `is_readonly = 0` e `is_prebuilt = 0`  
**And** todos os outros campos são copiados do original  
**And** uma resposta 201 Created é retornada com o novo template

#### Scenario: Prevenir clonagem com nome duplicado
**Given** um template "minha_estrategia" já existe  
**When** o usuário tenta clonar qualquer template com `new_name=minha_estrategia`  
**Then** uma resposta 409 Conflict é retornada  
**And** uma mensagem indica que o nome já existe  
**And** nenhum novo template é criado

---

### Requirement: UI de Edição de Template
**ID**: REQ-STRAT-UI-001

O sistema SHALL fornecer uma interface gráfica para editar parâmetros de otimização de templates.

#### Scenario: Acessar editor de template customizado
**Given** um template customizado "minha_estrategia" existe  
**When** o usuário navega para `/combo/edit/minha_estrategia`  
**Then** um formulário é exibido mostrando todos os parâmetros em `optimization_schema`  
**And** cada parâmetro tem campos de entrada para `min`, `max`, e `step`  
**And** os valores atuais são pré-preenchidos nos campos

#### Scenario: Salvar alterações do editor
**Given** o usuário está no editor de template  
**And** o usuário modificou alguns valores de `min` ou `max`  
**When** o usuário clica no botão "Salvar"  
**Then** os novos valores são enviados via `PUT /api/combos/meta/{template_name}`  
**And** um toast de sucesso é exibido: "Template atualizado com sucesso"  
**And** o usuário é redirecionado para `/combo/select`

#### Scenario: Validação em tempo real no formulário
**Given** o usuário está editando um parâmetro  
**When** o usuário define `min` maior que `max`  
**Then** uma mensagem de erro aparece abaixo do campo imediatamente  
**And** o botão "Salvar" é desabilitado  
**And** a mensagem desaparece quando a validação passa

---

### Requirement: Acesso ao Editor pela Página de Seleção
**ID**: REQ-STRAT-NAV-001

O sistema SHALL fornecer acesso conveniente ao editor de templates a partir da página de seleção.

#### Scenario: Botão de editar para templates customizados
**Given** o usuário está em `/combo/select`  
**And** um template customizado está sendo exibido  
**When** o usuário passa o mouse sobre o card do template  
**Then** um botão "Editar" aparece  
**When** o usuário clica no botão "Editar"  
**Then** o usuário é redirecionado para `/combo/edit/{template_name}`

#### Scenario: Botão de clonar para templates somente-leitura
**Given** o usuário está em `/combo/select`  
**And** um template pré-construído está sendo exibido  
**When** o usuário passa o mouse sobre o card do template  
**Then** um botão "Clonar & Editar" aparece (não "Editar")  
**When** o usuário clica no botão  
**Then** um modal pede um nome para o novo template  
**When** o usuário fornece um nome e confirma  
**Then** o sistema clona o template via API  
**And** o usuário é redirecionado para o editor do clone

---

### Requirement: Modo de Edição Avançada (JSON)
**ID**: REQ-STRAT-JSON-001

O sistema SHALL fornecer um modo de edição avançada com editor JSON para usuários técnicos que desejam editar diretamente a estrutura completa do template.

#### Scenario: Alternar para Modo Avançado
**Given** o usuário está no editor de template (`/combo/edit/{template_name}`)  
**When** o usuário clica no toggle "Modo Avançado"  
**Then** o formulário de campos individuais é substituído por um editor JSON  
**And** o editor exibe o JSON completo do template (incluindo `optimization_schema` e `template_data`)  
**And** o editor fornece syntax highlighting e validação em tempo real

#### Scenario: Editar e salvar JSON válido
**Given** o usuário está no Modo Avançado  
**And** o usuário modificou o JSON  
**When** o usuário clica em "Salvar"  
**And** o JSON é válido  
**Then** o template é atualizado no banco com os novos valores  
**And** um toast de sucesso é exibido  
**And** o usuário permanece no Modo Avançado

#### Scenario: Prevenir salvamento de JSON malformado
**Given** o usuário está no Modo Avançado  
**And** o usuário modificou o JSON com syntax error (ex: vírgula faltando)  
**When** o usuário tenta clicar em "Salvar"  
**Then** o botão "Salvar" está desabilitado  
**And** uma mensagem de erro indica a linha/coluna do erro de syntax  
**And** nenhuma requisição é enviada ao backend

#### Scenario: Validar estrutura de schema no JSON
**Given** o usuário está no Modo Avançado  
**And** o usuário modificou o JSON com valores inválidos (ex: `min > max`)  
**When** o usuário clica em "Salvar"  
**Then** uma requisição é enviada ao backend  
**And** o backend retorna 400 Bad Request com detalhes do erro  
**And** uma mensagem de erro é exibida ao usuário  
**And** o banco de dados permanece inalterado

## MODIFIED Requirements

*(Nenhum requisito existente foi modificado por esta mudança)*

## REMOVED Requirements

*(Nenhum requisito foi removido por esta mudança)*
