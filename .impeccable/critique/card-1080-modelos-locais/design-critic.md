# Crítica independente de Design — #1080

Data: 2026-10-08. Rodada sem-tela: 1 autor + 1 crítico; nenhum rework de conteúdo necessário.
Worktree: /srv/apps/dev/criptofarol/crypto-worktrees/card-1080-modelos-locais
Branch: card-1080-modelos-locais. Status Design conforme handoff do pai; nenhuma transição efetuada.

## Resultado

- P0–P2: nenhum achado de produto, escopo ou contrato observável que exija rework.
- P3: confirmar schemas, versões e ligação nativa de seleção OpenCode/dsh e capacidade de esforço Grok no Apply. Disposition: aceito como detalhe de Apply, já descrito em Design e tasks. Recusa significa cobertura pendente, nunca sucesso.
- Verdict de conteúdo: PASS; não exige rework.
- Gate global de atestação: PASS; trace autoritativo confirma autor e crítico em gpt-6-astra / medium, conforme mapa vigente. O BLOCKED inicial por unavailable foi superado pela evidência abaixo; isso não executa transição nem substitui aprovação humana.

## Fontes e limites

Lidas skills canônicas design-critic e covenant-flow, issue oalansilva/crypto#1080 via REST, proposal/design/tasks e nove delta specs, mapa vigente na raiz source. Nenhum transcript do pai, alteração OpenSpec/produto, teste de código, process_event, commit, push ou publicação.
OpenSpec strict PASS foi informado pelo pai; não foi repetido nem tratado como prova de integração. O inventário técnico do autor foi avaliado como proposta de contrato, sem alegar capacidade demonstrada de runtime.

## Análise do contrato

A história copiada conserva Problema, História, Entra e Não entra. Abrange Cursor, Codex, Grok, OpenCode e dsh; não reduz cobertura a Codex. O arquivo escolhido é externo ao Git na conta operacional do host executor, independente de repo/worktree; explicita a fronteira entre contas e não cria perfil por projeto. Futuros ajustes nos consumidores migrados dispensam novo card/commit/release; implantação inicial continua sujeita ao processo.

Preserva regras, papéis/faixas, modelos proibidos e gates versionados. Configuração ausente/inválida/incompatível causa erro visível sem herdar picker/mapa antigo/outro cliente. Esforço ou variant só existe onde suportado; schema/catalogue ou contrato ensaiado por versão valida capacidades. Não cria allowlist operacional fixa que inviabilize modelos já aceitos pelo host.

Migração preserva Cursor/Grok e distingue os pares Codex pedidos. Mapa vigente source confirma juizo.codex gpt-6-astra/medium e execucao.codex gpt-6.1-sol/high; mapa commitado antigo não revoga a escolha. Rotas OpenCode/dsh vêm da configuração efetiva não secreta; ausência deixa migração incompleta. Arquivo existente não é sobrescrito e pin não altera seleções.

Releitura ocorre a cada nascimento com captura imutável; proxies e auditoria comparam captura histórica. Editar configuração durante agente vivo não o retuna nem reprova retrospectivamente sua escolha. Edição entre reviewers/A-B da mesma faixa recusa tentativa parcial com selection_changed e exige nova onda explícita; outras faixas/clientes não invalidam a onda. Autor/crítico subsequentes podem seguir escolhas atualizadas preservando isolamento/faixa. Resume conserva captura; substituição exige novo nascimento. Isso concilia leitura atual no novo spawn com preservação dos agentes em andamento.

OpenCode propõe caminho nativo preservando restrições e retorno do task, sem presumir disponibilidade. dsh preserva guards por contexto, isolamento, grill deny e sessões anteriores. Pendências de schema/ligação são detalhes de Apply sob contrato definido: falhar antes de criar filho incorreto e manter cobertura pendente. Tasks 1.1, 2.1–2.4 e 4.4 não permitem tratar mock ou recusa como integração completa.

Solicitado/observado separados; not_applicable difere de unavailable. Falta de trace continua falhando gates. Nenhuma promessa de corrigir instrumentação ou provar modelo pelo arquivo local. Release apenas consome captura; não há autorização de release nem mudança T16.

## Rubrica sem-tela

UI impact: none
live_route: N/A
surface: none

Tokens presentes em linhas próprias no design.md. Justificativa coerente: configuração/adapters sem rota, interface ou copy do produto. Protótipo N/A adequado. Aprovação humana e crítica continuam exigidas.

## Metadados

Papel: design-critic. Cliente: Codex. Faixa: juizo.
Par exigido pelo mapa vigente e informado no handoff: gpt-6-astra / medium.
Par observado no runtime/trace: gpt-6-astra / medium.
Versão real do host: Codex CLI 0.162.0.
Sandbox observado: danger-full-access (Design; não se trata de onda Code Review).

Correção de evidência em 2026-10-08, sem nova rodada de crítica ou rework: inicialmente o retorno não expunha metadata e este snapshot registrou unavailable/BLOCKED. O pai localizou os traces autoritativos; foram consultados apenas registros session_meta e turn_context, sem ler conteúdo de transcript. A identidade do filho e os pares foram verificados diretamente, não inferidos do pedido.

Crítico: `/home/ubuntu/.codex/sessions/2026/10/08/rollout-2026-10-08T20-47-20-01a11d45-43a0-7510-a46c-12d287adae61.jsonl`; session_meta id `01a11d45-43a0-7510-a46c-12d287adae61`, agent_path `/root/design_critic_1080`, parent_thread_id `01a11d30-021c-7b21-ab05-28808c264476`, cli_version `0.162.0`; turn_context original `01a11d45-43c5-7563-9bdc-dedd8456ab42`, model `gpt-6-astra`, effort `medium`, sandbox_policy.type `danger-full-access`. O turno desta correção `01a11d4b-5953-72a3-bcd5-8b3ba0ca90bd` confirma o mesmo par/sandbox.

Autor: `/home/ubuntu/.codex/sessions/2026/10/08/rollout-2026-10-08T20-36-41-01a11d3b-8062-7170-a146-b945074ac62c.jsonl`; session_meta id `01a11d3b-8062-7170-a146-b945074ac62c`, agent_path `/root/design_autor_1080`, mesmo parent_thread_id, cli_version `0.162.0`; turn_context `01a11d3b-808c-7b43-8f12-cf493bc9f48c`, model `gpt-6-astra`, effort `medium`, sandbox_policy.type `danger-full-access`.

Mapa `/srv/apps/dev/criptofarol/source/.cursor/model-map.yaml` relido nesta correção: juizo.codex continua gpt-6-astra / medium. Único bloqueio de atestação deste snapshot resolvido. A análise, o verdict de conteúdo e os hashes originais abaixo permanecem preservados.
Não inferir observado do mapa, handoff, conteúdo ou identidade textual. Pai registra status final/payload pelo retorno real.

## Identidade dos artefatos examinados

- `openspec/changes/card-1080-modelos-locais/design.md`: SHA-256 `6683f33a2d659b3e98c1cab19446bdb2f0da7181d753e2d0cf2c2abdd70c2f9f`
- `openspec/changes/card-1080-modelos-locais/proposal.md`: SHA-256 `60af375a6351560c6af81c35a67131fed67de2f9e86124fddc8f679aaba142da`
- `openspec/changes/card-1080-modelos-locais/specs/covenant-flow/spec.md`: SHA-256 `f648b561c8f9193eb40cd111a5cd2d0ef90b2e9b7db9f74a902fb20f1b884415`
- `openspec/changes/card-1080-modelos-locais/specs/cursor-code-review/spec.md`: SHA-256 `570b017bf96269cd479b704a518350ae4a9b062e22ecd05fa41170b9c633f2e3`
- `openspec/changes/card-1080-modelos-locais/specs/cursor-harness/spec.md`: SHA-256 `2d533b4f4c82141de3292589ed3cf7c69ca56ae74673e68b54c5722a882c1ced`
- `openspec/changes/card-1080-modelos-locais/specs/developer-tooling/spec.md`: SHA-256 `b8afb1414e7d2da8ab7fa6bbc708f66581c47e4f342821ab0b9c488eca2efde1`
- `openspec/changes/card-1080-modelos-locais/specs/impeccable-design-gate/spec.md`: SHA-256 `3798bc55e515a2e3ebd3f7df60bf8574522192304ea5bd1cbe0aeb1da0c46a30`
- `openspec/changes/card-1080-modelos-locais/specs/kaizen-continuous-improvement/spec.md`: SHA-256 `d4bb30becda28a48718b7b3b758e2f04b939b2004114efc94d42e885b386b085`
- `openspec/changes/card-1080-modelos-locais/specs/llm-flow-emission/spec.md`: SHA-256 `8255269b57b9037afe4b10aab5615667e8f9061f80d4a24f536d5d40a47d52ae`
- `openspec/changes/card-1080-modelos-locais/specs/machine-model-selection/spec.md`: SHA-256 `9c6c6e604e41afa0e67e457904e2fe99647b11be82ffc0787dc889d57ae884d9`
- `openspec/changes/card-1080-modelos-locais/specs/process-harness/spec.md`: SHA-256 `774b75e7f8b55e5f87f019fcf13aee26968b2806e83b0e8a6ad1487354aa4f67`
- `openspec/changes/card-1080-modelos-locais/tasks.md`: SHA-256 `c86e5626f91b452fe2a757dd96776d9880cce11c54c0f20b8cdae8984f10f517`
