## 1. Procedimento e evidência segura

- [x] 1.1 Materializar runbook operacional deste Design com etapas DEV e release, responsáveis, autorizações concretas, condições de parada e recuperação sem segredo comprometido.
- [x] 1.2 Implementar coleta local e exportação por allowlist de evidências, fixando versão/configuração do scanner, cobertura de refs e distinção entre achados e falha; bruto somente em diretório restrito fora do Git.
- [x] 1.3 Verificar com fixtures sintéticas a não exposição de segredo em relatório, stdout/stderr, mensagens/caminhos e erros; comprovar que scanner incompleto não produz resultado limpo.

## 2. Inventário autorizado e higiene do tip

- [x] 2.1 Executar inventário autorizado das fontes disponíveis conforme Design; classificar todo alerta ou registrar pendência explícita com responsável, sem presumir comparação DEV/PROD já feita. Registrar eventual acesso negado sem contorno.
- [x] 2.2 Classificar controladamente todas as tabelas/colunas e texto/JSON do backup em cópia read-only restrita; registrar categorias e tratamento/pendências sem dados brutos.
- [x] 2.3 Preservar cópia restrita do backup, remover `.local_backups/` do índice e adicionar ignore, sem refazer #687 nem modificar configuração sensível.
- [x] 2.4 Validar ausência na árvore entregue e testar `git check-ignore` e inclusão habitual de probe inofensivo em checkout descartável.

## 3. Plano operacional pronto para execução

- [x] 3.1 Preparar matriz por segredo/ambiente com prova exigida, responsável e estado explícito de invalidação; executar somente operações efetivamente autorizadas, mantendo as restantes como pendências sem marcar revogação fictícia.
- [x] 3.2 Documentar testes controlados Binance, JWT access/refresh antigo versus novo e PostgreSQL antigo versus novo, consumidores/restart e recuperação; confirmar que nenhum teste exige ordens, saques ou restauração de segredo exposto.
- [x] 3.3 Preparar roteiro verificável de congelamento, refs/SHAs, proteções, backup cifrado do trabalho, clone dedicado, filtros e validação pré-publicação; ensaiar preservação/reescrita/recuperação em repositório sintético sem afetar refs reais.
- [x] 3.4 Preparar roteiro pós-publicação: clone independente, PR refs/caches/suporte, trabalho pendente reaplicado sobre história limpa, proteções restauradas e prova de não recontaminação.

## 4. Validação e handoff DEV

- [x] 4.1 Executar checks proporcionais, validação OpenSpec estrita e verificar que arquivos/artefatos de implementação não contêm material restrito; entregar diff para revisão no fluxo normal.
- [x] 4.2 Validar CI/QA visual padrão e, após integração, restart/smoke DEV com evidência sanitizada de login, banco e serviço necessário. Login QA não executado: dispensado explicitamente por Alan em 2026-10-13 ao responder “ignore isso” à pendência exclusiva desse teste. <!-- covenant-flow:after-qa -->
- [x] 4.3 Registrar handoff Done técnico com resultados DEV e registro operacional completo das pendências abaixo, responsável e condição de fechamento; não declarar incidente contido nem Pronto. <!-- covenant-flow:after-qa -->

Evidência pós-integração: [handoff DEV](handoff.md), 2026-10-12 UTC, revalidada em 2026-10-13 UTC; `develop` em `99a3070cd9d117539fe6de734361f07d5e1c4611`. CI/visual, integração/restart, saúde pública, PostgreSQL e workers principais comprovados. O scanner Telegram recusa intencionalmente o bot PROD em DEV; journal, configuração efetiva e smoke seguro da barreira comprovaram isolamento esperado, sem envio externo e sem defeito atribuído a #1071. O teste de login QA não foi executado por falta de canal protegido de credenciais; Alan dispensou exclusivamente esse teste em 2026-10-13 com “ignore isso”, permitindo o fechamento de 4.2 com essa limitação explícita. A dispensa não alcança invalidação de credenciais, testes de segurança JWT/Binance/banco, continuidade PROD, homologação ou release. Esses resultados não comprovam rotação nem remediação completa do incidente.

## 5. Registro operacional obrigatório da mesma entrega

As caixas acima acompanham a implementação/preparação e o Done DEV; sua conclusão não comprova as operações abaixo. O runbook/handoff manterá estados `pendente`, `bloqueado` ou `comprovado` para cada obrigação. Este registro acompanha #1071 até Pronto, mesmo após archive no fechamento da release. Não criar tarefa de código fictícia para autorizar produção nem esconder pendência ao marcar preparação concluída.

| Obrigação | Responsável | Condição para comprovar |
| --- | --- | --- |
| Contenção de visibilidade | Alan | Visibilidade privada verificada; não equivale a invalidação |
| Invalidação de todos os segredos históricos | Alan/Binance e operador autorizado | Matriz completa, provas autoritativas ou testes conclusivos; configuração DEV/PROD distinta |
| Conteúdo do backup e demais dados sensíveis | Operador | Classificação completa e tratamento registrado; zero alerta indeterminado para fecho |
| Continuidade DEV/PROD | Operador | Login novo, JWT antigo rejeitado, conectividade válida, serviços e URLs do overlay validados |
| Congelamento e preservação | Operador e donos dos worktrees | Mapa de refs/trabalho, cópia cifrada restaurável, janela e autorização concreta |
| Rewrite e publicação global | Operador, autorização de Alan | Homologação + release explícita, invalidação anterior, clone dedicado validado e refs publicadas conforme mapa |
| PR refs/caches/anexos/LFS aplicáveis | Operador/provedor | Resolução demonstrada; recusa ou falta de cobertura continua bloqueio |
| Recuperação e proteções | Operador e donos dos worktrees | Trabalho preservado e saneado, proteções restauradas, ausência de história contaminada |
| Pronto | Pai pelo fluxo existente | PROD validado, obrigações acima comprovadas, guards PASS e T16; limitações externas explícitas |
