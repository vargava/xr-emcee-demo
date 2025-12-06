#!/usr/bin/env python3
"""
Quick test script to verify the bot works without Docker
Useful for debugging API connectivity
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def test_api_connection():
    """Test if Anthropic API is accessible"""
    print("🧪 Testing Anthropic API connection...\n")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ ANTHROPIC_API_KEY not set in .env file")
        print("   Please edit .env and add your API key")
        return False
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Simple test message
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'API test successful!' and nothing else."}
            ]
        )
        
        response = message.content[0].text
        print(f"✅ API Response: {response}\n")
        print("🎉 Connection successful! You're ready to run the bot.\n")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}\n")
        print("Check your API key and internet connection.")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    exit(0 if success else 1)