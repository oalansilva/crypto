# Staging Deploy via GitHub Actions

The `deploy-staging` job in [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs only after a successful push to `develop` and only when staging deploy is explicitly enabled.

## Repository variable toggle

Set this repository variable to enable the job:

- `ENABLE_STAGING_DEPLOY=true`

If the variable is unset or `false`, the deploy job is skipped and CI remains green.

## Required repository variables

- `STAGING_SSH_HOST`: staging server hostname or IP
- `STAGING_SSH_PORT`: optional SSH port, defaults to `22`
- `STAGING_SSH_USER`: SSH user used by GitHub Actions
- `STAGING_APP_DIR`: absolute path to the repo checkout on the staging server
- `STAGING_HEALTHCHECK_URL`: optional HTTP endpoint checked after deploy
- `STAGING_DEPLOY_REF`: optional git ref to deploy, defaults to `develop`

## Required repository secret

- `STAGING_SSH_KEY`: private key with access to the staging server

## Remote deploy flow

The deploy job connects over SSH and runs:

```bash
cd "$STAGING_APP_DIR"
git fetch origin --prune
git checkout develop
git reset --hard "origin/${STAGING_DEPLOY_REF:-develop}"
./stop.sh
./start.sh
```

## Operational notes

- The staging server must already have the repo cloned and runtime env files configured.
- `start.sh` expects valid PostgreSQL-backed runtime environment variables on the server.
- Keep `deploy-staging` out of required PR checks; it is a post-merge push job for `develop`.
