# 🎤 Audio Test Demo - Quick Setup

## 🚀 Start API Server (Docker)

```bash
# Build and start the server
docker-compose build --no-cache && docker-compose up
```

**Wait for:** `🤖 FRIENDLY HOST BOT API SERVER` message

---

## 🎧 Setup Local Audio Test Client

### 1. Create isolated Python environment
```bash
python3 -m venv test_env
source test_env/bin/activate
```

### 2. Install dependencies
```bash
# Install PortAudio (required for microphone)
brew install portaudio

# Install Python packages
pip install websockets pyaudio SpeechRecognition pyttsx3 requests python-socketio pygame
```

### 3. Run the test
```bash
python laptop_audio_test.py
```

**Usage:**
- Speak when you see `🎤 Listening...`
- Wait 1 second of silence after speaking
- Bot will respond with ElevenLabs voice
- Press `Ctrl+C` to quit

---

## 🧹 Cleanup After Demo

### 1. Stop test client
```
Ctrl+C
```

### 2. Exit and delete Python environment
```bash
deactivate
rm -rf test_env
```

### 3. Stop Docker
```bash
docker-compose stop
docker-compose down --remove-orphans
```

---

## ⚡ Quick Reference

**Start everything:**
```bash
# Terminal 1 - API Server
docker-compose up

# Terminal 2 - Test Client
source test_env/bin/activate
python laptop_audio_test.py
```

**Stop everything:**
```bash
# Terminal 2
Ctrl+C
deactivate
rm -rf test_env

# Terminal 1
Ctrl+C
docker-compose down --remove-orphans
```

---

## 🔧 Troubleshooting

**PyAudio won't install:**
```bash
brew install portaudio
```

**Port 5000 in use:**
- Disable AirPlay Receiver in Mac System Settings
- Or use port 5001 (already configured in docker-compose.yml)

**Echo/feedback issues:**
- Use headphones
- Or speak louder and closer to mic than speaker volume

**No audio playback:**
- Check Docker logs for ElevenLabs API errors
- Verify `ELEVENLABS_API_KEY` is set in `.env`

---

## 📁 Files Needed

- `docker-compose.yml` (port 5001 exposed)
- `api_server.py` (Flask API)
- `main.py` (ConversationAgent)
- `reachy_controller.py` (gesture simulation)
- `laptop_audio_test.py` (test client)
- `.env` (ANTHROPIC_API_KEY, ELEVENLABS_API_KEY)

**That's it! 🎉**