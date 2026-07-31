## Context

A Home e a Carteira já usam a chave Binance do usuário via `/api/user/binance-credentials`. A primeira entrega colocou o formulário em `/preferences`. Alan pediu rework: o lugar certo é o **profile do usuário**, acessado pela barra de conta (Meu Perfil).

## Goals / Non-Goals

**Goals:**
- Formulário completo de Credenciais Binance em `/profile`.
- Acesso via menu da conta na barra (Meu Perfil), sem item separado Preferências na nav.
- Carteira com status + link para Meu Perfil.
- Redirect `/preferences` → `/profile` para não quebrar bookmarks.

**Non-Goals:**
- Embutir inputs de API Key no dropdown da barra (só o atalho Meu Perfil).
- Mudar Preferências do sistema (admin).
- Alterar contrato backend.

## Decisions

1. **Host = ProfilePage** — identidade + integrações da conta no mesmo lugar.
2. **Remover nav Preferências** — evita segunda porta de entrada; admin mantém Preferências do sistema.
3. **Redirect `/preferences` → `/profile`** — compatibilidade com a entrega anterior.
4. **CTA da Carteira** — “Configurar no Perfil” apontando para `/profile`.
5. **UI do Perfil (rework visual)** — um card com duas seções claras (`Dados da conta` / `Credenciais Binance`), inputs rotulados no padrão do perfil, CTA amarelo do DESIGN.md, sem painel estilo carteira; onboarding global oculto em `/profile`.

## Risks / Trade-offs

- [Usuário procura `/preferences`] → redirect silencioso para `/profile`.
- [Baseline visual muda] → atualizar preferences→profile e wallet.

## Migration Plan

1. Ship front com Profile + redirect + nav limpa.
2. Sem migração de dados.
3. Rollback: reverter front.

## Open Questions

- Nenhum bloqueante.
