#!/usr/bin/env python3
"""Test Gemini API connection"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(f"API Key found: {bool(GEMINI_API_KEY)}")
print(f"API Key (first 20 chars): {GEMINI_API_KEY[:20] if GEMINI_API_KEY else 'None'}")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello, I am working!'")
        
        print(f"\n✅ Gemini API is working!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"\n❌ Gemini API error: {e}")
        print(f"Error type: {type(e).__name__}")
else:
    print("\n❌ No API key found in environment")
