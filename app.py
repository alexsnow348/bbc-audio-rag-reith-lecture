"""
Main Gradio application for BBC Audio Scraper & Chat System.
Provides web interface for downloading, transcribing, and chatting with BBC audio.
"""

import gradio as gr
import base64
from pathlib import Path
from config import Config
from src.scraper.rss_scraper import RSScraper
from src.scraper.get_iplayer_wrapper import GetIPlayerWrapper
from src.transcription.transcriber import WhisperTranscriber
from src.transcription.audio_processor import AudioProcessor
from src.chat.vector_store import VectorStore
from src.chat.chat_engine import ChatEngine
from src.utils.file_manager import FileManager
from src.utils.pdf_generator import PDFGenerator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize components
rss_scraper = RSScraper()
iplayer = GetIPlayerWrapper()
transcriber = WhisperTranscriber()
audio_processor = AudioProcessor()
vector_store = VectorStore()
chat_engine = ChatEngine(vector_store)
file_manager = FileManager()
pdf_generator = PDFGenerator()

# ============================================================================
# TAB 1: DOWNLOAD AUDIO
# ============================================================================

def download_from_rss(feed_url: str, limit: int):
    """Download episodes from RSS feed"""
    try:
        if not feed_url:
            return "❌ Please enter an RSS feed URL"
        
        limit = int(limit) if limit else None
        files = rss_scraper.download_episodes(feed_url, limit)
        
        if files:
            return f"✅ Downloaded {len(files)} episode(s):\n" + "\n".join([f"- {f.name}" for f in files])
        else:
            return "❌ No episodes downloaded. Check the feed URL."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def download_with_iplayer(query: str):
    """Search and download with get_iplayer"""
    try:
        if not query:
            return "❌ Please enter a search query or URL"
        
        # Check if it's a URL or search query
        if query.startswith('http'):
            success = iplayer.download_by_url(query)
            if success:
                return f"✅ Downloaded from URL: {query}"
            else:
                return "❌ Download failed. Check logs for details."
        else:
            # Search for programmes
            results = iplayer.search(query)
            if not results:
                return f"❌ No programmes found for: {query}"
            
            # Show first 5 results
            output = f"Found {len(results)} programme(s):\n\n"
            for i, prog in enumerate(results[:5], 1):
                output += f"{i}. {prog['name']} - {prog['episode']}\n"
                output += f"   PID: {prog['pid']}\n\n"
            
            output += "\n💡 To download, use the PID with format: pid:<PID>"
            return output
    except Exception as e:
        return f"❌ Error: {str(e)}"

def list_downloads():
    """List downloaded audio files"""
    files = file_manager.list_audio_files()
    if files:
        return "\n".join([f"📁 {f.name}" for f in files])
    return "No audio files found"

def get_popular_feeds():
    """Get list of popular BBC feeds"""
    feeds = rss_scraper.list_available_feeds()
    output = "📻 Popular BBC Podcast Feeds:\n\n"
    for name, url in feeds.items():
        output += f"**{name.replace('_', ' ').title()}**\n{url}\n\n"
    return output

# ============================================================================
# TAB 2: TRANSCRIBE
# ============================================================================

def transcribe_file(audio_file, model_size: str, language: str):
    """Transcribe a single audio file"""
    try:
        if not audio_file:
            return "❌ Please select an audio file", ""
        
        # Update model if changed
        if model_size != transcriber.model_size:
            transcriber.model_size = model_size
            transcriber.model = None  # Force reload
        
        # Transcribe
        transcript_path = transcriber.transcribe_and_save(Path(audio_file), language)
        
        if transcript_path:
            # Read transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            return f"✅ Transcription complete!\nSaved to: {transcript_path.name}", transcript_text
        else:
            return "❌ Transcription failed", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

def transcribe_all(model_size: str, language: str):
    """Transcribe all audio files"""
    try:
        audio_files = file_manager.list_audio_files()
        if not audio_files:
            return "❌ No audio files found to transcribe"
        
        # Update model if changed
        if model_size != transcriber.model_size:
            transcriber.model_size = model_size
            transcriber.model = None
        
        transcripts = transcriber.batch_transcribe(audio_files, language)
        
        return f"✅ Transcribed {len(transcripts)}/{len(audio_files)} files successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def list_transcripts():
    """List all transcripts"""
    transcripts = file_manager.list_transcripts()
    if transcripts:
        return "\n".join([f"📄 {t.name}" for t in transcripts])
    return "No transcripts found"

def load_transcript(transcript_name: str):
    """Load a transcript for viewing"""
    try:
        transcript_path = Config.TRANSCRIPTS_DIR / transcript_name
        if transcript_path.exists():
            with open(transcript_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "Transcript not found"
    except Exception as e:
        return f"Error: {str(e)}"

def export_transcript_to_pdf(transcript_name: str):
    """Export a single transcript to PDF"""
    try:
        if not transcript_name:
            return "❌ Please select a transcript", None
        
        transcript_path = Config.TRANSCRIPTS_DIR / transcript_name
        if not transcript_path.exists():
            return "❌ Transcript not found", None
        
        # Generate PDF
        pdf_path = pdf_generator.generate_pdf(transcript_path)
        
        return f"✅ PDF generated successfully!\nSaved to: {pdf_path.name}", str(pdf_path)
    except Exception as e:
        return f"❌ Error: {str(e)}", None

def export_all_transcripts_to_pdf():
    """Export all transcripts to PDF"""
    try:
        transcripts = file_manager.list_transcripts()
        if not transcripts:
            return "❌ No transcripts found to export"
        
        pdf_paths = pdf_generator.batch_generate_pdfs()
        
        if pdf_paths:
            return f"✅ Generated {len(pdf_paths)} PDF(s) successfully!\n\nPDFs saved in: pdfs/"
        else:
            return "❌ No PDFs were generated"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ============================================================================
# TAB 3: PDF READER
# ============================================================================

def get_available_content():
    """Get list of available audio files and their corresponding PDFs/transcripts"""
    audio_files = file_manager.list_audio_files()
    content_list = []
    
    for audio_file in audio_files:
        # Get base name without extension
        base_name = audio_file.stem
        
        # Check for corresponding transcript and PDF
        transcript_path = Config.TRANSCRIPTS_DIR / f"{base_name}_transcript.txt"
        pdf_path = Config.PDF_DIR / f"{base_name}_transcript.pdf"
        
        if transcript_path.exists():
            content_list.append({
                'name': base_name,
                'audio': str(audio_file),
                'transcript': str(transcript_path) if transcript_path.exists() else None,
                'pdf': str(pdf_path) if pdf_path.exists() else None
            })
    
    return content_list

def load_content_for_reading(content_name: str):
    """Load audio and PDF for a selected content"""
    try:
        if not content_name:
            return None, "<p style='text-align: center; padding: 50px; color: #666;'>❌ Please select content to view</p>", "❌ Please select content to view"
        
        content_list = get_available_content()
        selected = next((c for c in content_list if c['name'] == content_name), None)
        
        if not selected:
            return None, "<p style='text-align: center; padding: 50px; color: #666;'>❌ Content not found</p>", "❌ Content not found"
        
        # Check if PDF exists, if not offer to generate it
        pdf_html = ""
        pdf_status = ""
        
        if selected['pdf'] and Path(selected['pdf']).exists():
            # Read PDF and convert to base64
            with open(selected['pdf'], 'rb') as f:
                pdf_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Create HTML with embedded PDF viewer using base64 data URI
            pdf_html = f"""
            <iframe src="data:application/pdf;base64,{pdf_data}" 
                    width="100%" 
                    height="800px" 
                    style="border: 1px solid #ddd; border-radius: 4px;">
                <p>Your browser does not support PDFs. 
                   <a href="data:application/pdf;base64,{pdf_data}" download="{content_name}.pdf">Download the PDF</a>
                </p>
            </iframe>
            """
            pdf_status = f"✅ Ready to read: {content_name}"
        else:
            pdf_html = "<p style='text-align: center; padding: 50px; color: #ff9800;'>⚠️ PDF not found. Click 'Generate PDF' to create it.</p>"
            pdf_status = f"⚠️ PDF not found. Click 'Generate PDF' to create it."
        
        return selected['audio'], pdf_html, pdf_status
        
    except Exception as e:
        return None, f"<p style='text-align: center; padding: 50px; color: #f44336;'>❌ Error: {str(e)}</p>", f"❌ Error: {str(e)}"

def generate_pdf_for_reader(content_name: str):
    """Generate PDF for the selected content if it doesn't exist"""
    try:
        if not content_name:
            return "<p style='text-align: center; padding: 50px; color: #666;'>❌ Please select content first</p>", "❌ Please select content first"
        
        transcript_path = Config.TRANSCRIPTS_DIR / f"{content_name}_transcript.txt"
        
        if not transcript_path.exists():
            return "<p style='text-align: center; padding: 50px; color: #f44336;'>❌ Transcript not found</p>", "❌ Transcript not found"
        
        # Generate PDF
        pdf_path = pdf_generator.generate_pdf(transcript_path)
        
        # Read PDF and convert to base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create HTML with embedded PDF viewer using base64 data URI
        pdf_html = f"""
        <iframe src="data:application/pdf;base64,{pdf_data}" 
                width="100%" 
                height="800px" 
                style="border: 1px solid #ddd; border-radius: 4px;">
            <p>Your browser does not support PDFs. 
               <a href="data:application/pdf;base64,{pdf_data}" download="{content_name}.pdf">Download the PDF</a>
            </p>
        </iframe>
        """
        
        return pdf_html, f"✅ PDF generated successfully!"
        
    except Exception as e:
        return f"<p style='text-align: center; padding: 50px; color: #f44336;'>❌ Error: {str(e)}</p>", f"❌ Error: {str(e)}"


# ============================================================================
# TAB 4: CHAT
# ============================================================================


def load_transcripts_to_vector_store():
    """Load all transcripts into vector store"""
    try:
        count = vector_store.add_all_transcripts()
        stats = vector_store.get_stats()
        return f"✅ Loaded {count} chunks from transcripts\n\nVector Store Stats:\n- Total chunks: {stats['total_chunks']}\n- Collection: {stats['collection_name']}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def chat_with_transcripts(message: str, history):
    """Chat with the transcripts"""
    if not chat_engine.is_ready():
        return history + [[message, "❌ Google AI API key not configured. Please set GOOGLE_AI_API_KEY in .env file."]]
    
    try:
        result = chat_engine.ask(message, use_rag=True)
        response = result['response']
        
        # Add source citations if available
        if result['sources']:
            sources_text = chat_engine.format_sources(result['sources'])
            response += f"\n\n**Sources:**\n{sources_text}"
        
        return history + [[message, response]]
    except Exception as e:
        return history + [[message, f"❌ Error: {str(e)}"]]

def clear_chat():
    """Clear chat history"""
    chat_engine.clear_history()
    return []

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(
    title="BBC Audio Scraper & Chat", 
) as app:
    gr.Markdown("""
    # 🎙️ BBC Audio Scraper, Transcription & Chat System
    
    Download BBC audio programmes, transcribe them using **free local AI** (Whisper), and chat with the transcripts using Google AI.
    """)
    
    with gr.Tabs():
        # ====================================================================
        # TAB 1: DOWNLOAD
        # ====================================================================
        with gr.Tab("📥 Download Audio"):
            gr.Markdown("### Download BBC Audio Programmes")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Option 1: RSS Feed (Recommended)")
                    rss_url = gr.Textbox(
                        label="RSS Feed URL",
                        placeholder="https://podcasts.files.bbci.co.uk/p00fzl9g.rss",
                        lines=1
                    )
                    rss_limit = gr.Number(label="Max Episodes", value=5, precision=0)
                    rss_btn = gr.Button("Download from RSS", variant="primary")
                    
                    gr.Markdown("#### Popular BBC Feeds")
                    feeds_btn = gr.Button("Show Popular Feeds")
                
                with gr.Column():
                    gr.Markdown("#### Option 2: get_iplayer")
                    iplayer_query = gr.Textbox(
                        label="Search Query or URL",
                        placeholder="Reith Lectures",
                        lines=1
                    )
                    iplayer_btn = gr.Button("Search/Download")
            
            download_output = gr.Textbox(label="Output", lines=10)
            
            gr.Markdown("#### Downloaded Files")
            refresh_downloads_btn = gr.Button("Refresh List")
            downloads_list = gr.Textbox(label="Audio Files", lines=5)
            
            # Event handlers
            rss_btn.click(download_from_rss, [rss_url, rss_limit], download_output)
            iplayer_btn.click(download_with_iplayer, iplayer_query, download_output)
            feeds_btn.click(get_popular_feeds, None, download_output)
            refresh_downloads_btn.click(list_downloads, None, downloads_list)
        
        # ====================================================================
        # TAB 2: TRANSCRIBE
        # ====================================================================
        with gr.Tab("📝 Transcribe"):
            gr.Markdown("### Transcribe Audio to Text (FREE - uses Whisper locally)")
            
            with gr.Row():
                with gr.Column():
                    audio_file = gr.Dropdown(
                        label="Select Audio File",
                        choices=[str(f) for f in file_manager.list_audio_files()],
                        interactive=True
                    )
                    refresh_audio_btn = gr.Button("Refresh Audio List")
                    
                    model_size = gr.Dropdown(
                        label="Whisper Model Size",
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="base",
                        info="Larger = more accurate but slower"
                    )
                    language = gr.Textbox(
                        label="Language Code", 
                        value="english",
                        info="Use 'english', 'spanish', 'french', etc."
                    )
                    
                    transcribe_btn = gr.Button("Transcribe Selected File", variant="primary")
                    transcribe_all_btn = gr.Button("Transcribe All Files")
                
                with gr.Column():
                    transcribe_output = gr.Textbox(label="Status", lines=3)
                    transcript_display = gr.Textbox(label="Transcript", lines=15)
            
            gr.Markdown("#### Saved Transcripts")
            refresh_transcripts_btn = gr.Button("Refresh List")
            transcripts_list = gr.Textbox(label="Transcript Files", lines=5)
            
            # Event handlers
            refresh_audio_btn.click(
                lambda: gr.Dropdown(choices=[str(f) for f in file_manager.list_audio_files()]),
                None,
                audio_file
            )
            transcribe_btn.click(
                transcribe_file,
                [audio_file, model_size, language],
                [transcribe_output, transcript_display]
            )
            transcribe_all_btn.click(
                transcribe_all,
                [model_size, language],
                transcribe_output
            )
            refresh_transcripts_btn.click(list_transcripts, None, transcripts_list)
            
            gr.Markdown("---")
            gr.Markdown("#### 📄 Export to PDF")
            gr.Markdown("Generate formatted PDF documents from your transcripts for offline reading")
            
            with gr.Row():
                with gr.Column():
                    transcript_selector = gr.Dropdown(
                        label="Select Transcript to Export",
                        choices=[t.name for t in file_manager.list_transcripts()],
                        interactive=True
                    )
                    refresh_pdf_list_btn = gr.Button("Refresh Transcript List")
                    
                    with gr.Row():
                        export_single_btn = gr.Button("📄 Export Selected to PDF", variant="primary")
                        export_all_btn = gr.Button("📚 Export All to PDF")
                
                with gr.Column():
                    pdf_output = gr.Textbox(label="Export Status", lines=3)
                    pdf_file = gr.File(label="Download PDF", visible=True)
            
            # PDF Export Event handlers
            refresh_pdf_list_btn.click(
                lambda: gr.Dropdown(choices=[t.name for t in file_manager.list_transcripts()]),
                None,
                transcript_selector
            )
            export_single_btn.click(
                export_transcript_to_pdf,
                transcript_selector,
                [pdf_output, pdf_file]
            )
            export_all_btn.click(
                export_all_transcripts_to_pdf,
                None,
                pdf_output
            )

        
        # ====================================================================
        # TAB 3: PDF READER
        # ====================================================================
        with gr.Tab("📖 Read & Listen"):
            gr.Markdown("### Read Transcripts While Listening to Audio")
            gr.Markdown("Select content to view the PDF transcript alongside the audio player")
            
            with gr.Row():
                with gr.Column(scale=1):
                    content_selector = gr.Dropdown(
                        label="Select Content",
                        choices=[c['name'] for c in get_available_content()],
                        interactive=True
                    )
                    refresh_content_btn = gr.Button("🔄 Refresh Content List")
                    load_content_btn = gr.Button("📖 Load Content", variant="primary")
                    generate_pdf_btn = gr.Button("📄 Generate PDF (if missing)")
                    
                    reader_status = gr.Textbox(label="Status", lines=2)
            
            gr.Markdown("---")
            
            # Audio player at the top - compact
            gr.Markdown("#### 🎧 Audio Player")
            audio_player = gr.Audio(
                label="",
                type="filepath",
                interactive=False,
                show_label=False
            )
            
            gr.Markdown("---")
            
            # PDF viewer takes full width for optimal reading
            gr.Markdown("#### 📄 PDF Transcript")
            pdf_viewer = gr.HTML(
                label="PDF Transcript",
                value="<p style='text-align: center; padding: 50px; color: #666;'>Select content and click 'Load Content' to view PDF</p>"
            )
            
            # Event handlers for PDF Reader
            refresh_content_btn.click(
                lambda: gr.Dropdown(choices=[c['name'] for c in get_available_content()]),
                None,
                content_selector
            )
            
            load_content_btn.click(
                load_content_for_reading,
                content_selector,
                [audio_player, pdf_viewer, reader_status]
            )
            
            generate_pdf_btn.click(
                generate_pdf_for_reader,
                content_selector,
                [pdf_viewer, reader_status]
            )
        
        # ====================================================================
        # TAB 4: CHAT
        # ====================================================================
        with gr.Tab("💬 Chat with Transcripts"):
            gr.Markdown("### AI-Powered Chat with Your Transcripts")
            
            with gr.Row():
                load_btn = gr.Button("📚 Load Transcripts to Vector Store", variant="primary")
                load_output = gr.Textbox(label="Status", lines=3)
            
            load_btn.click(load_transcripts_to_vector_store, None, load_output)
            
            gr.Markdown("---")
            
            chatbot = gr.Chatbot(label="Chat", height=400)
            msg = gr.Textbox(
                label="Your Question",
                placeholder="What are the main themes discussed in the lectures?",
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear Chat")
            
            # Event handlers
            submit_btn.click(chat_with_transcripts, [msg, chatbot], chatbot)
            msg.submit(chat_with_transcripts, [msg, chatbot], chatbot)
            clear_btn.click(clear_chat, None, chatbot)
            submit_btn.click(lambda: "", None, msg)  # Clear input after send
    
    gr.Markdown("""
    ---
    ### 💡 Quick Start Guide
    
    1. **Download**: Use the RSS feed URL for Reith Lectures: `https://podcasts.files.bbci.co.uk/p02p8xh7.rss`
    2. **Transcribe**: Select downloaded audio and click "Transcribe" (uses free Whisper AI)
    3. **Chat**: Load transcripts to vector store, then ask questions about the content!
    
    **Note**: Make sure to set your `GOOGLE_AI_API_KEY` in the `.env` file for chat functionality.
    """)

if __name__ == "__main__":
    logger.info("Starting BBC Audio Scraper & Chat application")
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
