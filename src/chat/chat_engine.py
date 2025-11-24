"""
Chat engine with Google AI (Gemini) and RAG capabilities.
Provides conversational interface for querying transcripts.
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from config import Config
from src.utils.logger import setup_logger
from src.chat.vector_store import VectorStore

logger = setup_logger(__name__)

class ChatEngine:
    """
    AI chat engine with RAG for transcript querying.
    Uses Google's Gemini model (free tier available).
    """
    
    def __init__(self, vector_store: VectorStore = None):
        """
        Initialize chat engine.
        
        Args:
            vector_store: Optional VectorStore instance (creates new if None)
        """
        self.vector_store = vector_store or VectorStore()
        self.conversation_history = []
        self.model = None
        
        # Configure Google AI
        if Config.GOOGLE_AI_API_KEY:
            genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(Config.GOOGLE_MODEL)
            logger.info(f"Initialized chat engine with model: {Config.GOOGLE_MODEL}")
        else:
            logger.warning("Google AI API key not configured. Chat functionality disabled.")
    
    def is_ready(self) -> bool:
        """Check if chat engine is ready to use"""
        return self.model is not None
    
    def ask(self, question: str, use_rag: bool = True, n_context: int = None) -> Dict:
        """
        Ask a question and get an AI response.
        
        Args:
            question: User question
            use_rag: Whether to use RAG (retrieve context from transcripts)
            n_context: Number of context chunks to retrieve
        
        Returns:
            Dictionary with response and metadata
        """
        if not self.is_ready():
            return {
                'response': "Error: Google AI API key not configured. Please set GOOGLE_AI_API_KEY in .env file.",
                'sources': [],
                'error': True
            }
        
        try:
            # Get context from vector store if RAG is enabled
            context = ""
            sources = []
            
            if use_rag:
                n_context = n_context or Config.TOP_K_RESULTS
                search_results = self.vector_store.search(question, n_context)
                
                if search_results:
                    context = self.vector_store.get_context(question, n_context)
                    sources = [
                        {
                            'source': result['metadata'].get('source', 'Unknown'),
                            'chunk_index': result['metadata'].get('chunk_index', 0),
                        }
                        for result in search_results
                    ]
                    logger.info(f"Retrieved {len(sources)} context chunks")
            
            # Build prompt
            if context:
                prompt = f"""You are a helpful assistant that answers questions based on BBC audio programme transcripts.

Context from transcripts:
{context}

User question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, say so. Always cite which source(s) you're referencing."""
            else:
                prompt = f"""You are a helpful assistant for BBC audio programme transcripts.

User question: {question}

Note: No relevant transcript context was found. Please provide a general response or ask the user to be more specific."""
            
            # Generate response
            logger.info(f"Generating response for: {question[:50]}...")
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Add to conversation history
            self.conversation_history.append({
                'question': question,
                'response': response_text,
                'sources': sources,
            })
            
            logger.info("Response generated successfully")
            
            return {
                'response': response_text,
                'sources': sources,
                'context_used': bool(context),
                'error': False
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': f"Error generating response: {str(e)}",
                'sources': [],
                'error': True
            }
    
    def chat(self, message: str, use_rag: bool = True) -> str:
        """
        Simple chat interface (returns just the response text).
        
        Args:
            message: User message
            use_rag: Whether to use RAG
        
        Returns:
            Response text
        """
        result = self.ask(message, use_rag)
        return result['response']
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history.
        
        Returns:
            List of conversation turns
        """
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Cleared conversation history")
    
    def format_sources(self, sources: List[Dict]) -> str:
        """
        Format source citations for display.
        
        Args:
            sources: List of source dictionaries
        
        Returns:
            Formatted source string
        """
        if not sources:
            return "No sources cited."
        
        unique_sources = {}
        for source in sources:
            source_path = source.get('source', 'Unknown')
            if source_path not in unique_sources:
                unique_sources[source_path] = []
            unique_sources[source_path].append(source.get('chunk_index', 0))
        
        formatted = []
        for i, (source_path, chunks) in enumerate(unique_sources.items(), 1):
            from pathlib import Path
            source_name = Path(source_path).stem if source_path != 'Unknown' else 'Unknown'
            formatted.append(f"{i}. {source_name} (chunks: {', '.join(map(str, chunks))})")
        
        return "\n".join(formatted)
