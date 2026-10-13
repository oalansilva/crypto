# Reprodução do Apply #1091

O [relatório final](report.md) reúne os critérios de aceite, resultados,
checks e limitações. Os pares aceitos, equivalência final, ablação e medidas
frio/quente estão em `accepted/verified/`.

O harness versionado está em `backend/scripts/discovery_benchmark_1091.py`.
Recebe `--root`, `--fixtures`, `--output` e `--baseline-revision`; não depende
dos scripts exploratórios temporários, de banco vivo ou de download de mercado.
O ambiente Python é escolhido pelo executor. Os fixtures são os arquivos
congelados de #945 e o export dos 14 templates é o versionado no backend.

```sh
python3 -m venv /caminho/ambiente
/caminho/ambiente/bin/python -m pip install -r backend/requirements.txt -r backend/requirements.lock
/caminho/ambiente/bin/python -m pip check
/caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py validate --output /caminho/evidencia
/caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py ablation --output /caminho/evidencia
/caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py suite --output /caminho/evidencia
NUMBA_CACHE_DIR=/caminho/cache-jit-preparacao-vazio /caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py jit --label preparacao-fria --output /caminho/evidencia
NUMBA_CACHE_DIR=/caminho/cache-jit-preparacao-vazio /caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py jit --label preparacao-quente --output /caminho/evidencia
NUMBA_CACHE_DIR=/caminho/cache-jit-vazio /caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py engine --cold --label jit-cold --output /caminho/evidencia
NUMBA_CACHE_DIR=/caminho/cache-jit-vazio /caminho/ambiente/bin/python backend/scripts/discovery_benchmark_1091.py engine --label jit-warm --output /caminho/evidencia
```

Use diretório de evidência novo para cada suite, pois o observer escreve JSONL
por worker. O suite alterna a ordem de cinco pares por cenário: Multi-MA/1INCH
long, Multi-MA/AAVE short e EMA+RSI/1INCH long. São sempre três workers,
2023-01-01 a 2025-01-01, split 70/30 e Deep 15m. Busca, rounds, score e grid
são os atuais. O primário exige 21.210 tentativas e zero falhas por execução.

`baseline` usa a reversão pós-945 no mesmo candidato, com LEGACY ausente.
O manifesto verifica os corpos Python de posição e Deep contra o AST literal
da revisão baseline, além de registrar SHA completo de baseline, hashes das
fontes candidatas, do harness, export, fixtures e dependências. Candidato ainda
não commitado é declarado; HEAD não é apresentado como SHA do candidato.
Nenhum campo do resultado é excluído. A comparação percorre estruturas,
DataFrames, índices e arrays completos, usa igualdade exata e mantém NaN nas
mesmas posições. Hashes são resumos adicionais.

Relatórios brutos `.log`/`.jsonl` são preservados em gzip determinístico. Os
resultados completos, idênticos em cada cenário, ficam em três arquivos
`<cenario>.result.json.gz`; cada execução tem link relativo para o seu resultado.
O SHA-256 nos summaries corresponde aos bytes JSON descomprimidos. A igualdade
estrutural ocorre antes dessa deduplicação, que também exige igualdade de bytes.

`ablation` mede cinco pares de batches congelados de 50 parâmetros por cenário,
sempre com fingerprint+Numba. O calculador experimental é uma cópia local da
função ligada a um executor TA-Lib privado; não modifica globals de produto
nem funções TA-Lib. A chave usa arrays efetivos completos, índice e kwargs;
saídas são cópias protegidas e entram no mesmo orçamento. Esse componente
não faz parte do motor entregue. A medição de batch é uma triagem de custo,
não um claim de ganho em toda a busca.

Para diagnóstico, `engine --template ema_rsi --profile --label diagnostico`
grava o perfil do primeiro batch de cada worker e do resultado final no pai.
Esses tempos têm `profiled_diagnostic_run=true` e não entram no aceite. A
primeira tentativa de profiling iniciou um profiler no pai antes do fork e
conflitou com os profilers dos workers; foi corrigida localmente no harness.

O candidato inicial passou Multi-MA/1INCH e AAVE, mas regrediu em EMA+RSI.
O rework substituiu a enumeração de Series de `DataFrame.memory_usage` por
contagem dos buffers, incluindo backing arrays e metadados; removeu boxing
de timestamps UTC na proteção do índice; e propagou o fingerprint entre
wrappers pandas do mesmo buffer privado congelado, com dtype/names e
referência forte. Índices externos mutáveis continuam sem memoização por id.
O contador foi triado em 1.000 frames de 512 linhas/18 colunas: 0,894 s antes
e 0,0174 s após a primeira correção. Esse microensaio não substitui os pares
do motor completo.

O tempo normal inclui snapshots, cópias, serialização e transporte aos workers.
Preparação de JIT é reportada separadamente. O monitor Linux `/proc` amostra
RSS agregado pai+descendentes a cada 50 ms; `ru_maxrss` registra os picos por
processo. RSS inclui runtime/JIT e buffers; páginas compartilhadas aparecem
no RSS de cada processo, portanto a soma não é PSS nem memória física exclusiva.
Não se confunde com o
orçamento de bytes retidos nos caches. O observer registra limites e evicções
ao concluir cada batch; testes adversariais também forçam evicção e rejeição
de item excessivo. Import/carregamento/manifesto são reportados separadamente.

`accepted/verified/` contém a medição do candidato final, incluindo todos os
três cenários de cinco pares. `--scenario ema-rsi`, `--scenario primary` e
`--scenario aave` permitem executá-los serialmente no mesmo diretório novo,
acumulando o relatório; cada cenário mantém a busca integral. Arquivos de
`final/` registram a medição anterior, que falhou por regressão em EMA+RSI.
Arquivos diretamente nesta pasta registram o ensaio preliminar interrompido
para corrigir ownership do índice e uniformizar signatures de JIT; nenhum
desses ensaios anteriores é a evidência final de aceite.
`apply-blocked.md` no diretório superior conserva a recusa histórica já superada
pela escrita protegida real do harness nesta continuação.

Validação CI é estrutural/invariante, sem deadline de desempenho. Os comandos
de teste usam banco dummy somente para import e não estabelecem conexão:

```sh
DATABASE_URL=postgresql+psycopg2://unused:unused@127.0.0.1:1/crypto_app_test PYTHONPATH=backend:. python -m pytest backend/tests/unit/test_card_1091_acceleration.py --timeout=0 -q
python3 scripts/validate_backend_unit_inventory.py --json
openspec validate card-1091-discovery-cache-numba --strict
git diff --check
```

Instalação limpa confirmada nesta VM Linux aarch64/Python 3.12, conforme
`../apply-blocked.md`; não há prova de instalação em outras plataformas.
Benchmarks não incluem downloads, fila da aplicação, HTTP ou persistência.
Avisos históricos de lógica de templates não são corrigidos neste card e
são registrados separados de falhas de trials.

Uma seleção inicial ampla terminou com 201 testes verdes, uma falha no
argumento opcional de intraday das fixtures finais (corrigida neste Apply) e
oito erros em fixtures `postgres_isolation` por conexão recusada ao URL dummy.
Esses oito casos de persistência não integram o ensaio de dados congelados;
não houve acesso a banco vivo. A seleção final de contratos usa
`-k 'not Persistence'`, e seus resultados estão em `final/contracts.log`.
