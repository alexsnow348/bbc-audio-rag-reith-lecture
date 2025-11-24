"""
Configuration management for BBC Audio Scraper system.
Loads environment variables and provides centralized config access.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # Base directories
    BASE_DIR = Path(__file__).parent
    DOWNLOADS_DIR = BASE_DIR / os.getenv('DOWNLOADS_DIR', 'downloads')
    TRANSCRIPTS_DIR = BASE_DIR / os.getenv('TRANSCRIPTS_DIR', 'transcripts')
    VECTOR_DB_DIR = BASE_DIR / os.getenv('VECTOR_DB_DIR', 'data/chroma_db')
    PDF_DIR = BASE_DIR / os.getenv('PDF_DIR', 'pdfs')
    
    # API Keys
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    
    # Whisper Settings (FREE local transcription)
    WHISPER_MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')  # tiny, base, small, medium, large
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # RAG Settings
    CHUNK_SIZE = 1000  # Characters per chunk for vector store
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5  # Number of relevant chunks to retrieve
    
    # Google AI Settings
    GOOGLE_MODEL = 'gemini-flash-latest'  # Free tier model - latest stable Gemini Flash
    TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        cls.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        cls.PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GOOGLE_AI_API_KEY:
            print("⚠️  Warning: GOOGLE_AI_API_KEY not set. Chat functionality will not work.")
            print("   Get a free API key at: https://makersuite.google.com/app/apikey")
        
        cls.ensure_directories()
        return True

# Initialize on import
Config.validate()
