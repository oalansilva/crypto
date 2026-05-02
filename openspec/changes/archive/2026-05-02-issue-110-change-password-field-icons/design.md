## Context

A tela `/change-password` usa o componente compartilhado `Input` com icones `lucide-react` nos tres campos de senha. O componente adiciona `pl-12` quando existe icone, mas a classe global `.input` define `padding: 0 var(--space-md)`, podendo sobrescrever o utilitario Tailwind dependendo da ordem final do CSS. O resultado visivel e o icone ocupando a mesma area do texto/placeholder.

## Goals / Non-Goals

**Goals:**

- Garantir espacamento estavel entre icone e texto nos inputs com icone.
- Corrigir a tela de alterar senha sem criar um padrao alternativo de formulario.
- Cobrir a regressao com um teste E2E focado em layout.

**Non-Goals:**

- Alterar fluxo de autenticacao, endpoint de troca de senha ou mensagens de toast.
- Redesenhar a pagina de seguranca.
- Adicionar dependencia visual ou biblioteca nova.

## Decisions

- Corrigir no componente compartilhado `Input`, usando padding inline calculado quando houver `icon`. Isso ataca a causa da colisao e preserva telas que ja usam `Input`.
- Manter a API do componente igual (`icon`, `label`, `error`), evitando mudanca em chamadas existentes.
- Validar a tela com Playwright por medicao de bounding boxes entre icone e input, alem do build frontend.

## Risks / Trade-offs

- [Risk] Inputs com `className` customizado podem tentar sobrescrever padding esquerdo.
  Mitigation: aplicar a classe de espacamento depois de `className`, mantendo prioridade para o caso com icone.
- [Risk] O teste visual pode ficar fragil se o tema mudar dimensoes.
  Mitigation: validar relacao espacial minima entre icone e inicio do campo, nao cor exata ou screenshot pixel-perfect.
