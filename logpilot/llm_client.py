import asyncio

from copilot import CopilotClient


class LLMClient:
    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def analyze(self, prompt: str) -> str:
        return asyncio.run(self._analyze_async(prompt))

    async def _analyze_async(self, prompt: str) -> str:
        client = CopilotClient()
        await client.start()
        session = await client.create_session({"model": self.model})

        result = ""
        done = asyncio.Event()

        def on_event(event):
            nonlocal result
            if event.type.value == "assistant.message":
                result = event.data.content
            elif event.type.value == "session.idle":
                done.set()

        session.on(on_event)
        await session.send({"prompt": prompt})
        await done.wait()
        await session.destroy()
        await client.stop()
        return result
