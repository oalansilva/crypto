# Design — card-504-digest-proof (card #504)

## Status e classificação

- **Status observado:** Design.
- **UI impact: none** — a change corrige exclusivamente a canonicalização e a verificação backend da prova OOS e adiciona testes unitários. Não altera componentes, conteúdo, estados ou fluxos visuais.

## Problema

A prova OOS vincula criptograficamente o resultado da otimização ao payload salvo como favorito. O caso pequeno `8953.0` → `8953` mostrou que o digest não pode depender apenas do tipo numérico Python. Porém, a correção original — converter todo float integral para `int` — introduziu outra divergência no payload homologado: `calmar_ratio=3.290195462758171e16` excede `Number.MAX_SAFE_INTEGER`; `int(float)` em Python produz `32901954627581712`, enquanto `JSON.stringify` envia `32901954627581710`. A evidência observada foi digest da issue `2301a454...`, digest do save `703a6548...`, `match=False`. A prova legítima permanece rejeitada com 422.

## Hipótese

Se a entrada do digest canonicalizar números conforme a precisão observável no transporte JSON/JavaScript — preservando inteiros seguros e representando valores fora desse intervalo pelo mesmo double IEEE-754 — então emissão e save produzirão o mesmo digest sem arredondar floats fracionários nem alterar conteúdo ainda distinguível pelo browser.

## Resultado esperado

- A prova emitida com um float integral continua válida quando o navegador devolve o mesmo valor como inteiro.
- O `calmar_ratio` real acima do intervalo seguro continua vinculado à mesma representação double quando o browser o devolve como inteiro decimal.
- O admin consegue promover o NO-GO apenas quando também fornece override explícito e tem permissão.
- NO-GO sem override continua bloqueado pelo motivo do gate; GO continua salvável sem override.
- Assinatura, propósito, expiração e vínculo com todo o restante do payload continuam obrigatórios.

## Decisão de design

### Canonicalização recursiva orientada ao transporte

Antes de `json.dumps`, `_canonical_digest` deve aplicar uma normalização pura e recursiva aos **valores** do payload. O limite inclusivo de inteiro seguro é `MAX_SAFE_INTEGER = 2^53 - 1`:

1. `bool` → preservar sem alteração, antes de testar `int`, pois `bool` herda de `int` em Python.
2. `float` não finito → rejeitar/falhar de forma fechada.
3. `float` finito, integral e dentro de `[-MAX_SAFE_INTEGER, MAX_SAFE_INTEGER]` → `int(value)`.
4. `float` finito fora dessa regra, inclusive integral acima do limite ou fracionário → preservar como `float`; não arredondar nem truncar.
5. `int` fora de `[-MAX_SAFE_INTEGER, MAX_SAFE_INTEGER]` → converter para o `float` IEEE-754 mais próximo. Se `float(value)` lançar `OverflowError` ou não resultar em valor finito, rejeitar/falhar de forma fechada.
6. `int` dentro do intervalo seguro → preservar como `int`.
7. `dict` → preservar as chaves e normalizar cada valor; `sort_keys=True` continua definindo a ordem final.
8. `list` → preservar ordem e cardinalidade e normalizar cada item.
9. Demais valores JSON nativos → preservar sem alteração.

A serialização continua compacta (`separators=(",", ":")`), com chaves ordenadas e codificação UTF-8, seguida de SHA-256. A mesma `_canonical_digest` permanece sendo chamada tanto por `issue_oos_promotion_proof` quanto por `verify_oos_promotion_proof`; não haverá lógica divergente entre emissão e verificação.

No caso real, a emissão preserva `3.290195462758171e16` como float por estar fora do intervalo seguro. No save, o inteiro decimal `32901954627581710` é reconvertido ao double mais próximo, que é o mesmo valor binário da emissão. Assim, as duas pontas chegam à mesma representação canônica antes de `json.dumps`.

### Semântica por tipo e edge cases

- **Floats não integrais:** permanecem floats; a correção não arredonda, trunca nem aplica tolerância. `1.5` não se torna `1`.
- **Zero negativo:** `-0.0` canonicaliza para `0`, consistente com o round-trip de números JSON pelo browser.
- **`None`, strings e booleans:** permanecem inalterados. Booleans são tratados antes de inteiros para não virarem `1`/`0` por herança de tipo.
- **Dicionários e listas aninhados:** são percorridos em qualquer profundidade necessária ao payload; a ordem das listas é significativa e não muda.
- **Chaves de dicionário:** não são transformadas. O contrato de `promotion_payload` usa chaves string compatíveis com objetos JSON.
- **NaN e ±Infinity:** não têm representação JSON interoperável e são rejeitados/fail-closed pela canonicalização; suportá-los fica fora do escopo.
- **Inteiros excessivamente grandes:** a conversão para double é protegida contra `OverflowError` e resultado não finito; nesses casos a prova não é emitida/aceita.
- **Objetos não JSON nativos:** o comportamento existente de `default=str` é preservado; ampliar ou restringir essa compatibilidade não faz parte do card.

### Segurança e integridade

A mudança cria equivalência entre representações numéricas que chegam ao mesmo `Number` IEEE-754 no fluxo browser. Campos removidos, adicionados ou modificados; floats fracionários distinguíveis; texto diferente; ordem/cardinalidade de listas diferente; assinatura inválida; propósito incorreto; e expiração continuam invalidando a prova. Não haverá fallback que aceite digest incompatível sem recomputar o payload completo.

Há uma limitação inevitável: inteiros distintos acima de `2^53` podem colapsar no mesmo `Number` JavaScript e, depois disso, não são distinguíveis pelo fluxo. O digest passa a vincular a precisão transportável pelo browser, não uma precisão inteira arbitrária perdida antes do save. Preservar essa distinção exigiria mudar o contrato para transportar tais números como strings ou outro formato tipado, fora deste card.

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
| Testes | Cobertura de `8953.0` → `8953`, do `calmar_ratio` real, limites `±(2^53-1)`, preservação de fracionários/bools e falhas para não finitos/overflow; conteúdo distinguível diferente deve falhar. |
| API/UI | Nenhuma alteração de contrato ou superfície. |

## Alternativas consideradas

1. **Converter todo float integral para `int`: rejeitada após homologação.** Resolve `8953.0`, mas inventa precisão inteira acima de `2^53` que diverge do valor serializado pelo browser.
2. **Normalizar apenas campos conhecidos (`metrics.trades`/`calmar_ratio`): rejeitada.** Deixaria o mesmo defeito em outros campos atuais ou futuros.
3. **Comparar payloads com tolerância numérica: rejeitada.** Introduz equivalências além da precisão exata do double e pode aceitar alteração real de valor.
4. **Transportar números grandes como strings: adiada.** Preservaria precisão inteira arbitrária, mas muda contratos backend/frontend e o formato do payload; não é necessário para vincular os valores que hoje trafegam como `Number`.
5. **Digest legado como fallback: rejeitada.** A prova é efêmera (seis horas); manter canonicalizações paralelas aumenta complexidade e superfície de erro.

## Riscos e mitigação

- **Risco — regressão em estruturas aninhadas:** mitigado por testes com dict/list em múltiplos níveis e `None`/bool/string.
- **Risco — colisão de inteiros inseguros:** aceita-se a equivalência apenas porque valores que colapsam no mesmo `Number` já são indistinguíveis no transporte browser; o limite fica explícito e testado.
- **Risco — normalização excessiva:** mitigado por converter floats integrais para `int` somente no intervalo seguro e nunca arredondar float fracionário.
- **Risco — overflow/não finitos:** mitigado por validação de finitude e falha fechada antes do digest.
- **Risco — prova pré-deploy invalidada:** aceito e documentado devido ao TTL curto; repetir otimização reemite a prova.
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

- **P0/P1:** nenhum achado aberto. O bloqueador pós-implementação da conversão irrestrita de floats integrais foi incorporado à decisão por limite seguro e canonicalização simétrica de inteiros inseguros.
- **P2 — compatibilidade de prova pré-deploy:** uma prova ainda dentro do TTL pode ter digest legado e exigir nova otimização. Disposição: risco aceito, limitado a seis horas, sem fallback para não ampliar a superfície de verificação.
- **P2 — inteiros distintos podem colapsar acima de `2^53`:** o fluxo browser não preserva essa distinção. Disposição: limitação aceita e explícita; a prova vincula a precisão transportável. Preservar precisão arbitrária exigiria um novo contrato tipado.
- **P2 — não finitos não têm round-trip JSON estável:** NaN/Infinity não são cobertos pela equivalência proposta. Disposição: fail-closed; suportá-los está fora do escopo.
- **P3 — `default=str` mantém canonicalização de tipos não JSON:** não é ideal como contrato criptográfico geral, mas alterar esse legado não é necessário para o card. Disposição: fora de escopo; a entrada esperada de `promotion_payload` é JSON-compatible.

### Avaliação

- **Produto:** a solução cobre tanto o caso seguro `8953.0` quanto o `calmar_ratio` real observado na validação em DEV, sem alterar a regra de negócio que protege promoções NO-GO.
- **Escopo:** correção mínima no ponto compartilhado por emissão e verificação; nenhuma superfície visual ficou sem classificação.
- **Regressão:** o principal risco é compatibilidade transitória de tokens emitidos antes do deploy, explicitamente limitado pelo TTL.
- **Segurança:** nenhuma permissão é ampliada e nenhuma parte do payload sai do digest; a equivalência fica limitada ao que o transporte JavaScript consegue distinguir.
- **Operação:** não requer migração, mudança de configuração ou ação persistente; nova otimização recupera uma prova transitória incompatível.
- **Referências avaliadas:** `proposal.md`, este `design.md`, `backend/app/services/oos_promotion_proof.py`, emissão em `backend/app/routes/combo_routes.py` e verificação em `backend/app/routes/favorites.py`. Prototype: N/A justificado.

## Design Agent verdict

**PASS** — o bloqueador pós-implementação foi refletido em uma decisão simétrica e verificável para inteiros seguros/inseguros, o caso real e a regressão `8953.0` têm critérios explícitos, não há P0/P1 aberto e nenhuma UI é afetada. Como o card já está em `Done`, o rework preserva esse status conforme a regra de não regressão e repete Code Review e QA antes de nova evidência técnica.
