from asyncio import Queue
from typing import List, Dict


class CodeExecutor:
    def __init__(self, name: str, args: Dict[str, bool]):
        self.name: str = name
        self.args: Dict[str, bool] = args
        self.color = "black"

    def __str__(self):
        return f"CodExec[name:{self.name}, args:{self.args}]"

    def __repr__(self):
        return self.__str__()


class Agent:

    def __init__(self, name: str, executors: Dict[str, CodeExecutor], addr: tuple, queue: Queue):
        self.name: str = name
        self.executors: Dict[str, CodeExecutor] = executors
        self.addr = addr
        self.queue = queue
        self.color = "black"

    def __str__(self):
        return f"Agent[name:{self.name}, addr{self.addr}, exec:{self.executors}]"

    def __repr__(self):
        return self.__str__()
