"""
FastAPI Backend for BBC Audio Scraper
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import downloads, transcripts, chat, history, files

app = FastAPI(
    title="BBC Audio Scraper API",
    description="Backend API for BBC Audio Scraper with transcription and chat capabilities",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(transcripts.router, prefix="/api/transcripts", tags=["transcripts"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(files.router, prefix="/api/files", tags=["files"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BBC Audio Scraper API",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
