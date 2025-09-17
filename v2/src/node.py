from collections import deque
from openai import AsyncOpenAI

from .client import Client
from .types import NodeType

class Node:
    def __init__(
        self,
        config: dict[str, ],
        args: dict[str, ],
        chat_history: deque[dict[str, str]],
        client: AsyncOpenAI
    ):
        self.go_to_config = config["go_to"]
        self.args = args
        self.client = Client(
            type=NodeType(config["type"]),
            config=config["client"],
            args=args,
            chat_history=chat_history,
            client=client
        )

    async def process(self):
        response = self.client.process()
        async for chunk in response:
            yield chunk

        if self.go_to_config["data"]:
            go_to_data = self.args[self.go_to_config["data"]]
            for case in self.go_to_config["cases"]:
                if go_to_data[case["name"]] == case["value"]:
                    self.args["next"] = {"to": case["to"], "step": case["step"], "finished": case.get("finished", False)}
                    return
        self.args["next"] = {
            "to": self.go_to_config["default"]["to"],
            "step": self.go_to_config["default"]["step"],
            "finished": self.go_to_config["default"].get("finished", False)
        }