#!/usr/bin/env python3
"""
API Server for Friendly Host Bot
Handles:
- WebSocket audio streams from Temi (mic input)
- HTTP personality controls from Meta Quest
- WebSocket audio output to Temi (speaker)
- Reachy gesture coordination
"""

import os
import json
import base64
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import speech_recognition as sr
from io import BytesIO
import wave
from dotenv import load_dotenv

# Import your existing components
# This is the KEY connection - api_server uses your existing ConversationAgent
from main import ConversationAgent, PersonalityEngine
from reachy_controller import ReachyMiniController, get_gesture_for_emotion

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Quest
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
conversation_agent = None
reachy_controller = None
speech_recognizer = sr.Recognizer()

# TTS options - we'll use a simple approach first
USE_ELEVENLABS = os.getenv("USE_ELEVENLABS", "false").lower() == "true"

if USE_ELEVENLABS:
    from elevenlabs.client import ElevenLabs
    elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def initialize_bot(personality="friendly_default", tone="neutral", scene="hackathon"):
    """Initialize the conversation agent and robot controller"""
    global conversation_agent, reachy_controller
    
    conversation_agent = ConversationAgent(personality, tone, scene)
    reachy_controller = ReachyMiniController()
    
    print(f"✅ Bot initialized: {personality} / {tone} / {scene}")


def speech_to_text(audio_data):
    """Convert audio bytes to text using ElevenLabs Speech-to-Text"""
    try:
        # If base64 encoded, decode first
        if isinstance(audio_data, str):
            audio_data = base64.b64decode(audio_data)
        
        # Wrap bytes in BytesIO for ElevenLabs
        audio_file = BytesIO(audio_data)
        
        # Use ElevenLabs Speech-to-Text
        transcription = elevenlabs_client.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",
            tag_audio_events=False,  # Set to False for simpler output
            language_code="eng",
            diarize=False,  # Set to False unless you need speaker identification
        )
        
        # Extract just the text from the transcription object
        text = transcription.text if hasattr(transcription, 'text') else str(transcription)
        print(f"📝 Transcribed: {text}")
        return text
        
    except Exception as e:
        print(f"❌ Error in speech_to_text: {e}")
        return None

def text_to_speech(text):
    """Convert text to speech audio using ElevenLabs"""
    try:
        if USE_ELEVENLABS:
            # High quality TTS
            audio_generator = elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Collect all audio bytes from the generator
            audio_bytes = b"".join(audio_generator)
            
            return base64.b64encode(audio_bytes).decode('utf-8')
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error in text_to_speech: {e}")
        return None


def get_gesture_from_response(response_text):
    """Analyze response to determine appropriate gesture"""
    response_lower = response_text.lower()
    
    # Self-deprecating (wheels/legs jokes)
    if 'wheel' in response_lower or 'roll' in response_lower or "can't walk" in response_lower:
        return "self_deprecating"
    
    # Excited/positive
    elif any(word in response_lower for word in ['great', 'awesome', 'excellent', 'amazing', 'wonderful']):
        return "excited"
    
    # Encouraging exploration
    elif any(word in response_lower for word in ['explore', 'check out', 'go see', 'meet', 'visit']):
        return "dismissive"
    
    # Thinking/questioning
    elif '?' in response_text:
        return "thinking"
    
    # Greeting
    elif any(word in response_lower for word in ['hello', 'hi ', 'hey', 'welcome']):
        return "happy"
    
    # Default
    else:
        return "neutral"


# ============================================================================
# HTTP ENDPOINTS (for Meta Quest control panel)
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot_initialized": conversation_agent is not None,
        "reachy_connected": reachy_controller.connected if reachy_controller else False
    })


@app.route('/initialize', methods=['POST'])
def initialize():
    """Initialize bot with personality settings from Quest"""
    try:
        data = request.json
        personality = data.get('personality', 'friendly_default')
        tone = data.get('tone', 'neutral')
        scene = data.get('scene', 'hackathon')
        custom_scene = data.get('custom_scene', '')
        
        initialize_bot(personality, tone, scene)
        
        if custom_scene:
            conversation_agent.set_scene(custom_scene)
        
        return jsonify({
            "status": "success",
            "message": f"Bot initialized with {personality}/{tone}",
            "config": {
                "personality": personality,
                "tone": tone,
                "scene": scene
            }
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/set_personality', methods=['POST'])
def set_personality():
    """Update personality mid-conversation"""
    if not conversation_agent:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 400
    
    try:
        data = request.json
        
        if 'personality' in data:
            personality_type = data['personality']
            if personality_type in PersonalityEngine.PERSONALITIES:
                conversation_agent.personality_engine.personality = \
                    PersonalityEngine.PERSONALITIES[personality_type]
        
        if 'tone' in data:
            conversation_agent.change_tone(data['tone'])
        
        if 'scene' in data:
            conversation_agent.set_scene(data['scene'])
        
        return jsonify({"status": "success", "message": "Settings updated"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset for new visitor"""
    if not conversation_agent:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 400
    
    try:
        data = request.json
        context_clues = data.get('context_clues', '')
        
        intro = conversation_agent.reset_for_new_person(context_clues)
        
        response_data = {
            "status": "success",
            "message": "Ready for new visitor",
            "total_visitors": conversation_agent.total_visitors
        }
        
        if intro:
            response_data["introduction"] = intro
            # Trigger happy gesture for greeting
            if reachy_controller:
                reachy_controller.perform_gesture(get_gesture_for_emotion("happy"))
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat_text():
    """
    Text-based chat endpoint (for testing without audio)
    Quest can use this to test the flow
    """
    if not conversation_agent:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 400
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"status": "error", "message": "No message provided"}), 400
        
        # Process through Claude
        response = conversation_agent.process_input(user_message)
        
        # Trigger gesture
        if reachy_controller:
            gesture = get_gesture_from_response(response)
            reachy_controller.perform_gesture(get_gesture_for_emotion(gesture))
        
        return jsonify({
            "status": "success",
            "response": response,
            "exchange_count": conversation_agent.exchange_count
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/available_options', methods=['GET'])
def get_available_options():
    """Return all available personalities, tones, and scenes for Quest UI"""
    return jsonify({
        "personalities": list(PersonalityEngine.PERSONALITIES.keys()),
        "personality_details": PersonalityEngine.PERSONALITIES,
        "tones": list(PersonalityEngine.TONES.keys()),
        "tone_details": PersonalityEngine.TONES,
        "scenes": list(PersonalityEngine.SCENES.keys()),
        "gestures": list(reachy_controller.GESTURES.keys()) if reachy_controller else []
    })


# ============================================================================
# WEBSOCKET ENDPOINTS (for Temi audio streaming)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected (Temi or Quest)"""
    print(f"🔌 Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'message': 'Connected to bot server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f"🔌 Client disconnected: {request.sid}")


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """
    Receive audio chunk from Temi
    
    Expected data format:
    {
        'audio': 'base64_encoded_audio_data',
        'format': 'wav',  # or 'raw'
        'sample_rate': 16000,
        'is_final': true/false  # true when user stops speaking
    }
    """
    try:
        if not conversation_agent:
            emit('error', {'message': 'Bot not initialized'})
            return
        
        audio_data = data.get('audio')
        is_final = data.get('is_final', True)
        
        if not is_final:
            # Not ready to process yet, accumulate chunks if needed
            return
        
        # Convert speech to text
        text = speech_to_text(audio_data)
        
        if not text:
            emit('transcription_error', {'message': 'Could not understand audio'})
            return
        
        # Emit transcription back to client
        emit('transcription', {'text': text})
        
        # Process through Claude
        response = conversation_agent.process_input(text)
        
        # Trigger gesture based on response
        if reachy_controller:
            gesture = get_gesture_from_response(response)
            reachy_controller.perform_gesture(get_gesture_for_emotion(gesture))
        
        # Convert response to speech (if using ElevenLabs)
        audio_response = text_to_speech(response)
        
        # Send response back to Temi
        emit('bot_response', {
            'text': response,
            'audio': audio_response,  # Will be None if not using ElevenLabs
            'exchange_count': conversation_agent.exchange_count
        })
        
    except Exception as e:
        print(f"❌ Error handling audio: {e}")
        emit('error', {'message': str(e)})


@socketio.on('text_message')
def handle_text_message(data):
    """
    Handle text messages via WebSocket (alternative to audio)
    Useful for testing and Quest text input
    """
    try:
        if not conversation_agent:
            emit('error', {'message': 'Bot not initialized'})
            return
        
        user_message = data.get('message', '')
        
        if not user_message:
            emit('error', {'message': 'No message provided'})
            return
        
        # Process through Claude
        response = conversation_agent.process_input(user_message)
        
        # Trigger gesture
        if reachy_controller:
            gesture = get_gesture_from_response(response)
            reachy_controller.perform_gesture(get_gesture_for_emotion(gesture))
        
        # Send response
        emit('bot_response', {
            'text': response,
            'exchange_count': conversation_agent.exchange_count
        })
        
    except Exception as e:
        print(f"❌ Error handling text message: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# STARTUP
# ============================================================================

def main():
    """Start the API server"""
    # Initialize with defaults
    initialize_bot()
    
    # Start server
    host = os.getenv("API_HOST", "0.0.0.0")  # Listen on all interfaces
    port = int(os.getenv("API_PORT", "5000"))
    
    print("\n" + "=" * 60)
    print("🤖 FRIENDLY HOST BOT API SERVER")
    print("=" * 60)
    print(f"\n🌐 Server running on http://{host}:{port}")
    print(f"\n📡 WebSocket endpoint: ws://{host}:{port}")
    print("\nEndpoints:")
    print("  HTTP:")
    print("    GET  /health")
    print("    GET  /available_options")
    print("    POST /initialize")
    print("    POST /set_personality")
    print("    POST /reset")
    print("    POST /chat")
    print("  WebSocket:")
    print("    - audio_chunk (from Temi)")
    print("    - text_message (for testing)")
    print("\n" + "=" * 60 + "\n")
    
    socketio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()