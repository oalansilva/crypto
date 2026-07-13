## Context

O Project 1 e a skill global hoje tratam `Code Review` como último gate antes do `Done` técnico. A CI já executa lint, build, testes Python com PostgreSQL e Playwright, mas Playwright depende de `RUN_E2E_PLAYWRIGHT` e de mudança em `frontend/**`; cobertura diferencial também só alerta. O resultado não fornece uma evidência visual automática e uniforme para cada card.

Esta mudança atravessa processo, GitHub Project, CI, frontend e runtime. O backend interno já possui uma etapa QA própria; a alteração alinha a entrega GitHub/Codex a essa intenção sem substituir a homologação humana.

## Goals / Non-Goals

**Goals:**

- Inserir `QA` entre `Code Review` e `Done` no fluxo oficial e no Project 1.
- Tornar o `qa-gate` uma síntese verificável dos checks de PR antes da integração em `develop`.
- Executar Playwright visual por padrão em qualquer card e preservar artefatos úteis em falhas.
- Permitir bypass visual somente quando o card tiver comentário explícito do dono do repositório e a label `qa-visual-skip`.
- Exigir evidência de CI, integração, restart e runtime antes do `Done` técnico.

**Non-Goals:**

- Automatizar a aprovação humana `Homologado` ou publicação em `main`.
- Fazer chamadas reais de trading, Binance ou usar segredos de produção nos testes.
- Alterar o fluxo interno de Kanban do produto além da documentação/alinhamento necessário.
- Aceitar regressão visual atualizando snapshots fora de Code Review.

## Decisions

### 1. QA é um Status explícito, não apenas um substatus

O campo `Status` ganha `QA` entre `Code Review` e `Done`; `Fluxo` recebe a mesma opção como espelho legado e mantém `Validate` somente para cards históricos.

**Rationale:** o Status é a fonte visual principal. Um substatus sozinho permitiria que cards fossem relatados como tecnicamente prontos sem o gate automático.

**Alternatives considered:** usar somente `Fluxo=Validate` foi rejeitado porque diverge do contrato atual de que Status prevalece.

### 2. O QA pré-integração ocorre em pull request para develop

Após review do diff e commit da branch, o card entra em QA e a PR para `develop` executa o `qa-gate`. A integração é permitida somente depois do gate verde. O push em `develop` mantém build/testes e o smoke/deploy existente; o agente ainda valida `./restart` e a URL antes de Done.

**Rationale:** checks obrigatórios do GitHub protegem merge por PR, não um merge local isolado. Separar QA pré-integração de smoke pós-integração mantém um SHA revisável e não confunde QA com homologação.

**Alternatives considered:** executar somente em push da branch foi rejeitado porque não garante bloqueio de integração; exigir staging para todo PR foi rejeitado porque staging é opcional no ambiente atual.

### 3. O job Playwright sempre termina verde ou vermelho, nunca é pulado implicitamente

O job `e2e-playwright` sempre é criado. Ele executa a suíte visual por padrão. Quando o opt-out é autorizado, o próprio job registra a dispensa e termina com sucesso; se label e comentário não coincidirem, falha.

**Rationale:** `skipped` não é uma evidência aceitável para um gate agregado e caminhos de arquivo não representam todos os impactos visuais de uma entrega.

**Alternatives considered:** condicionar o job a `frontend/**` ou a uma variável de repositório foi rejeitado por contrariar a validação visual em todos os cards.

### 4. Opt-out é rastreável e restrito ao Alan

O workflow consulta a issue vinculada à PR. A dispensa exige simultaneamente a label `qa-visual-skip` e comentário cujo texto comece com `QA visual dispensado por Alan.` publicado pelo dono do repositório. Sem PR/issue vinculada, a execução visual continua obrigatória.

**Rationale:** a label é legível pela automação e o comentário registra motivo/autor para auditoria. Exigir ambos impede bypass silencioso.

**Alternatives considered:** variável no workflow, label isolada ou comentário livre foram rejeitados por não preservar autorização auditável.

### 5. QA visual separa estabilidade visual de integração funcional

O Playwright visual usa viewport desktop/mobile e dados previsíveis/máscaras para conteúdo volátil. Testes backend e integração mantêm PostgreSQL e mocks apenas na borda de provedores externos; checks de runtime após `develop` validam a aplicação servida.

**Rationale:** snapshots instáveis reduzem confiança; mockar internamente reduz cobertura real. A separação mantém diffs visuais determinísticos sem perder testes de integração.

## Risks / Trade-offs

- [Suíte visual aumenta tempo de PR] → manter um conjunto crítico estável em cada card e executar regressão completa no fechamento/release.
- [Dados dinâmicos causam flake] → mascarar timestamps/preços e usar fixtures no teste visual, mantendo smoke separado para runtime.
- [PR sem issue vinculada não consegue dispensa] → este é comportamento intencional; padrão segue sendo executar QA visual.
- [Branch protection pode bloquear fluxos locais antigos] → habilitar o required check somente após o job e o nome estável `qa-gate` existirem e forem validados na branch.
- [Status Project e Fluxo legado divergem] → Status é autoritativo; sincronizar `Fluxo=QA` quando aplicável e preservar `Validate` para histórico.

## Migration Plan

1. Criar opção `QA` no Project 1 e atualizar seu README antes de usar o novo fluxo.
2. Atualizar skill global e regras locais com a mesma transição e critérios.
3. Adicionar label de dispensa, scripts frontend, specs visuais e jobs CI.
4. Executar testes locais/CI da própria branch e corrigir flakes.
5. Publicar PR para `develop`, exigir `qa-gate`, integrar após sucesso e validar runtime.
6. Rollback: remover `qa-gate` dos checks obrigatórios, restaurar o job anterior de E2E e manter cards em In Progress até nova decisão; não avançar cards por bypass.

## Open Questions

- A proteção obrigatória de `develop` será aplicada somente se a configuração atual do repositório permitir atualizar checks sem remover regras existentes.
