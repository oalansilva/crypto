# #1098 — continuação do mesmo Apply, correção de settings iniciais

Captura/birth originais mantidos: tentativa `7139a39e-952e-4f36-9d67-3d2414742c6b`, requested `gpt-6.1-sol/high`; observado permanece sujeito à coleta autoritativa do pai. Nenhum filho/agente/sessão externa novo foi aberto; sem process_event, commit/push, troca de modelo ou alteração de trust.

O pai informou integração do pacote anterior e trust humano do adapter `94069eb1ec311989fa0415d06c8029fe9eab21571288a362669ccafe3e2c04e3`. O bootstrap real saiu exit0, mas binding/refusal foram recusados por `review_coordinator_settings_changed`, porque o coletor rejeitava qualquer evento `thread_settings_applied`.

## Fonte real limitada a permissões

Coordenador `01a14c37-8033-7cd0-9f7b-643a0bd34ba4`, codex_exec/0.163.0. Fonte: `/home/ubuntu/.codex/sessions/2026/10/17/rollout-2026-10-17T23-34-28-01a14c37-8033-7cd0-9f7b-643a0bd34ba4.jsonl`. Inspeção restrita aos metadados session_meta ordinal0, turn_context ordinal7 e thread_settings_applied ordinal8; tipos/ordinais necessários confirmaram settings anteriores à primeira ferramenta. Nenhum conteúdo de prompt/marcador/sentinela foi mostrado ao agente, persistido na projeção ou alterado na origem.

O turno observado tem sandbox_policy read-only e perfil managed com filesystem restricted, uma entrada especial root/read, network restricted. Settings repetem modelo gpt-6.1-sol, effort high, cwd e raiz do card; approval_policy never e colaboração coerente com o turno. Os hashes das três linhas e a projeção sem task text ficam em `.cursor/tmp/card-1098-coordinator-settings-fix/native-settings-projection.json`.

`check_native_projection.py` retornou `permission_metadata_projection_validated`, explicitamente com binding/contexto/route_qualification `not_evaluated`. Trata-se de validação da forma nativa efetivamente observada, não de execução/retorno/qualificação de uma nova sessão ou de onda de Review.

## Delta candidato

Pacote `.cursor/tmp/card-1098-coordinator-settings-fix/`: três arquivos em `files/`, snapshots before, `coordinator-settings.patch`, manifesto, verificador/integrador, testes e README. O adapter ativo e seu manifesto não foram modificados por este filho; Design SHA-256 preservado `685305bec5e7664246b6304cfb9b24ee0f930ab53db45a7c171fc4124677d9b3`.

O coletor valida schema fechado, identidade do evento, turno ativo, par pedido/observado, cwd/raízes, perfil efetivo conhecido e sandbox. Settings iniciais só são aceitos antes de ferramentas/terminal; retomadas podem reaplicar a configuração completa idêntica antes do trabalho. Desconhecido/ausente/writable, ampliação de permissões/raízes, mudança de modelo/esforço/cwd/colaboração/aprovação, configuração divergente em resume ou evento tardio recusam. Repetição de turn_context não reinicia a fronteira.

Digests de settings/turn_context são conservados nas fontes do bootstrap e da continuação correspondente. Novos turnos válidos não mudam os refs de tentativas anteriores; alteração de fonte aceita permanece detectável. Testes usam fixtures controladas, sem substituir prova viva. Aprovação humana, contexto opção2, internal_context_attestation unavailable, leitura/deny/readback, dois reviewers e todos os gates existentes permanecem.

## Validação e próximo passo

Os 33 testes novos passaram, incluindo o ciclo contexto/probes/rota em fixtures com settings iniciais e reaplicações idênticas. Regressão combinada: **268 passed**, sem falhas/skips, quatro avisos de opções pytest já não reconhecidas pelo ambiente. Saída em `test-results.txt`, comando exato em `test-command.txt`. Verificação do pacote, git apply --check e manifesto ativo: PASS. A validação OpenSpec strict foi repetida após o registro desta evidência.

O pai coleta este retorno com o adapter ainda confiado e depois pode integrar usando `python3 .cursor/tmp/card-1098-coordinator-settings-fix/verify_package.py --integrate`, que aplica somente o delta e regenera/confere o manifesto pelo gerador preservado do consumidor. Sem cópia de adapters.json do nucleus ou trust automático.

Após integração/revisão pertinente, preparar **novo bootstrap**: os hashes de helper fixados no pacote antigo mudam, e não se editam pacote, digests ou trace para forçar reuso. Retomadas reais, C/S da própria sessão, perfis/probes e rota dedicada continuam pendentes de ensaio do pai. A correção não anuncia qualificação viva ou substituição integral. Nenhuma task de aceite foi promovida por prova ausente.
