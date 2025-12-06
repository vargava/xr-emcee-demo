# Friendly Host Bot 🤖

A personality-driven conversational AI agent for hackathon demonstration with Reachy robot integration.

## Quick Start (5 minutes)

### Prerequisites
- Docker Desktop installed on Mac M1
- Anthropic API key (from your Claude subscription)

### Setup

1. **Clone or copy these files to your Mac**

2. **Create your `.env` file:**
   ```bash
   cp .env.template .env
   ```
   
3. **Add your API key to `.env`:**
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

4. **Build and run:**
   ```bash
   docker-compose build
   docker-compose run --rm hackathon-bot
   ```

That's it! The bot should start and prompt you to select a personality.

## Available Personalities

1. **Pirate** - Jovial sea captain with pirate slang
2. **Garfield** - Lazy, sarcastic, food-loving cat energy
3. **Tech Bro** - Silicon Valley enthusiast with buzzwords
4. **Friendly Default** - Warm, welcoming standard host

## Usage

Once running:
- Type messages to chat with the bot
- Type `funnier` to increase humor level
- Type `reset` to clear conversation history
- Type `quit` to exit

The bot includes mentions in responses like "be funnier" or "make me laugh" to adjust humor dynamically.

## Architecture

```
User Input (text/audio) 
    ↓
Claude API (with personality system)
    ↓
Text Response + Gesture Hints
    ↓
Output (console/TTS) + Reachy Gestures
```

## Current Status (1-hour prototype)

✅ **Working:**
- Personality system (4 preset personalities)
- Claude API integration
- Dynamic humor adjustment
- Conversation memory
- Modular design for easy extension

🚧 **Stubbed (ready for integration):**
- Real microphone input (currently text-based)
- Text-to-speech output (currently console)
- Reachy robot SDK (gesture hints printed)
- Camera/video input
- XR display output

## Next Steps (Post-Hackathon)

### Phase 1: Real Audio (30 min)
- Integrate `pyaudio` for mic input
- Add `pyttsx3` or ElevenLabs for TTS
- Implement speech-to-text with Whisper or Google Speech

### Phase 2: Reachy Integration (1-2 hours)
- Install Reachy SDK
- Map emotions to actual gestures
- Test on actual Reachy hardware

### Phase 3: XR Display (2-3 hours)
- Unity project for Quest
- WebSocket communication
- Real-time text/image display

### Phase 4: Camera Input (1 hour)
- OpenCV for video capture
- Optional: Vision API integration

## Extending Personalities

Add new personalities in `main.py` → `PersonalityEngine.PERSONALITIES`:

```python
"your_personality": {
    "name": "Character Name",
    "traits": "Description of personality traits...",
    "humor_level": 5  # 1-10
}
```

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- Check your `.env` file exists
- Ensure API key is correct (starts with `sk-ant-`)

**Docker audio issues on Mac**
- Audio passthrough to Docker is complex on Mac
- For now, use text input/output
- For real audio, consider running directly on host

**Running without Docker:**
```bash
pip install -r requirements.txt
python main.py
```

## License

MIT - Built for hackathon fun! 🎉