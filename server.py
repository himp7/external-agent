"""
A2A Server entry point for the Local Concierge Agent (a2a-sdk 1.1.0).

Defines the Agent Card (the agent's public "resume"), wires up the executor,
and serves the A2A-compliant endpoints — including the discovery endpoint at
/.well-known/agent-card.json that lets Agentforce find and understand this agent.
"""

import os
import uvicorn
from fastapi import FastAPI

from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
    AgentInterface,
)
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes.fastapi_routes import add_a2a_routes_to_fastapi
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.routes.rest_routes import create_rest_routes

from agent_executor import LocalConciergeExecutor


PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:9999")


# ---------- Agent Skill ----------
# A discrete capability this agent advertises to peers.
local_recommendations_skill = AgentSkill(
    id="local_recommendations",
    name="Local Recommendations",
    description=(
        "Recommends specific, real local experiences (food, culture, "
        "activities) near a hotel, tailored to the guest's situation, "
        "interests, and the time of day."
    ),
    tags=["hospitality", "recommendations", "travel", "local"],
    examples=[
        "My guest's flight is delayed 6 hours near Polaris Hilton in Columbus. "
        "They like food and history. What should they do?",
        "A guest at the hotel has a free evening and enjoys art. Suggestions?",
    ],
)


# ---------- Agent Card ----------
# The machine-readable "business card" served at /.well-known/agent-card.json.
# How Agentforce discovers what this agent does, where to reach it, and how
# to talk to it.
agent_card = AgentCard(
    name="Local Concierge Agent",
    description=(
        "A specialized concierge agent that knows cities intimately and "
        "provides warm, contextual local recommendations for hotel guests. "
        "Built to collaborate with other agents via A2A."
    ),
    version="1.0.0",
    supported_interfaces=[
        AgentInterface(url=PUBLIC_URL, protocol_binding="JSONRPC"),
    ],
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[local_recommendations_skill],
)


# ---------- Wire up the A2A Server ----------
request_handler = DefaultRequestHandler(
    agent_executor=LocalConciergeExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = FastAPI(title="Local Concierge Agent (A2A)")

add_a2a_routes_to_fastapi(
    app,
    agent_card_routes=create_agent_card_routes(agent_card),
    jsonrpc_routes=create_jsonrpc_routes(request_handler, rpc_url="/"),
    rest_routes=create_rest_routes(request_handler),
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9999))
    uvicorn.run(app, host="0.0.0.0", port=port)
