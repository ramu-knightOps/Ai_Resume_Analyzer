# ATS Resume Analyzer

An intelligent resume analysis platform that combines hybrid resume parsing, semantic matching, ATS-style scoring, JD gap detection, bullet-quality feedback, interview prep, and PDF reporting in one workflow. 📄

Built with Streamlit and Python, the project is designed to help candidates understand how well their resume matches a target role and what to improve next. It also includes a lightweight API layer and an upgraded admin analytics console for monitoring usage and feedback.

## Highlights ✨

- Hybrid parser that reduces dependence on `pyresparser`
- Embedding-based resume-to-JD matching with vector-style semantic scoring
- Canonical skill normalization and resume-text evidence recovery
- Section-level ATS scoring with grouped category bars
- Bullet-quality checker with rewrite suggestions
- Resume-to-JD gap explainer across `Skills`, `Tools`, `Domain`, and `Evidence`
- Interview prep question generation from resume + JD context
- Downloadable PDF analysis report
- Admin Console v2 with cleaner visual analytics
- REST API for reusable analysis endpoints

## How It Works 🧠

1. A resume PDF is uploaded and converted into raw text.
2. A hybrid parser extracts name, contact info, degrees, sections, and skills.
3. Resume skills are normalized against a skill ontology with aliases.
4. Resume evidence and JD text are compared using semantic matching and fallback heuristics.
5. The app produces ATS scorecards, role-fit suggestions, gap insights, and targeted recommendations.

## Feature Set

### Candidate Experience

- Resume parsing from PDF uploads
- Skill recovery from parser output and raw resume text
- ATS-style section scoring with grouped visual categories
- Semantic role matching against curated role profiles
- Priority gap analysis from JD text
- Recovered semantic evidence display
- Bullet-strength review with suggestions
- Interview preparation questions
- Recommended courses and learning resources
- PDF report export

### Admin Experience

- Secure admin login via environment variables
- Executive metrics for processed profiles and feedback pulse
- Role, geography, and score analytics
- Feedback stream and record tables
- Candidate data export

### API

- Health check endpoint
- Full resume analysis endpoint
- Bullet-quality endpoint
- JD gap endpoint
- Interview-prep endpoint
- PDF report generation endpoint

## Project Structure 🗂️

```text
AI-Resume-Analyzer/
├── App/
│   ├── App.py
│   ├── analysis_data.py
│   ├── api_server.py
│   ├── parser_utils.py
│   ├── matching_utils.py
│   ├── resume_analysis_core.py
│   ├── ui_styles.py
│   ├── Courses.py
│   └── requirements.txt
├── pyresparser/
├── screenshots/
├── tests/
└── README.md
```

## Tech Stack 🛠️

- Python
- Streamlit
- Plotly
- PostgreSQL with `psycopg2`
- `pdfminer3`
- `sentence-transformers`
- `python-dotenv`
- optional `pyresparser` augmentation

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ramu-knightOps/Ai_Resume_Analyzer.git
cd Ai_Resume_Analyzer/AI-Resume-Analyzer
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
cd App
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Configure environment variables

Create `App/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
HF_TOKEN=optional_huggingface_token
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
ADMIN_CREDENTIALS=admin_one:password_one,admin_two:password_two
```

## Run the App 🚀

From the `App` directory:

```bash
streamlit run App.py
```

## Run the API

From the `App` directory:

```bash
python api_server.py
```

Base URL:

```text
http://127.0.0.1:8001
```

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/analyses`
- `POST /api/v1/analyses/bullet-quality`
- `POST /api/v1/analyses/jd-gap`
- `POST /api/v1/analyses/interview-prep`
- `POST /api/v1/reports/pdf`

### Example Request

```bash
curl -X POST http://127.0.0.1:8001/api/v1/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Asha",
    "resume_text": "Built APIs with FastAPI, Docker, PostgreSQL, and analytics dashboards.",
    "resume_skills": ["Python", "SQL", "Docker"],
    "job_description": "Looking for a backend engineer with FastAPI, Docker, authentication, and fintech API experience."
  }'
```

## Testing ✅

From the project root:

```bash
python3 -m unittest tests/test_matching_utils.py tests/test_parser_utils.py
```

To validate syntax:

```bash
python3 -m py_compile App/App.py App/parser_utils.py App/matching_utils.py App/resume_analysis_core.py
```

## Notes

- The parser now uses a hybrid strategy: custom text extraction first, optional `pyresparser` support second.
- Semantic matching works best when the embedding model can load successfully.
- Uploaded resumes and local env files should remain untracked.
- Admin console access should be configured locally through `ADMIN_CREDENTIALS`, or through the fallback `ADMIN_USERNAME` and `ADMIN_PASSWORD` pair.

## Git Hygiene

This repo ignores local-only development files such as:

- virtual environments
- uploaded resumes
- Python caches
- local `.env` files
- macOS metadata files

If any of those were tracked earlier, remove them once with:

```bash
git rm -r --cached App/Uploaded_Resumes App/__pycache__ tests/__pycache__ pyresparser/__pycache__
git rm --cached .DS_Store
```

## Roadmap 📌

- Improve section-aware project and experience extraction
- Add stronger bullet-level impact scoring
- Expand role coverage and recommendation quality further
- Add evaluation datasets for resume/JD matching quality

## License

This project is distributed under the license included in [LICENSE](/Users/raghusmac/Documents/ai_reseme_cloned_version/AI-Resume-Analyzer/LICENSE).
