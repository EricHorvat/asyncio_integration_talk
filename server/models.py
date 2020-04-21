from typing import List, Dict


class CodeExecutor:
    def __init__(self, name: str, args: Dict[str, bool]):
        self.name: str = name
        self.args: Dict[str, bool] = args

    def __str__(self):
        return f"CodExec[name:{self.name}, args:{self.args}]"

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {
            "name": self.name,
            "args": self.args
        }


class Agent:

    def __init__(self, name: str, executors: List[CodeExecutor], addr: tuple):
        self.name: str = name
        self.executors: List[CodeExecutor] = executors
        self.addr = addr

    def __str__(self):
        return f"Agent[name:{self.name}, addr{self.addr}, exec:{self.executors}]"

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {
            "name": self.name,
            "addr": self.addr,
            "executors": [e.__dict__() for e in self.executors],
        }
