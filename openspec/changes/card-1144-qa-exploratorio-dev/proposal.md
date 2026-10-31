## Why

Hoje ninguém usa o card no DEV como um usuário usaria antes do Done: o `qa-gate` testa o frontend com API simulada, e quem acha o que quebrou é o Alan, na homologação. Este card põe um agente para testar cada card no DEV, logado e olhando a tela, e segura o card fora do Done quando um critério falha.

Briefing copiado do issue #1144 (REST, 2026-10-30). As quatro seções abaixo são cópia literal do body.

## Problema

O QA de hoje testa só o frontend. O job `e2e-playwright` do `qa-gate` sobe o Vite com `VITE_E2E_AUTH_BYPASS=1` (sem login de verdade) e os specs interceptam a API com `page.route('**/api/**')`. Backend, banco, workers, provedores de mercado e login reais não entram no teste. Depois do merge, o passo "executar `./restart` e validar a URL" confere que o DEV está no ar, mas ninguém usa o card no DEV como um usuário usaria antes do Done. Quem descobre o que quebrou é o Alan, na homologação.

## História

Como Alan, quero que um agente teste cada card no DEV como uma pessoa de QA faria, logado e usando o produto de verdade, para chegar na homologação com o card já exercitado no ambiente real e com evidência do que passou e do que falhou.

## Entra

- [ ] Um agente de QA exploratório abre `https://dev.criptofarol.com.br` num navegador headless que roda no servidor (nada na tela do Alan) e dirige o navegador passo a passo, olhando a tela a cada passo, como uma pessoa. Não é um roteiro fixo.
- [ ] O agente entra com o usuário do Alan no DEV (decisão do Alan em 28/10/2026: é ambiente de DEV, não precisa de conta QA separada). A senha vem do cofre de segredos (bws) e nunca aparece no chat, no issue, no log nem no relatório. Hoje o cofre ainda não tem esse segredo (ver Evidência): o Alan cadastra a senha atual do DEV direto no cofre, uma vez (decisão do Alan em 28/10/2026). Isso é pré-requisito do piloto.
- [ ] O roteiro sai do card: os critérios de "Entra" do issue e o protótipo aprovado no Design. Para cada critério, o agente testa o caminho feliz e tenta quebrar: campo vazio ou inválido, duplo clique, voltar, recarregar no meio do fluxo, tela de celular, esperar o backtest ou o worker terminar de verdade.
- [ ] O agente olha também o que uma pessoa de QA olharia por baixo: erros no console e respostas 4xx/5xx da API.
- [ ] Dados da conta do Alan no DEV: o agente testa à vontade (decisão do Alan em 28/10/2026: "no ambiente de dev ele pode testar a vontade"). Pode criar, alterar e apagar favoritos, estratégias, alertas e configurações, inclusive os que já existiam, sem obrigação de devolver ao estado anterior. Vale só no DEV; nunca em PROD.
- [ ] Relatório por critério com PASS, FAIL ou NÃO TESTADO (com o motivo), print de cada achado e o vídeo da sessão. Bugs achados fora dos critérios entram numa seção separada. O relatório vira comentário no issue do card.
- [ ] O agente não muda o Status do card e não homologa. Homologar e não homologar continuam do Alan (T15/T18).
- [ ] O teste é etapa obrigatória de todo card: roda sempre que o card entra no DEV, antes do Done (decisão do Alan em 28/10/2026). Um FAIL num critério deixa o card fora do Done até a correção entrar no DEV e o critério passar de novo.
- [ ] Card que não muda nada visível no produto (backend, worker, processo): o agente testa pelas telas que dependem dele. Se nada muda no produto, o relatório diz "nada para testar no DEV" e o card não fica preso (decisão do Alan em 28/10/2026).
- [ ] Se cada teste também dá uma volta rápida pelas telas principais (regressão) fica para o Design decidir (Alan sem preferência em 28/10/2026). Achados de passagem, fora dos critérios do card, vão sempre numa seção à parte do relatório.
- [ ] Verificação: com a senha do DEV já no cofre, um piloto num card que já está em Done, com o relatório por critério (PASS, FAIL ou NÃO TESTADO, prints e vídeo) postado no issue desse card e a senha ausente do chat, do issue, do log e do relatório.

## Não entra

- Substituir o `qa-gate` ou os specs com mock. Eles continuam como estão; este teste é uma camada a mais.
- Testar em PROD.
- Criar conta QA separada no DEV (o Alan escolheu usar o próprio usuário).
- Conferir a chegada de alerta no Telegram: exige ligar um chat de teste e fica para outro card se for preciso.
- Teste 100% determinístico com stack própria (compose + provedores simulados): outro assunto, outro card se for preciso.

## What Changes

- Novo papel `qa-dev`: agente que testa no DEV, por blocos de critérios, com navegador headless no servidor, e devolve resultado por critério.
- A T14 passa a ter duas fases na mesma aresta `QA → Done`: a primeira integra e reinicia o DEV com o card ainda em `QA`; a segunda só move para `Done` depois do relatório do teste. Sem coluna nova e sem evento novo. Com `qa_dev` desligado no overlay, a T14 segue igual à de hoje.
- **BREAKING (processo):** com `qa_dev` ligado, `integrar_develop` deixa de terminar em `Done` na primeira chamada. Um FAIL para o card em `QA` à espera do Alan e, se o defeito for confirmado, devolve o card por T13 com o código já em `develop`. Card sem nenhum critério aprovado, ou com o DEV ou serviço parado, fica em `QA` até o Alan decidir.
- A sessão de login nasce fora do agente: um helper lê a senha do cofre, faz o login e entrega ao navegador uma sessão pronta. A senha não passa pelo modelo.
- Relatório por critério como comentário no issue, com veredito calculado por script e marcador lido pela T14. Prints e vídeo ficam na pasta do projeto no Drive.
- Trava no navegador do teste contra envio de ordem real na Binance.
- O motor (T14, papel, skill, relatório) nasce no `covenant-flow` e chega ao crypto pelo pin novo. O que é do crypto (login, Drive, registro do navegador, nomes) fica no consumidor.

## Capabilities

### New Capabilities

- `qa-dev-exploratorio`: o teste de QA no DEV: quando roda, sessão sem senha no modelo, blocos, relatório, evidência, regressão, casos de nada para testar e de espera, e piloto.

### Modified Capabilities

- `process-fsm-event`: T14 em duas fases com `qa_dev` ligado.
- `process-fsm`: a página Moore de QA nomeia as duas fases.
- `delivery-qa-stage`: Done técnico exige o relatório do teste no DEV quando `qa_dev` está ligado.
- `covenant-flow`: o runbook de fechamento de QA descreve o teste no DEV.

## Impact

- **`covenant-flow` (produto, worktree a partir da tag `v1.1.26`):** `.cursor/process-fsm.yaml`, `scripts/process-fsm/t14.py`, `process_event.py`, `fsm.py`, novo `qa_dev.py`, `.cursor/model-policy.yaml`, skill nova `qa-dev` e pontes, `covenant-flow/SKILL.md`, testes.
- **`crypto` (consumidor):** pin novo em `.covenant-flow/overlay.yaml` e chave `qa_dev`; `scripts/qa/`; passo no `qa-gate` (`.github/workflows/ci.yml`); `docs/crypto-overlay.md`; correção de `.agents/skills/playwright-cli/SKILL.md`; OpenSpec.
- **Servidor:** registro do Playwright MCP 0.0.83 na conta do Claude Code; pasta de estado em `~/.local/state/covenant-flow/qa-dev/`.
- **Alan:** faz a revisão de confiança do pin novo, roda `setup-dev.sh` no terminal, cadastra dois segredos no cofre (senha do DEV e conta Google para a evidência), roda `dev_session.py --check` e abre a evidência do piloto.
- **Não muda:** `qa-gate`, specs com mock, telas do produto, repositório do executor (`crypto-portao`) e o `PIN` dele.
