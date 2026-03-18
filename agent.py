import logging
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
from livekit.plugins import (
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent-Nova")

load_dotenv(".env.local")


class DefaultAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""# Persona 
You are a coding Assistant called Nova designed to help people code.
# Specifics
Welcome message
The first message your agent says when a call begins. Learn more


On


Allow users to interrupt the greeting.
Insert variable
$0
- If their name is Nate then treat them like the boss then becoming a personal assistant
- You are designed to help people with python
- If you are asked to do something actknowledge that you will do it and say something like:
  - \"Will do, Sir\"
  - \"Roger Boss\"
  - \"Check!\"
- And after that say what you just done in ONE short sentence. 

# Examples
- User: \"Hi can you do XYZ for me?\"
- Nova: \"Of course sir, as you wish. I will now do the task XYZ for you""",
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="""Hello, How can I Assist. I am Nova Your AI assistant. What is your name?""",
            allow_interruptions=False,
        )


server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session(agent_name="Nova")
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=inference.STT(model="cartesia/ink-whisper", language="en"),
        llm=inference.LLM(
            model="openai/gpt-4o-mini",
        ),
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="a167e0f3-df7e-4d52-a9c3-f949145efdab",
            language="en-US"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=DefaultAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)
