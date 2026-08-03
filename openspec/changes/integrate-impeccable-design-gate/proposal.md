## Why

A etapa de Design já exige protótipo fiel, crítica, navegador real e aprovação humana, mas ainda não possui um brief estruturado nem uma camada determinística para detectar problemas recorrentes de UX, acessibilidade, responsividade e acabamento visual. A integração do Impeccable torna essa evidência reproduzível no Codex sem substituir o `design-critic` nem a aprovação de Alan.

## What Changes

- Instalar e versionar o Impeccable localmente para o Codex, incluindo seu hook de detecção visual; registrar o CLI npm `3.5.0`, o payload da skill `4.0.4` e o commit npm resolvido.
- Criar contexto de produto para o Impeccable sem sobrescrever o `DESIGN.md` canônico do Cripto Farol.
- Tornar `shape`, crítica independente com dois subagents do mesmo LLM da sessão principal, `audit` e `polish` parte obrigatória do Design para cards com `UI impact: affected`.
- Registrar brief, críticas, auditoria, metadados de modelo, digest e validação de navegador no OpenSpec.
- Atualizar as regras do Codex e o contrato canônico `design-critic`; cards `UI impact: none` continuam com entrega enxuta e Impeccable N/A.
- Manter Cursor e os cards cancelados 362/369 fora do escopo desta integração.

## Capabilities

### New Capabilities

- `impeccable-design-gate`: define a execução reproduzível do Impeccable, a crítica dual-agent com herança do LLM principal, os artefatos obrigatórios e os critérios de PASS/BLOCKED no estágio de Design do Codex.

### Modified Capabilities

- None.

## Impact

- Afeta `.agents/skills/design-critic/`, regras de processo, configuração OpenSpec, arquivos de contexto do produto e hooks/skills locais do Codex.
- Adiciona dependência operacional do Impeccable versão fixada e de navegador real para validar protótipos.
- Não altera APIs, banco, runtime de produção ou superfícies de produto.
