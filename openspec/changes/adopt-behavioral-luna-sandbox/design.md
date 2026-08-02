## Context

Os perfis Luna pedem sandboxes diferentes por função, mas o Codex atual reaplica o sandbox da sessão principal depois de carregar o perfil. Na sessão usada pelo card 366, implementer e reviewer chegaram como `danger-full-access`/`disabled`. A opção 1 tentou recuperar uma barreira técnica com o bubblewrap oficial, porém a política AppArmor do servidor impediu a inicialização; desativar essa proteção está fora de escopo.

Esta mudança formaliza a opção 2 para todas as lanes Luna: o acesso efetivo pode ser amplo, enquanto a autorização real continua limitada pelo pacote da tarefa e é conferida pelo orquestrador antes/depois. Alan continua dono das aprovações humanas; Sol continua dono da orquestração e QA.

**UI impact: none.** A mudança afeta somente processo, configuração, skills e testes; nenhuma superfície do produto muda.

## Goals / Non-Goals

**Goals:**

- Fazer a opção 2 ser o contrato padrão de implementer, reviewer e release manager.
- Eliminar o bloqueio causado apenas por `danger-full-access` efetivo.
- Preservar os pinos exatos de agente/modelo/effort, threads novas e ausência de fallback.
- Detectar e bloquear alterações fora do escopo por meio de evidência antes/depois.
- Alinhar regras locais, skill de roteamento, perfis/testes e `alan-workflow`.

**Non-Goals:**

- Desativar ou modificar AppArmor, sysctl, user namespaces ou outras proteções do servidor.
- Alegar que conferência de arquivos equivale a isolamento do sistema operacional.
- Permitir que reviewer escreva, implementer alcance escopo não atribuído ou release comece sem autorização.
- Alterar o fluxo Kanban, a autoridade de Alan ou qualquer comportamento do produto.

## Decisions

### 1. Contenção comportamental será obrigatória em toda lane Luna

Cada pacote declarará worktree, base/head, arquivos ou módulos pertencentes à lane, comandos permitidos, ações externas permitidas e proibições. `fork_turns="none"` continuará obrigatório. A lane só recebe o contexto necessário e deve parar quando o trabalho exigir ampliar o escopo.

Antes do spawn, Sol registra o estado relevante. Depois do retorno, Sol confere o estado real e trata o relatório da Luna apenas como uma alegação. Implementação pode mudar somente os caminhos atribuídos; reviewer não pode produzir nenhuma mutação; release pode executar apenas as ações externas que Alan autorizou no pacote.

Alternativa descartada: confiar apenas no texto do prompt, sem conferência. Isso tornaria uma violação invisível.

### 2. Sandbox deixa de ser gate de igualdade e vira evidência de risco

Agent type, `gpt-5.6-luna`, effort `max` e `fork_turns="none"` continuam exatos e fail-closed. Sandbox e permission profile continuam obrigatoriamente observáveis e registrados, mas um sandbox efetivo ampliado não bloqueia sozinho a lane. Os perfis Luna passam a declarar a opção 2 de forma coerente; se o host entregar proteção mais estreita, ela é aceita como defesa adicional, sem remover as conferências comportamentais.

Alternativa descartada: exigir `workspace-write`/`read-only`. O runtime atual sobrescreve esses pedidos e a tentativa de bubblewrap não inicia sob a política de segurança preservada do host.

### 3. O reviewer será read-only por comportamento e prova

O reviewer continua em thread nova, recebe diff exato e instrução explícita de não escrever. Sol captura antes/depois o HEAD, `git status`, diff rastreado, arquivos não rastreados relevantes e digests. Qualquer mudança invalida o review, mantém Code Review bloqueado e exige classificação/restauração segura pelo orquestrador; o reviewer nunca corrige seus próprios achados.

Alternativa descartada: reutilizar a implementer. Independência de contexto e separação de responsabilidade continuam necessárias mesmo sem barreira de escrita do sistema operacional.

### 4. A auditoria será proporcional à função

- **Implementer:** compara base/head, lista de arquivos alterados e diff; somente caminhos atribuídos podem mudar. Serviço, board, commit, push e PR ficam proibidos salvo autorização explícita do pacote.
- **Reviewer:** exige estado idêntico antes/depois nos repositórios e worktrees em escopo; qualquer mutação bloqueia.
- **Release manager:** inventaria pacote, repositórios, worktrees, stashes e ações externas autorizadas; alterações fora do pacote ou código de produto bloqueiam a release.

As evidências públicas permanecem limitadas: agente, modelo, effort, sandbox, permission profile, digests/arquivos pertinentes e resultado. Segredos, caminhos de rollout, prompts integrais e valores de ambiente não são publicados.

### 5. A mudança será sincronizada em duas camadas

O repositório Cripto Farol recebe o contrato específico em `AGENTS.md`, `rules.md`, skill, perfis, testes, spec e descrição do Project. O processo geral recebe a mesma regra na skill global `alan-workflow`, em seu próprio repositório e fluxo de versionamento. Nenhuma camada poderá reintroduzir a opção 1 como requisito automático.

## Risks / Trade-offs

- **A lane consegue tecnicamente alcançar mais arquivos e comandos do que deveria** → pacote mínimo, proibições explícitas, conferência independente e bloqueio por qualquer desvio.
- **A comparação do Git não detecta toda leitura, rede ou mutação externa** → declarar esse risco residual em cada handoff e proibir ações externas não autorizadas; a opção 2 não será descrita como isolamento forte.
- **Arquivos ignorados ou outro repositório podem escapar de uma conferência estreita** → inventariar worktrees/repositórios em escopo e incluir arquivos não rastreados relevantes, além do diff comum.
- **Regras local e global podem divergir** → testes de contrato procuram linguagem antiga e exigem alinhamento das duas camadas antes do fechamento.
- **Um runtime futuro volta a respeitar sandbox estreito** → aceitar a proteção adicional, mantendo o mesmo contrato comportamental e sem depender dela para concluir a lane.

## Migration Plan

1. Versionar artifacts e obter aprovação humana deste design.
2. Atualizar regras, perfis, skill e testes do Cripto Farol em branch própria.
3. Atualizar `alan-workflow` em branch própria e registrar os dois SHAs/diffs no card.
4. Validar TOML, testes de contrato, OpenSpec e buscas por requisitos contraditórios.
5. Usar a nova regra somente em uma lane natural posterior ao carregamento da configuração e registrar antes/depois.
6. Se a auditoria comportamental falhar, reverter as mudanças de processo e manter a etapa bloqueada; não alterar a segurança do host.

## Open Questions

Nenhuma questão bloqueante. A aprovação deste design significa aceitar conscientemente que a opção 2 reduz a garantia técnica de isolamento e a substitui por disciplina e auditoria verificável.

## Prototype

N/A — mudança exclusivamente operacional, sem tela, interação ou componente visual.

## Design Critique

- **Escopo:** a primeira versão poderia apenas remover o check de sandbox; isso seria inseguro. O design foi corrigido para tornar pacote mínimo e auditoria antes/depois requisitos normativos.
- **Regressão de produto:** nenhuma UI/API muda. O risco está no processo de desenvolvimento, explicitamente separado do produto.
- **Risco operacional:** Git sozinho não prova ausência de leitura, rede ou mutação externa. O limite foi registrado como risco residual, com ações externas proibidas salvo autorização expressa.
- **Coerência:** modelo, effort, agente, thread nova, gates humanos e proibição de fallback continuam fail-closed; apenas a igualdade rígida do sandbox deixa de bloquear.
- **Sincronização:** incluir a skill global evita que uma instrução geral antiga volte a exigir a opção 1 depois da mudança local.
- **Referências avaliadas:** `proposal.md`; spec delta `stage-model-routing`; `Prototype: N/A` justificado.

**Design Agent verdict: PASS**
