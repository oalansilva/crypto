## Why

Segredos históricos em repositório público podem continuar permitindo acesso, e o backup segue versionado. A entrega precisa comprovar invalidação e limpar tip e histórico sob controle do projeto, preservando trabalho em curso.

## What Changes

- Inventário controlado de histórico, refs, configuração atual e conteúdo do backup; evidências sem material sensível.
- Rotação/revogação comprovada, continuidade DEV/PROD e invalidação de sessões JWT antigas.
- Remoção de `.local_backups/` do versionamento e prevenção de inclusão habitual.
- **BREAKING**: reescrita coordenada do histórico altera SHAs, exige recuperação dos worktrees e tratamento de refs/caches do GitHub, após invalidação comprovada.

## Capabilities

### New Capabilities

- `historical-secret-remediation`: contrato operacional de inventário, invalidação, limpeza e recuperação por ambiente.

### Modified Capabilities

Nenhuma. As proteções de #684/#687 permanecem; esta capacidade documenta a remediação incidente.

## Impact

Git/branches/tags/PRs, configuração protegida Binance/JWT/PostgreSQL em DEV/PROD, backup local e operação de release. Sem API ou interface nova. Ferramentas propostas: Gitleaks e git-filter-repo, executadas localmente na operação autorizada.

## Problema

O operador do Cripto Farol e as pessoas cujas contas ou dados dependem dele ficam expostos a acesso indevido porque o repositório está público, contém segredos no histórico e ainda publica um backup, invalidando a premissa de repositório privado usada em #687.

Diagnóstico atualizado em 2026-10-12 (somente presença, nomes e resultados; sem valores de segredos):

- `.env.binance`, `backend/.env` e `frontend/.env` estão ausentes do tip de `develop` e `main`, mas permanecem no histórico. Os achados conhecidos incluem credenciais Binance, `JWT_SECRET` e possível credencial em `WORKFLOW_DATABASE_URL`; `VITE_API_URL` e demais configurações precisam de classificação, não de rotação automática por serem variáveis.
- #687 removeu arquivos do tip e migrou configuração, sem rotacionar Binance; #695 foi encerrado como duplicata. #684 já entregou JWT fail-closed. Este card não refaz essas entregas.
- `.local_backups/backtest.db.bak.20260224T134424Z` continua no tip das duas branches e não está coberto pelo ignore. O schema mostra tabelas de backtests, estratégias e campos de texto/JSON, sem tabelas explícitas de usuários ou credenciais. As linhas não foram lidas: isso não prova ausência de dados pessoais ou segredos.
- Não há evidência localizada de inventário completo ou revogação Binance. A comparação dos valores históricos com DEV/PROD não foi executada: o controle de processo bloqueou a tentativa de leitura. Não há confirmação de coincidência, diferença ou rotação desses valores.

## História

Como operador do Cripto Farol, quero que nenhum segredo que já passou pelo Git público continue válido, e que nada sensível permaneça no tip, para que ler o repositório ou um clone/fork antigo não dê acesso à Binance, ao banco nem a sessões.

## Entra

- **Contenção (Alan, fora do código):** voltar o repositório para privado até terminar a revisão, registrando a verificação de visibilidade. Torná-lo privado não invalida cópias já feitas nem substitui a revogação.
- **Inventário completo:** examinar o conteúdo atual e todo o histórico disponível, incluindo branches, tags e o backup conhecido; registrar cada achado, sua classificação e resultado. Um possível segredo sem verificação permanece pendente, nunca vira “sem risco” por falta de evidência. Ferramentas e procedimento ficam no Design.
- **Revogação e rotação (Alan na Binance; operação autorizada em DEV/PROD):** gerar novo par Binance e revogar os pares expostos; trocar o segredo JWT e a credencial do banco quando algum valor histórico ainda estiver em uso ou válido. Outros segredos encontrados recebem o mesmo tratamento. Credencial já revogada exige comprovação, não nova rotação sem necessidade. Valores ficam somente em configuração protegida e fora do Git.
- **Backup e dados:** retirar `.local_backups/` do versionamento e impedir nova inclusão acidental. Classificar o conteúdo do backup por verificação controlada, sem publicar linhas ou valores; schema sozinho não encerra a análise. Dado pessoal ou sensível encontrado deve ter tratamento e pendência registrados, sem ser declarado eliminado de clones externos.
- **Critério de credenciais:** cada segredo histórico identificado tem evidência de revogação, expiração ou outra comprovação de que não permite mais acesso; DEV/PROD não reutilizam os valores comprometidos. Confirmar que a aplicação continua acessando os serviços com a configuração válida e que sessões assinadas com segredo JWT comprometido não são aceitas. Registrar somente nome da chave/serviço, presença, ambiente, data e resultado; nunca valor, hash de segredo ou saída bruta.
- **Critério do conteúdo atual:** ausência de material sensível e do backup na versão entregue; uma nova cópia em `.local_backups/` não entra no versionamento por inclusão habitual. Cada alerta do inventário tem resultado justificado, incluindo os classificados como configuração pública ou falso positivo.
- **Entrega por ambiente:** Done é a implementação integrada e validada em DEV, com pendências operacionais/PROD explicitadas; não afirma contenção completa enquanto houver segredo possivelmente válido sem comprovação. Pronto exige publicação, validação de PROD e encerramento dessas pendências no fluxo de release. Refinar este card não autoriza operar ambientes, trocar credenciais ou alterar visibilidade agora.
- **Histórico — decisão de Alan em 2026-10-12:** “Neste mesmo card — incluir a limpeza das versões antigas nesta entrega.” A remoção dos arquivos e blobs sensíveis das versões antigas publicadas entra nesta entrega, após comprovar a invalidação das credenciais comprometidas. Coordenar o impacto sobre branches, tags e cópias de trabalho sem apagar trabalho em curso. O resultado deve comprovar a ausência dos arquivos e blobs sensíveis no histórico publicado sob controle do projeto e registrar os limites relativos a forks, clones e outras cópias externas, cujo apagamento não pode ser garantido. Os mecanismos técnicos ficam no Design. Este registro de escopo não autoriza agora force-push, remoções ou release.

## Não entra

- Refazer a remoção de arquivos de configuração já entregue em #687 ou a proteção JWT de #684.
- Cifrar `api_secret` Binance em repouso (#692).
- Tornar o repositório público de novo (decisão separada, depois do Done).
- Garantir apagamento de forks, clones ou outras cópias que terceiros já tenham feito.

Relacionadas: #684, #687, #695, #692.
