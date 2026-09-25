## Context

Card [#1042](https://github.com/oalansilva/crypto/issues/1042), `Status=Design` na consulta ao Project 1. O problema é a divergência de fluxo, proteção de escrita e modelos quando Alan alterna entre Cursor e Codex CLI/IDE local. O issue é a autoridade de produto; `proposal.md` conserva literalmente Problema, História, Entra e Não entra.

O checkout contém `.cursor/process-fsm.yaml`, `scripts/process-fsm/{guard,paging,process_event}.py`, skills canônicas em `.cursor/skills/`, quatro adapters, `.cursor/model-map.yaml` com `juizo` e `execucao` Cursor (`label`/`slug`) e `forbid`. Não há `.codex/` versionado neste checkout. `.agents/skills/` já contém Impeccable e outras skills: a descoberta Codex deve criar pontes sem sobrescrever o fornecedor Impeccable. O mapa deste worktree pode divergir do `source` destino, inclusive por edição local não commitada; o pin deve inspecionar o destino vigente.

UI impact: none
live_route: N/A
surface: none

Justificativa: configuração de agentes, ferramentas e fluxo; nenhuma tela, rota, componente ou texto visível do produto é criado ou alterado.

## Goals / Non-Goals

**Goals:** Um quinto adapter local Codex, usado tanto no CLI quanto na IDE local, que lê a mesma lei e o mesmo mapa versionado, nega as escritas cobertas fora do gate, mantém filhos isolados, passa pelo card piloto e pode ser reproduzido pelo pin.

**Non-Goals:** Codex Cloud; modo Auto; alteração de T0–T18, gates humanos ou release; segunda FSM ou segundo mapa; código de `backend/` e `frontend/src/`; mudança de UI.

## Decisions

1. **Pele Codex, núcleo único.** A configuração de projeto sob `.codex/` será apenas adapter: hooks locais e eventual configuração de agentes, sem tabela de estados, eventos ou globs copiados. `SessionStart` chama o `paging.page()` existente para orientar pelo `Status`; `PreToolUse` normaliza `Bash` e `apply_patch` para `guard.decide()` antes da operação; `PostToolUse` e `Stop` encaminham eventos ao `hook.mjs` existente. O adapter usa `cwd`/raiz git reais, preserva hooks alheios e produz erro visível se o Guard não puder avaliar uma escrita de produto. O instalador copiará essa pele junto com o núcleo e quatro peles atuais. A decisão evita uma lei paralela e deixa `process_event` como única via de Status do agente.

2. **Skills canônicas por pontes.** Codex descobre skills em `.agents/skills/`; gerar stubs curtos para nomes canônicos de `.cursor/skills/`, cada um mandando ler o arquivo canônico, com checagem de cobertura e drift. Tratar conflitos de nome explicitamente: preservar `.agents/skills/impeccable/` (fornecedor) e reconciliar `design-critic` com o canônico `.cursor/skills/design-critic/`, sem duas versões normativas. Operações OpenSpec usam CLI e `openspec instructions`, não cópias de comandos Cursor. Sessão nova em cada superfície deve mostrar as skills e a página do `Status` correto.

3. **Mapa compartilhado aditivo.** Manter `.cursor/model-map.yaml` como arquivo único versionado. No momento da instalação, ler do **destino vigente** `juizo.label/slug`, `execucao.label/slug` e `forbid` e preservá-los integralmente; não usar os valores do worktree de Design ou do produto como substitutos. Adicionar somente o subbloco `codex` em cada faixa:

   ```yaml
   juizo:
     codex: {label: GPT-6 Sol, slug: gpt-6-sol, effort: high}
   execucao:
     codex: {label: GPT-6 Luna, slug: gpt-6-luna, effort: max}
   ```

   O trecho mostra apenas as **adições**, não um arquivo completo para copiar. Se o instalador encontrar alteração local ou conflito entre pin e mapa destino, deve recusar visivelmente ou exigir merge explícito com comparação do antes/depois; nunca sobrescrever silenciosamente `label`, `slug` ou qualquer entrada de `forbid`. O resolver lê o arquivo antes de **cada** spawn, valida faixa, modelo e esforço e passa ambos explicitamente. Arquivo/chave/valor ausente, incompatível ou modelo recusado pelo host: erro visível e nenhum filho; sem fallback para picker, `inherit`, outro modelo ou esforço padrão. Filhos já iniciados não mudam quando o mapa muda. Configuração estática de agente Codex não pode sobrescrever os valores dinâmicos do mapa; verificar a precedência efetiva no ensaio.

4. **Filhos e evidência.** Reusar os grupos de papéis do runbook: juízo para Design-autor/crítico e Assessments; execução para Apply, QA e reviewers. O pai monta prompt autocontido sem transcript; os dois reviewers recebem o mesmo diff exato materializado pelo pai, somente leitura, e retornam pareceres separados. O pai registra proxy de modelo e esforço observados, host `completed` e payload. Status só por `process_event`; T7 e demais gates humanos permanecem humanos. O piloto atravessa Design, aprovação humana, Apply, onda de dois reviews, QA e Done técnico. Se a prova de isolamento, modelo ou esforço falhar, a etapa não conta como sucesso.

5. **Proteção medida, sem promessa absoluta.** [Hooks oficiais](https://learn.chatgpt.com/docs/hooks) documentam `PreToolUse` para `Bash`/`exec_command` e `apply_patch`, hooks de projeto em `.codex/hooks.json`, revisão de confiança, e exclusões (ferramentas hosted e algumas rotas especializadas). Por isso, a propriedade verificável é negação real nas rotas do ensaio CLI e IDE: `develop` e `Todo`, por comando e edição; permissão de artefato em Design; produto só no worktree vinculado após T8. O ensaio usa arquivos descartáveis/fixtures, confirma que o byte não foi escrito após deny e registra versão do host, hook carregado, evento, decisão e resultado. Rotas sem hook, hook não confiado/desabilitado ou falha de avaliação ficam documentadas como limite cooperativo; não reivindicar modo Auto.

6. **Impeccable e pin.** O adapter encaminha o mesmo `PostToolUse` com caminho normalizado e `Stop` ao `hook.mjs`; testes com a mesma entrada UI comparam a condição de disparo e a saída nos cinco clientes, sem transformar o detector em bloqueio. Primeiro atualizar o produto `oalansilva/covenant-flow`, seus testes e instalador; depois aplicar o pin no Cripto. O pin faz leitura e comparação do mapa **no destino** antes de mesclar os subblocos Codex, preserva os campos Cursor e `forbid`, e registra diff para revisão. A descrição do board deixa de dizer “Codex inativo” somente depois do ensaio documentado; isso não autoriza “Auto”.

## Fontes e limites de verificação

- **Documentado:** [skills locais](https://learn.chatgpt.com/docs/build-skills) são descobertas em `.agents/skills/` do repo no CLI e IDE; [hooks](https://learn.chatgpt.com/docs/hooks) têm fontes de projeto, confiança e cobertura local parcial; [subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents) aceitam modelo/esforço explícitos, mas configuração customizada pode ter precedência; [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol) aceita `high` e [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) aceita `max` como `reasoning.effort` na API.
- **Ainda a provar no Apply:** disponibilidade desses slugs na conta/host Codex, aplicação efetiva do esforço em cada spawn, formato exato dos eventos no CLI e IDE locais, carregamento/confiança do hook, cobertura de comandos/edições e equivalência do detector nas superfícies reais. O suporte de `reasoning.effort` na API não prova acesso nem seleção no host Codex.

## Risks / Trade-offs

- [Hook não carregado, não confiado ou rota sem `PreToolUse`] → ensaio real por superfície; falha visível e classificação cooperativa, sem alegação de proteção universal.
- [Mapa aditivo quebra parser Cursor ou agente TOML sobrepõe spawn] → testes dos quatro clientes e prova de modelo/esforço efetivos por filho antes do pin.
- [Mapa do produto/worktree de Design substitui edição local do destino] → ler o destino no ato do pin, preservar top-level Cursor e todas as entradas de `forbid`; recusar conflito ou fazer merge explícito inspecionado.
- [Consulta de Status indisponível] → página `unread` e deny de produto; não inferir `Design` ou `Pronto para Dev` do texto do chat.
- [Conflito das skills em `.agents/skills/`] → inventário de nomes e teste de descoberta; preservar o fornecedor Impeccable e apontar ao canônico único.
- [Pin parcial ou divergência produto/consumidor] → instalador atômico/checagem de diff e rerun dos goldens; rollback pelo pin anterior e reversão dos arquivos versionados, sem mexer em produto de app.

## Migration Plan

Após T7, implementar e testar no produto Covenant Flow; inspecionar o mapa vigente no destino e instalar o pin versionado no Cripto preservando seus campos Cursor/`forbid`; executar goldens dos cinco adapters, ensaios CLI/IDE e piloto; registrar evidência e só então corrigir a descrição do board. Rollback: reverter somente os subblocos Codex e o adapter desta mudança, sem restaurar um mapa Cursor antigo sobre o destino; não há migração de dados nem deploy de UI.

## Open Questions

Nenhuma decisão de produto pendente. A disponibilidade dos modelos e a cobertura dos hooks são hipóteses técnicas com critérios de aprovação no Apply e no piloto.

## Prototype

N/A — nenhuma superfície visual do produto muda; não há protótipo HTML, rota viva ou digest visual.

## Impeccable

N/A — não há Design visual a avaliar. O adapter deve preservar o disparo Impeccable para cards futuros com UI afetada; `DESIGN.md` e Playwright de protótipo são N/A neste Design sem tela. Os gates Design e aprovação humana permanecem.

## Apply contract

- Somente após `Status=Pronto para Dev`/T8: quinto adapter, pontes de skills, mapa compartilhado, instalador, specs e testes; sem código de app nem UI.
- Preservar top-level Cursor e `forbid` lidos do destino vigente, mais a FSM; Codex juízo = `gpt-6-sol/high`, execução = `gpt-6-luna/max`; conflito = recusa visível ou merge explícito, nunca overwrite silencioso.
- Provar denies reais e modelo/esforço no CLI e IDE; concluir piloto e quatro regressões antes de atualizar descrição do board. Limites dos hooks ficam explícitos.

## Design Critique

- P1 fechado — o exemplo inicial podia sugerir restaurar modelos Cursor antigos ao instalar o pin. Disposition: um rework retirou esses valores do exemplo; `design.md`, `tasks.md` e specs agora exigem ler e preservar `label`/`slug` Cursor e todo `forbid` do destino vigente, com recusa visível ou merge explícito diante de conflito. O crítico isolado apontou o achado; o orquestrador verificou a correção e a validação estrita do OpenSpec. A aprovação humana do Design ainda cabe a Alan.
- P3 aceito, detalhe de Apply — disponibilidade de `gpt-6-sol/high` e `gpt-6-luna/max` e esforço efetivo no host Codex exigem ensaio real no CLI e IDE; a documentação de API não prova acesso local. Disposition: validar e recusar visivelmente se indisponíveis.
- P3 aceito — cobertura dos hooks é cooperativa, não universal. Disposition: testar deny real nas rotas cobertas, registrar exceções e não alegar modo Auto.
- Prototype: N/A — nenhuma superfície visual nova ou alterada; Impeccable, snapshot e validação de navegador de protótipo: N/A pelo mesmo motivo.
- Evidência: crítica independente isolada, rework único do autor e `openspec validate card-1042-codex-adapter --strict` válido; zero P0/P1 aberto.

Design Agent verdict: PASS
