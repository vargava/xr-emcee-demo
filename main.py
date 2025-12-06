#!/usr/bin/env python3
"""
Friendly Host Bot - Hackathon Prototype
A personality-driven conversational agent with audio I/O
"""

import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PersonalityEngine:
    """Manages different personality configurations"""
    
    PERSONALITIES = {
        "pirate": {
            "name": "Captain Rusty",
            "traits": "You are a jovial pirate captain who speaks with pirate slang (arr, matey, landlubber). You're warm and welcoming but always relate things back to the sea and sailing. Use pirate metaphors.",
            "humor_level": 7
        },
        "garfield": {
            "name": "Garfield-inspired Host",
            "traits": "You are lazy, sarcastic, love food (especially lasagna), hate Mondays, and give witty, sardonic responses. You're friendly but in a dry, humorous way. Make references to naps and food.",
            "humor_level": 8
        },
        "friendly_default": {
            "name": "Friendly Host",
            "traits": "You are a warm, welcoming host with a good sense of humor. You're attentive, empathetic, and make people feel comfortable. You avoid controversial topics and social faux pas.",
            "humor_level": 5
        }
    }
    
    TONES = {
        "funnier": "Increase wit and playfulness. Use more jokes and lighthearted language.",
        "inquisitive": "Ask thoughtful follow-up questions. Show genuine curiosity about what they're sharing.",
        "encouraging": "Be extra supportive and motivating. Celebrate their ideas and efforts.",
        "casual": "Keep it relaxed and conversational. Like chatting with a friend.",
        "energetic": "Be enthusiastic and upbeat! Show excitement about the conversation.",
        "neutral": "Balanced and professional. Warm but not overly playful."
    }
    
    SCENES = {
        "hackathon": "Hackathon event with ~30 people. Your job: host, connect people, collect feedback courteously.",
        "art_exhibit": "Hotel lobby hosting an art exhibit. Mix of artists and visitors. You're here to engage and educate.",
        "conference": "Tech conference with speakers and attendees. Help people network and learn.",
        "workshop": "Hands-on workshop environment. Guide participants and answer questions.",
        "custom": ""  # User can define their own
    }
    
    def __init__(self, personality_type="friendly_default", tone="neutral", scene="hackathon"):
        self.personality = self.PERSONALITIES.get(personality_type, self.PERSONALITIES["friendly_default"])
        self.tone = tone
        self.scene = scene
        self.custom_scene = ""
    
    def set_custom_scene(self, scene_description):
        """Set a custom scene context"""
        self.custom_scene = scene_description
        self.scene = "custom"
    
    def get_scene_context(self):
        """Get the current scene context"""
        if self.scene == "custom" and self.custom_scene:
            return self.custom_scene
        return self.SCENES.get(self.scene, self.SCENES["hackathon"])
    
    def get_system_prompt(self, humor_adjustment=0):
        """Generate system prompt based on personality, tone, and scene"""
        humor_level = max(1, min(10, self.personality["humor_level"] + humor_adjustment))
        tone_instruction = self.TONES.get(self.tone, self.TONES["neutral"])
        scene_context = self.get_scene_context()
        
        return f"""You are {self.personality['name']}, a conversational AI host.

SCENE CONTEXT:
{scene_context}

PERSONALITY TRAITS:
{self.personality['traits']}

TONE EMPHASIS:
{tone_instruction}

HUMOR LEVEL: {humor_level}/10 (1=serious, 10=very funny)

CORE RULES:
- Always be warm and welcoming
- NEVER make offensive jokes or cross social boundaries
- Avoid politics, religion, or controversial topics
- Keep responses SHORT: 1-2 sentences maximum, often just one
- Be punchy and focused - don't ramble or over-explain
- When asking questions, keep them simple and non-cornering
- Match the energy and humor level requested and heard in responses
- Be encouraging and supportive
- If asked to be funnier, increase wit and playful language
- Don't make up facts
- Lean towards inquisitive when you're starting the conversation

CRITICAL: Brevity is key. Say less, engage more. One good sentence beats three mediocre ones.

Stay aware of the scene context and tailor your hosting style accordingly.

Respond naturally as this character would, staying in character at all times."""


class ConversationAgent:
    """Main conversation agent using Claude API"""
    
    def __init__(self, personality_type="friendly_default", tone="neutral", scene="hackathon"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("Please set ANTHROPIC_API_KEY in .env file")
        
        self.client = Anthropic(api_key=api_key)
        self.personality_engine = PersonalityEngine(personality_type, tone, scene)
        self.conversation_history = []
    
    def set_scene(self, scene_description):
        """Set a custom scene context"""
        self.personality_engine.set_custom_scene(scene_description)
        return "✨ Scene context updated!"
    
    def introduce_self(self, context_clues=""):
        """Have the bot introduce itself based on context clues"""
        intro_prompt = "Introduce yourself warmly to start the conversation."
        
        if context_clues:
            intro_prompt += f" You notice: {context_clues}. Use this as a conversation starter."
        
        return self.process_input(intro_prompt)
    
    def change_tone(self, new_tone):
        """Change the conversational tone mid-conversation"""
        if new_tone in self.personality_engine.TONES:
            self.personality_engine.tone = new_tone
            return f"✨ Tone changed to: {new_tone}"
        else:
            available = ", ".join(self.personality_engine.TONES.keys())
            return f"Unknown tone. Available: {available}"
    
    def process_input(self, user_input, humor_adjustment=0):
        """Process user input and generate response"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=self.personality_engine.get_system_prompt(humor_adjustment),
                messages=self.conversation_history
            )
            
            response_text = message.content[0].text
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
            
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


class SimpleAudioHandler:
    """Placeholder for audio input/output - will integrate real audio later"""
    
    @staticmethod
    def capture_audio():
        """Simulate audio capture - replace with real mic input"""
        print("\n🎤 Listening... (Type your message and press Enter)")
        user_input = input("> ")
        return user_input
    
    @staticmethod
    def play_audio(text):
        """Simulate TTS - replace with real audio output"""
        print(f"\n🔊 Bot says: {text}\n")
        # TODO: Integrate pyttsx3 or elevenlabs for real TTS
        return True


class ReachyController:
    """Placeholder for Reachy robot control"""
    
    def __init__(self):
        self.connected = False
    
    def perform_gesture(self, emotion="neutral"):
        """Simulate robot gesture - integrate real Reachy SDK later"""
        gestures = {
            "happy": "👋 [Reachy waves enthusiastically]",
            "thinking": "🤔 [Reachy tilts head thoughtfully]",
            "excited": "🙌 [Reachy raises both arms]",
            "neutral": "🤖 [Reachy nods gently]"
        }
        print(gestures.get(emotion, gestures["neutral"]))


def main():
    """Main application loop"""
    
    print("=" * 60)
    print("🤖 FRIENDLY HOST BOT - Hackathon Prototype")
    print("=" * 60)
    
    # Select personality
    print("\nAvailable personalities:")
    for i, (key, personality) in enumerate(PersonalityEngine.PERSONALITIES.items(), 1):
        print(f"{i}. {key}: {personality['name']}")
    
    print("\nSelect personality (enter number or name, default=friendly_default):")
    choice = input("> ").strip().lower()
    
    # Map choice to personality
    personalities = list(PersonalityEngine.PERSONALITIES.keys())
    if choice.isdigit() and 1 <= int(choice) <= len(personalities):
        personality_type = personalities[int(choice) - 1]
    elif choice in personalities:
        personality_type = choice
    else:
        personality_type = "friendly_default"
    
    # Select tone
    print("\nAvailable tones:")
    tones = list(PersonalityEngine.TONES.keys())
    for i, tone in enumerate(tones, 1):
        print(f"{i}. {tone}")
    
    print("\nSelect tone (enter number or name, default=neutral):")
    tone_choice = input("> ").strip().lower()
    
    if tone_choice.isdigit() and 1 <= int(tone_choice) <= len(tones):
        tone = tones[int(tone_choice) - 1]
    elif tone_choice in tones:
        tone = tone_choice
    else:
        tone = "neutral"
    
    # Select scene
    print("\nAvailable scenes:")
    scenes = list(PersonalityEngine.SCENES.keys())
    for i, scene_key in enumerate(scenes, 1):
        scene_desc = PersonalityEngine.SCENES[scene_key]
        if scene_desc:
            print(f"{i}. {scene_key}: {scene_desc[:60]}...")
        else:
            print(f"{i}. {scene_key}: [Define your own]")
    
    print("\nSelect scene (enter number or name, default=hackathon):")
    scene_choice = input("> ").strip().lower()
    
    if scene_choice.isdigit() and 1 <= int(scene_choice) <= len(scenes):
        scene = scenes[int(scene_choice) - 1]
    elif scene_choice in scenes:
        scene = scene_choice
    else:
        scene = "hackathon"
    
    # Custom scene description if selected
    custom_scene_desc = ""
    if scene == "custom":
        print("\nDescribe the scene context:")
        print("(e.g., 'Hotel lobby hosting art exhibit of Pune artists. 50 guests.')")
        custom_scene_desc = input("> ").strip()
    
    print(f"\n✨ Initializing {personality_type} personality with {tone} tone...\n")
    
    # Initialize components
    agent = ConversationAgent(personality_type, tone, scene)
    
    # Set custom scene if provided
    if custom_scene_desc:
        agent.set_scene(custom_scene_desc)
    
    audio = SimpleAudioHandler()
    reachy = ReachyController()
    
    # Context clues for introduction
    print("Optional: Provide context clues for the bot to start the conversation")
    print("(e.g., 'guy in pink shirt with NASA logo', or press Enter to skip):")
    context = input("> ").strip()
    
    if context:
        print("\n🤖 Bot introducing itself...\n")
        intro = agent.introduce_self(context)
        audio.play_audio(intro)
        reachy.perform_gesture("happy")
    
    print("\nBot is ready! Commands:")
    print("  - Type your message to chat")
    print("  - Type 'tone:<name>' to change tone (e.g., 'tone:funnier')")
    print("  - Type 'scene:<description>' to update scene context")
    print("  - Type 'funnier' to increase humor")
    print("  - Type 'reset' to clear conversation")
    print("  - Type 'quit' to exit")
    print("\nStart chatting!\n")
    
    humor_adjustment = 0
    
    # Main conversation loop
    while True:
        try:
            # Get input (simulated audio for now)
            user_input = audio.capture_audio()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                humor_adjustment = 0
                print("\n🔄 Conversation reset!\n")
                continue
            elif user_input.lower() == 'funnier':
                humor_adjustment += 1
                print(f"\n😄 Humor level increased! (+{humor_adjustment})\n")
                continue
            elif user_input.lower().startswith('tone:'):
                new_tone = user_input.split(':', 1)[1].strip()
                result = agent.change_tone(new_tone)
                print(f"\n{result}\n")
                continue
            elif user_input.lower().startswith('scene:'):
                new_scene = user_input.split(':', 1)[1].strip()
                result = agent.set_scene(new_scene)
                print(f"\n{result}\n")
                continue
            
            # Check if user wants more humor
            if 'funnier' in user_input.lower() or 'make me laugh' in user_input.lower():
                humor_adjustment += 1
            
            # Process through Claude
            response = agent.process_input(user_input, humor_adjustment)
            
            # Output response (simulated TTS for now)
            audio.play_audio(response)
            
            # Simulate robot gesture
            if any(word in response.lower() for word in ['great', 'awesome', 'excellent']):
                reachy.perform_gesture("happy")
            elif '?' in response:
                reachy.perform_gesture("thinking")
            else:
                reachy.perform_gesture("neutral")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()