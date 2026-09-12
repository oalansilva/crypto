## Why

Na aba Acompanhando o administrador já vê as parciais (top-5) com GO/NO-GO e as seis métricas, mas não consegue promover nem excluir ali — tem de ir ao Decidir. Numa varredura longa a decisão fica adiada ou abandonada. Q1–Q7=A estão travadas: Promover e Excluir em cada linha das parciais, sempre que elas estão visíveis, só top-5, NO-GO só alerta, mesmos diálogos, pós-promover ocupa o lugar, pós-excluir some nas duas abas.

## What Changes

- Na tabela de parciais (top-5) da aba Acompanhando, cada linha elegível ganha **Promover** e **Excluir** — o mesmo padrão visual e de bloqueio do Decidir, sem mudar de aba.
- Vale com varredura **em curso**, **pausada** ou **recuperada** no F5 (parciais visíveis).
- NO-GO com amostra suficiente: selo visível; Promover continua disponível (aviso só alerta), igual ao Decidir (#896).
- Clique Promover abre o diálogo actual de favorito tier 3; Excluir abre o de descarte. Cancelar não mexe no candidato nem na varredura.
- Depois de promover: a linha fica **Favorito tier 3**, ocupa o lugar no top-5; a varredura **não** para.
- Depois de excluir: o candidato some das parciais **e** do Decidir da mesma varredura; o próximo já processado pode ocupar o lugar; não reabre o rascunho.
- Bloqueios existentes (baixa amostra / duplicata / já promovido) e a regra «ação numa aba actualiza o mesmo candidato na outra» continuam iguais ao Decidir.

Fora: lista completa/paginação/filtros no Acompanhando; Montar; motor/ranking/selo/Calmar; métricas da grelha (#906); Favoritos (#897); apagar favorito já promovido; reabrir Promover no Decidir (#896); redesign da aba.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-three-modes`: parciais top-5 do Acompanhando expõem Promover e Excluir; o top-5 não vira lista completa; Montar sem delta.
- `discovery-promotion`: promoção a partir das parciais visíveis usa o mesmo diálogo tier 3; NO-GO não trava; a linha permanece como Favorito tier 3; a varredura segue.
- `discovery-discard`: exclusão a partir das parciais usa o mesmo diálogo; some nas duas abas; o próximo processado pode ocupar o lugar; não reabre o rascunho.

## Impact

- Frontend: `DiscoveryPage.tsx` / `DiscoveryPage.css` — coluna Ação nas parciais (reuso de `action-cell` / `promote-action` / `discard-action` e dos diálogos já no Decidir); refresh do top-5 após discard.
- API: promote/discard já agem no candidato visível; sem API nova neste card. Se o servidor recusar com varredura a correr, o Apply fecha o contrato (produto exige que a ação no candidato visível funcione).
- Specs canónicas: `openspec/specs/discovery-three-modes`, `discovery-promotion`, `discovery-discard`.
- Protótipo: `frontend/public/prototypes/card-916-discovery-acompanhar-acoes/`.
- Sem mudança em Montar, motor, ranking, selo, métricas da grelha, Favoritos ou coluna Ação do Decidir.
