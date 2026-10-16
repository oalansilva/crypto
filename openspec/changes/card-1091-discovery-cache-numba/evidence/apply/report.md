# Apply #1091 — resultado final

Snapshots privados, caches limitados e os dois kernels Numba passaram a operar
no motor compartilhado. TA-Lib, busca, rounds, score, custos e três workers
mantêm seus contratos. O candidato final passou equivalência exata, reversão
e os três cenários de desempenho. Cache individual de indicadores foi excluído
após ablação desfavorável.

## Identidade e reprodução

Baseline pós-945: `64c1b97aec75b250ad4f32c0fd20692cf7a5f5b5`.
O candidato está sem commit; HEAD não identifica seus bytes. O
[manifesto final](accepted/verified/input-manifest.json) registra hashes SHA-256
de todas as fontes, requirements, sete fixtures e export dos 14 templates,
além dos hashes das fontes baseline. Os corpos Python de posição e Deep
foram comparados ao AST literal do baseline. Nenhum campo volátil foi excluído.

SHA-256 do harness final:
`48911d924f06a1e99824009f6d9f691815e9b57cc3e40b7379bdc45a22de2f64`.
Os 30 manifestos dos pares aceitos, a validação e a ablação usam os mesmos
bytes de fontes/harness, dependências e fixtures. Os bytes atuais foram
conferidos novamente contra esse manifesto após os ensaios.

Plataforma: Linux aarch64, glibc 2.39, Python 3.12.3, quatro CPUs disponíveis.
Instalação limpa e `pip check` passaram no ambiente de validação: Numba 0.68.0,
llvmlite 0.50.0, NumPy 2.4.6, pandas 3.0.3, TA-Lib 0.6.8 e pyarrow 24.0.0.
Somente Numba/llvmlite foram acrescentados aos requirements.

O [README](README.md) contém comandos parametrizados por raiz, fixtures,
ambiente Python, revisão baseline e saída. O harness versionado não depende
dos scripts exploratórios temporários, de banco vivo ou de downloads.

## Desempenho aceito

Cinco pares alternados por cenário, dados congelados de #945, 1d,
2023-01-01 a 2025-01-01, split 70/30, Deep 15m e três workers. O tempo do
motor inclui snapshots, cópias, serialização, transporte e resultado final.
Preparação JIT e imports/carregamento/manifesto têm medidas separadas.

| Cenário | Mediana baseline | Mediana candidato | Ganho | Pares melhores |
| --- | ---: | ---: | ---: | ---: |
| Multi-MA / 1INCH long | 35,1800 s | 30,2507 s | 14,01% | 5/5 |
| Multi-MA / AAVE short | 33,5146 s | 29,2238 s | 12,80% | 5/5 |
| EMA+RSI / 1INCH long | 11,2041 s | 10,6727 s | 4,74% | 4/5 |

O primário passou mediana menor e maioria dos pares melhores; 25% é objetivo,
sem piso contratual. Os secundários não apresentam regressão sustentada.
Não se descartou nenhum par. O primeiro par primário foi mais lento nos dois
modos e está preservado: 47,7571 s / 39,9574 s.

| Cenário | Baseline min–max / desvio amostral | Candidato min–max / desvio amostral |
| --- | --- | --- |
| Primário | 34,9062–47,7571 s / 5,5850 s | 29,6088–39,9574 s / 4,4809 s |
| AAVE | 33,3326–37,2897 s / 1,7022 s | 28,5019–31,6298 s / 1,2789 s |
| EMA+RSI | 10,4460–11,4055 s / 0,3745 s | 10,4707–11,0291 s / 0,2068 s |

O [relatório bruto](accepted/verified/performance.json) preserva todas as
durações individuais, ordem, RSS, limites de cache e resumos dos 30 runs.
Todos terminaram com zero falhas e igualdade estrutural integral; primário
e AAVE têm 21.210 trials por run, EMA+RSI tem 2.850. Resultado final, treino,
holdout e decisão GO/NO-GO foram comparados antes da deduplicação dos arquivos.
Os JSON completos estão em `accepted/verified/*.result.json.gz`, com logs
e JSONL por worker preservados em gzip determinístico.

## Frio, quente e memória

Preparação dos dois kernels em processo novo, diretório JIT inicialmente
vazio: **3,4390 s**; processo novo reutilizando o cache: **0,5221 s**.
Ambos registram posições/Deep compilados. Imports/carregamento/manifesto:
1,4270 s e 1,5432 s, respectivamente. Dados brutos em
[cold-preparation.jit.json](accepted/verified/cold-preparation.jit.json) e
[warm-preparation.jit.json](accepted/verified/warm-preparation.jit.json).

Primeira otimização com outro diretório JIT vazio: **39,0635 s**, incluindo
compilação dentro da execução normal. Execução seguinte, em processo novo
reutilizando esse diretório: **38,0942 s**, mais preparação separada de
0,5693 s. Imports/carregamento/manifesto: 1,7829 s / 2,3738 s. Ambos executaram
21.210 trials, sem falhas, com inputs intactos e os mesmos bytes JSON completos
do primário aceito; SHA-256:
`27b3d35b7e57213ac0308cfeb89b02d91a5a4c7da5b235ba21feab3b0156463f`.
Esses dois runs são evidência de startup, não substituem os cinco pares.

RSS Linux `/proc` amostrado a cada 50 ms, somando pai e descendentes:
1.418,89 MiB frio e 1.231,83 MiB quente. Nos 30 runs aceitos, mediana/máximo
do RSS agregado baseline: 962,70 / 1.001,60 MiB; candidato: 1.196,37 /
1.242,48 MiB. O aumento do runtime/JIT é um custo material. A soma inclui
páginas compartilhadas várias vezes: não é PSS nem memória física exclusiva.
Os summaries preservam `ru_maxrss` bruto do pai e de cada worker.

O orçamento LRU é por processo/execução: **64 MiB, 4.096 entradas e 32
snapshots**, calibrável internamente. Máximo observado no candidato dos
pares: **59,1030 MiB, 1.322 entradas e um snapshot**. Nos dois runs startup:
50,48 / 50,86 MiB. Todos os summaries satisfazem os três tetos; retenção no
pai após execução é zero. Não houve evicção nos runs normais. Os testes
adversariais forçam evicção, mudança de geração e rejeição de item excessivo,
contando buffers, referências fortes, views e metadados.

## Ablação de indicadores

Cinco pares alternados de batches congelados de 50 trials por cenário,
fingerprint+Numba nos dois lados, executor TA-Lib privado no harness e
igualdade exata. Medianas sem/com cache individual:

| Cenário | Sem cache individual | Com cache individual | Ganho | Pares melhores |
| --- | ---: | ---: | ---: | ---: |
| Primário | 0,8010 s | 0,8223 s | -2,65% | 2/5 |
| AAVE | 0,8098 s | 0,8320 s | -2,75% | 0/5 |
| EMA+RSI | 0,7955 s | 0,8124 s | -2,13% | 1/5 |

O cache individual foi excluído. Trata-se de triagem de batch, sem claim de
ganho no motor completo. Os pares brutos e a decisão estão em
[indicator-ablation.json](accepted/verified/indicator-ablation.json).
TA-Lib de produto não sofre monkeypatch global.

## Correção e checks

- [Equivalência final](accepted/verified/equivalence.json): **2.800 casos +
  568 edges**, 142,70 s, 14 templates × dois símbolos × long/short × 50
  parâmetros, indicadores/máscaras/sinais/trades/métricas e lógica completos.
  Tolerância zero, NaN nas mesmas posições, sem rounding ou campos excluídos.
- [Testes adversariais finais](accepted/unit-1091.log): **16 passed**, 21,67 s.
  Incluem mutações/ABA/metadata, cache frio/quente/evicção, ownership,
  limpeza sucessiva, fallback de compilação/cache sem escrita, erros de
  negócio, precedência das flags em processos novos, Timestamp máximo,
  1d/4h, intraday ausente/incompleto e custos.
- [Contratos existentes + novos](final/contracts.log): **73 passed,
  8 deselected**, 273,09 s, incluindo golden de vencedor/treino/holdout/
  GO-NO-GO e consumidores Descoberta/laboratório/batch/favoritos. Este run
  precede a última otimização do contador/índice privado; a suíte adversarial
  e a equivalência final foram repetidas sobre os bytes finais.
- `python3 scripts/validate_backend_unit_inventory.py --json`: **valid=true,
  82 arquivos/82 entradas**, sem ausências, duplicatas ou problemas semânticos.
- `openspec validate card-1091-discovery-cache-numba --strict`: **valid**.
- `openspec instructions apply --change card-1091-discovery-cache-numba --json`:
  **all_done, 19/19, zero pendentes**. O CLI também avisa que `rules.tasks`
  deve ser array de strings e ignora essas rules; a validação estrita passa.
- CI verifica correção/invariantes sem deadline de desempenho.

856 ocorrências preexistentes de aviso de lógica foram preservadas na última
equivalência. Os testes registram avisos de configuração Pydantic e overflow
histórico de CAGR separadamente de falhas de trials.

## Limitações e histórico

Instalação foi comprovada nesta plataforma aarch64/Python 3.12; outras
plataformas não foram ensaiadas. O host compartilhado tem dispersão visível,
por isso os pares completos e os dois runs startup permanecem publicados.
Benchmarks excluem downloads, fila, HTTP e persistência.

Uma seleção inicial ampla teve 201 passes, uma falha do argumento opcional
intraday (corrigida) e oito erros `postgres_isolation` com conexão recusada
ao banco dummy. A seleção final de contratos exclui esses oito casos de
persistência. Não houve acesso a banco vivo.

`final/performance.json` conserva uma medição anterior que falhou em
EMA+RSI. O rework reduziu custo de contagem de buffers e boxing de timestamps,
propagando fingerprints apenas entre wrappers de backing arrays privados
congelados. A evidência de aceite é exclusivamente `accepted/verified/`.
A recusa histórica de escrita em `../apply-blocked.md` foi superada nesta
continuação por escrita protegida real; não há P0 de infraestrutura ativo.

UI impact: none. Nenhum commit, push, deploy, mudança de coluna ou review
foi executado pelo Apply. Modelo/esforço solicitados: `gpt-6.1-sol` / `high`;
runtime/modelo/esforço observados: **unavailable** (o host não os expõe).
Não se inferiu runtime a partir da seleção. Spawns deste Apply: zero.

## Adendo T13 — formatação Black 26.10.1

Sobre `HEAD=471015eeb6b832dd6d17b83fb08bda7bfcb4409d`, Black 26.10.1
formatou somente os sete arquivos apontados pelo `backend-format` do CI.
Os hashes SHA-256 abaixo comparam `git show HEAD:<arquivo>` com os bytes
formatados. Para cada arquivo, a comparação direta de
`ast.dump(ast.parse(source), include_attributes=False)` foi **igual**,
sem considerar posições/atributos. Nenhuma lógica Python foi alterada.

| Arquivo | SHA-256 antes | SHA-256 depois | AST igual |
| --- | --- | --- | --- |
| `backend/app/services/combo_acceleration.py` | `bf8d928fd0217fed43782763008ed38a5fec314ea74e7a9cbd517d722fa59b80` | `6bba8a528d9e7045f2143c507d51a51e231ff8b07d01c0016269cbfb93490958` | sim |
| `backend/app/services/combo_cache.py` | `a4a9c50370407c62ea6e7301491e87530184d2337d131b267fe9b461c09b1488` | `a6b334a5472d2382b352ed8b4fd84f018f0a650c119202e3139e9d2d0ba8f329` | sim |
| `backend/app/services/deep_backtest.py` | `fd67b45054a9b30c90eb80813f558475e42dea924496acfeb05ce51cacb232b7` | `74d62e4ff379cebd576486892a3d9093640ef687f00ab0f4bcdba2834cd12df5` | sim |
| `backend/app/services/combo_optimizer.py` | `1f5b8de448856ac591edab2ae5f551813365d9880a71cbfe8f12fa775a4a3109` | `a95e8d31cdb825f3361d999215cf86e17b2f44d9f7f09c380c101abb94cc9e77` | sim |
| `backend/app/strategies/combos/combo_strategy.py` | `d22d9a29b9acb956c332c49c782ccb37f3fa434d6e9ea0175782cdcd4ca8988b` | `90e19a3211a724c29812730d767f428a53755f4db13e604c5cc2504514b5cded` | sim |
| `backend/scripts/discovery_benchmark_1091.py` | `48911d924f06a1e99824009f6d9f691815e9b57cc3e40b7379bdc45a22de2f64` | `bd0a573e5031b24a5f0c46bc42b42839daf953ed172ac54e19ff246551224161` | sim |
| `backend/tests/unit/test_card_1091_acceleration.py` | `b636138d70940f45ac7c4c7c5645fa678a229c529d391b858004379aed3f9bf4` | `919efd862043eb9610fa42d49ade3422e474e9ed81583ced34ca416a423d15cc` | sim |

Comandos executados no worktree, usando o ambiente isolado
`/tmp/card-1091-clean-env` (Python 3.12.3, Black 26.10.1):

- `python -m black --check backend` antes: exit 1, sete arquivos a formatar
  e 330 inalterados. `python -m black` seguido dos sete paths absolutos da
  tabela: exit 0, sete arquivos formatados.
- `python -m black --check backend` depois: exit 0, 337 arquivos inalterados.
- `PYTHONPATH=backend:backend/tests python -m pytest -q backend/tests/unit/test_card_1091_acceleration.py`:
  exit 0, **16 passed, 1 warning in 24.76s**; aviso Pydantic preexistente
  em `backend/app/config.py:21`.
- `openspec validate card-1091-discovery-cache-numba --strict`: exit 0, valid.
- `git diff --check`: exit 0, sem erros de whitespace.
- `openspec instructions apply --change card-1091-discovery-cache-numba --json`:
  exit 0, **all_done, 19/19**; aviso preexistente de `rules.tasks` preservado.

As medições em `accepted/verified/` e seus manifestos brutos foram produzidos
**antes desta formatação**. Os benchmarks não foram repetidos nem os
manifestos reescritos; a igualdade das ASTs não é uma nova medição de
desempenho. Modelo/esforço solicitados nesta correção: `gpt-6.1-sol` / `high`;
modelo/esforço observados: **unavailable**, sem inferência pela captura
`/tmp/card-1091-format-apply-model.json`. Spawns desta correção: zero.
