from server.logger import get_logger
from server.models import Agent, CodeExecutor

logger = get_logger()

agents = []


def process_message(message: dict, addr: tuple):
    if message['action'] == 'JOIN':
        if 'name' not in message or 'executors' not in message:
            logger.warning("Invalid join message")
            raise ValueError("Invalid join message")
        executors = [CodeExecutor(name=executor['name'], args=executor['args']) for executor in message['executors']]
        agent = Agent(name=message['name'], executors=executors, addr=addr)
        agents.append(agent)  # XXX SHOULD CHECK ADDR REPEATED


def disconnected_agent(addr: tuple):
    for x in agents:
        if x.addr == addr:
            agents.remove(x)
    print(4)