"""
Chat engine with Google AI (Gemini) and RAG capabilities.
Provides conversational interface for querying transcripts.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
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
        
        # Session management
        self.current_session_id = None
        self.session_start_time = None
        
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
    
    def ask(self, question: str, use_rag: bool = True, n_context: int = None, source_files: List[str] = None) -> Dict:
        """
        Ask a question and get an AI response.
        
        Args:
            question: User question
            use_rag: Whether to use RAG (retrieve context from transcripts)
            n_context: Number of context chunks to retrieve
            source_files: Optional list of source files to filter context by
        
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
                search_results = self.vector_store.search_filtered(question, source_files, n_context)
                
                if search_results:
                    context = self.vector_store.get_context(question, n_context, source_files)
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
                scope_info = ""
                if source_files:
                    from pathlib import Path
                    file_names = [Path(f).stem for f in source_files]
                    scope_info = f"\n\nNote: This answer is based only on the following selected transcripts: {', '.join(file_names)}"
                
                prompt = f"""You are a helpful assistant that answers questions based on BBC audio programme transcripts.

Context from transcripts:
{context}

User question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, say so. Always cite which source(s) you're referencing.{scope_info}"""
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
    
    # ========================================================================
    # Session Management Methods
    # ========================================================================
    
    def start_new_session(self) -> str:
        """
        Start a new chat session.
        
        Returns:
            Session ID
        """
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.conversation_history = []
        logger.info(f"Started new chat session: {self.current_session_id}")
        return self.current_session_id
    
    def save_session(self, session_name: str = None):
        """
        Save current session to disk.
        
        Args:
            session_name: Optional custom name for the session
        """
        if not self.current_session_id:
            self.start_new_session()
        
        session_data = {
            'session_id': self.current_session_id,
            'session_name': session_name or f"Chat {self.session_start_time.strftime('%Y-%m-%d %H:%M')}",
            'start_time': self.session_start_time.isoformat() if self.session_start_time else datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'message_count': len(self.conversation_history),
            'conversation': self.conversation_history
        }
        
        session_file = Config.CHAT_HISTORY_DIR / f"{self.current_session_id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved session to {session_file}")
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a previous session.
        
        Args:
            session_id: ID of the session to load
        
        Returns:
            True if loaded successfully, False otherwise
        """
        session_file = Config.CHAT_HISTORY_DIR / f"{session_id}.json"
        
        if not session_file.exists():
            logger.error(f"Session file not found: {session_file}")
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.current_session_id = session_data['session_id']
            self.session_start_time = datetime.fromisoformat(session_data['start_time'])
            self.conversation_history = session_data['conversation']
            
            logger.info(f"Loaded session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    def list_sessions(self) -> List[Dict]:
        """
        List all available chat sessions.
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        
        for session_file in Config.CHAT_HISTORY_DIR.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Create preview from first message
                preview = ""
                if session_data.get('conversation'):
                    first_msg = session_data['conversation'][0].get('question', '')
                    preview = first_msg[:100] + "..." if len(first_msg) > 100 else first_msg
                
                sessions.append({
                    'session_id': session_data['session_id'],
                    'session_name': session_data.get('session_name', 'Unnamed Session'),
                    'start_time': session_data['start_time'],
                    'last_updated': session_data.get('last_updated', session_data['start_time']),
                    'message_count': session_data.get('message_count', 0),
                    'preview': preview
                })
            except Exception as e:
                logger.error(f"Error reading session file {session_file}: {e}")
        
        # Sort by last updated (most recent first)
        sessions.sort(key=lambda x: x['last_updated'], reverse=True)
        return sessions
    
    def export_session(self, session_id: str, format: str = 'txt') -> Optional[Path]:
        """
        Export a session to a file.
        
        Args:
            session_id: ID of the session to export
            format: Export format ('txt', 'md', or 'json')
        
        Returns:
            Path to exported file or None if failed
        """
        session_file = Config.CHAT_HISTORY_DIR / f"{session_id}.json"
        
        if not session_file.exists():
            logger.error(f"Session not found: {session_id}")
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            export_dir = Config.CHAT_HISTORY_DIR / "exports"
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format == 'json':
                export_path = export_dir / f"chat_{timestamp}.json"
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            elif format == 'md':
                export_path = export_dir / f"chat_{timestamp}.md"
                content = self._format_session_as_markdown(session_data)
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            else:  # txt
                export_path = export_dir / f"chat_{timestamp}.txt"
                content = self._format_session_as_text(session_data)
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"Exported session to {export_path}")
            return export_path
        
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            return None
    
    def _format_session_as_text(self, session_data: Dict) -> str:
        """Format session as plain text"""
        lines = []
        lines.append(f"Chat Session: {session_data.get('session_name', 'Unnamed')}")
        lines.append(f"Date: {session_data['start_time']}")
        lines.append(f"Messages: {session_data.get('message_count', 0)}")
        lines.append("=" * 80)
        lines.append("")
        
        for turn in session_data.get('conversation', []):
            lines.append(f"Q: {turn['question']}")
            lines.append(f"A: {turn['response']}")
            lines.append("-" * 80)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_session_as_markdown(self, session_data: Dict) -> str:
        """Format session as markdown"""
        lines = []
        lines.append(f"# Chat Session: {session_data.get('session_name', 'Unnamed')}")
        lines.append(f"**Date:** {session_data['start_time']}")
        lines.append(f"**Messages:** {session_data.get('message_count', 0)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, turn in enumerate(session_data.get('conversation', []), 1):
            lines.append(f"## Message {i}")
            lines.append(f"**Question:** {turn['question']}")
            lines.append("")
            lines.append(f"**Answer:** {turn['response']}")
            lines.append("")
            if turn.get('sources'):
                lines.append("**Sources:**")
                for source in turn['sources']:
                    lines.append(f"- {source.get('source', 'Unknown')}")
                lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: ID of the session to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        session_file = Config.CHAT_HISTORY_DIR / f"{session_id}.json"
        
        try:
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_id}")
                return True
            else:
                logger.warning(f"Session file not found: {session_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
