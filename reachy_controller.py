#!/usr/bin/env python3
"""
Reachy Mini Controller
Handles both real robot control and simulation mode for testing
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Try to import Reachy SDK - gracefully handle if not available
try:
    from reachy2_sdk import ReachySDK
    REACHY_SDK_AVAILABLE = True
except ImportError:
    REACHY_SDK_AVAILABLE = False
    print("⚠️  Reachy SDK not installed - running in simulation mode")


class ReachyMiniController:
    """
    Reachy Mini robot controller with simulation mode
    
    Modes:
    - SIMULATION: Print gestures to console (for testing without robot)
    - REAL: Connect to actual Reachy Mini hardware
    """
    
    # Gesture definitions with joint positions
    GESTURES = {
        "wave": {
            "description": "Wave hello with right arm",
            "joints": {
                "r_shoulder_pitch": -60,
                "r_elbow_pitch": -90,
                "r_wrist_roll": 0
            },
            "animation": [
                {"r_wrist_yaw": 30, "duration": 0.3},
                {"r_wrist_yaw": -30, "duration": 0.3},
                {"r_wrist_yaw": 30, "duration": 0.3},
            ],
            "emoji": "👋"
        },
        "nod": {
            "description": "Nod head gently",
            "joints": {
                "neck_pitch": 10
            },
            "animation": [
                {"neck_pitch": 10, "duration": 0.5},
                {"neck_pitch": -10, "duration": 0.5},
                {"neck_pitch": 0, "duration": 0.5},
            ],
            "emoji": "🤖"
        },
        "spin": {
            "description": "Spin enthusiastically (torso rotation)",
            "joints": {
                "neck_yaw": 0
            },
            "animation": [
                {"neck_yaw": 45, "duration": 0.4},
                {"neck_yaw": -45, "duration": 0.4},
                {"neck_yaw": 0, "duration": 0.4},
            ],
            "emoji": "🌀"
        },
        "tilt_head": {
            "description": "Tilt head thoughtfully",
            "joints": {
                "neck_roll": 20
            },
            "animation": [
                {"neck_roll": 20, "duration": 0.6},
                {"neck_roll": 0, "duration": 0.6},
            ],
            "emoji": "🤔"
        },
        "dismissive_wave": {
            "description": "Gentle dismissive wave (shooing motion)",
            "joints": {
                "r_shoulder_pitch": -45,
                "r_elbow_pitch": -60,
            },
            "animation": [
                {"r_wrist_yaw": -20, "duration": 0.3},
                {"r_wrist_yaw": 20, "duration": 0.3},
                {"r_wrist_yaw": 0, "duration": 0.3},
            ],
            "emoji": "✋"
        },
        "celebrate": {
            "description": "Raise both arms in celebration",
            "joints": {
                "r_shoulder_pitch": -90,
                "l_shoulder_pitch": -90,
                "r_elbow_pitch": -45,
                "l_elbow_pitch": -45,
            },
            "animation": [
                {"r_shoulder_pitch": -90, "l_shoulder_pitch": -90, "duration": 0.5},
                {"r_shoulder_pitch": -60, "l_shoulder_pitch": -60, "duration": 0.5},
            ],
            "emoji": "🙌"
        },
        "rest": {
            "description": "Return to rest position",
            "joints": {},
            "animation": [],
            "emoji": "😌"
        }
    }
    
    def __init__(self):
        """Initialize Reachy controller"""
        self.simulation_mode = os.getenv("REACHY_SIMULATION_MODE", "true").lower() == "true"
        self.host = os.getenv("REACHY_HOST", "localhost")
        self.port = int(os.getenv("REACHY_PORT", "50055"))
        self.reachy = None
        self.connected = False
        
        # Try to connect if not in simulation mode
        if not self.simulation_mode and REACHY_SDK_AVAILABLE:
            self._connect()
        else:
            print(f"🎭 Reachy running in SIMULATION mode")
    
    def _connect(self):
        """Connect to real Reachy hardware"""
        try:
            print(f"🔌 Connecting to Reachy at {self.host}:{self.port}...")
            self.reachy = ReachySDK(host=self.host, port=self.port)
            self.connected = True
            print("✅ Connected to Reachy Mini!")
            
            # Turn on motors
            self.reachy.turn_on()
            
        except Exception as e:
            print(f"❌ Could not connect to Reachy: {e}")
            print("   Falling back to simulation mode")
            self.simulation_mode = True
            self.connected = False
    
    def perform_gesture(self, gesture_name="rest"):
        """
        Perform a gesture
        
        Args:
            gesture_name: Name of gesture from GESTURES dict
        """
        gesture = self.GESTURES.get(gesture_name, self.GESTURES["rest"])
        
        if self.simulation_mode:
            self._simulate_gesture(gesture_name, gesture)
        else:
            self._execute_gesture(gesture_name, gesture)
    
    def _simulate_gesture(self, name, gesture):
        """Simulate gesture for testing (print to console)"""
        emoji = gesture["emoji"]
        description = gesture["description"]
        print(f"{emoji} [Mini: {description}]")
        
        # Optionally print detailed animation sequence
        if os.getenv("REACHY_VERBOSE", "false").lower() == "true":
            print(f"   Joints: {gesture['joints']}")
            for step in gesture['animation']:
                print(f"   → {step}")
    
    def _execute_gesture(self, name, gesture):
        """Execute gesture on real robot"""
        if not self.connected:
            print("⚠️  Not connected to Reachy - cannot execute gesture")
            return
        
        try:
            # Set initial joint positions
            for joint_name, position in gesture["joints"].items():
                joint = getattr(self.reachy, joint_name, None)
                if joint:
                    joint.goal_position = position
            
            # Execute animation sequence
            for step in gesture["animation"]:
                for joint_name, position in step.items():
                    if joint_name != "duration":
                        joint = getattr(self.reachy, joint_name, None)
                        if joint:
                            joint.goal_position = position
                
                # Wait for step duration
                time.sleep(step.get("duration", 0.5))
            
            print(f"✅ Executed: {gesture['description']}")
            
        except Exception as e:
            print(f"❌ Error executing gesture '{name}': {e}")
    
    def goto_rest(self):
        """Return to rest position"""
        if self.connected and not self.simulation_mode:
            try:
                self.reachy.goto_rest_position()
            except Exception as e:
                print(f"❌ Error returning to rest: {e}")
        else:
            print("😌 [Mini: Return to rest position]")
    
    def disconnect(self):
        """Disconnect from robot and turn off motors"""
        if self.connected and not self.simulation_mode:
            try:
                self.reachy.turn_off()
                print("👋 Reachy disconnected")
            except Exception as e:
                print(f"⚠️  Error disconnecting: {e}")
    
    def get_status(self):
        """Get current robot status"""
        return {
            "connected": self.connected,
            "simulation_mode": self.simulation_mode,
            "host": self.host,
            "port": self.port,
            "available_gestures": list(self.GESTURES.keys())
        }


# Mapping from emotion/context to gesture
EMOTION_TO_GESTURE = {
    "happy": "wave",
    "thinking": "tilt_head",
    "excited": "spin",
    "dismissive": "dismissive_wave",
    "neutral": "nod",
    "self_deprecating": "spin",  # Mini spins mockingly
    "celebrating": "celebrate",
    "rest": "rest"
}


def get_gesture_for_emotion(emotion):
    """Map emotion to gesture name"""
    return EMOTION_TO_GESTURE.get(emotion, "rest")


if __name__ == "__main__":
    """Test script - run gestures in sequence"""
    print("🤖 Reachy Mini Controller Test")
    print("=" * 60)
    
    controller = ReachyMiniController()
    print("\nStatus:", controller.get_status())
    
    print("\n🎬 Testing all gestures...\n")
    
    for gesture_name in controller.GESTURES.keys():
        print(f"\nTesting: {gesture_name}")
        controller.perform_gesture(gesture_name)
        time.sleep(1)
    
    controller.goto_rest()
    controller.disconnect()
    
    print("\n✅ Test complete!")