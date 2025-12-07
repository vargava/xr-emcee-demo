# 🤖 Reachy Mini Integration Guide

## Quick Overview

Your bot now has full Reachy Mini support with:
- ✅ Real robot control via Reachy SDK
- ✅ Simulation mode for testing without hardware
- ✅ 7 expressive gestures
- ✅ Automatic gesture selection based on conversation
- ✅ Long-term memory across visitors

## Files Added/Updated

### New Files:
- `reachy_controller.py` - Main Reachy control module
- `test_reachy.py` - Comprehensive test suite

### Updated Files:
- `main.py` - Integrated Reachy controller, two-bot personality, long-term memory
- `requirements.txt` - Added `reachy2-sdk` and `websockets`
- `.env.template` - Added Reachy configuration options

## Configuration (.env)

Add these to your `.env` file:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Reachy Mini Configuration
REACHY_HOST=localhost                  # Change to robot's IP when ready
REACHY_PORT=50055                      # Default Reachy SDK port
REACHY_SIMULATION_MODE=true            # Set to 'false' for real robot
REACHY_VERBOSE=false                   # Set to 'true' for detailed gesture logs
```

## Available Gestures

| Gesture | Description | Triggered By |
|---------|-------------|--------------|
| `wave` | Wave hello | Happy greetings |
| `nod` | Gentle head nod | Neutral responses |
| `spin` | Enthusiastic spin | Excitement, self-deprecation |
| `tilt_head` | Thoughtful head tilt | Questions, thinking |
| `dismissive_wave` | Gentle shooing motion | Encouraging exploration |
| `celebrate` | Both arms raised | Celebration |
| `rest` | Return to rest position | End of interaction |

## Testing (No Robot Required!)

### Test 1: Quick Controller Test
```bash
python test_reachy.py
```

This runs a comprehensive test suite that:
1. Initializes controller
2. Tests all gestures in simulation
3. Validates emotion mapping
4. Simulates conversation flow
5. Tests rapid gesture switching

**Expected Output:**
```
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖
   REACHY MINI CONTROLLER - COMPREHENSIVE TEST SUITE
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖

==============================================================
  TEST 1: Controller Initialization
==============================================================

🎭 Reachy running in SIMULATION mode
✅ Controller initialized successfully!
   Mode: SIMULATION
   Host: localhost:50055
   Connected: False
   Available gestures: 7

[... more tests ...]

🎉 ALL TESTS PASSED! 🎉
```

### Test 2: Individual Gestures
```python
from reachy_controller import ReachyMiniController

controller = ReachyMiniController()

# Test specific gesture
controller.perform_gesture("wave")
controller.perform_gesture("spin")
controller.perform_gesture("celebrate")
```

### Test 3: In Main Application
Just run your bot normally:
```bash
docker-compose run --rm reachy-soul
```

All gestures will be simulated in console during conversation!

## Connecting to Real Robot

### Step 1: Find Robot IP
On your Reachy Mini's network:
```bash
# Reachy typically uses hostname
ping reachy.local

# Or scan network
arp -a | grep reachy
```

### Step 2: Update .env
```bash
REACHY_HOST=192.168.1.XXX          # Your robot's IP
REACHY_SIMULATION_MODE=false        # Enable real robot
```

### Step 3: Rebuild Docker
```bash
docker-compose build
docker-compose run --rm reachy-soul
```

### Step 4: Verify Connection
Look for this in startup:
```
🔌 Connecting to Reachy at 192.168.1.XXX:50055...
✅ Connected to Reachy Mini!
```

## How It Works in Conversation

### Automatic Gesture Selection

The bot analyzes its own responses and triggers gestures:

```python
# Example conversation:
User: "What are you?"
Bot: "I may not have legs, but I've got wheels!"
→ 🌀 [Mini spins mockingly]

User: "That's hilarious!"
Bot: "Glad you like it! Want to see something amazing?"
→ 🤔 [Mini tilts head thoughtfully]

User: "Sure!"
Bot: "Check out the VR demo in the corner!"
→ ✋ [Mini waves dismissively - gentle encouragement to explore]
```

### Gesture Triggers

From `main.py`:
```python
if 'wheel' in response or 'roll' in response:
    → self_deprecating (spin)
    
elif 'awesome' in response or 'amazing' in response:
    → excited (spin enthusiastically)
    
elif 'explore' in response or 'check out' in response:
    → dismissive (gentle wave)
    
elif '?' in response:
    → thinking (head tilt)
    
else:
    → neutral (nod)
```

## Long-Term Memory & Reset

### New "Reset" Behavior

When user types `reset`:
1. Current conversation saved to long-term memory
2. Short-term conversation cleared
3. Visitor count incremented
4. Option to provide context for next person

```
> reset

🔄 Moving to next visitor (Total so far: 3)

Optional: Provide context clues for next person (or press Enter to skip):
> woman with blue jacket, holding coffee

🤖 Bot introducing itself to new person...

🔊 Bot says: *yawns* Hey there! I see you've got the essentials - 
coffee in hand! I'm your lazy host here...
```

### What's Retained:
- ✅ Scene context (hackathon, art exhibit, etc.)
- ✅ Personality and tone
- ✅ Long-term memory (last 5 visitors)
- ✅ Total visitor count

### What's Cleared:
- ❌ Current conversation history
- ❌ Exchange count
- ❌ Specific details from this person

## Troubleshooting

### "reachy2-sdk not found"
```bash
# Rebuild Docker
docker-compose build --no-cache
```

### Robot doesn't move
1. Check `.env`: `REACHY_SIMULATION_MODE=false`
2. Verify network connection: `ping REACHY_HOST`
3. Check robot is powered on and SDK server running
4. Look for connection errors in console

### Gestures in wrong order
- This is expected in simulation - just showing what *would* happen
- On real robot, SDK handles timing automatically

### Want more verbose output
```bash
# In .env
REACHY_VERBOSE=true
```

This shows detailed joint positions for each gesture.

## Customizing Gestures

### Add New Gesture

Edit `reachy_controller.py`:

```python
GESTURES = {
    # ... existing gestures ...
    
    "point": {
        "description": "Point at something",
        "joints": {
            "r_shoulder_pitch": -45,
            "r_elbow_pitch": -90,
        },
        "animation": [
            {"r_wrist_pitch": -30, "duration": 0.4},
        ],
        "emoji": "👉"
    }
}
```

### Map Emotion to Gesture

Edit `reachy_controller.py`:

```python
EMOTION_TO_GESTURE = {
    # ... existing mappings ...
    "pointing": "point",
}
```

### Trigger in Conversation

Edit `main.py` gesture selection:

```python
elif 'over there' in response_lower or 'that way' in response_lower:
    reachy.perform_gesture(get_gesture_for_emotion("pointing"))
```

## Advanced: Custom Animation Sequences

```python
def perform_custom_sequence(controller):
    """Complex multi-gesture sequence"""
    controller.perform_gesture("wave")
    time.sleep(1)
    controller.perform_gesture("spin")
    time.sleep(0.5)
    controller.perform_gesture("celebrate")
    time.sleep(1)
    controller.goto_rest()
```

## Integration with Temi

The bot knows it's embodied in Temi (mobile platform) with Mini on top:

```python
# From system prompt:
"You ARE Temi, a mobile semi-autonomous robot"
"Mounted on top of you is Mini - a Reachy Mini robot"
"When you respond enthusiastically → Mini spins"
"When you're self-deprecating → Mini might spin mockingly"
```

This creates the two-bot comedy dynamic!

## Next Steps

1. ✅ Test in simulation mode (working now!)
2. 🚧 Connect to real Reachy hardware
3. 🚧 Fine-tune gesture timings
4. 🚧 Add custom gestures for your use case
5. 🚧 Integrate with Temi movement (separate SDK)

## Quick Command Reference

```bash
# Test gestures only
python test_reachy.py

# Run full bot (simulation)
docker-compose run --rm reachy-soul

# Run full bot (real robot)
# 1. Update .env: REACHY_SIMULATION_MODE=false
# 2. Set REACHY_HOST=<robot-ip>
docker-compose run --rm reachy-soul

# Rebuild after changes
docker-compose build --no-cache
```

---

**You're all set!** The Reachy integration is fully working in simulation mode. When you get the hardware, just update the .env and it'll work seamlessly! 🎉