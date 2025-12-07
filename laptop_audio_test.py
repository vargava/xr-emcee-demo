#!/usr/bin/env python3
"""
Laptop Audio Test Client
Uses your Mac's microphone and speaker to test the API server audio flow
"""

import socketio
import json
import base64
import speech_recognition as sr
import pyttsx3
import time

# Configuration
SERVER_URL = "http://localhost:5001"  # Socket.IO uses http:// not ws://

class LaptopAudioClient:
    """Test client using laptop's built-in mic and speaker"""
    
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.sio = socketio.Client()
        
        # Setup speech recognition (mic input)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Setup text-to-speech (speaker output)
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        self.tts.setProperty('volume', 0.9)
        
        # Setup Socket.IO event handlers
        self.setup_handlers()
        
        print("🎤 Initializing microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Ready!")
    
    def setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print(f"✅ Connected to {self.server_url}")
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print("🔌 Disconnected from server")
        
        @self.sio.on('bot_response')
        def on_bot_response(data):
            text = data.get('text', '')
            print(f"\n🤖 Bot: {text}\n")
            
            # Speak the response
            self.tts.say(text)
            self.tts.runAndWait()
        
        @self.sio.on('transcription')
        def on_transcription(data):
            print(f"📝 Heard: {data['text']}")
        
        @self.sio.on('error')
        def on_error(data):
            print(f"❌ Error: {data.get('message', 'Unknown error')}")
    
    def connect(self):
        """Connect to the API server"""
        try:
            self.sio.connect(self.server_url)
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"\nMake sure:")
            print(f"1. Docker is running: docker-compose up")
            print(f"2. API server is accessible at {self.server_url}")
            raise
    
    def send_audio(self):
        """Capture audio from mic and send to server"""
        print("\n🎤 Listening... (speak now)")
        
        try:
            with self.microphone as source:
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # Convert to WAV format
            audio_bytes = audio.get_wav_data()
            
            # Encode to base64
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Send to server via Socket.IO
            self.sio.emit('audio_chunk', {
                'audio': audio_b64,
                'format': 'wav',
                'sample_rate': 16000,
                'is_final': True
            })
            
            print("📤 Audio sent to server, waiting for response...")
            
        except sr.WaitTimeoutError:
            print("⏱️  No speech detected, try again")
        except Exception as e:
            print(f"❌ Error capturing audio: {e}")
    
    def run(self):
        """Main loop - continuously listen and respond"""
        self.connect()
        
        print("\n" + "="*60)
        print("🎙️  LAPTOP AUDIO TEST CLIENT")
        print("="*60)
        print("\nCommands:")
        print("  - Just speak when prompted")
        print("  - Press Ctrl+C to quit")
        print("\n" + "="*60 + "\n")
        
        try:
            while True:
                self.send_audio()
                
                # Small delay to hear response before next recording
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping...")
        finally:
            self.sio.disconnect()


def main():
    """Test the audio flow"""
    
    print("\n🔍 Testing API server connection...")
    
    # Check if server is reachable
    try:
        import requests
        response = requests.get("http://localhost:5001/health", timeout=2)
        print(f"✅ Server is healthy: {response.json()}")
    except Exception as e:
        print(f"❌ Cannot reach API server at http://localhost:5001")
        print(f"   Error: {e}")
        print(f"\nPlease start the server first:")
        print(f"   docker-compose up")
        return
    
    # Start audio client
    client = LaptopAudioClient()
    client.run()


if __name__ == "__main__":
    main()