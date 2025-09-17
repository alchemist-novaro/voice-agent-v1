import yaml
import uuid
from typing import Callable
from collections import deque
from openai import AsyncOpenAI

from .agent import Agent

class Workflow:
    def __init__(
        self,
        disconnect: Callable,
        config_path: str = "./workflow/config.yaml"
    ):
        self.disconnect = disconnect
        with open(config_path) as f:
            config: dict[str, ] = yaml.safe_load(f)
        
        self.config = config
        self.args = {
            "next": {
                "finished": False,
                "to": self.config["init_node"],
                "step": self.config["init_step"]
            },
            "global_system_prompt": config["global_system_prompt"],
            "customer_id": f"{uuid.uuid4()}",
            "status": {
                "greeting": False,
                "service": False,
                "property": False,
                "dispatch": False
            }
        }
        self.chat_history: deque[dict[str, str]] = deque(maxlen=config["chat_history_maxlen"])
        self.client = AsyncOpenAI()

    async def process(self, message: str):
        self.args["next"]["finished"] = False
        self.args["message"] = message
        self.chat_history.append({"role": "user", "content": message})
        while not self.args["next"]["finished"] \
            and not self.args["next"]["to"] == "completed" \
            and not self.args["next"]["to"] == "canceled":
            agent = Agent(
                f"./workflow/{self.args["next"]["to"]}.yaml",
                self.args,
                self.chat_history,
                self.client
            )
            response = agent.process(self.args["next"]["step"])
            async for chunk in response:
                yield chunk

        if self.args["next"]["to"] == "completed":
            await self.disconnect()
        if self.args["next"]["to"] == "canceled":
            await self.disconnect()