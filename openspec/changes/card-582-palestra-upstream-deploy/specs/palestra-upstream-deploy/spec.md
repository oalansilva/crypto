## ADDED Requirements

### Requirement: Deck versionado cobre os sete blocos da palestra

O repositório SHALL versionar um deck Markdown copiável para projetor da palestra **Do upstream ao deploy**, com blocos `--- SLIDE ---` (ou `## SLIDE N`) cobrindo os sete blocos do card #582: enquete, problema downstream, anatomia, skills como runbooks, caso Cripto Farol, falhas reais e modelo + Q&A. O bloco de skills MAY permanecer no arquivo já existente `docs/palestra-upstream-deploy-slide-skills.md`; o deck completo SHALL referenciá-lo sem duplicar o fluxo em vocabulário antigo.

#### Scenario: Deck completo no GitHub
- **WHEN** a change é aplicada
- **THEN** existe um Markdown versionado em `docs/` com slides dos sete blocos
- **AND** o texto distingue Done técnico, Homologado (Alan em develop) e Pronto (PROD + release-guard)
- **AND** o destino da palestra está identificado como Agile Brazil 2026 (Foz do Iguaçu)

### Requirement: Tom de conferência, não pitch de produto

O deck SHALL tratar o Cripto Farol como **caso real** de um relato de experiência para a plateia do Agile Brazil (agilidade, produto, engenharia). SHALL NOT ser copy de landing/comercial do produto. Termos internos (OpenSpec, Pronto para Dev, release-guard) SHALL ser introduzidos na primeira ocorrência.

#### Scenario: Abertura no evento
- **WHEN** o apresentador abre o deck
- **THEN** o primeiro bloco cita Agile Brazil 2026 e o caso Cripto Farol como experiência, não como oferta comercial

#### Scenario: Fidelidade ao fluxo atual
- **WHEN** um revisor lê o deck
- **THEN** as colunas citadas são `Em Refinamento → Todo → Design → Aprovação de Design → Pronto para Dev → Em desenvolvimento → Code Review → QA → Done → Homologado → Pronto`
- **AND** o harness citado é Cursor Agent com subagents `inherit`
- **AND** o path canônico de workflow global é `.cursor/skills/` (não `~/.codex/skills/` como contrato atual)
- **AND** não aparece fluxo genérico `Todo → In Progress` como contrato atual

### Requirement: Quatro gates humanos e mapa de skills no material

O material SHALL nomear os quatro gates que o agente nunca cruza (Em Refinamento→Todo; Aprovação de Design→Pronto para Dev; Done→Homologado; Homologado→Pronto) **e SHALL explicar por que cada um é human-in-the-loop** (decisão de julgamento ou irreversível), não apenas listá-los. SHALL cobrir pelo menos: `alan-workflow`, `alan-workflow-ambientes`, pipeline `/opsx:*` (new/ff/apply/verify/archive), `design-critic`, `impeccable`, `kaizen`, `playwright-cli`. O slide de agentes SHALL listar main, PO, DESIGN, DEV, QA, Kaizen + Alan e SHALL deixar explícito que não são seis modelos.

#### Scenario: Gates e papéis presentes
- **WHEN** o deck e o bloco de skills são lidos
- **THEN** os quatro gates humanos estão nomeados e localizados no diagrama ou slide equivalente
- **AND** os seis papéis + Alan aparecem com a nota `inherit`

#### Scenario: Tese HITL explícita
- **WHEN** o bloco de anatomia (7–11 min) é apresentado
- **THEN** o deck afirma que automação sem gates humanos é autonomia sem accountability
- **AND** cada um dos quatro gates tem o *porquê* (o que o humano decide vs o que o agente não pode cruzar)
- **AND** aparece a distinção: máquina nas transições verificáveis; humano no irreversível

### Requirement: Enquete de abertura e evidência de board/card real

O pacote SHALL incluir enquete de abertura com seis opções (triagem/refinamento, design, dev, code review, QA, homologação ou produção) e SHALL incluir evidência do board Project 1 (mapa das colunas reais com destaque a Em Refinamento) mais um exemplo de card real com Gist OpenSpec e comentário de evidência Done ou Pronto. Screenshot fotográfico do GitHub MAY ser substituído por mapa versionado das colunas reais quando captura autenticada do board não estiver disponível; a substituição SHALL ser explícita.

#### Scenario: Enquete versionada
- **WHEN** o apresentador abre o bloco 0–3 min
- **THEN** as seis opções de travamento estão no Markdown do deck
- **AND** a mecânica de contagem ao vivo (mão no ar ou número no chat) está escrita no mesmo deck

#### Scenario: Card exemplo rastreável
- **WHEN** o walkthrough do caso real é apresentado
- **THEN** o material aponta um issue existente do Project 1 com link de Gist OpenSpec e de comentário de evidência
- **AND** o exemplo não inventa Gist ou SHA

### Requirement: Superfície do produto inalterada

A change SHALL NOT alterar rotas, componentes, APIs, migrations ou tokens visuais do produto Cripto Farol. `UI impact` permanece `none`. Google Slides / Drive NÃO é critério de aceite deste card quando a CLI `gog` estiver sem credenciais; o Markdown no GitHub é a fonte canônica. Ensaio cronometrado permanece fora do Done técnico. Submissão de CFP/Even3 NÃO faz parte desta change (site oficial: encerrada em 26 de julho de 2026).

#### Scenario: Sem delta de produto
- **WHEN** o diff da change é revisado
- **THEN** não há alteração em `frontend/src`, `backend/` ou `DESIGN.md`
- **AND** o ensaio cronometrado não é marcado como entregue pelo agente
