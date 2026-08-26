## ADDED Requirements

### Requirement: Forgot-password não loga e-mail, token ou link em INFO
O handler de forgot-password SHALL NOT gravar o e-mail do usuário, o token de reset nem o URL/link de reset em logs de nível INFO.

#### Scenario: Pedido de reset
- **WHEN** um cliente chama forgot-password para um e-mail existente
- **THEN** qualquer log INFO emitido por esse fluxo SHALL NOT conter o endereço de e-mail
- **AND** SHALL NOT conter o token de reset
- **AND** SHALL NOT conter o reset link
