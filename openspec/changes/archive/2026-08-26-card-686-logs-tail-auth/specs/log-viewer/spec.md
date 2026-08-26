## ADDED Requirements

### Requirement: Tail de logs exige admin autenticado
`GET /api/logs/tail` SHALL exigir `Depends(get_current_admin)`. Pedido sem credencial válida SHALL retornar 401. Pedido autenticado de usuário fora de `ADMIN_EMAILS` SHALL retornar 403. Pedido de admin SHALL retornar 200 com o contrato de cursor já especificado, sem conteúdo extra de filesystem.

#### Scenario: Anônimo
- **WHEN** um cliente chama `/api/logs/tail` sem Bearer válido
- **THEN** a resposta SHALL ser HTTP 401
- **AND** SHALL NOT incluir o conteúdo do arquivo de log

#### Scenario: Autenticado não-admin
- **WHEN** um usuário autenticado que não é admin chama `/api/logs/tail`
- **THEN** a resposta SHALL ser HTTP 403
- **AND** SHALL NOT incluir o conteúdo do arquivo de log

#### Scenario: Admin autenticado
- **WHEN** um admin autenticado chama `/api/logs/tail` com Bearer
- **THEN** a resposta SHALL ser HTTP 200
- **AND** SHALL manter allowlist `full_execution_log` / `backtest_debug` e o cursor incremental

### Requirement: Resposta do tail não expõe path de filesystem
A resposta JSON de `/api/logs/tail` SHALL NOT incluir a chave `path` nem qualquer caminho absoluto de arquivo, inclusive quando o arquivo ainda não existe.

#### Scenario: 200 sem path
- **WHEN** um admin autenticado recebe 200 do tail
- **THEN** o JSON SHALL NOT conter a chave `path`
- **AND** SHALL NOT conter substrings de filesystem absoluto do host (ex. prefixos `/srv/` ou `full_execution_log.txt` como localização)

### Requirement: Viewer envia Bearer e torna 401/403 observáveis
`BackendLogViewer` SHALL enviar `Authorization: Bearer` em cada pedido ao tail (incluindo captura de cursor e polls). Em HTTP 401 o painel SHALL mostrar estado observável de não logado. Em HTTP 403 SHALL mostrar estado observável de não admin. O chrome do modal (título **Logs do Backend**, **Fechar**, área mono, rolagem) SHALL permanecer o existente.

#### Scenario: Poll autenticado
- **WHEN** um admin autenticado abre **Ver logs**
- **THEN** o cliente SHALL incluir header `Authorization: Bearer`
- **AND** a área SHALL iniciar em `Aguardando eventos…` como hoje

#### Scenario: 401 visível
- **WHEN** o tail responde 401
- **THEN** o banner de erro do modal SHALL exibir `HTTP 401` e indicação de que é preciso estar logado
- **AND** o layout do modal SHALL NOT ser redesenhado

#### Scenario: 403 visível
- **WHEN** o tail responde 403
- **THEN** o banner de erro do modal SHALL exibir `HTTP 403` e indicação de que só admin pode ver logs
- **AND** o layout do modal SHALL NOT ser redesenhado

## MODIFIED Requirements

### Requirement: O contrato legado de tail permanece compatível
Chamadas a `GET /api/logs/tail` que omitem `after_offset` SHALL continuar retornando as últimas `lines` linhas com os campos `name`, `lines` e `content` (sem `path`). Os campos de cursor SHALL permanecer aditivos. A chamada SHALL continuar autenticada como admin.

#### Scenario: Consumidor existente solicita últimas linhas
- **WHEN** um admin chama `/api/logs/tail` apenas com `name` e `lines`
- **THEN** a seleção e o conteúdo das últimas linhas SHALL permanecer equivalentes ao comportamento anterior autenticado
- **AND** nenhum parâmetro de cursor novo SHALL ser obrigatório
- **AND** a chave `path` SHALL NOT estar presente
