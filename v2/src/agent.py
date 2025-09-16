import yaml
from collections import deque
from openai import AsyncOpenAI

from .node import Node, NodeType

class Agent:
    def __init__(
        self,
        config_path: str,
        args: dict[str, ],
        chat_history: deque[dict[str, str]],
        client: AsyncOpenAI
    ):
        with open(config_path) as f:
            config: dict[str, ] = yaml.safe_load(f)

        self.nodes = {key: Node(
            node_config,
            args,
            chat_history,
            client
        ) for key, node_config in config["nodes"].items()}

    async def process(self, step: str):
        node = self.nodes[step]
        response = node.process()
        async for chunk in response:
            yield chunk