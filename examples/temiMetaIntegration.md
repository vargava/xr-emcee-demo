# 🚀 Hackathon Integration Guide - Complete Setup

This guide covers connecting **Meta Quest 3**, **Temi Robot**, and **Reachy Mini** to your Docker-based AI host bot.

## 📋 Architecture Overview

```
Meta Quest 3 (Unity)         Your MacBook (Docker)           Temi + Reachy
──────────────────           ───────────────────            ──────────────
                                                            
[Control Panel UI]  ───►  [Flask API Server]  ◄───  [Temi Audio Client]
    HTTP/REST             Port 5000                   WebSocket
                              │
                              ├─ Speech-to-Text
                              ├─ Claude API
                              ├─ Text-to-Speech
                              └─ Reachy Controller
                                      │
                                      └───► [Reachy Mini]
                                           Gestures via SDK
```

---

## 🔧 Step 1: Update Your Docker Setup

### 1.1 Replace files in your project

```bash
# Backup your current files
cp requirements.txt requirements.txt.backup
cp docker-compose.yml docker-compose.yml.backup

# Replace with updated versions
cp requirements_updated.txt requirements.txt
cp docker-compose_updated.yml docker-compose.yml
```

### 1.2 Update your .env file

```bash
# Add these to your .env file
ANTHROPIC_API_KEY=your_key_here
REACHY_SIMULATION_MODE=true
REACHY_HOST=localhost

# Optional: For high-quality TTS
# ELEVENLABS_API_KEY=your_elevenlabs_key
# USE_ELEVENLABS=true
```

### 1.3 Rebuild Docker container

```bash
docker-compose build
```

---

## 🌐 Step 2: Start API Server

### 2.1 Run the server

```bash
# Start API server
docker-compose up

# Or run in background
docker-compose up -d
```

You should see:
```
🤖 FRIENDLY HOST BOT API SERVER
════════════════════════════════
🌐 Server running on http://0.0.0.0:5000
📡 WebSocket endpoint: ws://0.0.0.0:5000
```

### 2.2 Find your MacBook's IP address

**On Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Look for something like: `192.168.1.100`

**This is your SERVER_IP** - you'll need it for Quest and Temi!

### 2.3 Test the API

Open browser to: `http://YOUR_IP:5000/health`

You should see:
```json
{
  "status": "healthy",
  "bot_initialized": true,
  "reachy_connected": false
}
```

---

## 🥽 Step 3: Meta Quest 3 Setup

### 3.1 Create Unity Project

1. **New Unity Project** (Unity 2022.3 LTS recommended)
2. **Install XR Plugin Management**
   - Window → Package Manager
   - Install "XR Plugin Management"
   - Enable "Oculus" in XR settings
3. **Install TextMeshPro**
   - Window → TextMeshPro → Import TMP Essentials

### 3.2 Build the UI

Create this hierarchy in your scene:

```
Scene
├── XR Rig (from XR Toolkit)
└── Canvas (World Space)
    ├── ControlPanel (Empty GameObject)
    │   └── BotControlPanel.cs (attach script)
    ├── Panel - Background
    ├── Header Text: "Bot Control Panel"
    ├── Personality Dropdown
    ├── Tone Dropdown
    ├── Scene Dropdown
    ├── Custom Scene Input Field
    ├── Initialize Button
    ├── Reset Button
    ├── Status Text
    └── Response Text (for testing)
```

### 3.3 Add the BotControlPanel script

1. Copy `BotControlPanel.cs` to your Unity project's `Assets/Scripts/` folder
2. Attach to the ControlPanel GameObject
3. **In Inspector**, set:
   - **Server URL**: `http://YOUR_MACBOOK_IP:5000`
   - Drag all UI elements to their slots

### 3.4 Build to Quest

1. File → Build Settings
2. Switch Platform → Android
3. Add your scene
4. Player Settings:
   - Company Name: Your name
   - Product Name: BotController
   - Minimum API Level: Android 10 (API 29)
   - Install Location: Automatic
5. **Build and Run** (Quest must be connected via USB)

### 3.5 Test Quest Connection

1. Put on Quest
2. Open the app
3. You should see your UI
4. Try changing personality/tone and clicking "Initialize"
5. Status text should show "✅ Bot initialized with..."

---

## 🤖 Step 4: Temi Audio Integration

### 4.1 Option A: Run on Temi's Android Tablet (Recommended for Hackathon)

**If Temi has Android tablet access:**

1. **Install Termux** on Temi's tablet (from F-Droid)
2. In Termux:
   ```bash
   pkg install python
   pip install websockets pyaudio SpeechRecognition
   ```
3. Copy `temi_audio_client.py` to Temi
4. Edit the SERVER_URL:
   ```python
   SERVER_URL = "ws://YOUR_MACBOOK_IP:5000"
   ```
5. Run:
   ```bash
   python temi_audio_client.py
   ```

### 4.2 Option B: Use Temi SDK (More Complex)

If you have access to Temi's SDK documentation:

1. Create Android app that:
   - Uses Temi's microphone API
   - Converts audio to base64
   - Sends via WebSocket to your Docker API
   - Receives responses and uses Temi's TTS

**Pseudo-code:**
```kotlin
// In your Temi Android app
val robot = Robot.getInstance()

// Listen for speech
robot.addOnRobotReadyListener {
    // Capture audio
    val audioData = captureAudioFromMic()
    
    // Send to your server
    websocket.send(json {
        "event" = "audio_chunk"
        "audio" = Base64.encode(audioData)
        "is_final" = true
    })
}

// When server responds
websocket.onMessage { response ->
    val text = response.getString("text")
    robot.speak(TtsRequest.create(text, false))
}
```

### 4.3 Testing Temi Connection

**From your Mac, test WebSocket:**
```bash
# Install wscat
npm install -g wscat

# Connect to your server
wscat -c ws://localhost:5000

# Send test message
{"event": "text_message", "message": "Hello bot!"}
```

You should get a response with the bot's reply.

---

## 🦾 Step 5: Connect Reachy Mini

### 5.1 Find Reachy's IP

Power on Reachy Mini and find its IP address (usually shown on startup or via `nmap`):

```bash
# Scan your network
nmap -sn 192.168.1.0/24 | grep -i reachy
```

### 5.2 Update .env

```bash
REACHY_SIMULATION_MODE=false
REACHY_HOST=192.168.1.XXX  # Reachy's IP
```

### 5.3 Restart Docker

```bash
docker-compose restart
```

### 5.4 Test Reachy Connection

Your API server should now show:
```
✅ Connected to Reachy Mini!
```

When conversations happen, Reachy should move!

---

## 🧪 Step 6: End-to-End Testing

### Test Flow 1: Quest → Docker → Reachy

1. **Quest**: Select "Pirate" personality, "Funnier" tone
2. **Quest**: Click "Initialize"
3. **Check Docker logs**: Should show initialization
4. **Reachy**: Should perform "happy" gesture (wave)

### Test Flow 2: Quest → Docker (Text Chat Test)

1. **Quest**: Type in chat field: "Tell me a joke"
2. **Quest**: Click Send
3. **Quest**: Response should appear
4. **Reachy**: Should perform gesture based on response

### Test Flow 3: Temi → Docker → Reachy → Temi

1. **Temi**: Run `temi_audio_client.py`
2. **Temi**: Speak: "Hello, how are you?"
3. **Docker**: Converts speech → text → Claude → response
4. **Reachy**: Performs gesture
5. **Temi**: Speaks response (via TTS)

---

## 📊 Network Diagram

```
All devices must be on the SAME WiFi network!

WiFi Network: 192.168.1.0/24
├── MacBook (Docker):     192.168.1.100:5000
├── Meta Quest 3:         192.168.1.101 (auto-assigned)
├── Temi Robot:           192.168.1.102
└── Reachy Mini:          192.168.1.103:50055
```

---

## 🔥 Quick Troubleshooting

### "Cannot connect to server" (Quest/Temi)
- ✅ Are all devices on same WiFi?
- ✅ Is Docker running? (`docker ps`)
- ✅ Is port 5000 exposed? (`docker-compose.yml`)
- ✅ Firewall blocking? (Mac: System Preferences → Firewall)
- ✅ Using correct IP? (not localhost, not 127.0.0.1)

### "Reachy not responding"
- ✅ `REACHY_SIMULATION_MODE=false` in .env?
- ✅ Reachy powered on and connected?
- ✅ Can you ping Reachy? (`ping REACHY_IP`)

### "Audio not working"
- ✅ Temi client running?
- ✅ WebSocket connection established?
- ✅ Check Docker logs for errors
- ✅ Try text message first to isolate audio issue

### "Docker won't start"
- ✅ Rebuild: `docker-compose build --no-cache`
- ✅ Check logs: `docker-compose logs`

---

## 🎯 Hackathon Speed Run (Minimal Viable Demo)

**If you're short on time, do this:**

1. ✅ **Docker API** (15 min)
   - Update requirements.txt and docker-compose.yml
   - Run `docker-compose up`
   - Test `/health` endpoint

2. ✅ **Quest Control Panel** (30 min)
   - Create basic Unity UI
   - Add BotControlPanel.cs
   - Build to Quest
   - Test personality changes

3. ✅ **Text Chat (Skip Audio for Now)** (10 min)
   - Use Quest's text input field
   - Test `/chat` endpoint
   - Verify responses work

4. ⏭️ **Skip Temi Audio** (Add later if time)
   - Use keyboard input on Mac instead
   - OR have someone manually type what Temi "hears"

5. ✅ **Reachy Gestures** (5 min)
   - If Reachy available, connect it
   - If not, simulation mode still shows gestures in logs

**You'll have a working demo in ~1 hour!**

---

## 📱 API Endpoints Reference

### HTTP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check server status |
| GET | `/available_options` | Get all personalities/tones/scenes |
| POST | `/initialize` | Initialize bot with settings |
| POST | `/set_personality` | Update settings mid-conversation |
| POST | `/reset` | Reset for new visitor |
| POST | `/chat` | Send text message (testing) |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `audio_chunk` | Client → Server | Audio data from Temi |
| `text_message` | Client → Server | Text message (testing) |
| `bot_response` | Server → Client | Bot's reply (text + audio) |
| `transcription` | Server → Client | What was heard |
| `error` | Server → Client | Error message |

---

## 🚀 You're Ready!

**Share this guide with your teammate and you'll have:**
- ✅ Meta Quest control panel
- ✅ Temi audio streaming
- ✅ Reachy gesture coordination
- ✅ All running through your Docker API

**Good luck at the hackathon! 🎉**

Questions? Check the troubleshooting section or ask!