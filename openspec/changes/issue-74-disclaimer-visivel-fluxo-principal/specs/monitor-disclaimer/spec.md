# Specification: Disclaimer visível no fluxo principal

## Requirements

1. Deve existir um componente reutilizável com texto de isenção:
   - Produto educacional.
   - Apoio à decisão, sem recomendação financeira.
   - Sem promessa de lucro ou retorno garantido.
2. O aviso deve aparecer no `LoginPage` e no `MonitorPage` em primeira sessão.
3. O aviso deve poder ser dispensado e não reaparecer na mesma sessão após dismissal.
4. Estilo deve manter contraste adequado e não conflitar com o layout principal.

## Acceptance Criteria

- Acesso não autenticado em `/login`: mensagem aparece sem interação de autenticação prévia.
- Usuário autenticado em `/monitor`: mensagem aparece na primeira sessão e pode ser dispensada.
- Após dispensar, o aviso não reaparece enquanto persistir `sessionStorage` da sessão.
- Copy auditável e sem linguagem de guru/garantia de lucro.

## Risks / tradeoffs

- A sessão é rastreada em `sessionStorage`, então o aviso reaparece após novo ciclo de navegador.
- O aviso pode ser dispensado para reduzir ruído de leitura recorrente.
