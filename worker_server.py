from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions,
    JobContext,
    cli,
    WorkerOptions
)
from livekit.plugins import (
    deepgram,
    silero,
    noise_cancellation
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from dotenv import load_dotenv
import uuid
import asyncio

from src.agent_llm import AgentLLM
from src.apis import CloseConversation

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="")


async def entrypoint(ctx: JobContext):
    async def disconnect():
        await ctx.room.disconnect()

    session = AgentSession(
        stt=deepgram.STT(),
        llm=AgentLLM(uuid.uuid4(), "./workflows/test.yaml", disconnect),
        tts=deepgram.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    assistant = Assistant()

    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Example: generate a reply; your agent may raise CloseConversation internally
    await session.generate_reply(instructions="say hello to the user")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
