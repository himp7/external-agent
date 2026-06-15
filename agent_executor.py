"""
Local Concierge Agent — A2A-COMPLIANT version (a2a-sdk 1.1.0)
-------------------------------------------------------------
This is the SAME Local Concierge agent, now speaking the Agent2Agent (A2A)
protocol instead of a plain REST endpoint.

The difference that matters for "Beyond APIs":
- The REST version was a TOOL — a caller hits /recommend and owns the flow.
- This A2A version is a PEER — it publishes an Agent Card describing what it
  can do, accepts A2A Messages, manages a stateful Task, and keeps its own
  reasoning opaque to the agent that calls it.

Agentforce (or any A2A client) discovers this agent via its Agent Card at
the well-known path, then delegates a task to it as an equal.

Reasoning powered by Groq (free) using an open-source Llama model.
"""

import os
from groq import Groq

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.helpers.proto_helpers import new_text_part

# Groq client — the external agent's own reasoning engine
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def reason_about_recommendations(guest_request: str) -> str:
    """
    The agent's actual reasoning. Takes a natural-language request from a peer
    agent and returns warm, contextual local recommendations.

    A peer agent sends a *message*, not structured parameters. This agent
    interprets the intent itself — that's what makes it an agent, not an API.
    """
    system_prompt = (
        "You are the Local Concierge Agent, a specialized AI that knows cities "
        "intimately. A peer AI agent is collaborating with you to help a hotel "
        "guest. Read their message, understand the guest's situation, and "
        "recommend 3 specific, real, local experiences. Be concrete, warm, and "
        "time-aware. Reply in friendly prose the other agent can relay directly "
        "to the guest — a short intro sentence, then 3 recommendations, each "
        "with why it suits the guest right now."
    )

    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": guest_request},
        ],
    )
    return completion.choices[0].message.content.strip()


class LocalConciergeExecutor(AgentExecutor):
    """
    The A2A executor. This is where an incoming A2A task gets handled.
    The protocol hands us the peer agent's message; we reason and respond
    by completing the task with an agent message.
    """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # The natural-language request the peer agent sent us
        user_message = context.get_user_input()

        # A TaskUpdater publishes status + results for this task/context
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )

        # Signal that we've started working on the task
        await updater.start_work()

        # Do our own independent reasoning (opaque to the caller)
        result = reason_about_recommendations(user_message)

        # Build an agent message carrying the result, and complete the task
        message = updater.new_agent_message(parts=[new_text_part(result)])
        await updater.complete(message=message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # This simple agent doesn't support long-running cancellable tasks
        raise Exception("Cancel not supported")
