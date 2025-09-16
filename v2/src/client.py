import json
from string import Template
from collections import deque
from openai import AsyncOpenAI

from .types import NodeType
from .apis import API_FUNCTIONS

class Client:
    def __init__(
        self,
        type: NodeType,
        config: dict[str, ],
        args: dict[str, ],
        chat_history: deque[dict[str, str]],
        client: AsyncOpenAI
    ):
        self.type = type
        self.config = config
        self.args = args
        self.history = chat_history
        self.client = client
        self.global_system_prompt = args["global_system_prompt"]

    async def process(self):
        match self.type:
            case NodeType.ANALYZE:
                client_prompt = Template(self.config["prompt"]).safe_substitute(self.args)
                messages = [his for his in self.history] + [
                    {"role": "system", "content": self.global_system_prompt},
                    {"role": "system", "content": client_prompt}
                ]
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )

                data_str = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        data_str += chunk.choices[0].delta.content

                data_str = data_str.replace("```json", "").replace("```", "")
                data = json.loads(data_str)

                print(data)
                
                self.args[self.config["return"]] = data

                return
            
            case NodeType.PROCESS:
                client_prompt = Template(self.config["prompt"]).safe_substitute(self.args)
                messages = [his for his in self.history] + [
                    {"role": "system", "content": self.global_system_prompt},
                    {"role": "system", "content": client_prompt}
                ]
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )

                full_text = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk
                        full_text += chunk.choices[0].delta.content

                self.history.append({"role": "assistant", "content": full_text})

                return

            case NodeType.CALLBACK:
                args = {key: self.args[key] for key in self.config["args"]}
                if self.config["return"]:
                    self.args[self.config["return"]] = \
                        API_FUNCTIONS[self.config["name"]](self.args["customer_id"], args)
                else:
                    API_FUNCTIONS[self.config["name"]](self.args["customer_id"], args)

                return