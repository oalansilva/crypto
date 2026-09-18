## Problema

Quem manda correr uma varredura na Descoberta em produção vê a tela perder o acompanhamento: banner vermelho «Não foi possível verificar a varredura ativa» / «O sweep continua protegido no servidor. Tente novamente antes de iniciar outra run.», aba Acompanhar em «Acompanhando #—» e rascunho vazio no Montar. A varredura **continua no servidor**. Sair, deslogar e logar de novo reconstitui a tela corretamente sobre a mesma run em curso.

## História

Como operador em produção,
quero que a Descoberta continue mostrando a varredura que já está a correr no servidor — ou recupere sozinha, sem eu deslogar —,
para eu não achar que perdi a conexão nem ficar bloqueado de acompanhar essa run ou de iniciar outra.

## Entra

- Tela Descoberta em PROD (`https://criptofarol.com.br/combo/discovery`), operador autenticado (não é o ecrã «Sessão expirada»).
- Sempre que há varredura em curso no servidor, a tela reconstitui **sozinha** o Acompanhar dessa run: número verdadeiro (não «#—») e progresso. O operador não clica nem desloga.
- Given a varredura segue viva no servidor e a tela iria cair no banner vermelho + Montar vazio + «Acompanhando #—»: When a reconstituição automática corre, Then o operador vê Acompanhar dessa run (número verdadeiro e progresso) sem tocar em «Tentar novamente» e sem logout/login.
- «Tentar novamente» só entra se a reconstituição automática falhar de novo. Não é o caminho feliz.
- Essa falha de tela **não** cancela nem duplica a varredura no servidor. Iniciar outra enquanto a primeira segue viva continua bloqueado; o desbloqueio de «iniciar outra» é ver o Acompanhar (e só então cancelar / montar de novo, se quiser).
- Logout/login deixa de ser o conserto.
- Q1=A (2026-09-17): reconstituição sozinha; clique só na falha da automática.
- Evidência 2026-09-17 (PROD, conta Alan, badge PROD):
  - URL: `https://criptofarol.com.br/combo/discovery?_sm_nck=1`
  - Banner: «Não foi possível verificar a varredura ativa» / «O sweep continua protegido no servidor.» Botão «Tentar novamente» visível no banner.
  - Aba Montar activa; rascunho vazio (0 templates, 0 símbolos); preflight bloqueado («0 combinações»); aba Acompanhar em «Acompanhando #—».
  - Isto é o ecrã de falha de verificação com rascunho novo, não o Acompanhar logo após Iniciar.
  - Teste do operador: sair, deslogar, logar de novo → a tela carrega a descoberta ainda em curso.

## Não entra

- Restaurar após F5 (#664, já Pronto) — o furo agora é a verificação falhar com a sessão ainda autenticada, não o reload em si. O banner vermelho e o botão «Tentar novamente» já existem; este card não redesenha modos.
- Clique em «Tentar novamente» como caminho feliz (Q1=A).
- Acompanhar que mente «em curso» depois de a run já ter fechado (#954).
- Defaults do rascunho (#952) — o rascunho vazio na evidência é o Montar sem sweep visível, não o default em si.
- Ecrã «Sessão expirada» (recarregar página).
- Acelerar worker, Deep/WF, promoção/favorito.
- Combo `/combo/select`, Favoritos, Monitor.
- Inventar ecrã novo de modos além de Montar / Acompanhar / Decidir.

## Why

Em produção, com sessão autenticada, a Descoberta perde o Acompanhar da varredura que o servidor ainda está a correr: banner vermelho, «Acompanhando #—» e rascunho vazio no Montar. Logout/login reconstitui a mesma run. O operador precisa que a tela recupere sozinha, sem deslogar e sem tratar «Tentar novamente» como caminho feliz.

## What Changes

- Com varredura em curso no servidor e sessão autenticada, `/combo/discovery` reconstitui **sozinha** o Acompanhar dessa run: número verdadeiro (não «#—») e progresso. Sem clique. Sem logout.
- Se a verificação iria cair no banner vermelho + Montar vazio + «Acompanhando #—», a reconstituição automática corre até hidratar o Acompanhar; o operador não toca em «Tentar novamente».
- «Tentar novamente» só aparece se essa reconstituição automática falhar de novo. Não é o caminho feliz.
- A falha de tela não cancela nem duplica a run no servidor. Iniciar outra continua bloqueado até o operador ver o Acompanhar.
- Logout/login deixa de ser o conserto.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-three-modes`: com sweep não-terminal vivo no servidor e sessão autenticada, o modo visível reconstitui-se sozinho em Acompanhar dessa run (número verdadeiro e progresso); Montar vazio + «Acompanhando #—» deixa de ser o estado estável desta falha de verificação.
- `discovery-sweep`: a verificação do sweep activo, quando falha com a sessão ainda autenticada, repete-se sozinha até hidratar o Acompanhar; «Tentar novamente» só após essa automática falhar de novo; start de outra run permanece bloqueado; a run no servidor não é cancelada nem duplicada.

## Impact

- Frontend: `DiscoveryPage.tsx` — `restoreSession` / `recoveryStatus`: repetir a verificação sozinha quando a sessão continua autenticada, até o Acompanhar hidratar; o banner vermelho e «Tentar novamente» só no residual dessa automática; Iniciar outra continua bloqueado até o Acompanhar visível.
- Backend/worker: fora (não acelerar worker; o GET do sweep activo já existe; a run continua protegida no servidor).
- Specs canónicas: `openspec/specs/discovery-three-modes`, `openspec/specs/discovery-sweep`.
- Protótipo: `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/`.
- Fora: F5/#664; clique em «Tentar novamente» como caminho feliz; #954; #952; ecrã «Sessão expirada»; acelerar worker; Combo/Favoritos/Monitor; ecrã novo de modos.
