# Design — card-504-digest-proof (card #504)

## Status e classificação

- **Status observado:** Design.
- **UI impact: none** — a change corrige exclusivamente a canonicalização e a verificação backend da prova OOS e adiciona testes unitários. Não altera componentes, conteúdo, estados ou fluxos visuais.

## Problema

A prova OOS vincula criptograficamente o resultado da otimização ao payload salvo como favorito. Hoje o digest depende não apenas do valor JSON, mas do tipo numérico Python presente em cada ponta. Um preço emitido como `8953.0` é serializado pelo navegador como `8953`; o digest muda e uma prova legítima é rejeitada com 422. Isso bloqueia especificamente o caminho de promoção que deveria permitir a um admin salvar um candidato NO-GO com override explícito.

## Hipótese

Se a entrada do digest representar de forma única todo número finito sem parte fracionária, então payloads semanticamente equivalentes antes e depois do round-trip JSON produzirão o mesmo digest, sem tornar equivalentes conteúdos que diferem em valor, estrutura ou texto.

## Resultado esperado

- A prova emitida com um float integral continua válida quando o navegador devolve o mesmo valor como inteiro.
- O admin consegue promover o NO-GO apenas quando também fornece override explícito e tem permissão.
- NO-GO sem override continua bloqueado pelo motivo do gate; GO continua salvável sem override.
- Assinatura, propósito, expiração e vínculo com todo o restante do payload continuam obrigatórios.

## Decisão de design

### Canonicalização recursiva

Antes de `json.dumps`, `_canonical_digest` deve aplicar uma normalização pura e recursiva aos **valores** do payload:

1. `float` finito com `value.is_integer() == True` → `int(value)`.
2. `dict` → preservar as chaves e normalizar cada valor; `sort_keys=True` continua definindo a ordem final.
3. `list` → preservar ordem e cardinalidade e normalizar cada item.
4. Demais valores → preservar sem alteração.

A serialização continua compacta (`separators=(",", ":")`), com chaves ordenadas e codificação UTF-8, seguida de SHA-256. A mesma `_canonical_digest` permanece sendo chamada tanto por `issue_oos_promotion_proof` quanto por `verify_oos_promotion_proof`; não haverá lógica divergente entre emissão e verificação.

### Semântica por tipo e edge cases

- **Floats não integrais:** permanecem floats; a correção não arredonda, trunca nem aplica tolerância. `1.5` não se torna `1`.
- **Zero negativo:** `-0.0` canonicaliza para `0`, consistente com o round-trip de números JSON pelo browser.
- **`None`, strings e booleans:** permanecem inalterados. A checagem específica de `float` evita tratar `bool` como inteiro por herança de tipo em Python.
- **Dicionários e listas aninhados:** são percorridos em qualquer profundidade necessária ao payload; a ordem das listas é significativa e não muda.
- **Chaves de dicionário:** não são transformadas. O contrato de `promotion_payload` usa chaves string compatíveis com objetos JSON.
- **NaN e ±Infinity:** não são convertidos para inteiro; o guard de finitude evita exceção/conversão indevida. Esses valores não têm representação JSON interoperável e, se sofrerem alteração no transporte, a prova deve falhar fechada. Rejeitá-los globalmente ou mudar a política atual de serialização fica fora desta correção localizada, pois pode alterar resultados legados do otimizador.
- **Objetos não JSON nativos:** o comportamento existente de `default=str` é preservado; ampliar ou restringir essa compatibilidade não faz parte do card.

### Segurança e integridade

A mudança cria equivalência somente entre um float integral finito e o inteiro de mesmo valor. Campos removidos, adicionados ou modificados; floats fracionários diferentes; texto diferente; ordem/cardinalidade de listas diferente; assinatura inválida; propósito incorreto; e expiração continuam invalidando a prova. Não haverá fallback que aceite digest incompatível sem recomputar o payload completo.

### Compatibilidade de provas

- **Novas provas:** emissão e verificação usam a nova canonicalização e permanecem estáveis no round-trip alvo.
- **Provas não expiradas emitidas antes do deploy:** podem deixar de verificar quando contêm floats integrais, porque seu claim guarda o digest legado. O impacto é limitado pelo TTL de seis horas; o caminho de recuperação é repetir a otimização para emitir nova prova.
- **Provas expiradas:** continuam rejeitadas pelo JWT e não serão reabilitadas.
- **Sem fallback legado:** evita complexidade e dupla semântica de digest em uma credencial efêmera. Operacionalmente, o deploy deve aceitar a curta janela de reemissão ou ocorrer após drenar o TTL quando necessário.

## Escopo técnico

| Área | Decisão |
| --- | --- |
| Serviço | Alteração localizada em `backend/app/services/oos_promotion_proof.py`. |
| Emissão | Continua gravando `purpose`, `digest`, `iat` e `exp` no JWT HS256. |
| Verificação | Continua validando assinatura, algoritmo, expiração, propósito e igualdade do digest. |
| Testes | Cobertura unitária da equivalência recursiva e da verificação end-to-end da prova; conteúdo diferente deve falhar. |
| API/UI | Nenhuma alteração de contrato ou superfície. |

## Alternativas consideradas

1. **Normalizar apenas `metrics.trades`: rejeitada.** Resolveria o exemplo, mas deixaria o mesmo defeito em `parameters`, `oos_metrics`, `oos_verdict` ou novos campos aninhados.
2. **Comparar payloads com tolerância numérica: rejeitada.** Introduz ambiguidade no vínculo criptográfico e pode aceitar alteração real de valor.
3. **Remover `metrics.trades` do digest: rejeitada.** Enfraquece a integridade da prova e permite promover conteúdo diferente do otimizado.
4. **Digest legado como fallback: rejeitada.** A prova é efêmera (seis horas); manter duas canonicalizações aumenta complexidade e superfície de erro sem necessidade duradoura.

## Riscos e mitigação

- **Risco — regressão em estruturas aninhadas:** mitigado por testes com dict/list em múltiplos níveis e `None`/bool/string.
- **Risco — normalização excessiva:** mitigado por converter apenas floats finitos com parte fracionária zero, sem arredondamento ou tolerância.
- **Risco — prova pré-deploy invalidada:** aceito e documentado devido ao TTL curto; repetir otimização reemite a prova.
- **Risco — NaN/Infinity no payload:** permanece fail-closed quando o transporte não preserva o valor; política ampla para não finitos fica fora do card.
- **Risco — relaxar indevidamente o gate NO-GO:** mitigado por não alterar `oos_gate_decision`, autorização de admin ou os requisitos de prova.

## Prototype

**N/A.** `UI impact: none`: a correção é backend-only, não cria nem altera superfície visual e, portanto, não requer protótipo.

## Prototype Validation

**N/A.** Não existe protótipo ou interação visual a validar em navegador. A evidência desta change será unitária/API e o QA visual padrão do projeto será tratado no gate de QA, sem atribuir mudança visual ao card.

## Impeccable Brief

**N/A.** O pipeline Impeccable se aplica a superfícies de UI; esta change altera apenas canonicalização criptográfica no backend.

## Impeccable Critique

**N/A.** Não há interface, hierarquia, interação, responsividade ou estado visual a criticar.

## Impeccable Audit

**N/A.** Não há implementação de frontend para auditar em acessibilidade, performance visual, responsividade ou theming.

## Impeccable Trace

**N/A.** Nenhum target visual, protótipo ou execução do pipeline Impeccable foi necessário devido a `UI impact: none`.

## Design Critique

### Achados por severidade

- **P0/P1:** nenhum achado aberto.
- **P2 — compatibilidade de prova pré-deploy:** uma prova ainda dentro do TTL pode ter digest legado e exigir nova otimização. Disposição: risco aceito, limitado a seis horas, sem fallback para não ampliar a superfície de verificação.
- **P2 — não finitos não têm round-trip JSON estável:** NaN/Infinity não são cobertos pela equivalência proposta. Disposição: aceito e fail-closed; mudar sua política pode gerar regressão no otimizador e está fora do defeito reproduzido.
- **P3 — `default=str` mantém canonicalização de tipos não JSON:** não é ideal como contrato criptográfico geral, mas alterar esse legado não é necessário para o card. Disposição: fora de escopo; a entrada esperada de `promotion_payload` é JSON-compatible.

### Avaliação

- **Produto:** a solução remove o falso bloqueio sem alterar a regra de negócio que protege promoções NO-GO.
- **Escopo:** correção mínima no ponto compartilhado por emissão e verificação; nenhuma superfície visual ficou sem classificação.
- **Regressão:** o principal risco é compatibilidade transitória de tokens emitidos antes do deploy, explicitamente limitado pelo TTL.
- **Segurança:** nenhuma permissão é ampliada e nenhuma parte do payload sai do digest; conteúdos não equivalentes continuam rejeitados.
- **Operação:** não requer migração, mudança de configuração ou ação persistente; nova otimização recupera uma prova transitória incompatível.
- **Referências avaliadas:** `proposal.md`, este `design.md`, `backend/app/services/oos_promotion_proof.py`, emissão em `backend/app/routes/combo_routes.py` e verificação em `backend/app/routes/favorites.py`. Prototype: N/A justificado.

## Design Agent verdict

**PASS** — decisão localizada e coerente com a causa raiz, critérios verificáveis definidos, zero P0/P1 aberto, riscos transitórios classificados e nenhuma UI afetada. O card continua sujeito a `Aprovação de Design` humana antes de `Pronto para Dev` e de qualquer implementação.
