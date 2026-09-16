## Why

Quem abre a Descoberta para montar uma varredura já encontra Templates e Símbolos pré-escolhidos e Time Frames com 4 horas e 1 dia marcados. O operador quer começar vazio e escolher o que entra; o único default desejado é 1 dia.

## What Changes

- Rascunho novo na Descoberta (primeira abertura **ou** botão «Novo rascunho»): Templates nenhum selecionado (contagem 0, sem chips); Símbolos nenhum selecionado (mesma regra); Time Frames só **1 dia** marcado e **4 horas** desmarcado.
- Continua bloqueado iniciar sem ao menos 1 template e 1 símbolo. O aviso «Falta fazer» aparece logo no rascunho novo — consequência do pedido, não regresso.
- O operador ainda marca templates, símbolos e 4 horas depois, como hoje.
- Reabrir uma varredura já gravada traz o que estava marcado; **não** aplica estes defaults por cima. Se a varredura gravada não tiver Time Frame, não cair de volta em 4 horas + 1 dia.
- «Novo rascunho» passa a aplicar estes defaults (hoje só libera o configurador e **não** limpa a seleção).

Fora: tela Combo; catálogo de templates ou lista de símbolos; preflight/limite/promoção; redesenhar o layout das três opções; Direção, período e métrica de ranking (ficam como hoje).

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-catalog-selection`: rascunho novo não pré-escolhe os primeiros templates nem os primeiros símbolos; as summaries abrem em 0 selecionados, sem chips.
- `discovery-three-modes`: rascunho novo no modo Montar abre com Time Frames só em **1 dia**; «Novo rascunho» aplica os mesmos defaults; restaurar varredura já gravada reaproveita os eixos gravados sem overlay destes defaults.

## Impact

- Frontend: `DiscoveryPage.tsx` — deixar de pré-escolher `flat.slice(0, 3)` / `list.slice(0, 4)` quando o rascunho não é restore; default de Time Frames `['1d']` em vez de `['4h', '1d']`; `newDraft` limpa Templates/Símbolos e aplica Time Frames só 1 dia; `hydrateFromSweep` não cai em `['4h', '1d']` quando o eixo gravado vem vazio.
- Sem mudança de API, catálogo, preflight, limite, promoção, Combo, Direção, período ou ranking.
- Specs canónicas: `openspec/specs/discovery-catalog-selection`, `discovery-three-modes`.
- Protótipo: `frontend/public/prototypes/card-952-discovery-rascunho-defaults/`.
