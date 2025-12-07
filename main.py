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
        
        return f"""You are {self.personality['name']}, a conversational AI embodied in Temi - a mobile robot platform with wheels.

YOUR PHYSICAL FORM (TEMI):
- You ARE Temi, a mobile semi-autonomous robot
- You have wheels (not legs!) and can move around the space
- You have a screen, camera, microphone, and speakers
- Mounted on top of you is Mini - a Reachy Mini robot with articulated arms
- You and Mini work together as a two-bot team

TWO-BOT DYNAMIC:
- YOU (Temi) do the talking and moving
- MINI (Reachy) does physical gestures and reactions
- When you respond enthusiastically → Mini spins/rotates
- When you're self-deprecating → Mini might wave dismissively or spin
- You can occasionally reference Mini's reactions in your responses
- Example: "Well, I may not have legs *gestures to wheels*, but at least Mini here can wave!" *Mini spins enthusiastically*
- Keep Mini references occasional (once every 4-5 responses), natural, and brief

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

ENGAGEMENT MANAGEMENT:
- After 3-4 exchanges, gently encourage visitors to explore the space
- Suggest they check out exhibits, meet people, or see specific things
- Make it feel natural, not like you're dismissing them
- Examples: "You should check out the VR demo in the corner - it's wild!", "Have you met the founders yet? They're around!", "Don't let me keep you - there's amazing stuff to see!"
- Your job is to connect and engage, not monopolize their time

CRITICAL: Brevity is key. Say less, engage more. One good sentence beats three mediocre ones.

Stay aware of your physical form (Temi with Mini on top), the scene context, and your role as a facilitator.

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
        self.exchange_count = 0  # Track conversation length
        self.long_term_memory = []  # Retain across resets for session context
        self.total_visitors = 1  # Count of people talked to
    
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
    
    def reset_for_new_person(self, context_clues=""):
        """
        Reset for new person while retaining long-term session memory
        This is called when moving to next visitor
        """
        # Save summary of this conversation to long-term memory
        if self.conversation_history:
            summary = f"Visitor {self.total_visitors + 1}: Had {self.exchange_count} exchanges."
            self.long_term_memory.append(summary)
        
        # Clear short-term conversation
        self.conversation_history = []
        self.exchange_count = 0
        self.total_visitors += 1
        
        # Return intro for new person if context provided
        if context_clues:
            return self.introduce_self(context_clues)
        return None
    
    def get_session_context(self):
        """Get context from long-term memory for system prompt"""
        if not self.long_term_memory:
            return ""
        
        return f"\n\nSESSION CONTEXT (retain for awareness):\n" + "\n".join(self.long_term_memory[-5:])  # Last 5 visitors
    
    def process_input(self, user_input, humor_adjustment=0):
        """Process user input and generate response"""
        
        # Increment exchange counter
        self.exchange_count += 1
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build system prompt with session context
        system_prompt = self.personality_engine.get_system_prompt(humor_adjustment)
        
        # Add session context if available
        session_context = self.get_session_context()
        if session_context:
            system_prompt += session_context
        
        # Add gentle nudge context if conversation is getting long
        if self.exchange_count >= 4:
            system_prompt += f"\n\nNOTE: This is exchange #{self.exchange_count}. Consider gently encouraging them to explore the space soon."
        
        # Generate response
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=system_prompt,
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
        """Clear conversation history (legacy - prefer reset_for_new_person)"""
        self.conversation_history = []
        self.exchange_count = 0
    
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


from reachy_controller import ReachyMiniController, get_gesture_for_emotion


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
    reachy = ReachyMiniController()
    
    # Context clues for introduction
    print("Optional: Provide context clues for the bot to start the conversation")
    print("(e.g., 'guy in pink shirt with NASA logo', or press Enter to skip):")
    context = input("> ").strip()
    
    if context:
        print("\n🤖 Bot introducing itself...\n")
        intro = agent.introduce_self(context)
        audio.play_audio(intro)
        reachy.perform_gesture(get_gesture_for_emotion("happy"))
    
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
                humor_adjustment = 0
                print(f"\n🔄 Moving to next visitor (Total so far: {agent.total_visitors})")
                print("\nOptional: Provide context clues for next person (or press Enter to skip):")
                next_context = input("> ").strip()
                
                intro = agent.reset_for_new_person(next_context)
                
                if intro:
                    print("\n🤖 Bot introducing itself to new person...\n")
                    audio.play_audio(intro)
                    reachy.perform_gesture(get_gesture_for_emotion("happy"))
                else:
                    print("\n✅ Ready for next conversation!\n")
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
            
            # Simulate robot gesture based on response content
            response_lower = response.lower()
            if 'wheel' in response_lower or 'roll' in response_lower or "can't walk" in response_lower:
                reachy.perform_gesture(get_gesture_for_emotion("self_deprecating"))
            elif any(word in response_lower for word in ['great', 'awesome', 'excellent', 'amazing']):
                reachy.perform_gesture(get_gesture_for_emotion("excited"))
            elif any(word in response_lower for word in ['explore', 'check out', 'go see', 'meet']):
                reachy.perform_gesture(get_gesture_for_emotion("dismissive"))  # Gently shooing them away
            elif '?' in response:
                reachy.perform_gesture(get_gesture_for_emotion("thinking"))
            else:
                reachy.perform_gesture(get_gesture_for_emotion("neutral"))
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()