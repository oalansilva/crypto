# Change Proposal: Lab Real-time Logs

## Why

Atualmente, quando um step do Lab está em execução (ex: `combo_optimization` na fase `implementation`), o usuário não tem visibilidade do progresso ou dos logs em tempo real. Isso cria uma experiência de "caixa preta" onde o usuário fica esperando sem saber o que está acontecendo.

A tela de configuração de combo (`/combo/configure`) já possui um botão "Ver Logs" que mostra logs em tempo real durante a otimização. O Lab precisa da mesma funcionalidade para proporcionar transparência e melhor UX durante a execução de steps.

## What

Adicionar visualização de logs em tempo real na tela do Lab durante a execução de steps, similar ao botão "Ver Logs" da tela de configuração de combo.

## Scope

- Backend: Endpoint SSE para streaming de logs do step em execução
- Frontend: Botão "Ver Logs" e painel de logs na tela do Lab (durante execução)
- Integração com sistema de logs existente do combo

## Success Criteria

- [ ] Usuário pode clicar em "Ver Logs" durante execução de step no Lab
- [ ] Logs aparecem em tempo real (streaming) no painel
- [ ] Design consistente com a tela de configuração de combo
- [ ] Funciona para todos os steps que geram logs (combo_optimization, etc.)
