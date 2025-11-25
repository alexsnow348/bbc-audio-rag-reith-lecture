"""
Vector store for transcript storage and semantic search using ChromaDB.
Enables RAG (Retrieval-Augmented Generation) for chat functionality.
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
from config import Config
from src.utils.logger import setup_logger
from src.utils.file_manager import FileManager

logger = setup_logger(__name__)

class VectorStore:
    """
    Vector database for storing and searching transcripts.
    Uses ChromaDB with built-in embeddings (free, no API needed).
    """
    
    def __init__(self, collection_name: str = "transcripts"):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self.file_manager = FileManager()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(Config.VECTOR_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "BBC audio transcripts"}
        )
        
        logger.info(f"Initialized vector store with collection: {collection_name}")
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def add_transcript(self, transcript_path: Path, metadata: Dict = None) -> int:
        """
        Add a transcript to the vector store.
        
        Args:
            transcript_path: Path to transcript file
            metadata: Optional metadata dictionary
        
        Returns:
            Number of chunks added
        """
        transcript_path = Path(transcript_path)
        
        if not transcript_path.exists():
            logger.error(f"Transcript not found: {transcript_path}")
            return 0
        
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Load metadata
        file_metadata = self.file_manager.load_metadata(transcript_path)
        if metadata:
            file_metadata.update(metadata)
        
        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Split transcript into {len(chunks)} chunks")
        
        # Prepare data for ChromaDB
        ids = [f"{transcript_path.stem}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                'source': str(transcript_path),
                'chunk_index': i,
                'total_chunks': len(chunks),
                **file_metadata
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks from {transcript_path.name} to vector store")
        return len(chunks)
    
    def add_all_transcripts(self) -> int:
        """
        Add all transcripts from the transcripts directory.
        
        Returns:
            Total number of chunks added
        """
        transcripts = self.file_manager.list_transcripts()
        logger.info(f"Found {len(transcripts)} transcripts to add")
        
        total_chunks = 0
        for transcript_path in transcripts:
            chunks_added = self.add_transcript(transcript_path)
            total_chunks += chunks_added
        
        logger.info(f"Added {total_chunks} total chunks from {len(transcripts)} transcripts")
        return total_chunks
    
    def search(self, query: str, n_results: int = None) -> List[Dict]:
        """
        Search for relevant transcript chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of result dictionaries with text and metadata
        """
        n_results = n_results or Config.TOP_K_RESULTS
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None,
                })
        
        logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
        return formatted_results
    
    def search_filtered(self, query: str, source_files: List[str] = None, n_results: int = None) -> List[Dict]:
        """
        Search for relevant transcript chunks, optionally filtered by source files.
        
        Args:
            query: Search query
            source_files: Optional list of source file paths to filter by
            n_results: Number of results to return
        
        Returns:
            List of result dictionaries with text and metadata
        """
        n_results = n_results or Config.TOP_K_RESULTS
        
        # Build where clause for filtering
        where_clause = None
        if source_files:
            # Filter by source files
            where_clause = {
                "$or": [{"source": {"$eq": str(source)}} for source in source_files]
            }
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None,
                })
        
        logger.info(f"Found {len(formatted_results)} filtered results for query: {query[:50]}...")
        return formatted_results
    
    def get_context(self, query: str, n_results: int = None, source_files: List[str] = None) -> str:
        """
        Get context string for LLM from search results.
        
        Args:
            query: Search query
            n_results: Number of results to include
            source_files: Optional list of source files to filter by
        
        Returns:
            Formatted context string
        """
        results = self.search_filtered(query, source_files, n_results)
        
        if not results:
            return "No relevant information found in the transcripts."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'Unknown')
            source_name = Path(source).stem if source != 'Unknown' else 'Unknown'
            context_parts.append(f"[Source {i}: {source_name}]\n{result['text']}\n")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear all data from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "BBC audio transcripts"}
        )
        logger.info("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with stats
        """
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'database_path': str(Config.VECTOR_DB_DIR),
        }
