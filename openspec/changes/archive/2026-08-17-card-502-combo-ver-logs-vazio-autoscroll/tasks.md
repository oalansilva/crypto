## 1. Backend — cursor incremental compatível

- [x] 1.1 Estender `GET /api/logs/tail` com `after_offset` opcional, validado como inteiro não negativo, mantendo o caminho sem cursor idêntico ao tail atual
- [x] 1.2 Capturar o EOF em um snapshot consistente e retornar `next_offset`, `file_size`, `file_id` (inode/device) e `cursor_reset` como campos aditivos
- [x] 1.3 Implementar leitura incremental binária em ordem com limite `MAX_INCREMENTAL_BYTES`, avanço de `next_offset` pelos bytes efetivamente entregues e retenção de sufixo UTF-8 incompleto
- [x] 1.4 Tratar truncamento/rotação: reset quando `after_offset > file_size` ou `file_id` divergir do snapshot atual (`cursor_reset: true`)
- [x] 1.5 Cobrir com testes: tail legado, captura de cursor, sem bytes novos, múltiplos incrementos sem duplicação, burst acima do limite, UTF-8 dividido, truncamento e rename com arquivo novo menor/igual/maior

## 2. Frontend — sessão limpa e polling incremental

- [x] 2.1 Ao abrir, limpar conteúdo/erro, ativar aderência ao final e fazer uma requisição-base single-flight cujo conteúdo é descartado e cujo `next_offset`/`file_id` inicia a sessão
- [x] 2.2 Nos polls seguintes de 2 s, enviar `after_offset`/`file_id`, anexar somente incrementos e avançar o cursor sem duplicar ou reordenar linhas; single-flight (poll seguinte só após resposta atual) e descarte de respostas obsoletas de sessões fechadas
- [x] 2.3 Tratar `cursor_reset` reiniciando a sessão no arquivo atual (limpar conteúdo exibido, capturar novo EOF) sem erro permanente
- [x] 2.4 No fechamento/unmount, cancelar requisição em voo, limpar interval e descartar cursor/conteúdo para garantir reabertura limpa
- [x] 2.5 Exibir `Aguardando eventos…` enquanto a sessão não recebeu conteúdo novo e manter erro recuperável sem substituir conteúdo já recebido (status de erro com cor âmbar)

## 3. Frontend — rolagem e acessibilidade

- [x] 3.1 Controlar `isAtBottom` com limiar de 24 px; após append, rolar somente quando a aderência já estava ativa
- [x] 3.2 Exibir estados textuais `Rolagem automática`/`Rolagem pausada` em live region (`role=status`) e ação acessível **Ir para o fim** durante pausa
- [x] 3.3 Preservar fechamento por botão, fundo e Escape; conter foco no modal e devolvê-lo ao acionador
- [x] 3.4 Garantir uso desktop/mobile, área de log rolável por touch, sem overflow horizontal da página e sem corte em viewport baixa/landscape (layout flexível do painel)

## 4. Validação

- [x] 4.1 Testar contrato backend de cursor e compatibilidade dos demais consumidores de `/logs/tail`
- [x] 4.2 Testar frontend com timers/fetch controlados: abertura vazia, ordem, autoscroll, pausa, estabilidade de posição, retomada e reabertura limpa
- [ ] 4.3 Executar Playwright desktop 1280×800+ e mobile 390×844, incluindo botão/fundo/Escape, foco, console/page errors e asserts críticos do card
- [x] 4.4 Executar validação OpenSpec da change e checks proporcionais antes de Code Review
