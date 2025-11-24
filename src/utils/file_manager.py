"""
File management utilities for organizing downloads, transcripts, and metadata.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileManager:
    """Manages file operations for audio files and transcripts"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    @staticmethod
    def get_file_hash(filepath: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            filepath: Path to file
        
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def save_metadata(filepath: Path, metadata: Dict[str, Any]):
        """
        Save metadata as JSON file alongside the main file.
        
        Args:
            filepath: Path to main file
            metadata: Dictionary of metadata
        """
        metadata_path = filepath.with_suffix('.json')
        metadata['file_hash'] = FileManager.get_file_hash(filepath)
        metadata['created_at'] = datetime.now().isoformat()
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to {metadata_path}")
    
    @staticmethod
    def load_metadata(filepath: Path) -> Dict[str, Any]:
        """
        Load metadata from JSON file.
        
        Args:
            filepath: Path to main file
        
        Returns:
            Metadata dictionary or empty dict if not found
        """
        metadata_path = filepath.with_suffix('.json')
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def list_audio_files() -> list:
        """
        List all audio files in downloads directory.
        
        Returns:
            List of audio file paths
        """
        audio_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.flac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(Config.DOWNLOADS_DIR.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    @staticmethod
    def list_transcripts() -> list:
        """
        List all transcript files.
        
        Returns:
            List of transcript file paths
        """
        return sorted(Config.TRANSCRIPTS_DIR.glob('*.txt'))
