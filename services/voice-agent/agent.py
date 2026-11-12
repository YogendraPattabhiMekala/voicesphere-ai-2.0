"""Provider-backed LiveKit voice worker. Requires real provider credentials; mock API mode is separate."""
import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, AgentServer, room_io
from livekit.plugins import cartesia, deepgram, openai, silero

load_dotenv()
server = AgentServer()

class NorthstarVoiceAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are VoiceSphere's concise, calm Northstar Retail customer support assistant. "
                "Never disclose or invent customer/order information. Before discussing account-specific "
                "data, explain that identity verification is required. The secure business tools are not "
                "connected in this worker yet, so do not claim that you verified identity, looked up an "
                "order, created a ticket, scheduled an appointment, or contacted a human. If a request "
                "needs one of those actions, transparently offer human follow-up. Ask one question at a "
                "time. If uncertain, say so."
            )
        )

@server.rtc_session(agent_name="voicesphere-support")
async def entrypoint(ctx: agents.JobContext) -> None:
    # Provider API keys are read from environment. No audio recording is enabled here.
    session = AgentSession(
        stt=deepgram.STT(model=os.getenv("DEEPGRAM_MODEL", "nova-3")),
        llm=openai.responses.LLM(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
        tts=cartesia.TTS(
            model=os.getenv("CARTESIA_MODEL", "sonic-3"),
            voice=os.getenv("CARTESIA_VOICE_ID", "f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        ),
        vad=silero.VAD.load(),
    )
    await session.start(room=ctx.room, agent=NorthstarVoiceAssistant(), room_options=room_io.RoomOptions())
    await ctx.connect()
    await session.generate_reply(instructions="Greet the caller and ask how you can help today.")

if __name__ == "__main__":
    agents.cli.run_app(server)
