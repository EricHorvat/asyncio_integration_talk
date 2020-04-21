from typing import List, Dict


class CodeExecutor:
    def __init__(self, name: str, args: Dict[str, bool]):
        self.name: str = name
        self.args: Dict[str, bool] = args


class Agent:

    def __init__(self, name: str, executors: List[CodeExecutor], addr: tuple):
        self.name: str = name
        self.executors: List[CodeExecutor] = executors
        self.addr = addr
