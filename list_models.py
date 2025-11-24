"""
Quick script to list available Google AI models
"""
import google.generativeai as genai
from config import Config

# Configure API
genai.configure(api_key=Config.GOOGLE_AI_API_KEY)

print("Available models:")
print("-" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print("-" * 80)
