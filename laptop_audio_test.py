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
import threading
from pynput import keyboard

# Configuration
SERVER_URL = "http://localhost:5001"  # Socket.IO uses http:// not ws://

class LaptopAudioClient:
    """Test client using laptop's built-in mic and speaker"""
    
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.sio = socketio.Client()
        
        # State management - prevent listening while bot is speaking
        self.bot_is_speaking = False
        self.waiting_for_response = False
        self.last_audio_sent_time = 0
        self.response_timeout = 15  # seconds
        
        # Setup speech recognition (mic input)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust recognition sensitivity
        self.recognizer.energy_threshold = 6000  # Very high - only capture loud/close speech
        self.recognizer.dynamic_energy_threshold = False  # Don't auto-adjust
        self.recognizer.pause_threshold = 1.5  # Longer pause before considering done
        
        # Setup text-to-speech (speaker output)
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        self.tts.setProperty('volume', 0.9)
        
        # Setup Socket.IO event handlers
        self.setup_handlers()
        
        # Setup keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        
        print("🎤 Initializing microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Ready!")
    
    def on_key_press(self, key):
        """Handle keyboard shortcuts"""
        try:
            # Spacebar - Reset conversation
            if key == keyboard.Key.space:
                print("\n⚡ SPACEBAR: Resetting conversation...")
                self.reset_conversation()
                return
            
            # Up arrow - Make conversation funnier
            if key == keyboard.Key.up:
                print("\n⚡ UP ARROW: Making it funnier...")
                self.change_tone("funnier")
                return
            
            # Right arrow - Switch to pirate
            if key == keyboard.Key.right:
                print("\n⚡ RIGHT ARROW: Switching to pirate...")
                self.change_personality("pirate")
                return
                
        except AttributeError:
            # Not a special key
            pass
    
    def reset_conversation(self):
        """Reset for new visitor"""
        try:
            # Pause audio immediately
            self.bot_is_speaking = True
            self.waiting_for_response = False  # Clear waiting flag!
            
            time.sleep(0.3)  # Let any pending audio clear
            
            # Make API call
            import requests
            response = requests.post(
                self.server_url + '/reset',
                json={'context_clues': ''},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Reset! Visitor #{data.get('total_visitors', '?')}\n")
            else:
                print(f"❌ Reset failed: {response.text}")
            
            # Resume listening - clear ALL flags
            time.sleep(0.5)
            self.bot_is_speaking = False
            self.waiting_for_response = False  # Ensure it's clear!
            
        except Exception as e:
            print(f"❌ Reset error: {e}")
            self.bot_is_speaking = False
            self.waiting_for_response = False
    
    def change_tone(self, tone):
        """Change conversational tone"""
        try:
            import requests
            response = requests.post(
                self.server_url + '/set_personality',
                json={'tone': tone},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Tone → {tone}\n")
            else:
                print(f"❌ Tone change failed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def change_personality(self, personality):
        """Change bot personality"""
        try:
            import requests
            response = requests.post(
                self.server_url + '/set_personality',
                json={'personality': personality},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Personality → {personality}\n")
            else:
                print(f"❌ Personality change failed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print(f"✅ Connected to {self.server_url}")
            # Reset state on reconnect
            self.bot_is_speaking = False
            self.waiting_for_response = False
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print("🔌 Disconnected from server")
            # Clear waiting state
            self.waiting_for_response = False
            self.bot_is_speaking = False
        
        @self.sio.on('bot_response')
        def on_bot_response(data):
            text = data.get('text', '')
            audio_b64 = data.get('audio')  # ElevenLabs audio in base64
            
            print(f"\n🤖 Bot: {text}\n")
            
            # Set speaking flag BEFORE speaking
            self.bot_is_speaking = True
            self.waiting_for_response = False
            
            # Play the audio
            if audio_b64:
                # We have ElevenLabs audio - play it!
                try:
                    import pygame
                    from io import BytesIO
                    
                    # Decode base64 audio
                    audio_bytes = base64.b64decode(audio_b64)
                    
                    # Initialize pygame mixer if not already
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    
                    # Load and play audio
                    audio_file = BytesIO(audio_bytes)
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    
                    # Wait for audio to finish
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    print("🔊 ElevenLabs audio finished")
                    
                    # Short buffer to let sound dissipate
                    time.sleep(1)
                    
                except ImportError:
                    print("⚠️  pygame not installed, using fallback TTS")
                    # Fallback to pyttsx3
                    self.tts.say(text)
                    self.tts.runAndWait()
                    # Need longer wait for pyttsx3
                    word_count = len(text.split())
                    time.sleep(max(3, (word_count / 2.5) + 2))
                except Exception as e:
                    print(f"⚠️  Audio playback error: {e}, using fallback TTS")
                    self.tts.say(text)
                    self.tts.runAndWait()
                    # Need longer wait for pyttsx3
                    word_count = len(text.split())
                    time.sleep(max(3, (word_count / 2.5) + 2))
            else:
                # No audio from server, use local TTS
                print("ℹ️  No audio from server, using local TTS")
                self.tts.say(text)
                self.tts.runAndWait()
                # Need longer wait for pyttsx3
                word_count = len(text.split())
                time.sleep(max(3, (word_count / 2.5) + 2))
            
            # Done speaking
            self.bot_is_speaking = False
            print("✅ Ready to listen again...")
        
        @self.sio.on('transcription')
        def on_transcription(data):
            print(f"📝 Transcribed: {data['text']}")
            self.waiting_for_response = True
        
        @self.sio.on('error')
        def on_error(data):
            print(f"❌ Error: {data.get('message', 'Unknown error')}")
            self.waiting_for_response = False
    
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
        
        # Don't listen if bot is currently speaking
        if self.bot_is_speaking:
            time.sleep(0.5)
            return
        
        # Check if we've been waiting too long for a response
        if self.waiting_for_response:
            elapsed = time.time() - self.last_audio_sent_time
            if elapsed > self.response_timeout:
                print(f"⏱️  Response timeout ({elapsed:.0f}s), resetting...")
                self.waiting_for_response = False
            else:
                time.sleep(0.5)
                return
        
        print("\n🎤 Listening... (speak now)")
        
        try:
            with self.microphone as source:
                # Listen for speech with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Check if we actually captured meaningful audio
            # If audio is too short, skip it (likely noise or echo)
            audio_duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
            if audio_duration < 1.0:  # Less than 1 second - likely echo
                print("⏭️  Audio too short (echo?), skipping...")
                return
            
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
            self.waiting_for_response = True
            self.last_audio_sent_time = time.time()  # Track when we sent it
            
        except sr.WaitTimeoutError:
            # No speech detected - this is normal, just continue
            pass
        except Exception as e:
            print(f"❌ Error capturing audio: {e}")
    
    def run(self):
        """Main loop - continuously listen and respond"""
        self.connect()
        
        # Start keyboard listener in background
        self.keyboard_listener.start()
        
        print("\n" + "="*60)
        print("🎙️  LAPTOP AUDIO TEST CLIENT")
        print("="*60)
        print("\nHow it works:")
        print("  1. Speak naturally when you see '🎤 Listening...'")
        print("  2. Wait 1 second of silence after speaking")
        print("  3. Bot will respond and speak back")
        print("  4. After bot finishes, you can speak again")
        print("\n⌨️  Keyboard shortcuts:")
        print("  SPACEBAR    → Reset conversation (new visitor)")
        print("  UP ARROW    → Make conversation funnier")
        print("  RIGHT ARROW → Switch to pirate personality")
        print("\nPress Ctrl+C to quit")
        print("="*60 + "\n")
        
        try:
            while True:
                self.send_audio()
                # Short sleep to avoid tight loop
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping...")
        finally:
            self.keyboard_listener.stop()
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