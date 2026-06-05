# College Admin Collaboration Copilot

An AI-powered college administration assistant built with FastAPI. The copilot answers student policy questions from college PDF documents, searches student/project/research datasets, recommends students for requirements, creates complaint tickets, and supports a Twilio WhatsApp webhook.

## DEMO 
 You Tube - https://www.youtube.com/watch?v=klP66BOgKHQ

## Features

- Policy Q&A using RAG over college administration PDFs
- Semantic search over projects, internships, hackathons, certifications, and research-paper datasets
- Student matching and 360-degree student profile endpoints
- Complaint ticket creation and ticket lookup
- Twilio WhatsApp webhook integration
- Simple browser UI served from `ui.html`
- FAISS vector indexes generated from local PDF and CSV data

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn
- SQLAlchemy with SQLite fallback or PostgreSQL via `DATABASE_URL`
- Sentence Transformers (`all-MiniLM-L6-v2`) for embeddings
- FAISS for vector search
- Groq API for LLM answer generation and intent classification
- Twilio webhook support for WhatsApp

## Project Structure

```text
college_copilot/
  app/
    api/             FastAPI route modules
    database/        SQLAlchemy session setup
    datasets/        CSV dataset ingestion, search, and analytics
    intelligence/    Student profile, recommendations, and portfolio logic
    rag/             PDF loading, chunking, embedding, retrieval, and generation
    router/          Intent classification
    tickets/         Ticket models and service layer
  config/            Dataset configuration
  data/
    csv/             CSV datasets
    pdfs/            College policy/admin PDFs
    vector_store/    Generated FAISS indexes and metadata
  scripts/           Ingestion scripts
  tests/             Pytest test suite
  ui.html            Frontend UI
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/SandeshAwate6055/College-Admin-Collaboration-Copilot.git
cd College-Admin-Collaboration-Copilot
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create your environment file.

```bash
copy .env.example .env
```

Then update `.env` with your keys and database URL if needed.

## Environment Variables

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=sqlite:///./college_copilot.db
TWILIO_ACCOUNT_SID=optional_twilio_account_sid
TWILIO_AUTH_TOKEN=optional_twilio_auth_token
TWILIO_WHATSAPP_FROM=optional_twilio_whatsapp_number
DATASETS_CONFIG=config/datasets.json
```

If `DATABASE_URL` is not provided, the app uses a local SQLite database named `college_copilot.db`.

## Data and Indexing

Place policy documents in `data/pdfs/` and CSV datasets in `data/csv/`.

Build the FAISS indexes before asking policy or dataset questions:

```bash
python scripts/ingest_all.py
```

This creates generated index files under `data/vector_store/`.

## Run the App

```bash
uvicorn app.main:app --reload
```

Open:

- UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Useful Endpoints

- `POST /chat` - classify a message, answer policy questions, search datasets, or create tickets
- `GET /tickets/{student_id}` - list complaint tickets for a student
- `GET /api/search/projects?q=...` - semantic project search
- `GET /api/search/papers?q=...` - semantic research-paper search
- `GET /api/match/students?requirement=...` - match students to a requirement
- `GET /api/datasets` - list configured datasets
- `POST /api/datasets/ingest` - ingest all configured CSV datasets
- `GET /api/student/{prn_or_roll_no}/profile` - dataset-backed student profile
- `GET /api/intelligence/student/{prn_or_roll_no}` - student 360 profile
- `POST /api/intelligence/recommend` - student recommendations
- `POST /whatsapp` - Twilio WhatsApp webhook

Example chat request:

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"student_id\":\"S001\",\"message\":\"What is the CGPA calculation rule?\"}"
```

## PostgreSQL with Docker

The included `docker-compose.yml` starts a PostgreSQL database:

```bash
docker compose up -d
```

Use this database URL in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/college_copilot
```

## Tests

```bash
pytest
```

## Notes

- `.env`, virtual environments, database files, logs, generated FAISS indexes, and local tunneling binaries are intentionally ignored.
- Keep only source files, tests, documentation, PDF/CSV source data, and configuration in Git.
- Re-run `python scripts/ingest_all.py` whenever source PDFs or CSV datasets change.
