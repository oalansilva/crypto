# Monitor Home Route (Frontend)

## Requirement

- O fluxo de autenticação (login ou cadastro) deve terminar em `/monitor`.
- A raiz autenticada da aplicação (`/`) deve atuar como entrada operacional e
  redirecionar para `/monitor`.
- Quando acesso protegido exigir autenticação, o retorno deve preservar a rota de origem em `location.state.returnTo`.
- A navegação principal não deve chamar `/` de “Playground”; `/monitor` é a home operacional.

### Scenario: Login bem-sucedido

- **WHEN** um usuário autentica com credenciais válidas em `/login`
- **THEN** o app navega para `/monitor` com `replace`.

### Scenario: Cadastro/autologin bem-sucedido

- **WHEN** um novo usuário finaliza o cadastro em `/login` (modo `register`)
- **THEN** o app navega para `/monitor` com `replace`.

### Scenario: Usuário autenticado abre `/`

- **WHEN** um usuário autenticado acessa `/`
- **THEN** a rota principal autenticada redireciona para `/monitor`.

### Scenario: Usuário sem autenticação cai em /login e retorna após login

- **WHEN** usuário sem autenticação acessa `/signals` e é enviado para `/login` com `state.returnTo`
- **AND** faz login com sucesso
- **THEN** a navegação retorna para `/signals`.

### Scenario: Navegação principal reflete home operacional

- **WHEN** usuário está no layout autenticado
- **THEN** o item de acesso principal aponta para `Monitor` em `/monitor` e não para `Playground` em `/`.
