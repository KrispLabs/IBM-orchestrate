# IBM Orchestrate

> **Zero-Touch Test Generation & Maintenance** — an AI-driven CI companion that reads your code, writes the tests, and keeps them green as your codebase evolves.

IBM Orchestrate is a full-stack platform that plugs into your GitHub workflow and uses **IBM watsonx.ai (Granite models)** as a smart test-engineering assistant. Push code, and Orchestrate analyzes the diff, generates or updates the corresponding tests, opens a PR with the changes, and surfaces test-health insights on a live dashboard — no manual test-writing required.

---

## Why IBM Orchestrate?

Engineering teams routinely spend 20–40% of their time writing and rewriting tests. Tests rot the moment business logic shifts, coverage drifts downward, and reviewers waste cycles on boilerplate assertions instead of meaningful logic. Orchestrate closes the loop:

- **Always-on test coverage** — every push is analyzed, every behavior change is mirrored in the test suite.
- **No manual rewrites** — when a function signature or branch changes, the AI rewrites the affected tests in place.
- **Full visibility** — a real-time dashboard shows test health, change timelines, and productivity metrics per repository.

---

## Innovations

| Innovation | What it does |
|---|---|
| **AST-aware diff analysis** | Parses Python ASTs (and grows from there) to identify which functions, classes, and branches actually changed — so the AI only regenerates tests that need it, instead of nuking the whole file. |
| **watsonx Granite-powered generation** | Uses IBM's Granite code models via `ibm-watsonx-ai` to produce idiomatic, framework-aware tests (pytest, factory-boy patterns) rather than generic stubs. |
| **Webhook → Celery → AI pipeline** | A push hits the GitHub webhook, Django enqueues a Celery job, and an async worker handles AST diffing + AI generation without blocking the API. Designed to scale horizontally. |
| **Auto-PR with traceability** | Generated tests come back as a pull request with links to the originating commit and a per-file `ChangeEvent` audit trail. |
| **Insights API** | Test-health, timeline, and productivity endpoints expose metrics that feed the React dashboard — and can be consumed by any internal tool. |
| **Self-healing tests** | When the AI detects an existing test that conflicts with new behavior, it updates the assertions in-place rather than appending duplicates. |
| **Containerized end-to-end** | One `docker-compose up` brings up Postgres, Redis, Django, Celery worker + beat, and the Vite frontend. |

---

## Tech Stack

**Backend**
- **Django 5** + **Django REST Framework** — API surface and ORM
- **Celery + Redis** — async webhook processing, scheduled jobs via Celery Beat
- **PostgreSQL 15** — durable store for repos, files, tests, and change events
- **IBM watsonx.ai (`ibm-watsonx-ai==1.1.2`)** — Granite code model inference
- **PyGithub** + custom webhook signing — GitHub App integration
- **`ast` + `astpretty` + `networkx`** — code structure analysis and dependency graphing
- **JWT (SimpleJWT)** + python-jose — authentication
- **pytest, pytest-django, pytest-playwright, factory-boy, coverage** — the test stack the system writes *for* you and *with*
- **Gunicorn + Whitenoise** — production serving

**Frontend**
- **React 18** + **Vite 5** — fast SPA with HMR
- **TailwindCSS** — design system
- **TanStack Query** — server-state caching
- **Zustand** — client-state store
- **Recharts** — test-health and productivity visualizations
- **React Router v6** + **Axios** + **lucide-react**

**Infrastructure**
- **Docker** + **docker-compose** — reproducible local + deploy environments
- **GitHub App + Webhooks** — push/PR event ingestion
- **Render-ready** (`runtime.txt` pinned to Python 3.11)

---

## Architecture

```
┌──────────────┐       push / PR        ┌────────────────┐
│   GitHub     │ ─────────────────────▶ │  Django API    │
│  Repository  │     (HMAC-signed       │  /github/...   │
└──────────────┘       webhook)         └────────┬───────┘
                                                 │ enqueue
                                                 ▼
       ┌────────────────────┐            ┌────────────────┐
       │  PostgreSQL        │ ◀───────── │  Celery Worker │
       │  repos / files /   │   persist  │  + Beat        │
       │  tests / events    │            └───────┬────────┘
       └────────────────────┘                    │ AST diff
                ▲                                ▼
                │                       ┌────────────────┐
                │ insights API          │  IBM watsonx   │
                │                       │  Granite model │
       ┌────────┴───────────┐           └────────────────┘
       │   React Dashboard  │
       │   (Vite + Tailwind)│
       └────────────────────┘
```

### Flow

1. **Push** — developer pushes to a connected GitHub repo.
2. **Webhook** — `POST /api/github/webhook/` verifies the HMAC signature and records a `WebhookEvent`.
3. **Dispatch** — Django enqueues a Celery task on Redis.
4. **Analysis** — the worker pulls the diff, runs AST-level analysis to find changed functions, classes, and branches.
5. **Generation** — `apps/ai_engine` calls watsonx.ai with structured context; Granite returns generated/updated test files.
6. **Persistence** — `CodeFile`, `TestFile`, and `ChangeEvent` rows are written.
7. **Pull Request** — a PR is opened back on GitHub with the new/updated tests.
8. **Insights** — the dashboard polls the insights API for live metrics.

---

## Setup Guide

### Prerequisites

- Python **3.11+**
- Node.js **20+**
- PostgreSQL **15+**
- Redis **7+**
- Docker & Docker Compose *(optional, recommended)*
- IBM Cloud account with **watsonx.ai** access
- A **GitHub App** (instructions below)

### Option A — Quick Start with Docker

```bash
git clone https://github.com/KrispLabs/IBM-orchestrate.git
cd IBM-orchestrate

cp backend/.env.example backend/.env
# Edit backend/.env with your watsonx + GitHub credentials

docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

Open:
- Frontend → http://localhost:5173
- API → http://localhost:8000
- Admin → http://localhost:8000/admin

### Option B — Manual Setup

#### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit
```

Required `backend/.env` keys:

```env
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ibm_orchestrate_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

WEBHOOK_SECRET=your-webhook-secret
GITHUB_APP_ID=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_WATSONX_API_KEY=your-api-key
IBM_WATSONX_PROJECT_ID=your-project-id

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

```bash
createdb ibm_orchestrate_db
python manage.py migrate
python manage.py createsuperuser
```

Run the four processes in separate terminals:

```bash
python manage.py runserver                 # Django API
celery -A config worker -l info            # async worker
celery -A config beat   -l info            # scheduled jobs
redis-server                               # if not running already
```

#### 2. Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api" > .env
npm run dev
```

#### 3. IBM watsonx.ai

1. Sign in to [IBM Cloud](https://cloud.ibm.com/).
2. Provision a **watsonx.ai** instance.
3. **Manage → Access (IAM) → API keys** → create a key.
4. Copy your **Project ID** from watsonx.ai project settings.
5. Paste both into `backend/.env`.

#### 4. GitHub App

1. **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App**.
2. Configure:
   - Homepage URL → your deployment URL
   - Webhook URL → `https://<your-domain>/api/github/webhook/`
   - Webhook secret → same value as `WEBHOOK_SECRET`
3. Permissions: **Contents: R/W**, **Pull requests: R/W**, **Metadata: R**.
4. Subscribe to events: **Push**, **Pull request**.
5. Generate a private key and store it; fill in the `GITHUB_*` env vars.

---

## API Reference

### GitHub Integration
- `POST /api/github/webhook/` — webhook receiver (HMAC-verified)
- `GET  /api/github/health/` — liveness check

### AI Engine
- `POST /api/ai/generate/` — generate tests for a code file
- `POST /api/ai/update/` — update existing tests against new code

### Insights
- `GET /api/insights/metrics/` — top-line metrics
- `GET /api/insights/test-health/<repo_id>/` — repo test health
- `GET /api/insights/timeline/<repo_id>/` — change timeline
- `GET /api/insights/productivity/` — productivity stats
- `GET /api/insights/repos/` — list connected repos
- `GET /api/insights/repos/<repo_id>/` — repo detail

---

## Testing

```bash
# Backend
cd backend && pytest

# Frontend (Playwright e2e wired in)
cd frontend && npm test
```

---

## Deployment

### Backend

```bash
docker build -f docker/Dockerfile.backend -t ibm-orchestrate-backend .
docker run -p 8000:8000 --env-file backend/.env ibm-orchestrate-backend
```

### Frontend

```bash
cd frontend
npm run build
# deploy dist/ to Vercel, Netlify, or behind nginx
```

A pinned `runtime.txt` (Python 3.11) and `gunicorn` make the backend Render/Heroku-ready out of the box.

---

## Project Layout

```
IBM-orchestrate/
├── backend/
│   ├── apps/
│   │   ├── ai_engine/          # watsonx integration + prompt templates
│   │   ├── authentication/     # JWT auth
│   │   ├── ci_pipeline/        # async orchestration tasks
│   │   ├── github_integration/ # webhook handler + GitHub App client
│   │   └── insights/           # metrics + dashboard API
│   ├── config/                 # Django settings, Celery app
│   ├── tests/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/           # axios API client
│   │   └── store/              # zustand stores
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
└── runtime.txt
```

---

## Troubleshooting

| Symptom | Check |
|---|---|
| DB connection refused | `pg_isready`, then `psql -U postgres -d ibm_orchestrate_db` |
| Celery tasks not firing | `celery -A config inspect ping` and confirm Redis is up (`redis-cli ping`) |
| Webhook not received | GitHub App → "Recent Deliveries"; confirm `WEBHOOK_SECRET` matches |
| Frontend can't reach API | `VITE_API_URL` in `frontend/.env` and `CORS_ALLOWED_ORIGINS` in backend |
| watsonx 401/403 | regenerate IAM API key; confirm Project ID matches the watsonx project |

---

## Contributing

Fork, branch, PR. CI runs `pytest` and lint on every push. Please keep generated test fixtures out of commits — Orchestrate will regenerate them.

## License

MIT.

---

*Built with IBM watsonx Granite — IBM Orchestrate Team.*
