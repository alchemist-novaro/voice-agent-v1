import yaml
from collections import deque

from .node import Node

class Workflow:
    def __init__(self, workflow_file: str, customer_id: str):
        with open(workflow_file) as f:
            config = yaml.safe_load(f)

        self.customer_id = customer_id

        self.init_node: int = config["init_node"]
        self.config: dict[str,] = config["init_config"]
        self.node_configs = { node_config["id"]: node_config for node_config in config["nodes"] }

        self.global_history: deque[dict[str, str]] = deque(maxlen=config["global_history_num"])
        self.topic_history: dict[str, deque[dict[str, str]]] = { node_config["id"]: deque(maxlen=config["topic_history_num"]) for node_config in config["nodes"] }
        self.summaries: deque[str, str] = deque(maxlen=config["summary_num"])
        self.running = False

    def process(self):
        current_node = Node(
            self.init_node,
            self.customer_id,
            self.node_configs[self.init_node]["path"], 
            self.config,
            self.global_history,
            self.topic_history,
            self.summaries
        )
        self.running = True

        while self.running:
            try:
                next_id = current_node.process()
                print(next_id)
                if next_id == -1:
                    self.running = False
                    continue

                current_node = Node(
                    next_id,
                    self.customer_id,
                    self.node_configs[next_id]["path"], 
                    self.config,
                    self.global_history,
                    self.topic_history,
                    self.summaries
                )
            except Exception as e:
                print(e)
                self.running = False