# System Architecture Diagram

## Complete Hackathon Setup - Multi-Device Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HACKATHON DEMO SYSTEM                               │
│                   AI-Powered Conversational Robot Host                      │
└─────────────────────────────────────────────────────────────────────────────┘


                           ┌──────────────────┐
                           │   WiFi Network   │
                           │  192.168.1.0/24  │
                           └────────┬─────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 │                  │                  │
         ┌───────▼──────┐   ┌──────▼──────┐   ┌──────▼───────┐
         │ Meta Quest 3 │   │   MacBook   │   │ Temi + Reachy│
         │              │   │   (Docker)  │   │   Robots     │
         │ 192.168.1.101│   │192.168.1.100│   │192.168.1.102+│
         └──────┬───────┘   └──────┬──────┘   └──────┬───────┘
                │                  │                  │
                │    HTTP/REST     │   WebSocket      │
                │    Port 5000     │   Port 5000      │
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     Flask API Server        │
                    │   (api_server.py)           │
                    │                             │
                    │  • HTTP Endpoints           │
                    │  • WebSocket Server         │
                    │  • Speech-to-Text           │
                    │  • Text-to-Speech           │
                    └──────────┬──────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼───────┐  ┌──▼────────┐  ┌─▼──────────┐
        │Conversation   │  │  Reachy   │  │   Claude   │
        │   Agent       │  │Controller │  │    API     │
        │  (main.py)    │  │(.py)      │  │ (Sonnet 4) │
        └───────────────┘  └───────────┘  └────────────┘
```

---

## Data Flow Diagrams

### 1️⃣ Personality Control Flow (Quest → Docker)

```
Meta Quest 3                      Docker API                   Bot State
─────────────                    ─────────────                ───────────

┌──────────────┐
│ User selects │
│ "Pirate"     │
│ personality  │
└──────┬───────┘
       │
       │ HTTP POST /initialize
       │ {personality: "pirate",
       │  tone: "funnier"}
       │
       ▼
 ┌─────────────┐
 │ Flask API   │─────► Initialize
 │ /initialize │       ConversationAgent
 └─────────────┘       with new settings
       │
       │ Response: 200 OK
       │ {status: "success"}
       │
       ▼
 ┌─────────────┐
 │ Update UI   │
 │ "✅ Bot     │
 │ initialized"│
 └─────────────┘
```

### 2️⃣ Voice Conversation Flow (Temi → Docker → Reachy)

```
Temi Robot              Docker API                Claude API           Reachy Mini
──────────             ────────────              ──────────           ───────────

🎤 Capture audio
   │
   │ base64 audio data
   │ WebSocket
   │
   ▼
 ┌───────────┐
 │ Speech-to │
 │   Text    │
 └─────┬─────┘
       │
       │ "Hello, what's
       │  this event?"
       │
       ▼
 ┌───────────┐         ┌─────────┐
 │ Process   │────────►│ Claude  │
 │  Input    │         │ Sonnet  │
 └───────────┘         └────┬────┘
       │                    │
       │                    │ "Ahoy matey!
       │                    │  This be a..."
       │                    │
       │◄───────────────────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
 ┌───────────┐                      ┌─────────┐
 │ Analyze   │                      │ Send to │
 │ Response  │                      │  Temi   │
 │ for       │                      │  TTS    │
 │ Emotion   │                      └─────────┘
 └─────┬─────┘                            │
       │                                  │
       │ emotion: "happy"                 │
       │                                  │
       ▼                                  ▼
 ┌───────────┐                      🔊 Temi speaks:
 │ Trigger   │                      "Ahoy matey!..."
 │ Gesture   │
 └─────┬─────┘
       │
       │ SDK command
       │
       ▼
                                    👋 Reachy waves!
```

### 3️⃣ Text Chat Test Flow (Quest → Docker)

```
Quest (Test Mode)           Docker API              Claude           Reachy
─────────────────          ────────────            ──────           ──────

User types:
"Tell me a joke"
   │
   │ HTTP POST /chat
   │ {message: "Tell me a joke"}
   │
   ▼
 Process input ──────────► Generate ────► "Why did the..."
                           response
   │                          │
   │◄─────────────────────────┘
   │
   ├────────────────┐
   │                │
   ▼                ▼
Display          Trigger
response         gesture (spin)
   │                │
   │                └──────────────────────► 🌀 Reachy spins
   │
   ▼
"Bot: Why did the
 robot cross the road?
 To get to the
 other gigabyte!"
```

---

## Component Interaction Matrix

| Component | Talks To | Protocol | Data Sent | Data Received |
|-----------|----------|----------|-----------|---------------|
| **Quest** | Docker API | HTTP POST | Personality settings | Status, responses |
| **Quest** | Docker API | HTTP POST | Chat messages | Bot replies |
| **Temi** | Docker API | WebSocket | Audio chunks (base64) | Text responses, audio |
| **Docker API** | Claude API | HTTPS | Conversation context | Text responses |
| **Docker API** | Reachy | SDK/WiFi | Gesture commands | Status |
| **ConversationAgent** | Claude | API | Messages array | Response |
| **ReachyController** | Reachy | SDK | Joint positions | Sensor data |

---

## Network Topology

```
                    ┌─────────────────────┐
                    │    WiFi Router      │
                    │  192.168.1.1        │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          │                    │                    │
    ┌─────▼─────┐        ┌─────▼─────┐       ┌─────▼─────┐
    │  Quest 3  │        │  MacBook  │       │   Temi    │
    │ .101      │        │  .100     │       │   .102    │
    │           │        │           │       │           │
    │ Unity App │◄──────►│  Docker   │◄─────►│Audio Client│
    │           │  HTTP  │  Flask    │  WS   │           │
    └───────────┘        │  :5000    │       └───────────┘
                         │           │
                         │           │       ┌───────────┐
                         │           │◄─────►│  Reachy   │
                         │           │  SDK  │   .103    │
                         │           │       │           │
                         └───────────┘       │  Mini Bot │
                              │              └───────────┘
                              │
                              │ HTTPS
                              ▼
                    ┌─────────────────┐
                    │  Anthropic API  │
                    │  (Internet)     │
                    └─────────────────┘
```

---

## Port Configuration

```
Service            Port    Protocol   Access
───────────────────────────────────────────────
Flask HTTP         5000    TCP        0.0.0.0 (all)
WebSocket          5000    TCP/WS     0.0.0.0 (all)
Reachy SDK         50055   gRPC       Reachy IP only
Claude API         443     HTTPS      Internet

Firewall Rules Needed:
─────────────────────────
MacBook: Allow incoming on port 5000
Quest:   Outgoing to MacBook:5000
Temi:    Outgoing to MacBook:5000
Reachy:  Allow incoming on 50055
```

---

## File Structure on Docker Container

```
/app  (inside container)
├── api_server.py          ← NEW - Main API server
├── main.py                ← Your existing bot logic
├── reachy_controller.py   ← Reachy gesture control
├── requirements.txt       ← Updated dependencies
├── docker-compose.yml     ← Updated with port 5000
├── .env                   ← Config (API keys, IPs)
└── logs/                  ← Optional logging

When running:
─────────────
Process: python api_server.py
Listening: 0.0.0.0:5000
Connected to: Anthropic API (internet)
Connected to: Reachy (192.168.1.103:50055)
Accepting from: Quest, Temi (any IP on network)
```

---

## State Management

```
┌──────────────────────────────────────────────────────┐
│              Bot State (In Memory)                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  conversation_agent                                  │
│  ├─ personality: "pirate"                            │
│  ├─ tone: "funnier"                                  │
│  ├─ scene: "hackathon"                               │
│  ├─ conversation_history: [...]                      │
│  ├─ exchange_count: 3                                │
│  └─ total_visitors: 1                                │
│                                                      │
│  reachy_controller                                   │
│  ├─ connected: true                                  │
│  ├─ current_gesture: "wave"                          │
│  └─ simulation_mode: false                           │
│                                                      │
└──────────────────────────────────────────────────────┘

State Changes:
─────────────
• Quest sends /initialize → Updates personality/tone
• Quest sends /reset → Clears conversation_history, increments visitors
• Temi sends audio → Adds to conversation_history
• Response triggers → Updates current_gesture
```

---

## Timing Diagram (Typical Interaction)

```
Time   Quest          Docker          Claude          Reachy         Temi
────   ─────          ──────          ──────          ──────         ────
0ms    Initialize ─►
10ms                 Setup bot
20ms                              ◄─ (no call yet)
30ms              ◄─ 200 OK
                                                                  ◄─ User speaks
500ms                                                             "Hello"
510ms                          ◄─ Audio data ─────────────────────┘
550ms                 STT:
                      "Hello"
600ms                           ─► Process ─►
900ms                           ◄─ Response ◄─
                                  "Ahoy!"
920ms                                              ─► Wave cmd ─►
950ms                                                          👋 Waves
1000ms                         ─► TTS audio ──────────────────────►
1100ms                                                             🔊 Speaks
```

---

## Error Handling Flow

```
Error Source         Detection           Recovery Action
────────────────────────────────────────────────────────────
Quest can't connect  HTTP timeout        • Check IP address
                                         • Verify Docker running
                                         • Test /health endpoint

Audio stream fails   WebSocket error     • Fallback to text chat
                                         • Log error, continue

Claude API down      API error 500       • Return cached response
                                         • Or user-friendly error

Reachy offline       SDK connection      • Switch to simulation
                     failed              • Log gestures instead

Speech recognition   STT returns None    • Emit "didn't understand"
fails                                    • Ask user to repeat
```

---

## Development vs Production

```
Development (Laptop)          Production (Hackathon Demo)
────────────────────          ───────────────────────────
• REACHY_SIMULATION_MODE=true • REACHY_SIMULATION_MODE=false
• Text chat testing           • Full audio streaming
• Gestures in console         • Real robot gestures
• Localhost connections       • WiFi network connections
• Single developer machine    • Multi-device setup
```

---

## Scaling Considerations

```
Current Setup (MVP):          Future Enhancements:
───────────────────          ────────────────────
• 1 conversation at a time   • Queue multiple visitors
• Single Docker container    • Load balanced containers
• In-memory state           • Redis for shared state
• Manual reset              • Auto-detect new person
• WiFi only                 • Cloud deployment option
```

This architecture is designed for hackathon speed while remaining extensible! 🚀