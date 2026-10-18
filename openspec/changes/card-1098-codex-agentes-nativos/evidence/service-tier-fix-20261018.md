# Continuação Apply — metadado service tier, 18/10/2026

Mesmo Apply da entrada via T10, ainda Em desenvolvimento; captura/birth `3e3a9801-4160-4f84-90e1-b143c08fc8a9` preservados, sem retuning. Não houve novo T8, agente, reviewer ou coordenador aberto por este filho. O pai informou integração/revisão do pacote anterior, adapter `29d99b9ee34933575d0c982a653b9db2154849fc0167c40d3b4441f89ada48b5`; isso é procedência informada, não nova gravação de trust neste turno.

## Tentativa recusada

Novo bootstrap: `dedicated-bootstrap-c56805fcd88f042319b6d2a5.package.json`, coordenador `01a14c8d-0db5-7b60-8f6d-c3ae88480673`; recusa de rota negativa esperada confirmada pelo pai. A continuação `dedicated-context-47ab121e95e28e3857fd1e80.package.json` terminou exit0 no launcher, mas seu preflight nativo terminou exit1 / `review_coordinator_settings_changed`. O qualify do plano `abfd554d-0ee9-46dc-948c-68f65ff53b19.birth.context-plan.json` recusou configurações diferentes da original. Nenhum filho nativo foi observado nessa continuação; nenhum parecer produto foi aceito.

Fonte: `/home/ubuntu/.codex/sessions/2026/10/18/rollout-2026-10-18T01-07-54-01a14c8d-0db5-7b60-8f6d-c3ae88480673.jsonl`. Inspeção limitada a metadata/identidade/hashes/resultados de comandos: settings 8 têm tier `default`; 26/27 têm `priority`; **única chave diferente = service_tier**. Não foram lidos ou emitidos prompts/marcadores S/C nem conteúdo do plano ou dos payloads. O histórico original continua recusado e não foi alterado para fazê-lo passar.

## Contrato e candidato

A [referência oficial OpenAI](https://learn.chatgpt.com/docs/config-file/config-reference) descreve service tier como preferência de processamento para turnos novos, independente de modelo/esforço. A política local de seleção autoriza explicitamente `model`/`reasoning_effort`; o Design mantém verificação de contexto, identidade, binding e read-only. Classificar somente essa chave como metadado não autorizador é a interpretação de implementação desses contratos, sem inferir billing ou tier aplicado pelo servidor.

Pacote **inativo** `.cursor/tmp/card-1098-service-tier-fix/`: coletor, suíte e procedimento; snapshots before, patch/hashes/verificador e integração única pelo gerador preservado do consumidor. O schema completo é validado antes de comparar a projeção dos campos autorizadores. Apenas `service_tier` fica fora dessa comparação; permanece string obrigatória não vazia. Settings completos continuam diferentes, com valores/rows/raw hashes reais preservados por turno. Modelo, esforço, provider, permissões, cwd/raízes, aprovações, colaboração e plugins permanecem estritos; campos desconhecidos não são ignorados.

As fronteiras anteriores continuam: início antes de ferramentas ou intervalo terminal → próximo turno. Mudança após trabalho, ausência/divergência de turno/terminal, ampliação ou alteração até transitória de autorização continuam negadas, mesmo se acompanhadas por tier diferente. Não foi pinado tier ou alterada seleção/configuração da conta.

## Verificação e próximos passos

Projeção sanitizada real PASS: valores observados `default/priority/priority`; refs 7/8 pertencem ao bootstrap, 26/27/29 à retomada. Configurações completas diferentes, campos autorizadores iguais e hashes originais distintos foram verificados sem reescrever fonte. Essa prova é restrita à configuração/ordem/permissões projetadas; contexto C/S e binding completo permanecem `not_evaluated` nela.

A suíte exercita mudança em ambos os sentidos, validade do schema, hashes/turnos, todos os campos autorizadores e o preflight CLI de contexto com tier diferente, que só pode liberar `diagnostic_only`. Inclui ciclo contexto/probes/rota de contrato e o preflight produto auditado contra escrita/cache/rede. Não houve outro erro real exercitado após a recusa nessa fonte; a ausência de spawn impede alegar sucesso ou diagnosticar fases não executadas.

Regressão combinada: **336 passed**, quatro avisos de opções pytest preexistentes no ambiente. OpenSpec strict, manifesto ativo e comparação dos três arquivos ativos aos snapshots before PASS. Logs/comando/projeção e receita de integração estão no pacote inativo.

Pacote final verificado: `integrated=false`, `trust=not_changed`, `git apply --check` PASS. Manifesto SHA-256 `ac36c77ba846b643cce95c2a206f6bf4258e3b25cf3ed6d6043b456a0df4a96a`; patch SHA-256 `d749ee24ae1bfc6e2f3e7eaf06b9619ef48ba764d4c6840d698adf23cd252e68`. Três candidatos, pin-base v1.1.22; integração pelo gerador do consumidor sem cópia de manifesto do nucleus.

Adapter/manifesto ativos, trust, conta, permissões, FSM, Design/digest aprovado e traces preservados. Depois de coletar este mesmo Apply, o pai verifica/integra o pacote, faz revisão pertinente e prepara novos bootstrap/pacotes com os hashes novos. Não reutilizar alterando os pacotes históricos. A qualificação viva do código novo continua pendente; progresso **23/35** e impedimento de distribuição `target_outside_binding` preservados. `internal_context_attestation=unavailable`.

Proxies: design 4067 palavras; HTML gerado/copiado N/A; spawns deste filho 0. Proxy modelo: apply-coluna → GPT-6.1 Sol (`gpt-6.1-sol`), esforço solicitado high; observação runtime/continuação deve ser coletada pelo pai contra a captura original.
