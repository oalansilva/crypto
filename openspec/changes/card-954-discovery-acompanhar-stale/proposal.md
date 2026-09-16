## Why

Quem acompanha uma varredura na Descoberta vê o Acompanhar parado em «EM CURSO / Varredura em execução / 0 de 1» e «Parciais ainda carregando», embora **essa mesma** varredura já tenha terminado no servidor — e, enquanto ainda corre, a linha do candidato pode não aparecer nas parciais mesmo depois de o resultado já existir. Testemunho DEV 2026-09-16: Acompanhar `#00e9a4d28e114099bc18fc85d5500df3` 0/1 vazio com o banco `completed` 1/1 (`RS-263BF9A075`); o print do leaderboard era o Histórico de **outra** run.

## What Changes

- Enquanto a varredura activa **ainda não fechou**, se o candidato já existe as parciais top-5 mostram essa linha; a frase «Parciais ainda carregando» **não** permanece. O progresso não fica 0 de N se essa run já processou combinações (Q2=B).
- Quando o servidor fecha **esta** run: o Acompanhar deixa de dizer que está em curso (chip EM CURSO, «Varredura em execução», contador 0 de N). Sem clicar e sem F5, o operador passa a ver o ranking fechado no **Decidir desta varredura**. Não há ecrã «Acompanhar já concluída» (Q1=A).
- A copy «separado do Histórico exibido» pode ficar enquanto a activa ainda corre. Abrir o Histórico de **outra** run **não** conta como conserto.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-three-modes`: o modo Acompanhar existe só enquanto a run activa ainda não fechou; no instante em que o servidor a marca terminal, a vista passa ao Decidir **desta** run (ranking hidratado), sem ecrã Acompanhar concluída e sem F5.
- `discovery-leaderboard`: as parciais do Acompanhar passam a reflectir o candidato assim que ele existir nesta run (não ficam no vazio «Parciais ainda carregando»); o contador do progresso desta run não fica 0 de N se já processou.

## Impact

- Frontend: `DiscoveryPage.tsx` — o intervalo que já actualiza o sweep activo também relê as parciais; no término troca o modo para Decidir desta run e hidrata o ranking. Sem unir ao Histórico de outra run. Sem ecrã novo de modos.
- Backend/worker: fora (não acelerar worker; o GET da run activa já deve devolver `processed`/`state` correntes).
- Specs canónicas: `openspec/specs/discovery-three-modes`, `openspec/specs/discovery-leaderboard`.
- Protótipo: `frontend/public/prototypes/card-954-discovery-acompanhar-stale/`.
- Fora: ecrã «Acompanhar já concluída»; unir ao Histórico/Decidir de **outra** run; #952 / #948 / #949 / #916 / #664; Combo `/combo/select`, Favoritos, Monitor; acelerar worker; inventar ecrã novo além de Montar / Acompanhar / Decidir.
