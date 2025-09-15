import yaml
from collections import deque

from .action import Action

class Node:
    def __init__(
        self,
        id: int,
        customer_id: str,
        config_path: str,
        args: dict[str,],
        global_history: deque[dict[str, str]],
        topic_history: dict[str, deque[dict[str, str]]],
        summaries: deque[str, str]
    ):
        with open(config_path) as f:
            config: dict[str,] = yaml.safe_load(f)

        self.customer_id = customer_id
        self.shared: dict[str,] = args
        self.id = id
        self.note = config["note"]
        self.next_id = -1
        self.actions = [Action(
            self.customer_id,
            self.shared,
            action,
            global_history,
            topic_history,
            summaries
        ) for action in config["actions"]]

    def process(self):
        for action in self.actions:
            action.process()
            if action.next_id is not None:
                self.next_id = action.next_id
        return self.next_id