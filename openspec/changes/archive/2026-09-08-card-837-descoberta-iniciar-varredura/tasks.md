# Tasks: Descoberta — Iniciar começa a varredura da seleção atual (card #837)

> Fonte: proposal + design § Apply contract. Só após `Status=Pronto para Dev` (T7). Proto já fechado em Design.

## 1. Spec canónica

- [ ] 1.1 Aplicar o delta `openspec/changes/card-837-descoberta-iniciar-varredura/specs/discovery-sweep/spec.md` em `openspec/specs/discovery-sweep/spec.md`: começo novo pós-terminal, bloqueio orientado com execução, sem duplicata na mesma seleção, erro em linguagem de operação (aceite 1–7).

## 2. Backend — criação da varredura (aceite 1–5, 7)

- [ ] 2.1 **Iniciar** pós-terminal (cancelada/concluída/falha) trata a seleção da tela como começo novo: nova varredura com a seleção enviada, mesmo que igual à da run morta; nunca reabre a run morta nem devolve 409 do caminho feliz (aceite 2, 3).
- [ ] 2.2 Com varredura em execução, **Iniciar** de outra seleção não cria segunda nem substitui a ativa; resposta orienta cancelar antes (aceite 4).
- [ ] 2.3 Repetição na mesma seleção em criação/execução retorna a existente sem duplicar (aceite 5).
- [ ] 2.4 Falha de início devolve mensagem em linguagem de operação (o que fazer), sem JSON/jargão (aceite 7).

## 3. Frontend — DiscoveryPage (aceite 1–7)

- [ ] 3.1 Pós-terminal, rascunho editável e **Iniciar** clicável sem exigir **Novo rascunho**; clique inicia nova varredura da seleção da tela e mostra progresso (aceite 1–3).
- [ ] 3.2 Com execução em curso e outra seleção, **Iniciar** bloqueado com aviso para cancelar antes (aceite 4).
- [ ] 3.3 Duplo clique / repetição na mesma seleção em criação/execução: sem duplicata, mostra a existente (aceite 5).
- [ ] 3.4 Após reload pós-cancelar, **Iniciar** monta e inicia a seleção da tela sem segundo botão e sem limpar navegador (aceite 6).
- [ ] 3.5 Erro de início em texto de operação, sem JSON/jargão; sem mudar preflight, limite, leaderboard, promoção, descarte ou o identificador interno do rascunho (aceite 7).

## 4. Testes (aceite 1–7)

- [ ] 4.1 Cobrir: início de rascunho válido; pós-terminal com seleção diferente e igual (nova varredura, sem reabrir morta); execução + outra seleção (bloqueio orientado); repetição mesma seleção (sem duplicata); reload pós-cancelar; erro operacional sem JSON.
- [ ] 4.2 Playwright da rota `/combo/discovery` nos fluxos do § Prototype do design.

## 5. Proto (já em Design)

- [ ] 5.1 Protótipo clone+delta em `frontend/public/prototypes/card-837-descoberta-iniciar-varredura/index.html` (URL DEV). Apply não reescreve o HTML; usa-o como spec de layout.
