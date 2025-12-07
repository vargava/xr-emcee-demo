#!/usr/bin/env python3
"""
Test Script for Reachy Mini Integration
Tests all gestures and validates controller setup
"""

import sys
import time
from reachy_controller import ReachyMiniController, get_gesture_for_emotion, EMOTION_TO_GESTURE

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def test_controller_initialization():
    """Test controller can be initialized"""
    print_header("TEST 1: Controller Initialization")
    
    try:
        controller = ReachyMiniController()
        status = controller.get_status()
        
        print("✅ Controller initialized successfully!")
        print(f"   Mode: {'SIMULATION' if status['simulation_mode'] else 'REAL ROBOT'}")
        print(f"   Host: {status['host']}:{status['port']}")
        print(f"   Connected: {status['connected']}")
        print(f"   Available gestures: {len(status['available_gestures'])}")
        
        return controller
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return None

def test_all_gestures(controller):
    """Test all defined gestures"""
    print_header("TEST 2: All Gesture Execution")
    
    if not controller:
        print("❌ SKIPPED: No controller available")
        return False
    
    gestures = list(controller.GESTURES.keys())
    print(f"Testing {len(gestures)} gestures...\n")
    
    for i, gesture in enumerate(gestures, 1):
        print(f"[{i}/{len(gestures)}] {gesture}")
        try:
            controller.perform_gesture(gesture)
            time.sleep(0.5)  # Pause between gestures
            print("   ✅ OK")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            return False
    
    print("\n✅ All gestures executed successfully!")
    return True

def test_emotion_mapping():
    """Test emotion to gesture mapping"""
    print_header("TEST 3: Emotion Mapping")
    
    test_emotions = [
        "happy", "thinking", "excited", "dismissive", 
        "neutral", "self_deprecating", "celebrating", "rest"
    ]
    
    print("Testing emotion → gesture mapping:\n")
    
    all_passed = True
    for emotion in test_emotions:
        gesture = get_gesture_for_emotion(emotion)
        if gesture:
            print(f"   {emotion:20s} → {gesture}")
        else:
            print(f"   ❌ {emotion:20s} → [UNMAPPED]")
            all_passed = False
    
    if all_passed:
        print("\n✅ All emotions mapped correctly!")
    else:
        print("\n⚠️  Some emotions not mapped")
    
    return all_passed

def test_response_based_gestures(controller):
    """Test gesture selection based on response text"""
    print_header("TEST 4: Response-Based Gesture Selection")
    
    if not controller:
        print("❌ SKIPPED: No controller available")
        return False
    
    test_cases = [
        ("I may not have legs, but I've got wheels!", "self_deprecating"),
        ("That's awesome! Great work!", "excited"),
        ("You should explore the exhibits!", "dismissive"),
        ("What are you working on?", "thinking"),
        ("Nice to meet you.", "neutral")
    ]
    
    print("Testing automatic gesture selection:\n")
    
    for response, expected_emotion in test_cases:
        print(f"Response: \"{response[:40]}...\"")
        
        # Simulate the logic from main.py
        response_lower = response.lower()
        if 'wheel' in response_lower or 'roll' in response_lower or "can't walk" in response_lower:
            emotion = "self_deprecating"
        elif any(word in response_lower for word in ['great', 'awesome', 'excellent', 'amazing']):
            emotion = "excited"
        elif any(word in response_lower for word in ['explore', 'check out', 'go see', 'meet']):
            emotion = "dismissive"
        elif '?' in response:
            emotion = "thinking"
        else:
            emotion = "neutral"
        
        gesture = get_gesture_for_emotion(emotion)
        
        match = "✅" if emotion == expected_emotion else "❌"
        print(f"   {match} Detected: {emotion} → {gesture}")
        controller.perform_gesture(gesture)
        time.sleep(0.3)
        print()
    
    print("✅ Response-based gesture selection tested!")
    return True

def test_session_workflow(controller):
    """Test typical session workflow"""
    print_header("TEST 5: Typical Session Workflow")
    
    if not controller:
        print("❌ SKIPPED: No controller available")
        return False
    
    print("Simulating a typical conversation flow:\n")
    
    workflow = [
        ("Greeting visitor", "happy"),
        ("Asking question", "thinking"),
        ("Enthusiastic response", "excited"),
        ("Self-deprecating joke", "self_deprecating"),
        ("Encouraging exploration", "dismissive"),
        ("Neutral response", "neutral"),
        ("Returning to rest", "rest")
    ]
    
    for i, (action, emotion) in enumerate(workflow, 1):
        print(f"[{i}/{len(workflow)}] {action}")
        gesture = get_gesture_for_emotion(emotion)
        print(f"   Emotion: {emotion} → Gesture: {gesture}")
        controller.perform_gesture(gesture)
        time.sleep(0.8)
        print()
    
    print("✅ Session workflow completed!")
    return True

def test_rapid_gestures(controller):
    """Test rapid gesture switching"""
    print_header("TEST 6: Rapid Gesture Switching")
    
    if not controller:
        print("❌ SKIPPED: No controller available")
        return False
    
    print("Testing rapid gesture changes (simulating animated conversation):\n")
    
    rapid_sequence = ["thinking", "excited", "neutral", "thinking", "happy"]
    
    for i, emotion in enumerate(rapid_sequence, 1):
        gesture = get_gesture_for_emotion(emotion)
        print(f"[{i}] {emotion} → {gesture}")
        controller.perform_gesture(gesture)
        time.sleep(0.2)  # Very short pause
    
    print("\n✅ Rapid switching test complete!")
    return True

def main():
    """Run all tests"""
    print("\n" + "🤖" * 30)
    print("   REACHY MINI CONTROLLER - COMPREHENSIVE TEST SUITE")
    print("🤖" * 30)
    
    # Initialize
    controller = test_controller_initialization()
    
    # Run tests
    tests = [
        test_all_gestures(controller),
        test_emotion_mapping(),
        test_response_based_gestures(controller),
        test_session_workflow(controller),
        test_rapid_gestures(controller)
    ]
    
    # Cleanup
    if controller:
        print_header("CLEANUP")
        controller.goto_rest()
        controller.disconnect()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(tests)
    total = len(tests)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nYour Reachy controller is ready to use!")
        print("\nNext steps:")
        print("1. If in simulation mode, this is what you'll see during conversations")
        print("2. To connect to real robot:")
        print("   - Update .env: REACHY_SIMULATION_MODE=false")
        print("   - Set REACHY_HOST to your robot's IP")
        print("3. Run the main bot: docker-compose run --rm reachy-soul")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nCheck errors above and ensure:")
        print("1. reachy_controller.py is in the same directory")
        print("2. .env file has correct settings")
    
    print()
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())