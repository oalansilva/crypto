# visual-analysis-routing Specification

## Purpose
TBD - created by syncing change card-399-vision-router. Update Purpose after archive.
## Requirements
### Requirement: Roteamento automático de análise de imagem
O opencode SHALL rotear automaticamente tarefas que envolvem imagens para o agente `vision` com modelo `opencode-go/qwen3.7-plus`, sem intervenção manual do usuário.

#### Scenario: Imagem anexada na conversa
- **WHEN** o usuário anexa uma imagem a uma mensagem e o modelo da sessão não suporta visão
- **THEN** o plugin vision-router salva o anexo, substitui a image part por placeholder com o caminho do arquivo e instrui a delegação da análise ao agente vision (qwen3.7-plus)

#### Scenario: Screenshot gerado por tool em tarefa visual
- **WHEN** um tool (Playwright, browser-debugger) gera screenshot/PNG em tarefa de análise visual
- **THEN** a análise do screenshot é delegada ao agente vision (qwen3.7-plus)

#### Scenario: Imagem anexada em card/issue do GitHub
- **WHEN** a tarefa exige analisar uma imagem anexada a um card/issue do GitHub
- **THEN** o agente baixa o anexo e delega a análise ao agente vision (qwen3.7-plus), registrando o roteamento

#### Scenario: Julgamento visual do QA (diff/baseline/artifact)
- **WHEN** a tarefa exige julgamento visual de `diff.png`/`actual.png` de falha do Playwright, revisão de baselines atualizados, artifacts de falha do CI, screenshots de `qa_artifacts/` ou gráficos/sinais exportados (`artifacts-signals-*.png`, `output/`)
- **THEN** a análise visual é delegada ao agente vision (qwen3.7-plus) e o roteamento é registrado

#### Scenario: Comparação antes/depois
- **WHEN** a tarefa compara duas ou mais imagens (fidelidade de protótipo, mudança de UI, revisão visual)
- **THEN** a comparação é feita pelo agente vision (qwen3.7-plus) via `/vision` multi-imagem

### Requirement: Agente vision com modelo fixo
O repositório SHALL definir um subagent `vision` com `model: opencode-go/qwen3.7-plus` e prompt especializado em análise visual rigorosa.

#### Scenario: Subagent vision disponível
- **WHEN** uma tarefa de análise visual delega ao subagent `vision`
- **THEN** o request roda com o modelo `opencode-go/qwen3.7-plus` (attachment: true)

### Requirement: Evidência de roteamento
O plugin SHALL registrar cada roteamento (sessão, origem, destino, arquivo) em `.impeccable/vision-router.jsonl` para auditoria.

#### Scenario: Log de roteamento
- **WHEN** o plugin roteia uma imagem ao agente vision
- **THEN** um registro é anexado a `.impeccable/vision-router.jsonl` com sessão, modelo origem, modelo destino e caminho do arquivo
