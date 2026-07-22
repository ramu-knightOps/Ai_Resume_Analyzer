# Resume Analyzer

Resume Analyzer is a Streamlit application and lightweight HTTP API for evaluating resumes against a target job description. It extracts resume details, scores ATS coverage, identifies skill gaps, reviews bullet quality, and generates a PDF report.

## Features

- Resume PDF parsing with a deterministic fallback
- ATS-style section scoring and role-fit suggestions
- Resume-to-job-description skill gap analysis
- Evidence-backed JD requirement mapping with exact supporting resume lines
- Bullet improvement suggestions and interview preparation prompts
- PDF report generation
- Admin analytics backed by SQLite or PostgreSQL
- JSON API for reusing the analysis services

## Project layout

```text
.
├── backend/app/
│   ├── api/routes/                # HTTP route modules
│   ├── models/                    # Domain and persistence models
│   ├── schemas/                   # API request and response contracts
│   ├── services/                  # Resume analysis use cases
│   └── main.py                    # Backend server entry point
├── frontend/
│   ├── app.py                     # Streamlit frontend launcher
│   └── api_client.py              # HTTP connection to the backend
├── tests/                         # Unit and API integration tests
├── data/                          # Local runtime data (ignored except .gitkeep)
├── docs/                          # Screenshots and project reference material
├── requirements.txt               # Core dependencies
├── requirements/                  # Optional semantic and development extras
├── Dockerfile
├── start.sh
└── pyproject.toml
```

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Optional local embedding support:

```bash
pip install -r requirements/semantic.txt
```

Development tools:

```bash
pip install -r requirements/dev.txt
```

## Configuration

Copy the environment template and update only the values you need:

```bash
cp .env.example .env
```

SQLite works without PostgreSQL configuration. For PostgreSQL, provide all of `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.

Set either `ADMIN_CREDENTIALS` or the `ADMIN_USERNAME` and `ADMIN_PASSWORD` pair to enable the admin console.

## Run

Start the backend first:

```bash
python -m backend.app.main
```

Then, in a second terminal, start the Streamlit frontend:

```bash
streamlit run app.py
```

Or use the deployment entry point:

```bash
bash start.sh
```

The frontend sends resume analysis requests to `http://127.0.0.1:8001` by default. Set `BACKEND_API_URL` when the backend runs elsewhere.

Start the API directly on `http://127.0.0.1:8001`:

```bash
python -m backend.app.main
```

Available API endpoints:

- `GET /api/v1/health`
- `POST /api/v1/analyses`
- `POST /api/v1/analyses/bullet-quality`
- `POST /api/v1/analyses/jd-gap`
- `POST /api/v1/analyses/interview-prep`
- `POST /api/v1/reports/pdf`

## Test

```bash
coverage run --source=backend.app -m unittest discover -s tests -v
coverage report -m --fail-under=80
```

The current test suite covers the API, parsing, matching, evidence-backed requirement mapping, analysis, PDF fallback, and package structure.
It currently contains 35 tests and reaches 94% backend coverage.

## Deployment

The included `Dockerfile`, `nixpacks.toml`, and `start.sh` are ready for container or Railway-style deployments. Persist `data/` only for local prototypes; use PostgreSQL for shared deployment data.

## License

See [LICENSE](LICENSE).
