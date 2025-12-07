# Integration Guide - Phase 2 Development

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT LAYER                              │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│  Microphone │   Camera     │  Reachy      │   XR Headset    │
│   (Audio)   │   (Video)    │  (Sensors)   │   (Gestures)    │
└─────┬───────┴──────┬───────┴──────┬───────┴─────────┬───────┘
      │              │               │                  │
      v              v               v                  v
┌─────────────────────────────────────────────────────────────┐
│              PROCESSING LAYER (Docker Container)            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Speech-to-  │  │   Computer   │  │   Personality   │   │
│  │     Text     │  │    Vision    │  │     Engine      │   │
│  │  (Whisper)   │  │  (OpenCV)    │  │   (Prompts)     │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
│                            v                                 │
│                  ┌──────────────────┐                        │
│                  │   Claude API     │                        │
│                  │  (Sonnet 4.5)    │                        │
│                  └─────────┬────────┘                        │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             v
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                             │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│  Speakers   │   Display    │   Reachy     │   XR Headset    │
│    (TTS)    │   (Text)     │  (Motion)    │  (Visuals)      │
└─────────────┴──────────────┴──────────────┴─────────────────┘
```

## Phase-by-Phase Integration

### PHASE 1: Real Audio (30-60 minutes)

**Current Status:** Text-based console I/O  
**Goal:** Real microphone input and speaker output

#### 1.1 Speech-to-Text Integration

Replace `SimpleAudioHandler.capture_audio()` with:

```python
import speech_recognition as sr

class RealAudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def capture_audio(self):
        """Capture audio from microphone and convert to text"""
        with self.microphone as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error: {e}")
            return None
```

#### 1.2 Text-to-Speech Integration

Replace `SimpleAudioHandler.play_audio()` with:

```python
import pyttsx3

class RealAudioHandler:
    def __init__(self):
        # ... microphone setup ...
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed
        self.tts_engine.setProperty('volume', 0.9)
    
    def play_audio(self, text):
        """Convert text to speech and play"""
        print(f"🔊 Bot says: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        return True
```

**Alternative (Better Quality):** Use ElevenLabs API
```python
# pip install elevenlabs
from elevenlabs import generate, play, set_api_key

def play_audio(self, text):
    audio = generate(text=text, voice="Adam", model="eleven_monolingual_v1")
    play(audio)
```

### PHASE 2: Reachy Robot Integration (1-2 hours)

**Prerequisites:**
- Reachy robot on same network
- Reachy SDK installed: `pip install reachy-sdk`

#### 2.1 Connect to Reachy

```python
from reachy_sdk import ReachySDK

class ReachyController:
    def __init__(self, reachy_ip="localhost"):
        try:
            self.reachy = ReachySDK(host=reachy_ip)
            self.connected = True
            print(f"✅ Connected to Reachy at {reachy_ip}")
        except Exception as e:
            print(f"⚠️ Could not connect to Reachy: {e}")
            self.connected = False
    
    def perform_gesture(self, emotion="neutral"):
        """Perform actual Reachy gestures"""
        if not self.connected:
            return
        
        gestures = {
            "happy": self._wave_hello,
            "thinking": self._tilt_head,
            "excited": self._raise_arms,
            "neutral": self._nod
        }
        
        gesture_func = gestures.get(emotion, self._nod)
        gesture_func()
    
    def _wave_hello(self):
        """Wave with right arm"""
        # Move to waving position
        self.reachy.r_arm.r_shoulder_pitch.goal_position = -60
        self.reachy.r_arm.r_elbow_pitch.goal_position = -90
        # Wave motion
        for _ in range(3):
            self.reachy.r_arm.r_wrist_yaw.goal_position = 30
            time.sleep(0.3)
            self.reachy.r_arm.r_wrist_yaw.goal_position = -30
            time.sleep(0.3)
        # Return to rest
        self.reachy.goto_rest_position()
    
    def _nod(self):
        """Nod head gently"""
        self.reachy.head.neck_pitch.goal_position = 10
        time.sleep(0.5)
        self.reachy.head.neck_pitch.goal_position = -10
        time.sleep(0.5)
        self.reachy.head.neck_pitch.goal_position = 0
```

#### 2.2 Emotion Detection from Claude Response

Add sentiment analysis to map responses to gestures:

```python
def analyze_emotion(text):
    """Simple keyword-based emotion detection"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['great', 'awesome', 'excellent', 'wonderful']):
        return "happy"
    elif any(word in text_lower for word in ['hmm', 'think', 'consider', '?']):
        return "thinking"
    elif any(word in text_lower for word in ['wow', 'amazing', '!!']):
        return "excited"
    else:
        return "neutral"
```

### PHASE 3: Camera/Computer Vision (1 hour)

#### 3.1 Video Capture

```python
import cv2

class VisionHandler:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # Default camera
        
    def capture_frame(self):
        """Capture a single frame"""
        ret, frame = self.camera.read()
        if ret:
            return frame
        return None
    
    def save_snapshot(self, filename="snapshot.jpg"):
        """Save current frame"""
        frame = self.capture_frame()
        if frame is not None:
            cv2.imwrite(filename, frame)
            return filename
        return None
```

#### 3.2 Send Image to Claude

```python
import base64

def process_with_vision(self, user_text, image_path=None):
    """Process text with optional image context"""
    
    content = [{"type": "text", "text": user_text}]
    
    if image_path:
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode()
        
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_data
            }
        })
    
    message = self.client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=self.personality_engine.get_system_prompt(),
        messages=[{"role": "user", "content": content}]
    )
    
    return message.content[0].text
```

### PHASE 4: XR/Unity Integration (2-3 hours)

#### 4.1 Unity Setup for Meta Quest

**Unity Project Structure:**
```
XRHostDisplay/
├── Assets/
│   ├── Scenes/
│   │   └── MainDisplay.unity
│   ├── Scripts/
│   │   ├── WebSocketClient.cs
│   │   ├── TextDisplay.cs
│   │   └── PersonalityVisualizer.cs
│   └── Materials/
└── Packages/
    └── XR Plugin Management
```

#### 4.2 WebSocket Communication (Python Side)

```python
# pip install websockets
import asyncio
import websockets
import json

class XRBridge:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.connections = set()
    
    async def handle_connection(self, websocket):
        self.connections.add(websocket)
        try:
            async for message in websocket:
                # Handle incoming messages from Quest
                pass
        finally:
            self.connections.remove(websocket)
    
    async def send_response(self, text, emotion="neutral"):
        """Send bot response to all connected XR devices"""
        if not self.connections:
            return
        
        data = json.dumps({
            "type": "response",
            "text": text,
            "emotion": emotion,
            "timestamp": time.time()
        })
        
        await asyncio.gather(
            *[conn.send(data) for conn in self.connections]
        )
    
    async def start(self):
        """Start WebSocket server"""
        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()  # Run forever
```

#### 4.3 Unity WebSocket Client (C#)

```csharp
using UnityEngine;
using WebSocketSharp;
using TMPro;

public class WebSocketClient : MonoBehaviour
{
    private WebSocket ws;
    public TextMeshProUGUI responseText;
    
    void Start()
    {
        // Connect to Python backend
        ws = new WebSocket("ws://YOUR_DOCKER_IP:8765");
        
        ws.OnMessage += (sender, e) => {
            var data = JsonUtility.FromJson<BotResponse>(e.Data);
            DisplayResponse(data);
        };
        
        ws.Connect();
    }
    
    void DisplayResponse(BotResponse response)
    {
        responseText.text = response.text;
        // Trigger animations based on emotion
        UpdateVisuals(response.emotion);
    }
}
```

## Docker Networking for Multi-Component Setup

Update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hackathon-bot:
    build: .
    container_name: friendly-host-bot
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    ports:
      - "8765:8765"  # WebSocket for XR
      - "5000:5000"  # Optional REST API
    volumes:
      - ./:/app
      - /dev/snd:/dev/snd
    devices:
      - /dev/snd
      - /dev/video0  # Camera access
    network_mode: bridge
```

## Testing Strategy

### Unit Tests
```bash
# Test API connection
python test_api.py

# Test audio (Phase 1)
python -c "from main import RealAudioHandler; h = RealAudioHandler(); h.capture_audio()"

# Test Reachy connection (Phase 2)
python -c "from main import ReachyController; r = ReachyController('reachy.local'); print(r.connected)"
```

### Integration Tests
```bash
# Full system test
docker-compose run --rm hackathon-bot
```

## Troubleshooting

**Audio doesn't work in Docker on Mac**
- Run directly: `python main.py` (install deps: `pip install -r requirements.txt`)
- Audio devices are hard to pass to Docker on macOS

**Reachy not connecting**
- Check network: `ping reachy.local`
- Verify Reachy SDK version matches robot firmware
- Check firewall settings

**XR headset can't connect**
- Ensure Quest and computer on same network
- Check WebSocket port (8765) is exposed
- Use Docker host IP, not localhost

## Next-Level Features

1. **Multi-modal responses** - Images + text in XR
2. **Gesture recognition** - Quest hand tracking → commands
3. **Spatial audio** - 3D positioned TTS in XR
4. **Emotion recognition** - CV on user's face
5. **Multi-user** - Multiple people at hackathon booth

## Performance Tips

- Use `claude-haiku-4` for faster responses (sub-second)
- Cache common responses for repeated questions
- Stream responses word-by-word for lower latency
- Use local STT (Whisper) instead of cloud APIs

Good luck at the hackathon! 🚀