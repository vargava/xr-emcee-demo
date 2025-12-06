#!/usr/bin/env python3
"""
Automated test conversation to verify bot works correctly
Useful for quick validation without manual interaction
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ConversationAgent, PersonalityEngine

load_dotenv()

def run_test_conversations():
    """Run automated test conversations with different personalities"""
    
    print("=" * 70)
    print("🧪 AUTOMATED BOT TEST - Running Test Conversations")
    print("=" * 70)
    print()
    
    # Test scenarios
    test_cases = [
        {
            "personality": "pirate",
            "questions": [
                "Hello! How are you today?",
                "Tell me about yourself",
                "Make me laugh!"
            ]
        },
        {
            "personality": "garfield",
            "questions": [
                "What's your favorite food?",
                "How do you feel about Mondays?",
            ]
        },
        {
            "personality": "tech_bro",
            "questions": [
                "What's the next big thing in tech?",
                "Tell me about AI"
            ]
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        personality = test_case["personality"]
        print(f"\n{'='*70}")
        print(f"Testing Personality: {personality.upper()}")
        print(f"{'='*70}\n")
        
        try:
            agent = ConversationAgent(personality)
            
            for i, question in enumerate(test_case["questions"], 1):
                print(f"Test {i}/{len(test_case['questions'])}: {question}")
                print("-" * 70)
                
                response = agent.process_input(question)
                
                if response and not response.startswith("Error"):
                    print(f"✅ PASS")
                    print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
                else:
                    print(f"❌ FAIL - No valid response")
                    print(f"Got: {response}")
                    all_passed = False
                
                print()
            
            # Test humor adjustment
            print("Test: Humor Adjustment")
            print("-" * 70)
            response = agent.process_input("Tell me a joke", humor_adjustment=3)
            if response and not response.startswith("Error"):
                print("✅ PASS - Humor adjustment working")
                print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            else:
                print("❌ FAIL - Humor adjustment failed")
                all_passed = False
            
            print()
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYour bot is ready for the hackathon! 🎉")
        print("\nNext steps:")
        print("1. Run: docker-compose run --rm hackathon-bot")
        print("2. Choose a personality")
        print("3. Start chatting!")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct API key")
        print("2. Verify internet connection")
        print("3. Run: python test_api.py")
    
    print()
    return all_passed

if __name__ == "__main__":
    try:
        success = run_test_conversations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)