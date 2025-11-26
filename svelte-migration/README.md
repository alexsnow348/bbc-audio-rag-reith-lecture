# Svelte Migration Directory

This directory contains the planning and implementation for migrating the BBC Audio Scraper from Gradio to **Svelte 5 + Bit UI + Tailwind CSS**.

## Contents

- **[MIGRATION_PLAN.md](./MIGRATION_PLAN.md)** - Comprehensive migration plan with architecture, phases, and timeline
- **backend/** - FastAPI backend (to be created)
- **frontend/** - Svelte frontend (to be created)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- Docker (optional, for containerized deployment)

### Backend Setup (FastAPI)

```bash
# Create backend directory
mkdir -p backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-multipart pydantic

# Run development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Svelte)

```bash
# Create Svelte project
npm create vite@latest frontend -- --template svelte-ts
cd frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install bits-ui lucide-svelte @tanstack/svelte-query axios

# Initialize Tailwind
npx tailwindcss init -p

# Run development server
npm run dev
```

## Architecture

```
┌─────────────────────┐
│  Svelte Frontend    │
│  (Port 5173)        │
│  - Bit UI           │
│  - Tailwind CSS     │
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (Port 8000)        │
│  - Whisper AI       │
│  - Vector Store     │
│  - Google AI        │
└─────────────────────┘
```

## Migration Status

- [x] Planning complete
- [ ] Backend API implementation
- [ ] Frontend setup
- [ ] Component development
- [ ] Integration testing
- [ ] Deployment

## Resources

- [Svelte Documentation](https://svelte.dev/)
- [Bit UI Components](https://www.bits-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Current Gradio App

The current working Gradio application with history features is running in the parent directory. You can continue using it while the migration is in progress.

Access at: http://localhost:7860
