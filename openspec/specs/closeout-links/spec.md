# closeout-links Specification

## Purpose
TBD - created by archiving change card-872-dsh-closeout-links. Update Purpose after archive.
## Requirements
### Requirement: Regra geral: qualquer ligação local vira clicável

QUALQUER endereço de máquina local que chegue ao chat SHALL ser entregue como endereço clicável equivalente, abrível no dispositivo do Alan; caminho do servidor sozinho SHALL NOT contar como entrega.

#### Scenario: caminho local no chat vira clicável

- **Given** um caminho de máquina local chegaria ao chat,
- **When** a mensagem é entregue,
- **Then** a mensagem contém o endereço clicável equivalente, sem caminho sozinho e sem abertura direta.

#### Scenario: `file://` ou porta do painel vira clicável

- **Given** um endereço `file://` ou de porta do painel chegaria ao chat,
- **When** a mensagem é entregue,
- **Then** a mensagem contém o endereço clicável equivalente, sem endereço local sozinho e sem abertura direta.

### Requirement: Caso primário: links dos documentos do dia

A mensagem de fechamento SHALL conter um endereço clicável para cada um dos dois documentos do dia já publicados: o doc do lote e o diário de melhorias.

#### Scenario: docs publicados, fechamento reportado

- **Given** os dois documentos do dia estão publicados (URL blob em main existente),
- **When** o fechamento do lote é reportado no chat,
- **Then** a mensagem contém o endereço clicável do doc do lote E o endereço clicável do diário de melhorias, cada URL inteira e clicável.

### Requirement: Caso primário: links dos pedidos de integração

A mensagem de fechamento SHALL conter os endereços clicáveis dos pedidos de integração do pacote (código e docs).

#### Scenario: pacote com PRs de código e docs

- **Given** o pacote possui PRs de código e de docs,
- **When** o fechamento é reportado,
- **Then** a mensagem contém o endereço clicável do PR de código E o endereço clicável do PR de docs.

### Requirement: Proibição de abertura direta e de erro visível

A mensagem SHALL NOT conter tentativa de abertura direta (`xdg-open`, `open`, `start`, caminho de navegador, chamada a opener) nem erro visível de abertura; quando abertura direta não existe, o substituto SHALL ser o endereço clicável.

#### Scenario: aceite geral: qualquer ligação local

- **Given** qualquer endereço local chegaria ao chat,
- **When** a mensagem é entregue,
- **Then** a mensagem contém o endereço clicável equivalente, sem tentativa de abertura direta.

#### Scenario: abertura direta indisponível

- **Given** abertura direta indisponível (ex.: Linux headless sem navegador),
- **When** seria hora de abrir,
- **Then** sem erro visível (nenhum exit code, stack, "xdg-open: ...", "no browser" ou equivalente); o substituto é o endereço clicável.

### Requirement: SÓ link, sem caminho de apoio

Caminho do servidor sozinho (ex.: `/srv/...`, `file://...`, caminho de worktree, porta do painel) SHALL NOT contar como entrega; a entrega SHALL trazer SÓ endereços clicáveis, sem caminho de apoio — mesmo quando os links estão presentes, nenhum caminho de servidor SHALL acompanhar a entrega.

#### Scenario: link acompanhado de caminho não satisfaz

- **Given** a mensagem contém os links exigidos,
- **When** a mensagem também contém um caminho de servidor como apoio,
- **Then** a entrega é considerada inválida (viola "SÓ endereço clicável").

### Requirement: Formato clicável

Cada endereço exigido SHALL aparecer como URL nua inteira em linha própria ou como link markdown `[texto](url)` com URL válida `https://...`; URLs quebradas em múltiplas linhas ou truncadas SHALL NOT satisfazer os requisitos 1–3.

#### Scenario: URL quebrada

- **Given** uma URL exigida aparece quebrada/truncada,
- **When** o aceite é verificado,
- **Then** o requisito correspondente é considerado não atendido.

