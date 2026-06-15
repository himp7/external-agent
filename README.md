# 🤝 Local Concierge Agent — A2A Edition
### The agent-to-agent peer for "Beyond APIs" — Buckeye Dreamin' 2026

This is the **same** Local Concierge agent — but it now speaks the
**Agent2Agent (A2A) protocol** instead of a plain REST endpoint.

This is the half of your demo that proves the thesis. The REST version was a
*tool*. This version is a *peer*.

---

## 🔑 The Core Difference

| | REST version (`/recommend`) | A2A version (this) |
|---|---|---|
| What it is | A tool | A peer agent |
| Discovery | You hardcode the URL | Published **Agent Card** at `/.well-known/agent-card.json` |
| Contract | Custom JSON you invented | Standard A2A Message + Task lifecycle |
| Input | Structured params | A natural-language **message** the agent interprets |
| Reasoning | Caller orchestrates | Agent reasons **independently & opaquely** |

The caller (Agentforce) never sees *how* this agent thinks. It sends a task,
gets a result. That opacity is the whole point of "Beyond APIs."

---

## 🧩 How It's Built (a2a-sdk 1.1.0)

- **`agent_executor.py`** — `LocalConciergeExecutor` handles an incoming A2A
  task: reads the peer's message, reasons via Groq, completes the task with an
  agent message.
- **`__main__.py`** — defines the **Agent Skill** + **Agent Card**, wires the
  executor into a FastAPI app via the official A2A route helpers, and serves
  the discovery endpoint.

Key A2A endpoints exposed automatically:
- `GET /.well-known/agent-card.json` — discovery (the Agent Card)
- `POST /message:send` — send a task to the agent
- `GET/POST /tasks/...` — task lifecycle management

---

## 🔑 Free Groq Key

Same as the REST version — grab one at [console.groq.com](https://console.groq.com)
(email, no card). You'll set it as `GROQ_API_KEY` in Render.

---

## 🚀 Deploy to Render

1. Push this folder to a GitHub repo (key NOT in code)
2. [render.com](https://render.com) → New → Web Service → connect repo
3. Render auto-detects `render.yaml`
4. Add env vars:
   - `GROQ_API_KEY` = your Groq key
   - `PUBLIC_URL` = your Render URL once known (e.g. `https://local-concierge-a2a.onrender.com`)
5. Deploy

> After first deploy you'll know your URL. Set `PUBLIC_URL` to it and redeploy
> so the Agent Card advertises the correct public endpoint.

---

## 🧪 Test It

**Discover the agent (the Agent Card):**
```bash
curl https://your-a2a-url.onrender.com/.well-known/agent-card.json
```

**Send it a task (A2A message):**
```bash
curl -X POST https://your-a2a-url.onrender.com/message:send \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "ROLE_USER",
      "parts": [{"text": "My guest is at Polaris Hilton in Columbus, flight delayed 6 hours, loves food and history. What should they do?"}]
    }
  }'
```

---

## 🔌 Connect to Agentforce

In Agentforce (Summer '26+), register this agent's Agent Card URL as an
external A2A agent. Agentforce discovers the card, performs the OAuth handshake,
and can then delegate the "local recommendations" task to this peer.

This becomes the **A2A path** in your side-by-side demo — contrasted with the
Apex-callout path that treats the same agent as a mere tool.
