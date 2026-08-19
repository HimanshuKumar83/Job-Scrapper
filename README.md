# JobPulse — Resilient Job Data Ingestion Platform

## Overview
JobPulse is a lightweight ingestion platform that collects public job listings from a legitimate source, normalizes the data, stores it in PostgreSQL, and exposes the information through a FastAPI API and a React dashboard. The design emphasizes resilience: retries, rate limiting, circuit-breaking, source health tracking, fallback ingestion, and structured observability.

## Problem Statement
A reliable ingestion system must handle real-world unpredictability: rate limits, transient HTTP failures, malformed payloads, duplicate listings, schema drift, and source outages. The platform must continue working without violating site terms or bypassing authentication or bot protections.

## Architecture
```mermaid
flowchart TD
    A[Public Job Source] --> B[Source Adapter]
    B --> C[Rate Limiter]
    C --> D[HTTP Client]
    D --> E[Retry Policy]
    E --> F[Response Validator]
    F --> G[Parser]
    G --> H[Normalizer]
    H --> I[Deduplication]
    I --> J[PostgreSQL]
    D --> K[Source Health Monitor]
    E --> K
    K --> L[Circuit Breaker]
    L --> M[Fallback Source]
    M --> B
    J --> N[FastAPI]
    N --> O[React Dashboard]
```

## Features
- Public Jobicy JSON API adapter with a Remote OK JSON API fallback
- Controlled sandbox adapter for deterministic failure demonstrations
- Rate limiting and retry/backoff
- HTTP 429 handling with respect for Retry-After
- Circuit breaker and degraded-source state
- Deduplication by source + external_id and content hash
- PostgreSQL persistence with normalized model
- FastAPI endpoints for health, jobs, metrics, and ingestion control
- Dashboard for status, metrics, source health, and recent jobs
- Safe failure simulation via sandbox scenarios

## Tech Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Ingestion: httpx, feedparser, BeautifulSoup, APScheduler
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Testing: pytest

## Project Structure
```text
jobpulse/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── ingestion/
│   │   ├── services/
│   │   ├── sources/
│   │   ├── schemas/
│   │   ├── config.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── DECISIONS.md
└── docs/
```

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env
```

## Environment Variables
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/jobpulse
PRIMARY_SOURCE=jobicy
FALLBACK_SOURCE=remoteok
INGESTION_INTERVAL_MINUTES=30
REQUESTS_PER_MINUTE=30
MIN_REQUEST_INTERVAL_SECONDS=2
MAX_RETRIES=3
BACKOFF_BASE_SECONDS=1
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_COOLDOWN_SECONDS=60
FRONTEND_ORIGIN=http://localhost:5173
SANDBOX_SCENARIO=normal
```

## Running Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Running Frontend
```bash
cd frontend
npm install
npm run dev
```

## Running with Docker
```bash
docker compose up --build
```

## Running Tests
```bash
cd backend
pytest -q
```

## API Documentation
The API is available via FastAPI Swagger at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Ingestion Flow
1. Select a source adapter
2. Rate limit and authenticate requests as needed
3. Fetch data from the public endpoint
4. Validate status and response shape
5. Parse and normalize jobs
6. Deduplicate by external_id and content hash
7. Persist valid records to PostgreSQL
8. Update source health and metrics

## Resilience Strategy
- Retry only transient HTTP and network failures
- Respect 429 and Retry-After headers
- Exponential backoff with conservative defaults
- Circuit breaker for degraded source protection
- Fallback source after repeated failure
- Structured logs and ingestion run metrics

## Failure Simulation
Use the sandbox source to demo resilience by setting `FALLBACK_SOURCE=sandbox`, then choose a scenario:
```bash
export SANDBOX_SCENARIO=rate_limited
```
Supported modes include: normal, rate_limited, timeout, server_error, malformed_response, empty_response.

## Deployment
1. Deploy the backend service from `backend/` to Render or Railway using the Dockerfile.
2. Provision managed PostgreSQL and set `DATABASE_URL` to its private or public connection URL.
3. Set `PRIMARY_SOURCE=jobicy`, `FALLBACK_SOURCE=remoteok`, and `CORS_ORIGINS` to the deployed frontend URL.
4. Deploy `frontend/` to Vercel and set `VITE_API_URL` to the deployed backend URL.
5. Verify `/health`, `/docs`, and `POST /api/ingestion/run` on the deployed backend.

The Remote OK public API requests that consumers link back to Remote OK and identify it as a source; the dashboard preserves the source name and listing URLs for that purpose. Never commit production credentials.

## Responsible Scraping / ToS Boundary
This project intentionally does not bypass CAPTCHA, authentication, access controls, anti-bot protections, or source restrictions. It uses a legitimate public job feed or a controlled sandbox, and the architecture is designed to degrade gracefully instead of evading blocks.

## Screenshots
Add screenshots here once the app is running locally.

## Future Improvements
- Add durable task queue with scheduled workers
- Expand adapters for additional public job feeds
- Improve metrics dashboards and source drift detection
- Add per-source configuration in the admin UI
