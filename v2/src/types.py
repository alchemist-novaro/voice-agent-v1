from enum import Enum

class NodeType(str, Enum):
    ANALYZE = "analyze"
    PROCESS = "process"
    CALLBACK = "callback"