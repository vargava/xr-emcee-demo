"""
Temi Audio Client - Example Integration
This shows how to stream audio from Temi's microphone to your Docker API

NOTE: This is example code showing the pattern. Actual Temi SDK integration
will depend on whether you're:
1. Running this on Temi's Android tablet (use Temi Android SDK)
2. Or connecting to Temi remotely (use Temi's REST API)

For hackathon speed, OPTION 2 is recommended if Temi supports it.
"""

import asyncio
import websockets
import json
import base64
import pyaudio
import wave
from io import BytesIO

class TemiAudioClient:
    """
    Client that captures audio from Temi's mic and streams to Docker API
    """
    
    def __init__(self, server_url="ws://192.168.1.100:5000"):
        """
        Args:
            server_url: WebSocket URL of your Docker API server
                       (use your MacBook's local IP, not localhost)
        """
        self.server_url = server_url
        self.websocket = None
        
        # Audio settings - match what Temi provides
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"✅ Connected to {self.server_url}")
            
            # Listen for responses
            asyncio.create_task(self.listen_for_responses())
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    async def listen_for_responses(self):
        """Listen for bot responses from server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get('type') == 'bot_response' or 'text' in data:
                    text = data.get('text', '')
                    audio_b64 = data.get('audio')
                    
                    print(f"\n🤖 Bot: {text}\n")
                    
                    # If audio provided, play it (or send to Temi's speaker)
                    if audio_b64:
                        self.play_audio(base64.b64decode(audio_b64))
                    else:
                        # Use Temi's built-in TTS
                        self.speak_on_temi(text)
                
                elif data.get('type') == 'transcription':
                    print(f"📝 Heard: {data['text']}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
    
    def start_listening(self):
        """Start capturing audio from microphone"""
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        print("🎤 Listening... (Press Ctrl+C to stop)")
    
    def stop_listening(self):
        """Stop audio capture"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    async def stream_audio(self, duration_seconds=5):
        """
        Capture and stream audio for specified duration
        
        Args:
            duration_seconds: How long to record
        """
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * duration_seconds)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        
        # Convert to WAV format
        audio_data = b''.join(frames)
        
        # Encode to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send to server
        await self.websocket.send(json.dumps({
            'event': 'audio_chunk',
            'audio': audio_b64,
            'format': 'raw',
            'sample_rate': self.RATE,
            'is_final': True
        }))
        
        print("📤 Audio sent to server")
    
    async def send_text_message(self, message):
        """Send text message instead of audio (for testing)"""
        await self.websocket.send(json.dumps({
            'event': 'text_message',
            'message': message
        }))
    
    def speak_on_temi(self, text):
        """
        Use Temi's built-in TTS to speak
        
        If running on Temi's tablet, use Temi SDK:
        from com.robotemi.sdk import Robot
        robot = Robot.getInstance()
        robot.speak(text)
        
        For now, this is a placeholder
        """
        print(f"🔊 [Temi should speak]: {text}")
        # TODO: Integrate Temi SDK TTS here
    
    def play_audio(self, audio_bytes):
        """Play audio on Temi's speaker (if server provides TTS audio)"""
        # TODO: Send to Temi's speaker
        print("🔊 [Playing audio on Temi]")
    
    async def run_conversation_loop(self):
        """Main conversation loop - listens and responds"""
        await self.connect()
        self.start_listening()
        
        try:
            while True:
                # Wait for voice activity detection (VAD)
                # For simplicity, we'll record in chunks
                print("\n🎤 Speak now...")
                await self.stream_audio(duration_seconds=3)
                
                # Wait for response before next recording
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
        finally:
            self.stop_listening()
            await self.websocket.close()
    
    def __del__(self):
        """Cleanup"""
        self.audio.terminate()


# ============================================================================
# SIMPLIFIED VERSION - Voice Activity Detection
# ============================================================================

class TemiAudioClientVAD:
    """
    Smarter version that detects when user is speaking
    Records while they talk, stops when silent
    """
    
    def __init__(self, server_url="ws://192.168.1.100:5000"):
        self.server_url = server_url
        self.websocket = None
        self.recognizer = None
        
        # Use SpeechRecognition library for easier VAD
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except ImportError:
            print("⚠️ speech_recognition not installed. Install: pip install SpeechRecognition")
    
    async def connect(self):
        self.websocket = await websockets.connect(self.server_url)
        print(f"✅ Connected to {self.server_url}")
        asyncio.create_task(self.listen_for_responses())
    
    async def listen_for_responses(self):
        async for message in self.websocket:
            data = json.loads(message)
            if 'text' in data:
                text = data['text']
                print(f"\n🤖 Bot: {text}\n")
                # Use Temi TTS here
    
    async def listen_and_send(self):
        """Listen for speech and send to server"""
        with self.microphone as source:
            print("🎤 Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source)
            
            while True:
                print("\n🎤 Listening...")
                try:
                    # This blocks until speech is detected
                    audio = self.recognizer.listen(source, timeout=30)
                    
                    # Convert to bytes
                    audio_bytes = audio.get_wav_data()
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    
                    # Send to server
                    await self.websocket.send(json.dumps({
                        'event': 'audio_chunk',
                        'audio': audio_b64,
                        'format': 'wav',
                        'sample_rate': 16000,
                        'is_final': True
                    }))
                    
                    print("📤 Sent audio to server")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    async def run(self):
        await self.connect()
        await self.listen_and_send()


# ============================================================================
# MAIN - Example Usage
# ============================================================================

async def main():
    # Replace with your MacBook's local IP
    SERVER_URL = "ws://192.168.1.100:5000"
    
    print("=" * 60)
    print("🎤 Temi Audio Client")
    print("=" * 60)
    print(f"\nConnecting to: {SERVER_URL}")
    print("\nMake sure:")
    print("1. Docker API server is running on your MacBook")
    print("2. Temi and MacBook are on same WiFi network")
    print("3. You've replaced SERVER_URL with your MacBook's IP")
    print("\n" + "=" * 60 + "\n")
    
    # Use the simpler VAD version
    client = TemiAudioClientVAD(SERVER_URL)
    
    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())