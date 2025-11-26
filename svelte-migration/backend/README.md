# BBC Audio Scraper - FastAPI Backend

Backend API for the BBC Audio Scraper application.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Downloads
- `POST /api/downloads/rss` - Download from RSS feed
- `POST /api/downloads/iplayer` - Download with get_iplayer
- `GET /api/downloads` - List downloaded files

### Transcripts
- `POST /api/transcripts/transcribe` - Transcribe single file
- `POST /api/transcripts/batch` - Transcribe all files
- `GET /api/transcripts` - List transcripts
- `GET /api/transcripts/{id}` - Get transcript
- `POST /api/transcripts/{id}/export` - Export to PDF

### Chat
- `POST /api/chat/load-vectors` - Load transcripts to vector store
- `POST /api/chat/message` - Send chat message
- `POST /api/chat/sessions` - Create session
- `GET /api/chat/sessions` - List sessions
- `GET /api/chat/sessions/{id}` - Get session
- `DELETE /api/chat/sessions/{id}` - Delete session
- `POST /api/chat/sessions/{id}/export` - Export session

### History
- `GET /api/history/listening` - Get listening history
- `POST /api/history/listening` - Mark content accessed
- `PUT /api/history/listening/{name}` - Mark as completed
- `GET /api/history/stats` - Get statistics

### Files
- `GET /api/files/audio` - List audio files
- `GET /api/files/audio/{id}` - Stream audio
- `GET /api/files/pdfs` - List PDFs
- `GET /api/files/pdfs/{id}` - Get PDF

## Development

The backend reuses the existing Python modules from the parent directory:
- `src/scraper/` - RSS and get_iplayer functionality
- `src/transcription/` - Whisper transcription
- `src/chat/` - Vector store and chat engine
- `src/utils/` - File management and utilities

## Next Steps

1. Implement TODO items in route handlers
2. Add proper error handling
3. Add request validation
4. Add authentication (optional)
5. Add rate limiting
6. Add logging
7. Write tests
