# Heirloom 🍲

*Family recipes, passed down.*

A small web app to keep the family's recipes in one place and share them. You create a **cookbook**, send the link
(or its 8-character code) to the family, and everyone can add, edit and search recipes. No accounts, no passwords.

Built for the *Cloud Deployments* seminar (UPM · EMSE) by **Celia Banegas**: three services running in Azure.

```mermaid
flowchart LR
    U([Browser]) -->|HTTPS| W["Frontend<br/>HTML + JS<br/><b>Blob Storage static website</b>"]
    U -->|"HTTPS · fetch /api/..."| A["API<br/>Python · FastAPI<br/><b>Azure Container Apps</b>"]
    A -->|"TLS · sslmode=require"| D[("PostgreSQL 16<br/><b>Azure Database for PostgreSQL</b><br/>flexible server")]
    GH[GitHub Actions] -.->|image| H[(Docker Hub)]
    H -.->|pull| A
    GH -.->|upload| W
```

| Part | Tech | Where it runs | How it gets there |
|---|---|---|---|
| `web/` | Plain HTML, CSS and JavaScript (no build step) | Azure Blob Storage, static website | Terraform creates it, GitHub Actions uploads it |
| `api/` | Python 3.13, FastAPI, psycopg 3 | Azure Container Apps (scale 0–2) | Docker image on Docker Hub, GitHub Actions rolls it out |
| database | PostgreSQL 16 | Azure Database for PostgreSQL flexible server (B1ms) | Terraform |

## API

| Method | Path | Does |
|---|---|---|
| `GET` | `/health` | API + database check, returns the running version (commit SHA) |
| `POST` | `/api/cookbooks` | Create a cookbook → `{ code, name }` |
| `GET` | `/api/cookbooks/{code}` | Cookbook name and number of recipes |
| `GET` | `/api/cookbooks/{code}/recipes?q=` | List recipes, search by title, ingredient or author |
| `POST` | `/api/cookbooks/{code}/recipes` | Add a recipe |
| `GET` `PUT` `DELETE` | `/api/cookbooks/{code}/recipes/{id}` | Read, update, delete a recipe |

Interactive docs: `<API URL>/docs`.

### Configuration (environment variables only, nothing in code)

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | — (required) | Postgres connection string. In Azure it is a **Container App secret** (`secretref:`) |
| `CORS_ORIGIN` | `http://localhost:8080` | Frontend origin allowed to call the API (comma-separated for several) |
| `PORT` | `8000` | Port the container listens on |
| `APP_VERSION` | `dev` | Set at build time from the commit SHA |

The frontend reads the API URL at runtime from `config.js`, so the same files work locally and in the cloud.

## Run it locally

```bash
docker compose up --build
```

- App: http://localhost:8080
- API: http://localhost:8000/health · docs at http://localhost:8000/docs

Tests (they need a real Postgres):

```bash
docker run -d --name heirloom-test-db -p 5432:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=heirloom postgres:16-alpine
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
DATABASE_URL=postgresql://postgres:test@localhost:5432/heirloom pytest
```

## Deploy to Azure

### 1. Infrastructure with Terraform

```bash
az login
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # subscription ID + a DB password
terraform init
terraform plan
terraform apply
terraform output                              # website_url, storage_account_name, resource_group
```

### 2. API image

```bash
docker build --platform linux/amd64 -t <dockerhub-user>/heirloom-api:1.0 ./api
docker push <dockerhub-user>/heirloom-api:1.0
```

### 3. Container App

```bash
RG=$(terraform -chdir=infra/terraform output -raw resource_group)
LOC=$(terraform -chdir=infra/terraform output -raw location)
DB_URL=$(terraform -chdir=infra/terraform output -raw database_url)
WEB=$(terraform -chdir=infra/terraform output -raw website_url); WEB=${WEB%/}

az containerapp env create -n cae-heirloom -g "$RG" -l "$LOC"
az containerapp create -n heirloom-api -g "$RG" --environment cae-heirloom \
  --image docker.io/<dockerhub-user>/heirloom-api:1.0 \
  --ingress external --target-port 8000 --min-replicas 0 --max-replicas 2 \
  --secrets database-url="$DB_URL" \
  --env-vars DATABASE_URL=secretref:database-url CORS_ORIGIN="$WEB"
```

### 4. Frontend

```bash
API=https://$(az containerapp show -n heirloom-api -g "$RG" --query properties.configuration.ingress.fqdn -o tsv)
mkdir -p /tmp/site && cp web/index.html web/app.js web/styles.css /tmp/site/
echo "window.HEIRLOOM_CONFIG = { apiUrl: \"$API\" };" > /tmp/site/config.js
az storage blob upload-batch --account-name "$(terraform -chdir=infra/terraform output -raw storage_account_name)" \
  -s /tmp/site -d '$web' --overwrite --auth-mode key
```

### 5. CI/CD (GitHub Actions)

| Workflow | Trigger | Does |
|---|---|---|
| `api` | changes in `api/` | pytest against a Postgres service container → build image `heirloom-api:<sha>` → push to Docker Hub → `az containerapp update` → smoke test on `/health` |
| `web` | changes in `web/` | JS syntax check → write `config.js` with the API URL → upload to `$web` |

Pull requests run tests/checks only. Azure login uses **OIDC** (a managed identity with a federated credential for
`main`), so no Azure password is stored in GitHub. Settings needed in *Settings → Secrets and variables → Actions*:

- Secret: `DOCKERHUB_TOKEN`
- Variables: `DOCKERHUB_USERNAME`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
  `AZURE_RESOURCE_GROUP`, `CONTAINER_APP_NAME`, `STORAGE_ACCOUNT_NAME`, `API_URL`

## Good practices followed

- No secrets in the repo: `DATABASE_URL` lives in a Container App secret, the DB password in an ignored
  `terraform.tfvars`, the Docker Hub token in a GitHub secret, and Azure login is passwordless (OIDC).
- Small images: multi-stage `python:3.13-slim` build (only the virtualenv is copied), runs as a non-root user;
  the frontend image (local only) is `nginx-unprivileged:alpine`.
- Images tagged with the commit SHA, so every revision is traceable and a rollback is "deploy an older SHA".
- Postgres connection over TLS (`sslmode=require`), CORS restricted to the frontend's origin.

## What I would change for real production

- **Private networking:** put Container Apps in a VNet and use Postgres private access instead of
  "allow Azure services" + public endpoint.
- **Key Vault + managed identity** for the database credentials (or Entra ID auth to Postgres) instead of a password.
- **Real authentication:** today anyone with the code can edit a cookbook. Add sign-in (e.g. Entra External ID)
  and roles (owner / editor / reader).
- **Remote Terraform state** in a storage account with locking, and the Container App in Terraform too.
- **CDN / Front Door** with a custom domain in front of the static website.
- **Migrations** with a tool (Alembic) instead of `CREATE TABLE IF NOT EXISTS` at startup.
- **Monitoring:** Application Insights / OpenTelemetry, alerts on errors and latency; `min-replicas 1` to avoid
  cold starts; zone-redundant HA and longer backup retention for the database.
- **Private registry** (Azure Container Registry) instead of a public Docker Hub image.
