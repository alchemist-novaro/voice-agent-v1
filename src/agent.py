import threading
from datetime import datetime
import time
import openai
from typing import Callable

from .workflow import Workflow
from .apis import input_messages, output_chunks, input_required, output_finished, CloseConversation

class Agent:
    def __init__(
        self,
        config_path: str,
        customer_id: str,
        disconnect: Callable
    ):
        self.customer_id = customer_id
        self.workflow = Workflow(config_path, customer_id)
        self.disconnect = disconnect

        threading.Thread(target=self.workflow.process, daemon=True).start()

    @property
    def input_required(self):
        return self.customer_id in input_required and input_required[self.customer_id]

    async def process(self, message: str):
        while self.customer_id not in input_required or not input_required[self.customer_id]:
            time.sleep(0.1)

        input_messages[self.customer_id] = (message, datetime.now())

        while self.customer_id not in output_chunks:
            if not self.workflow.running:
                stream = self.handle_close_conversation()
                async for chunk in stream:
                    yield chunk

                return
            time.sleep(0.1)
        while True:
            try:
                value = output_chunks[self.customer_id].get(timeout=1)[0]
                yield value
            except CloseConversation:
                raise
            except Exception as e:
                print(e)
                if self.customer_id in output_finished and output_finished[self.customer_id]:
                    break
                else:
                    continue
    
        del output_chunks[self.customer_id]
        del output_finished[self.customer_id]

    async def handle_close_conversation(self):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[his for his in self.workflow.global_history] + [{"role": "system", "content": "Based on chat history, make correspond good bye text."}],
            stream=True
        )
        for chunk in response:
            yield chunk

        await self.disconnect()