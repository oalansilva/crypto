## 1. Guard de evidência do pacote

- [x] 1.1 Adicionar ao `scripts/release-guard` a validação dos comentários de homologação dos cards `Homologado`/`Pronto` informados em `RELEASE_CARDS`
- [x] 1.2 Validar e normalizar IDs de `RELEASE_CARDS`, deduplicar cards e tratar falhas de GitHub/JSON como warning em `audit` e blocker em `post`
- [x] 1.3 Cobrir por teste os casos comentário presente/ausente, consulta indisponível, lista ausente, ID inválido e duplicado

## 2. Recuperação retroativa

- [x] 2.1 Validar o fluxo `--transition homologado --dry-run` e dedupe ref-less do helper com testes focados
- [x] 2.2 Executar dry-run nos cards 456, 457, 458, 463 e 464 usando o commit publicado da release 2026-08-11
- [x] 2.3 Após confirmar a homologação preexistente, postar exatamente um comentário canônico em cada card e revalidar o pacote pelo guard

## 3. Documentação e verificação

- [x] 3.1 Atualizar `AGENTS.md` para exigir o helper na transição para `Homologado` e registrar o saneamento em `docs/kaizen-log.md`
- [x] 3.2 Rodar testes focados dos scripts, `bash -n`, validação OpenSpec da change e `/opsx:verify`
- [x] 3.3 Executar review do diff exato, QA visual obrigatório/dispensa autorizada, integrar em `develop`, rodar `./restart` e validar a URL DEV antes de Done técnico
