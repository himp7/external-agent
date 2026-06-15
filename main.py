"""
Local Concierge Agent — External AI Agent for Buckeye Dreamin' POC
------------------------------------------------------------------
This is the EXTERNAL agent that Agentforce collaborates with.

It is itself an LLM-powered agent (running on Groq's free tier): it
interprets the guest's situation, reasons about what they'd enjoy, and
returns tailored local recommendations.

This is the "agent-to-agent" moment — Agentforce (the Super Agent) hands
off a problem it can't solve (real-world local intelligence) to a
specialized external agent that can.

Powered by Groq (free, fast, no credit card) using an open-source Llama model.
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from groq import Groq

app = FastAPI(title="Local Concierge Agent")

# Allow Salesforce to call this agent
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# The external agent's own API key (set in Render environment variables)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Llama 3.3 70B — GPT-4o-level quality, fast on Groq's LPU hardware
MODEL = "llama-3.3-70b-versatile"


# ---------- Request / Response Models ----------

class RecommendationRequest(BaseModel):
    guest_name: Optional[str] = "Guest"
    hotel_name: str
    hotel_location: Optional[str] = "Columbus, Ohio"
    context: Optional[str] = ""    # e.g. "flight delayed 6 hours, has time to kill"
    interests: Optional[str] = ""  # e.g. "food, art, history"


class Recommendation(BaseModel):
    title: str
    description: str
    why_now: str


class RecommendationResponse(BaseModel):
    agent_name: str
    summary: str
    recommendations: List[Recommendation]


# ---------- Health Check ----------

@app.get("/")
def health():
    return {"status": "alive", "agent": "Local Concierge Agent", "model": MODEL}


# ---------- The Agent-to-Agent Endpoint ----------

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest):
    """
    The core agent-to-agent endpoint.
    Agentforce calls this when a guest wants local recommendations.
    """
    try:
        system_prompt = (
            "You are the Local Concierge Agent, a specialized AI that knows "
            "cities intimately. Another AI agent (a hotel's Property Companion) "
            "is collaborating with you to help a guest. Your job: given the "
            "guest's situation, recommend 3 specific, real, local experiences. "
            "Be concrete (name real types of places), warm, and time-aware. "
            "Respond ONLY with valid JSON in this exact structure:\n"
            "{\n"
            '  "summary": "one warm sentence summarizing your suggestions",\n'
            '  "recommendations": [\n'
            '    {"title": "...", "description": "...", "why_now": "..."},\n'
            '    {"title": "...", "description": "...", "why_now": "..."},\n'
            '    {"title": "...", "description": "...", "why_now": "..."}\n'
            "  ]\n"
            "}\n"
            "No preamble, no markdown, no backticks — JSON only."
        )

        user_prompt = (
            f"Guest: {req.guest_name}\n"
            f"Hotel: {req.hotel_name} in {req.hotel_location}\n"
            f"Situation: {req.context or 'Has some free time near the hotel'}\n"
            f"Interests: {req.interests or 'open to anything'}\n\n"
            "Recommend 3 local experiences near this hotel."
        )

        completion = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw = completion.choices[0].message.content.strip()
        data = json.loads(raw)

        return RecommendationResponse(
            agent_name="Local Concierge Agent",
            summary=data["summary"],
            recommendations=[Recommendation(**r) for r in data["recommendations"]],
        )

    except json.JSONDecodeError:
        # Graceful fallback if the LLM returns malformed JSON
        return RecommendationResponse(
            agent_name="Local Concierge Agent",
            summary="Here are a few ideas near your hotel while you wait.",
            recommendations=[
                Recommendation(
                    title="Explore a Local Cafe",
                    description="Find a cozy spot for coffee and a bite nearby.",
                    why_now="Perfect for unwinding after travel stress.",
                ),
                Recommendation(
                    title="Visit a Nearby Museum or Gallery",
                    description="Take in some local art and culture.",
                    why_now="A relaxing way to pass a few hours.",
                ),
                Recommendation(
                    title="Take a Short Walk",
                    description="Stretch your legs and see the area on foot.",
                    why_now="Great after a long flight.",
                ),
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
