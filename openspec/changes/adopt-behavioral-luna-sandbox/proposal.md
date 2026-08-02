## Why

O Codex reaplica o sandbox da sessão principal às lanes Luna, fazendo o pedido `workspace-write` ou `read-only` chegar como `danger-full-access`; neste servidor, a tentativa de restaurar isolamento técnico com bubblewrap falhou por uma proteção do host que não deve ser desativada. Precisamos tornar explícita e auditável a opção 2: aceitar o acesso ampliado, limitar a lane por contrato e comprovar antes/depois que ela respeitou o escopo.

## What Changes

- **BREAKING**: deixar de bloquear uma lane Luna somente porque o sandbox efetivo foi ampliado para `danger-full-access`, desde que a ampliação seja observável e a contenção comportamental obrigatória seja aplicada.
- Manter fail-closed para agent type, modelo, effort, `fork_turns="none"`, permission profile observável e proibição de fallback.
- Exigir pacote autocontido com propriedade explícita de arquivos, ações proibidas e limites externos para cada lane Luna.
- Exigir inventário e digest do estado relevante antes/depois, auditoria do diff e interrupção imediata diante de mutação fora do escopo.
- Tratar Code Review como read-only comportamental quando o host ampliar o sandbox solicitado, sempre em thread nova e com prova de ausência de mutação.
- Registrar em todo handoff o sandbox ampliado e o risco residual de não haver barreira do sistema operacional.
- Atualizar regras, skill de roteamento, perfis e testes de contrato do projeto; alinhar também o processo global `alan-workflow` para que futuras instruções não reintroduzam o bloqueio antigo.
- Preservar as proteções do servidor; nenhuma alteração em AppArmor, sysctl, user namespaces ou launcher de sandbox faz parte desta mudança.

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova. -->

### Modified Capabilities

- `stage-model-routing`: substituir a exigência de sandbox estrito nas lanes Luna por contenção comportamental verificável quando o runtime ampliar o sandbox solicitado.

## Impact

- Regras e operação: `AGENTS.md`, `rules.md`, descrição do GitHub Project e documentação operacional aplicável.
- Roteamento: `.codex/skills/stage-model-routing/`, perfis Luna em `.codex/agents/` e seus testes de contrato.
- Processo global: skill `alan-workflow`, em repositório próprio, mantendo o mesmo contrato da opção 2.
- Segurança: não reduz as proteções do host, mas aceita risco residual maior dentro do processo do agente; qualquer mutação fora do escopo continua bloqueante.
- Produto e APIs: nenhuma tela, endpoint, banco ou comportamento funcional do Cripto Farol muda.
