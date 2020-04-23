from typing import Dict
from server.models import Agent

from asyncio import Queue

agents: Dict[tuple, Agent] = {}
update_websocket_queue: Queue = Queue()

