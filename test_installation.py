"""
Quick test script to verify the installation and basic functionality.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import gradio
        print("✅ gradio")
    except ImportError:
        print("❌ gradio - run: pip install gradio")
        return False
    
    try:
        import whisper
        print("✅ openai-whisper")
    except ImportError:
        print("❌ openai-whisper - run: pip install openai-whisper")
        return False
    
    try:
        import google.generativeai
        print("✅ google-generativeai")
    except ImportError:
        print("❌ google-generativeai - run: pip install google-generativeai")
        return False
    
    try:
        import chromadb
        print("✅ chromadb")
    except ImportError:
        print("❌ chromadb - run: pip install chromadb")
        return False
    
    try:
        import feedparser
        print("✅ feedparser")
    except ImportError:
        print("❌ feedparser - run: pip install feedparser")
        return False
    
    print("\n✅ All required packages are installed!\n")
    return True

def test_config():
    """Test configuration"""
    print("Testing configuration...")
    try:
        from config import Config
        Config.validate()
        print(f"✅ Config loaded")
        print(f"   - Downloads dir: {Config.DOWNLOADS_DIR}")
        print(f"   - Transcripts dir: {Config.TRANSCRIPTS_DIR}")
        print(f"   - Whisper model: {Config.WHISPER_MODEL_SIZE}")
        
        if Config.GOOGLE_AI_API_KEY:
            print(f"   - Google AI API: Configured ✅")
        else:
            print(f"   - Google AI API: Not configured ⚠️")
            print(f"     Set GOOGLE_AI_API_KEY in .env file for chat functionality")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_scraper():
    """Test RSS scraper"""
    print("\nTesting RSS scraper...")
    try:
        from src.scraper.rss_scraper import RSScraper
        scraper = RSScraper()
        feeds = scraper.list_available_feeds()
        print(f"✅ RSS scraper initialized")
        print(f"   - Available feeds: {len(feeds)}")
        return True
    except Exception as e:
        print(f"❌ RSS scraper error: {e}")
        return False

def test_transcriber():
    """Test Whisper transcriber"""
    print("\nTesting Whisper transcriber...")
    try:
        from src.transcription.transcriber import WhisperTranscriber
        transcriber = WhisperTranscriber(model_size='tiny')
        print(f"✅ Whisper transcriber initialized")
        print(f"   - Model: {transcriber.model_size}")
        print(f"   - Note: Model will download on first use (~39MB for 'tiny')")
        return True
    except Exception as e:
        print(f"❌ Transcriber error: {e}")
        return False

def test_chat():
    """Test chat engine"""
    print("\nTesting chat engine...")
    try:
        from src.chat.chat_engine import ChatEngine
        from src.chat.vector_store import VectorStore
        
        vector_store = VectorStore()
        chat_engine = ChatEngine(vector_store)
        
        print(f"✅ Chat engine initialized")
        print(f"   - Vector store: {vector_store.collection_name}")
        print(f"   - Ready: {chat_engine.is_ready()}")
        
        if not chat_engine.is_ready():
            print(f"   ⚠️  Set GOOGLE_AI_API_KEY in .env to enable chat")
        
        return True
    except Exception as e:
        print(f"❌ Chat engine error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BBC Audio Scraper - Installation Test")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_config,
        test_scraper,
        test_transcriber,
        test_chat,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to use the application!")
        print("Run: python app.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
