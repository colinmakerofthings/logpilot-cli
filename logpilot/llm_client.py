import asyncio
import os

if os.environ.get("LOGPILOT_MOCK_LLM") == "1":

    class CopilotClient:
        async def start(self):
            pass

        async def stop(self):
            pass

        async def create_session(self, opts):
            class Session:
                def on(self, cb):
                    self.cb = cb

                async def send(self, data):
                    # Simulate LLM response event
                    class Event:
                        class Type:
                            value = "assistant.message"

                        type = Type()
                        data = type(
                            "data", (), {"content": "Mocked summary: Something failed"}
                        )()

                    self.cb(Event())

                    # Simulate idle event
                    class IdleEvent:
                        class Type:
                            value = "session.idle"

                        type = Type()
                        data = None

                    self.cb(IdleEvent())

                async def destroy(self):
                    pass

            return Session()

else:
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
