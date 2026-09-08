# Tasks — card-852-descoberta-tres-modos

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Shell dos 3 modos em DiscoveryPage

- [ ] 1.1 — Introzuzir estado de modo derivado do sweep (Montar / Acompanhando #X / Decidir); 1 visível por vez; rascunho colapsa ao iniciar; leaderboard trava no sweep em curso. Parciais do Acompanhar: top-5 travadas do sweep em curso, sem paginação nem re-perguntar o rascunho (protótipo: mock estático). Preservar fora do switch de modos (sem regressão): botão Descartar por linha + copy destrutiva, estados dedup (`duplicate`/`already_promoted`), bloco 409, nota de revalidação sob lock, painel 403, bloco stale, sessão expirada.
- [ ] 1.2 — Preservar foco/acessibilidade atuais (heading de progresso, traps de modal, rótulos); sem regressão de teclado/leitor de tela.

## 2. Preflight humano

- [ ] 2.1 — Render 3 linhas (`N combinações · ~T estimado · janela/período`) + lista de impedimentos quando bloqueado; mover fórmula/hash/token/chave para `<details>` expansível. Preset default do seletor = `Todo o histórico` (opções menores continuam); preflight default e CTA refletem o histórico cheio com as datas da janela (ajuste Alan 2026-09-07; sem mudar motor).
- [ ] 2.2 — CTA `Iniciar varredura — N, ~T` estável e dominante; bloqueio nomeando diferença (mesmo escopo vs outro) + link "ver progresso".

## 3. Leaderboard decidível

- [ ] 3.1 — 1 ordenação + 3 colunas de risco por padrão (Calmar, Max DD, Trades/cobertura); resto em expansão por linha; página 10–15 (confirmar performance/custo do 3 atual no apply).
- [ ] 3.2 — Filtros sem re-perguntar rascunho; evidência (janela, candles, fees) e rank global estável preservados.

## 4. Seleção inline + edição avançada

- [ ] 4.1 — Busca + contador + marcar/desmarcar inline para casos comuns; modal vira "edição avançada" com exatamente **2 ações de eixo inteiro** e visíveis: Selecionar todos (marca todos os itens do eixo) e Limpar seleção (desmarca tudo); o escopo filtrado é resolvido inline (sem ação própria na edição avançada); contador do modal ao vivo (`X de N`) + contador inline refletindo após Aplicar (ajuste Alan 2026-09-07).
- [ ] 4.2 — Esconder `short` do caminho feliz (rascunho + filtros) até haver dados; consistência entre os dois.

## 5. Promoção com resumo de risco

- [ ] 5.1 — Modal com retorno, queda máxima, trades, cobertura, janela lado a lado + destino Tier 3 + onde ver depois. Dialog íntegro: header + corpo DENTRO do `role=dialog` (não repetir o typo do protótipo pré-fix: `</div>` no lugar de `</header>` nas linhas ~246/270). Preservar no modal do vivo: Descartar por linha, estados dedup/409, nota de revalidação sob lock — fora do switch de modos.

## 6. Verificação

- [ ] 6.1 — Playwright funcional+visual da rota `/combo/discovery` nos 3 modos (desktop+mobile); `openspec verify`; validação contra o protótipo `frontend/public/prototypes/card-852-descoberta-tres-modos/`.
