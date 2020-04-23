from asyncio import Queue, sleep

from server.logger import get_logger
from server.models import Agent, CodeExecutor
from server.data_structures import update_websocket_queue, agents

logger = get_logger()


async def process_message(message: dict, queue: Queue, addr: tuple):
    if message['action'] == 'JOIN':
        if 'name' not in message or 'executors' not in message:
            logger.warning("Invalid join message")
            raise ValueError("Invalid join message")
        executors = {
            executor['name']:
                CodeExecutor(name=executor['name'], args=executor['args']) for executor in message['executors']
        }
        agent = Agent(name=message['name'], executors=executors, addr=addr, queue=queue)
        agents[agent.addr] = agent
        await update_websocket_queue.put("agent")
    if message['action'] == 'RUN_STATUS':
        if 'executor_name' not in message:
            logger.warning("Invalid join message")
            raise ValueError("Invalid join message")
        agent = agents[addr]
        if message["executor_name"] in agent.executors:

            if "running" in message:
                if message["running"]:
                    executor_color(agent, message['executor_name'], "goldenrod")
                else:
                    executor_color(agent, message['executor_name'], "red")
                    await update_websocket_queue.put("agent")
                    await sleep(1)
                    executor_color(agent, message['executor_name'], "black")

            if "successful" in message:
                if message["successful"]:
                    color = "darkgreen"
                else:
                    color = "magenta"
                executor_color(agent, message['executor_name'], color)
                await update_websocket_queue.put("agent")
                await sleep(1)
                executor_color(agent, message['executor_name'], "black")
        else:
            agent.color = "red"
            await update_websocket_queue.put("agent")
            await sleep(1)
            agent.color = "black"

        await update_websocket_queue.put("agent")


def executor_color(agent, executor_name, color):
    agent.executors[executor_name].color = color


async def disconnected_agent(addr: tuple):
    del agents[addr]
    await update_websocket_queue.put("agent")
