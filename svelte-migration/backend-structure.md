# Backend API Structure

This will contain the FastAPI backend for the BBC Audio Scraper.

## Directory Structure (Planned)

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── downloads.py     # Download endpoints
│   │   ├── transcripts.py   # Transcription endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   ├── history.py       # History endpoints
│   │   └── files.py         # File serving endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Pydantic request models
│   │   └── responses.py     # Pydantic response models
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py          # CORS configuration
│       └── error_handler.py # Error handling
├── src/                     # Reuse existing Python modules
├── tests/
│   ├── test_downloads.py
│   ├── test_transcripts.py
│   ├── test_chat.py
│   └── test_history.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints (Planned)

See [MIGRATION_PLAN.md](../MIGRATION_PLAN.md#key-endpoints) for detailed endpoint specifications.

## Setup Instructions

Coming soon...
