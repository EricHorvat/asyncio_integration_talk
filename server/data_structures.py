from typing import List,Dict
from server.models import Agent

from asyncio import Queue

agents: List[Agent] = []
update_websocket_queue: Queue = Queue()
run_queues: Dict[str, Queue] = {}

