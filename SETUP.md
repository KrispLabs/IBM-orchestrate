# IBM Orchestrate - Setup Guide

Complete setup instructions for the IBM Orchestrate automated test generation system.

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd IBM-orchestrate

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Admin: http://localhost:8000/admin
```

## Manual Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Environment Variables

Create `backend/.env`:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ibm_orchestrate_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# GitHub
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_APP_ID=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# IBM WatsonX
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_WATSONX_API_KEY=your-api-key
IBM_WATSONX_PROJECT_ID=your-project-id

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb ibm_orchestrate_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Backend Services

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat (for scheduled tasks)
celery -A config beat -l info

# Terminal 4: Redis (if not using Docker)
redis-server
```

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Start development server
npm run dev
```

## IBM WatsonX Setup

1. Go to [IBM Cloud](https://cloud.ibm.com/)
2. Create a watsonx.ai instance
3. Navigate to "Manage" → "Access (IAM)" → "API keys"
4. Create a new API key
5. Get your Project ID from watsonx.ai project settings
6. Update `.env` with your credentials

## GitHub App Setup

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Configure:
   - **App name**: IBM Orchestrate Test Generator
   - **Homepage URL**: Your application URL
   - **Webhook URL**: `https://your-domain.com/api/github/webhook/`
   - **Webhook secret**: Generate a secure random string
4. Set permissions:
   - Repository contents: Read & Write
   - Pull requests: Read & Write
   - Metadata: Read-only
5. Subscribe to events: Push, Pull request
6. Generate and download private key
7. Update `.env` with credentials

## API Endpoints

### GitHub Integration
- `POST /api/github/webhook/` - GitHub webhook receiver
- `GET /api/github/health/` - Health check

### AI Engine
- `POST /api/ai/generate/` - Generate tests for code
- `POST /api/ai/update/` - Update existing tests

### Insights
- `GET /api/insights/metrics/` - Overall metrics
- `GET /api/insights/test-health/<repo_id>/` - Repository test health
- `GET /api/insights/timeline/<repo_id>/` - Activity timeline
- `GET /api/insights/productivity/` - Productivity statistics
- `GET /api/insights/repos/` - List repositories
- `GET /api/insights/repos/<repo_id>/` - Repository details

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## Deployment

### Backend (Django + Celery)

```bash
# Build Docker image
docker build -f docker/Dockerfile.backend -t ibm-orchestrate-backend .

# Run with environment variables
docker run -p 8000:8000 --env-file .env ibm-orchestrate-backend
```

### Frontend (React)

```bash
# Build for production
cd frontend
npm run build

# Serve with nginx or deploy to Vercel/Netlify
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -U postgres -d ibm_orchestrate_db
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

### Celery Not Processing Tasks
```bash
# Check Celery worker is running
celery -A config inspect active

# Check Redis connection
celery -A config inspect ping
```

### Frontend API Connection Issues
- Verify `VITE_API_URL` in frontend/.env
- Check CORS settings in backend settings
- Ensure backend is running on correct port

## Architecture

```
┌─────────────┐
│   GitHub    │
│  Webhook    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Django    │────▶│    Celery    │
│   Backend   │     │    Worker    │
└──────┬──────┘     └──────┬───────┘
       │                   │
       │                   ▼
       │            ┌──────────────┐
       │            │  IBM WatsonX │
       │            │   (Granite)  │
       │            └──────────────┘
       │
       ▼
┌─────────────┐
│   React     │
│  Frontend   │
└─────────────┘
```

## Flow

1. **Code Push** → GitHub webhook triggers
2. **Webhook Handler** → Creates WebhookEvent, triggers Celery task
3. **Celery Worker** → Processes code changes
4. **AI Engine** → Calls IBM WatsonX to generate/update tests
5. **Database** → Stores CodeFile, TestFile, ChangeEvent
6. **Frontend** → Displays results in dashboard

## Support

For issues or questions:
- Check the logs: `docker-compose logs -f`
- Review the documentation
- Open an issue on GitHub

---

Made with Bob - IBM Orchestrate Team