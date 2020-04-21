from server.logger import get_logger
from server.models import Agent, CodeExecutor
from server.data_structures import update_websocket_queue, agents

logger = get_logger()


async def process_message(message: dict, addr: tuple):
    if message['action'] == 'JOIN':
        if 'name' not in message or 'executors' not in message:
            logger.warning("Invalid join message")
            raise ValueError("Invalid join message")
        executors = [CodeExecutor(name=executor['name'], args=executor['args']) for executor in message['executors']]
        agent = Agent(name=message['name'], executors=executors, addr=addr)
        agents.append(agent)  # XXX SHOULD CHECK ADDR REPEATED
        await update_websocket_queue.put(True)


async def disconnected_agent(addr: tuple):
    for x in agents:
        if x.addr == addr:
            agents.remove(x)
    await update_websocket_queue.put(True)
    print(4)