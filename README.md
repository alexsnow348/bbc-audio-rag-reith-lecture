# 🎙️ BBC Audio RAG

> Download BBC podcasts, transcribe with Whisper, and chat with transcripts using Gemini AI and RAG

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/managed%20by-uv-blue)](https://docs.astral.sh/uv/)

A complete end-to-end system for downloading, transcribing, and intelligently querying BBC audio content. Built entirely with **free and open-source tools** — no paid APIs required for transcription!

### ✨ What Makes This Special

- 🆓 **100% Free Transcription**: Uses OpenAI Whisper locally (no API costs)
- 🧠 **Smart RAG System**: Semantic search with ChromaDB vector database
- 🤖 **AI-Powered Chat**: Query transcripts using Google's Gemini AI
- 🎨 **Beautiful UI**: Intuitive Gradio web interface
- 📦 **Modern Stack**: Managed with `uv` for fast, reliable dependency management
- 🚀 **Deploy Ready**: One-click deployment to HuggingFace Spaces

## 🎯 Features

### 📥 Audio Download
- Download BBC podcasts via RSS feeds (recommended)
- Support for get_iplayer for BBC iPlayer content
- Batch download multiple episodes
- Popular BBC podcast feeds included

### 🎯 Free Local Transcription
- Powered by OpenAI Whisper (runs on your machine)
- Multiple model sizes: `tiny`, `base`, `small`, `medium`, `large`
- No API costs or usage limits
- Batch transcription support
- Automatic audio preprocessing

### 💬 AI-Powered Chat with RAG
- Chat with your transcripts using Google Gemini AI
- Retrieval-Augmented Generation (RAG) for accurate answers
- ChromaDB vector database for semantic search
- Source citations for transparency
- Conversation history tracking

### 🌐 Web Interface
- Clean, intuitive Gradio interface
- Three main tabs: Download, Transcribe, Chat
- Real-time progress updates
- File management built-in

## �️ Tech Stack

### Core Technologies
- **[Python 3.9+](https://www.python.org/)** - Programming language
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager and project manager
- **[Gradio](https://gradio.app/)** - Web UI framework

### AI & ML
- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech-to-text transcription (local, free)
- **[Google Gemini](https://ai.google.dev/)** - Large language model for chat (free tier available)
- **[ChromaDB](https://www.trychroma.com/)** - Vector database for semantic search
- **[LangChain](https://www.langchain.com/)** - LLM application framework

### Audio Processing
- **[FFmpeg](https://ffmpeg.org/)** - Audio/video processing
- **[pydub](https://github.com/jiaaro/pydub)** - Audio manipulation

### Data & Utilities
- **[feedparser](https://feedparser.readthedocs.io/)** - RSS feed parsing
- **[requests](https://requests.readthedocs.io/)** - HTTP library
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment variable management

## �📋 Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (modern Python package manager)
- FFmpeg (for audio processing)
- Google AI API key (free tier available)
- Optional: get_iplayer for BBC iPlayer downloads

## 🚀 Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 2. Clone and Setup

```bash
cd /home/wut/playground/reith-lecture

# Create virtual environment and install all dependencies
uv sync
```

This will:
- Create a `.venv` virtual environment
- Install all dependencies from `pyproject.toml`
- Set up the project in editable mode

### 3. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### 3. Install get_iplayer (Optional)

```bash
# Ubuntu/Debian
sudo apt install get-iplayer

# macOS
brew install get_iplayer

# Or install from: https://github.com/get-iplayer/get_iplayer
```

### 4. Configure API Keys

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Google AI API key:

```
GOOGLE_AI_API_KEY=your_api_key_here
```

Get a free Google AI API key at: https://makersuite.google.com/app/apikey

## 💻 Usage

### Run the Gradio App

```bash
uv run python app.py
```

Then open your browser to `http://localhost:7860`

### Command Line Usage

**Download audio from RSS feed:**
```bash
uv run python -c "from src.scraper.rss_scraper import RSScraper; scraper = RSScraper(); scraper.download_episodes('https://podcasts.files.bbci.co.uk/p00fzl9g.rss', limit=5)"
```

**Transcribe audio:**
```bash
uv run python -c "from src.transcription.transcriber import WhisperTranscriber; transcriber = WhisperTranscriber(model_size='base'); transcript = transcriber.transcribe_and_save('downloads/episode.mp3'); print(transcript)"
```

**Chat with transcripts:**
```bash
uv run python -c "from src.chat.chat_engine import ChatEngine; chat = ChatEngine(); response = chat.ask('What are the main themes discussed?'); print(response['response'])"
```

## 📁 Project Structure

```
reith-lecture/
├── app.py                      # Main Gradio application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
├── src/
│   ├── scraper/
│   │   ├── bbc_scraper.py    # BBC website scraper
│   │   ├── get_iplayer_wrapper.py  # get_iplayer wrapper
│   │   └── rss_scraper.py    # RSS feed parser
│   ├── transcription/
│   │   ├── transcriber.py    # Whisper transcription (FREE)
│   │   └── audio_processor.py # Audio utilities
│   ├── chat/
│   │   ├── vector_store.py   # ChromaDB for RAG
│   │   └── chat_engine.py    # Google AI chat engine
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── file_manager.py    # File management
├── downloads/                  # Downloaded audio files
├── transcripts/               # Generated transcripts
├── data/                      # Vector database
└── tests/                     # Unit tests
```

## 🌐 Deploy to HuggingFace Spaces

1. Create a new Space at https://huggingface.co/spaces
2. Choose "Gradio" as the SDK
3. Upload all files from this project
4. Add your `GOOGLE_AI_API_KEY` in Space Settings → Repository secrets
5. Your app will be live!

## 🎓 Example: Reith Lectures

The Reith Lectures are available as a podcast:

**RSS Feed:** `https://podcasts.files.bbci.co.uk/p00fzl9g.rss`

Use the Download tab in the Gradio app or:

```python
from src.scraper.rss_scraper import RSScraper

scraper = RSScraper()
scraper.download_episodes('https://podcasts.files.bbci.co.uk/p00fzl9g.rss', limit=10)
```

## 🔧 Troubleshooting

**Whisper is slow:**
- Use a smaller model: `tiny`, `base`, or `small`
- Upgrade to a GPU-enabled machine for faster transcription

**FFmpeg not found:**
- Make sure FFmpeg is installed and in your PATH
- Test with: `ffmpeg -version`

**get_iplayer not working:**
- Update: `get_iplayer --refresh`
- Check BBC availability in your region

## 📝 License

MIT License - Free for personal and educational use.

## ⚠️ Disclaimer

This tool is for personal use and educational purposes. Please respect BBC's terms of service and copyright.
