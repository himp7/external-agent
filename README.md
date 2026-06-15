# 🌍 Local Concierge Agent
### The External AI Agent for "Beyond APIs" — Buckeye Dreamin' 2026

This is the **external agent** that Salesforce Agentforce collaborates with.
It's an LLM-powered agent (running on **Groq's free tier**) that interprets a
guest's situation and returns tailored local recommendations — the
"agent-to-agent" moment of the demo.

**No credit card. No paid keys.** Groq's free tier gives 14,400 requests/day.

---

## 🏗️ Architecture

```
Guest → Agentforce (Super Agent) → [needs local intel] → Local Concierge Agent (this) → back to Agentforce → Guest
```

Agentforce can't know what's happening around the hotel in real-time.
So it hands off to this specialized agent. This agent *reasons* about the
guest's context and responds — not just data exchange, but interpretation.

---

## 🔑 Get a Free Groq Key (2 minutes)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email (no credit card)
3. API Keys → Create API Key
4. Copy it — you'll paste it into Render as an env var

---

## 🚀 Deploy to Render (free)

1. Push this folder to a GitHub repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Render auto-detects `render.yaml`
5. Add environment variable: `GROQ_API_KEY` = your Groq key
6. Deploy

Your agent will be live at: `https://local-concierge-agent.onrender.com`

---

## 🧪 Test Locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn main:app --reload
```

Then test:
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "guest_name": "James",
    "hotel_name": "Polaris Hilton",
    "hotel_location": "Columbus, Ohio",
    "context": "Flight delayed 6 hours, has time to kill",
    "interests": "food and local history"
  }'
```

---

## 📡 API

### `POST /recommend`

**Request:**
```json
{
  "guest_name": "James",
  "hotel_name": "Polaris Hilton",
  "hotel_location": "Columbus, Ohio",
  "context": "Flight delayed 6 hours",
  "interests": "food, art"
}
```

**Response:**
```json
{
  "agent_name": "Local Concierge Agent",
  "summary": "A few warm ideas to make your wait enjoyable...",
  "recommendations": [
    {"title": "...", "description": "...", "why_now": "..."}
  ]
}
```

---

## ⚡ Model

Uses **llama-3.3-70b-versatile** on Groq — GPT-4o-level quality,
300+ tokens/sec. Fast enough that the agent-to-agent handoff feels instant
in a live demo. Uses Groq's native JSON mode for reliable structured output.

---

## 🔌 Next Step: Connect to Agentforce

After this is live, we create an Apex action in Salesforce that makes an
HTTP callout to this agent's `/recommend` endpoint. That Apex action becomes
the `Local_Recommendations` subagent's tool.

**Don't forget:** Render's free tier sleeps after ~15 min idle. Hit the `/`
health endpoint once before your session to wake it up.
