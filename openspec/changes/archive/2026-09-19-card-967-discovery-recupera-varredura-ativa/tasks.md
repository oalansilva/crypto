# Tasks — card-967-discovery-recupera-varredura-ativa

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Reconstituição automática do Acompanhar

- [x] 1.1 — Se a verificação do sweep activo falha com a sessão ainda autenticada, repetir sozinha até hidratar o Acompanhar dessa run (número verdadeiro e progresso). Sem clique. Sem logout.
- [x] 1.2 — Payload com sweep não-terminal conhecido abre Acompanhar e mostra os contadores mesmo se `hydrateFromSweep` ainda falhar; não estacionar em Montar vazio + «Acompanhando #—».
- [x] 1.3 — Enquanto a automática corre, não mostrar o banner vermelho de falha; loading «Verificando varredura ativa…» MAY permanecer.

## 2. Residual e bloqueio

- [x] 2.1 — «Tentar novamente» só depois de a reconstituição automática esgotar. Não é o caminho feliz.
- [x] 2.2 — Falha de tela não cancela nem duplica a run no servidor. Iniciar outra continua bloqueado até o operador ver o Acompanhar.
- [x] 2.3 — 401 continua «Sessão expirada» (fora). F5/#664, #954, #952, worker, Combo/Favoritos/Monitor, modos novos: fora.

## 3. Verificação

- [x] 3.1 — Testes: GET activo falha uma vez e o retry automático hidrata Acompanhar sem clique; payload sem axes ainda mostra `sweep_id` + progresso; residual só após teto (banner + retry, start bloqueado).
- [x] 3.2 — Playwright `/combo/discovery` contra o proto `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/` (desktop+mobile): landmarks; Acompanhar com número verdadeiro e progresso; banner vermelho ausente; 0 console/pageerror.
- [x] 3.3 — `openspec verify` desta change.
