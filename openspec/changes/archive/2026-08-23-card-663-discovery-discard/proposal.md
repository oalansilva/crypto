# Change: Descartar (e promover) resultado de Discovery no leaderboard

## Why

Depois de uma varredura, o administrador precisa decidir o destino de cada candidato: promover a favorito tier 3 **ou** tirar do ranking se não for usar. Hoje a promoção some ou fica só desabilitada (baixa amostra, duplicata, já promovido) e **não existe exclusão**. Candidatos indesejados permanecem no leaderboard e poluem a revisão.

## What Changes

- Mantém promoção a tier 3 com confirmação; se estiver bloqueada, o botão **permanece visível** com motivo (não some da coluna Ação).
- Adiciona **Excluir** por resultado (`result_id`) no leaderboard da varredura selecionada, com modal de confirmação.
- Persistência do descarte: o resultado não reaparece ao recarregar a mesma varredura; promoção de resultado descartado é rejeitada.
- Não apaga favorito já criado; linha `already_promoted` não oferece Excluir (só estado Favorito tier 3).
- Fora de escopo: apagar varredura inteira, lixeira/undo, reescrever ranking/walk-forward.

## Capabilities

### New Capabilities

- `discovery-discard`: descarte administrativo persistente de um resultado de varredura.

### Modified Capabilities

- `discovery-leaderboard`: coluna Ação com promover (sempre visível quando aplicável) + excluir; filtro padrão omite descartados.
- `discovery-promotion`: rejeita promover `discarded`; UI de promoção permanece na linha até descarte ou promoção bem-sucedida.

## Impact

- **UI impact: affected** — delta no leaderboard de Discovery (ações + modal de exclusão), mesma tela/shell.
- Backend: estado `discarded` no resultado; endpoint autenticado admin; leaderboard GET exclui descartados por padrão.
- Frontend: `DiscoveryPage` action-cell e modal.
- Sem mudança de motor de otimização.

## Card

[#663](https://github.com/oalansilva/crypto/issues/663)
