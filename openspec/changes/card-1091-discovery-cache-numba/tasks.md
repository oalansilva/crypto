## 1. Referência e reprodução

- [x] 1.1 Preservar baseline pós-945 e criar harness versionado parametrizado por raiz, fixtures e commits, sem depender dos paths temporários ou monkeypatch global de produto.
- [x] 1.2 Validar manifesto de inputs/export de templates e registrar campos voláteis antes de implementar comparação estrutural exata de resultados, indicadores, máscaras, trades e métricas.
- [x] 1.3 Confirmar instalação limpa de Numba/llvmlite com Python/NumPy/pandas/TA-Lib do repo e atualizar requirements.txt/lock sem upgrades alheios; documentar plataforma testada.

## 2. Contextos e caches

- [x] 2.1 Implementar snapshots privados imutáveis e identidade completa de dados/índice/esquema com geração, fonte e papel da janela, incluindo transporte ao worker.
- [x] 2.2 Isolar treino, final e holdout+burn-in mantendo os limites e filtros atuais; tratar chamadas externas sem contexto confiável sem memoização insegura.
- [x] 2.3 Aplicar tetos de entradas/bytes e LRU aos caches tocados, lifecycle por execução, ownership de arrays e chaves completas de índice/coverage/intraday/parâmetros resolvidos.
- [x] 2.4 Validar mutação OHLCV/índice interno, metadata herdada, A→B→A, fria/quente, evicção, aliases/defaults, tentativa de mutação e execuções sucessivas; medir memória retida e RSS agregado.

## 3. Núcleos e reversão

- [x] 3.1 Extrair e compilar núcleo de posições preservando float64, NaN/zero, expressões, ordem e prioridade stop/sinal com fastmath=False e sem paralelismo adicional.
- [x] 3.2 Extrair núcleo Deep preservando índices int64, janela semiaberta, primeiro stop, sobreposição e fim sem saída; manter PnL/custos/serialização em fontes atuais.
- [x] 3.3 Integrar adaptadores no motor comum e fallback Python por falta/incompatibilidade de compilação; testar cache JIT sem escrita e assinatura inelegível sem mascarar erros de negócio.
- [x] 3.4 Implementar reversão interna de todos os componentes #1091 ao baseline pós-945 e testar precedência distinta da flag LEGACY, em processos novos/caches limpos.

## 4. Indicadores e equivalência

- [x] 4.1 Avaliar cache individual local a TA-Lib com entradas/kwargs efetivos e saídas protegidas; manter apenas mediante benefício repetido contra fingerprint+Numba, registrando ablação.
- [x] 4.2 Executar equivalência nos 14 templates, dois símbolos, long/short, 50 parâmetros (2.800 casos) e pelo menos 568 edges, ampliando para indicadores/máscaras/trades completos/holdout/GO-NO-GO sem tolerância.
- [x] 4.3 Validar 1d/4h, Deep 15m/fallback diário com cobertura ausente/incompleta, custos e contratos de Descoberta/laboratório/batch/favoritos com testes apropriados existentes.
- [x] 4.4 Registrar avisos preexistentes separadamente e confirmar zero falhas e busca integral no cenário de 21.210 tentativas, sem alterar grid/rodadas/score/workers.

## 5. Ganho e evidência

- [x] 5.1 Medir cinco pares alternados aquecidos no cenário primário com mesmo hardware/dados/três workers; exigir mediana menor e três pares melhores, registrando durações/dispersão/commits/deps e igualdade integral.
- [x] 5.2 Repetir cinco pares AAVE short e EMA+RSI/1INCH long, corrigindo regressão sustentada; executar ablação do cache indicador e registrar decisão final.
- [x] 5.3 Medir primeira execução/JIT frio/quente e memória pai+workers, incluindo snapshots/transporte no tempo normal; demonstrar limites/evicção e reversão exata.
- [x] 5.4 Versionar harness final, manifesto e relatórios brutos, documentar comandos reproduzíveis/limitações e executar validação OpenSpec estrita e checks pertinentes sem deadline temporal em CI.

## 6. Integração com #1093

- [x] 6.1 Integrar com o limite de memória e a recuperação sem OOM do #1093 (merge de develop): caches de 15m/indicadores/cobertura passam pelo mesmo Cache/BUDGET limitado (64 MiB, 4.096 entradas, 32 snapshots) com Snapshot/Numba preservados, execução em streaming via ResultSpool e reversão `COMBO_OPTIMIZER_1091_DISABLED` mantida.
