from enum import Enum
from collections import deque
import json

from .apis import API_FUNCTIONS

class ActionType(str, Enum):
    CALLBACK = "callback"
    PROCESS = "process"
    ANALYZE = "analyze"
    GO_NEXT = "go_next"

class Action:
    def __init__(
        self, 
        customer_id: str,
        shared: dict[str,], 
        config: dict[str,],
        global_history: deque[dict[str, str]],
        topic_history: dict[str, deque[dict[str, str]]],
        summaries: deque[str, str]
    ):
        self.customer_id = customer_id
        self.shared = shared
        self.config = config
        self.type = ActionType(config["type"])
        self.global_history = global_history
        self.topic_history = topic_history
        self.summaries = summaries
        self.next_id = None

    def process(self):
        match self.type:

            case ActionType.CALLBACK:
                func_name: str = self.config["name"]
                args = { arg: self.shared[arg] for arg in self.config["args"] }
                return_name: str = self.config["return"]
                if return_name:
                    self.shared[return_name] = API_FUNCTIONS[func_name](self.customer_id, args)
                else:
                    API_FUNCTIONS[func_name](self.customer_id, args)

                return

            case ActionType.PROCESS:
                ref_summary: bool = self.config["ref_summary"]
                if ref_summary:
                    summaries: deque[(str, str)] = self.summaries
                else:
                    summaries: deque[(str, str)] = []

                ref_history: bool = self.config["ref_history"]
                if ref_history:
                    history: deque[dict[str, str]] = self.global_history
                else:
                    history: deque[dict[str, str]] = []

                args = { arg: self.shared.get(arg, None) for arg in self.config["args"] }
                prompt: str = self.config["prompt"]
                for arg, value in args.items():
                    prompt = prompt.replace(f"{{{arg}}}", str(value))

                messages = [{"role": "user", "content": f"{name}'s summary:\n{summary}"} for name, summary in summaries] + [his for his in history]
                messages.append({"role": "system", "content": prompt})
                assist = API_FUNCTIONS["output_cmd"](self.customer_id, messages)
                answer = API_FUNCTIONS["input_cmd"](self.customer_id)

                return_name = self.config["return"]
                self.shared[return_name] = answer

                self.global_history.extend([
                    {"role": "assistant", "content": assist},
                    {"role": "user", "content": answer}
                ])
                
                return
            
            case ActionType.ANALYZE:
                ref_summary: bool = self.config["ref_summary"]
                if ref_summary:
                    summaries: deque[(str, str)] = self.summaries
                else:
                    summaries: deque[(str, str)] = []

                ref_history: bool = self.config["ref_history"]
                if ref_history:
                    history: deque[dict[str, str]] = self.global_history
                else:
                    history: deque[dict[str, str]] = []

                args = { arg: self.shared.get(arg, None) for arg in self.config["args"] }
                prompt: str = self.config["prompt"]
                for arg, value in args.items():
                    prompt = prompt.replace(f"{{{arg}}}", str(value))

                messages: list[dict[str, str]] = [{"role": "user", "content": f"{name}'s summary:\n{summary}"} for name, summary in summaries] + [his for his in history]
                messages.append({"role": "system", "content": prompt})
                data_str: str = API_FUNCTIONS["inner_process"](self.customer_id, messages)
                data_str = data_str.replace("```json", "").replace("```", "")
                data = json.loads(data_str)

                print(data)

                return_name = self.config["return"]
                self.shared[return_name] = data

                return

            case ActionType.GO_NEXT:
                if self.config["arg"]:
                    data: dict[str,] = self.shared[self.config["arg"]]
                    go_to: dict[str, dict[str,]] = self.config["go_to"]

                    for key, value in go_to.items():
                        go_to_data = value.get(data[key], None)
                        if go_to_data:
                            self.next_id = go_to_data["id"]
                            return
                
                self.next_id = self.config["default"]["id"]
                
                return