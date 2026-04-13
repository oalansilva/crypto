# Contrato de sprint

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta sprint
remover funcionalidade kaban

## Fora de escopo
- Remover a aplicacao Kanban standalone.
- Alterar paginas fora do fluxo de remocao de acesso ao Kanban no app crypto.

## Comportamentos esperados
- A rota `/kanban` nao deve mais existir no app crypto.
- A navegacao principal nao deve mais exibir o item `Kanban`.
- O restante da navegacao do app crypto deve continuar funcional.

## Sensores obrigatorios
- Build do frontend com `npm --prefix frontend run build`.

## Evidencias esperadas
- Diff removendo a rota `/kanban` de `frontend/src/App.tsx`.
- Diff removendo o item `Kanban` de `frontend/src/components/AppNav.tsx`.
- Build do frontend concluido com sucesso.

## Riscos conhecidos
- Ainda existem outras referencias a Kanban no frontend fora deste item claimado e elas precisam ser tratadas nos proximos work items.
