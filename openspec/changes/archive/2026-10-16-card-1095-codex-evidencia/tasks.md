## 1. Fonte e contrato de evidência

- [x] 1.1 Confirmar no host alvo a correlação entre spawn nativo, child/parent thread, nascimento, turn_context e terminal/retorno; registrar campos disponíveis e limitações reais sem declarar suporte antecipado.
- [x] 1.2 Implementar envelope versionado e driver de leitura do runtime Codex com requested/observed separados, captura imutável, identidade por turno e proveniência verificável; usar o índice apenas como localizador.
- [x] 1.3 Implementar extração mínima protegida, digest estável, persistência idempotente e validação de integridade sem guardar prompts/transcripts completos nem aceitar metadados manuais como prova.

## 2. Preflight e coleta automática

- [x] 2.1 Implementar preflight da sessão/host/versão/schema/fonte e destino de evidência, com resultado ready/blocked e causas acionáveis; capacidade não comprovada deve ficar unverified.
- [x] 2.2 Integrar preflight à orquestração Codex antes de cada nascimento e às transições dependentes em process_event, preservando Status/artefatos em recusa e sem novas arestas ou mudanças nos demais adapters.
- [x] 2.3 Integrar coleta final ao proxy Codex após retorno nativo, incluindo espera limitada por flush, correspondência terminal/payload e validação de todos os turnos relevantes contra a captura do nascimento.
- [x] 2.4 Implementar recuperação idempotente para fonte temporariamente indisponível e diagnóstico de novo nascimento obrigatório para origem irrecuperável/divergência; preservar artefatos sem promover tentativa recusada a sucesso.

## 3. Gates e ensaios de recusa

- [x] 3.1 Integrar verificação de proveniência nos consumidores Codex, mantendo par capturado, completed/payload, crítica e gates humanos obrigatórios.
- [x] 3.2 Integrar coleta da onda Code Review no pai gravável após ambos os retornos, preservando sessão de spawn e filhos read-only, papéis/filhos distintos, mesmo diff SHA-256 e verify-wave/checklist.
- [x] 3.3 Testar ausência de fonte antes de spawn/transição, host/schema desconhecido, contexto de cliente ambíguo, permissão revogada após preflight, timeout/evento truncado e preservação dos artefatos.
- [x] 3.4 Testar modelo/esforço divergentes ou ausentes, identidade/nascimento/turno errados, captura alterada, seleção local posterior, continuação divergente e último turno válido após divergência anterior.
- [x] 3.5 Testar terminal sem payload, fonte conflitante, digest adulterado, tentativa de usar flags observadas manuais, recoleta duplicada e regressões de sandbox/diff/onda e dos demais adapters.

## 4. Prova real e documentação

- [x] 4.1 Executar ensaio explícito de qualificação com filho nativo no host alvo: captura, nascimento, retorno completed com conteúdo, coleta automática e gate consumidor aprovados sem preencher observação manualmente; registrar fonte e versão reais e resumo sanitizado reproduzível.
- [x] 4.2 Demonstrar recusas no caminho real do coletor/gate e separar essas evidências das fixtures; exigir a prova real positiva antes de declarar qualquer host/versão suportado.
- [x] 4.3 Atualizar runbook canônico e documentação Codex/model-selection com comandos finais, matriz por host/versão, limites de hooks/cooperatividade, recuperação e distinção entre exploração, simulação e suporte comprovado.
- [x] 4.4 Validar OpenSpec e executar a suíte pertinente de harness/proxies/process_event/review; vincular resultados e provas aos requisitos sem implementar ou alterar o escopo do #1086.

## 5. Follow-up operacional: inspeção read-only (2026-10-13)

- [x] 5.1 Corrigir a recusa real `destination_unwritable` do preflight de review: inspecionar o destino privado preparado sem exigir `W_OK` na sessão read-only; validar escrita efetiva no `prepare` do pai gravável, preservando receipts e gates de runtime/sandbox/diff.
- [x] 5.2 Ensaiar a regressão com `W_OK` negado e nenhuma escrita durante inspeção; manter recusa para destino ausente, não-diretório, inseguro ou ilegível, e para escrita revogada no pai antes do receipt.
- [x] 5.3 Revalidar a suíte pertinente/OpenSpec, registrar a descoberta e os limites em `evidence.md`/runbook e republicar as tasks no Gist existente sem reescrever o Design aprovado.

O ensaio real de uma nova onda read-only cabe ao pai após este Apply; está pendente e não é declarado aprovado por estes testes de contrato. A sessão/receipts da descoberta permanecem preservados como diagnóstico; não servem como prova de execução dos reviewers. Detalhes em `evidence.md`.

## 6. Correção dos achados mecânicos da primeira onda real w3 (2026-10-13)

- [x] 6.1 Persistir continuações válidas em snapshots imutáveis da mesma tentativa/captura, revalidando todos os turnos e snapshots anteriores; manter um único proxy sem aceitar adulteração ou divergência anterior.
- [x] 6.2 Recusar envelopes de qualificação no gate de Code Review e substituir o ensaio que os aceitava por casos de review normal qualificado e rejeição explícita de qualificação.
- [x] 6.3 Executar regressões e suíte pertinente/OpenSpec, fazer uma verificação de conteúdo da correção e registrar comandos/resultados/limites, preservando o Design aprovado; entregar os paths ao pai para republicação no Gist existente.
