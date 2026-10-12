## ADDED Requirements

### Requirement: Inventário cobre conteúdo e fontes controladas sem expor segredos

A remediação SHALL inventariar conteúdo atual, todas as versões históricas disponíveis, branches, tags, refs de PR acessíveis, cópias locais controladas e o backup conhecido. Cada fonte MUST ter cobertura ou limitação explícita; cada alerta MUST receber classificação e resultado justificados. A evidência SHALL conter somente identificação opaca, nome da chave/serviço, presença, ambiente, data e resultado/classificação, sem valor, hash de segredo, fingerprint ou saída bruta. Metadados técnicos sensíveis e material bruto SHALL permanecer restritos fora do Git.

#### Scenario: Scanner encontra possível senha
- **WHEN** o scanner ou a análise controlada identifica possível credencial em uma versão histórica
- **THEN** o inventário registra achado pendente até classificação e comprovação de invalidação ou justificativa de configuração pública/falso positivo
- **AND** ausência de comparação autorizada com DEV/PROD SHALL NOT ser registrada como diferença ou rotação comprovada

#### Scenario: Falha ou cobertura incompleta
- **WHEN** uma ref/fonte não pode ser lida ou o scanner termina com erro operacional
- **THEN** a execução SHALL registrar cobertura incompleta e impedir que zero achados seja usado como prova de inventário concluído

#### Scenario: Evidência sanitizada
- **WHEN** uma fixture sintética inclui valores em match, linha, mensagem, caminho e erro de scanner
- **THEN** o exportador SHALL omitir os valores e campos brutos e emitir apenas campos permitidos

### Requirement: Backup sai do versionamento e recebe análise de conteúdo

O projeto SHALL remover `.local_backups/` do índice, impedir sua inclusão habitual por ignore e analisar controladamente o conteúdo do backup conhecido. Schema isolado SHALL NOT encerrar a classificação. Segredos e dados pessoais/sensíveis encontrados MUST ter responsável, tratamento e resultado ou pendência.

#### Scenario: Inclusão habitual não republica backup
- **WHEN** uma cópia inofensiva é criada em `.local_backups/` após a mudança e ocorre inclusão Git habitual sem força
- **THEN** nenhum arquivo desse diretório SHALL entrar no índice
- **AND** a árvore entregue SHALL estar sem o backup conhecido

#### Scenario: Campos texto ou JSON contêm dado sensível
- **WHEN** a inspeção read-only do backup classifica conteúdo como sensível
- **THEN** a evidência SHALL registrar categoria e tratamento sem linhas/valores
- **AND** o arquivo SHALL ser removido também do histórico controlado na fase autorizada

### Requirement: Segredos históricos deixam de permitir acesso

Cada segredo histórico identificado SHALL ter evidência de revogação, expiração verificável ou outra comprovação de que não permite acesso. DEV/PROD MUST usar configuração válida distinta de todos os valores comprometidos aplicáveis. Credenciais comprovadamente inválidas não exigem rotação redundante. Rewrite MUST aguardar essa comprovação completa.

#### Scenario: Binance exposta
- **WHEN** Alan e o operador concluem a troca e revogação dos pares expostos
- **THEN** o serviço SHALL funcionar com o par válido e a evidência SHALL demonstrar invalidação dos antigos por prova autoritativa ou teste controlado conclusivo
- **AND** falha de rede, restrição de IP ou valor novo diferente isoladamente SHALL NOT comprovar revogação

#### Scenario: JWT histórico ainda utilizável
- **WHEN** o segredo é substituído e todos os validadores são recarregados
- **THEN** tokens access e refresh não expirados de teste controlado assinados com segredo histórico SHALL ser rejeitados
- **AND** login/token novo equivalente SHALL funcionar sem fallback para o segredo comprometido

#### Scenario: Credencial PostgreSQL exposta
- **WHEN** uma credencial histórica ainda permite autenticação
- **THEN** o operador SHALL invalidá-la, atualizar consumidores, tratar sessões antigas e comprovar conexão nova válida e rejeição antiga no endpoint correto sem exibir dados

### Requirement: Reescrita preserva trabalho e valida antes de publicar

A operação SHALL congelar atualizações concorrentes, inventariar refs e trabalhos em curso, manter recuperação restrita testada e executar rewrite em clone completo novo dedicado. MUST remover caminhos, aliases e ocorrências sensíveis, inclusive conteúdo binário e mensagens quando presentes. A publicação SHALL depender de validação local completa, mapa de refs e autorização operacional concreta de Alan para refs/proteções/force-push. Este Design SHALL NOT ser tratado como essa autorização.

#### Scenario: Ref mudou durante a janela
- **WHEN** a ref remota difere do SHA antigo esperado no mapa validado
- **THEN** a publicação SHALL parar sem sobrescrever trabalho concorrente e exigir novo inventário/validação

#### Scenario: Branch de outro card em andamento
- **WHEN** há worktree com commits ou alterações não commitadas
- **THEN** o operador SHALL preservar e testar recuperação do trabalho, mapear sua base limpa e obter conferência do responsável antes da liberação
- **AND** não SHALL apagar a branch por estar fora do pacote de release

#### Scenario: Validação antes do push
- **WHEN** o rewrite local terminou
- **THEN** scanner, busca controlada de valores/blobs conhecidos, cobertura de refs e comparação de árvores SHALL demonstrar ausência do material e preservação das alterações previstas antes de qualquer publicação

### Requirement: História publicada e cópias controladas permanecem limpas

Após a publicação autorizada, o operador SHALL validar a história remota por clone independente, recuperar worktrees sem merges da história contaminada e restaurar proteções. Refs de PR/caches e anexos controláveis SHALL ter resolução comprovada ou pendência impeditiva de Pronto. Clones/forks de terceiros SHALL ser explicitamente excluídos de garantias de eliminação.

#### Scenario: Cache sensível continua acessível
- **WHEN** a história de branches/tags está limpa mas uma ref de PR ou cache mantém conteúdo sensível
- **THEN** a remediação SHALL registrar acompanhamento com o provedor e permanecer incompleta para Pronto enquanto não houver resolução
- **AND** recusa do provedor SHALL ser reportada como bloqueio, não eliminação comprovada

#### Scenario: Recuperação após publicação parcial
- **WHEN** parte das refs foi atualizada e outra parte falhou
- **THEN** o operador SHALL manter congelamento, restaurar proteções e reconciliar a partir do mapa validado sem republicar história contaminada

### Requirement: Entrega respeita ambientes e gates humanos

Done SHALL significar implementação integrada e validada em DEV com pendências operacionais/PROD explícitas, sem alegar contenção completa enquanto houver possível segredo válido. Pronto SHALL exigir homologação humana, release solicitada, invalidação comprovada, limpeza histórica sob controle do projeto e deploy/validação PROD no fluxo vigente. A mudança SHALL NOT refazer #684/#687, tornar o repo público novamente ou criar bypass de gates.

#### Scenario: Done com manutenção global futura
- **WHEN** implementação e QA DEV passaram, mas falta autorização/execução da manutenção global ou operação PROD
- **THEN** o handoff SHALL identificar precisamente o trabalho restante, responsável e condição de fechamento
- **AND** a operação SHALL permanecer neste card e impedir sua declaração como Pronto

#### Scenario: Falha da credencial nova
- **WHEN** o smoke falha após rotação
- **THEN** a recuperação SHALL usar configuração inédita válida ou componente pausado, nunca o segredo comprometido

#### Scenario: Fechamento final
- **WHEN** PROD e a limpeza global autorizada foram validados e todas as pendências impeditivas foram encerradas
- **THEN** o pai SHALL usar os guards e `process_event fechar_release` conforme o fluxo existente
- **AND** merge em main isolado SHALL NOT comprovar Pronto
