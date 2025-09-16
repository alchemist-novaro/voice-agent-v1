import yaml
import uuid
from collections import deque
from openai import AsyncOpenAI

from .agent import Agent

class Workflow:
    def __init__(
        self,
        config_path: str = "./workflow/config.yaml"
    ):
        with open(config_path) as f:
            config: dict[str, ] = yaml.safe_load(f)
        
        self.config = config
        self.args = {
            "global_system_prompt": config["global_system_prompt"],
            "customer_id": f"{uuid.uuid4()}"
        }
        self.chat_history: deque[dict[str, str]] = deque(maxlen=config["chat_history_maxlen"])
        self.client = AsyncOpenAI()

    async def process(self, message: str):
        init_node = self.config["init_node"]
        init_step = self.config["init_step"]
        self.args["next"] = {"to": init_node, "step": init_step}
        self.args["message"] = message
        self.chat_history.append({"role": "user", "content": message})
        while not self.args["next"]["to"] == "finish":
            agent = Agent(
                f"./workflow/{self.args["next"]["to"]}.yaml",
                self.args,
                self.chat_history,
                self.client
            )
            response = agent.process(self.args["next"]["step"])
            async for chunk in response:
                yield chunk