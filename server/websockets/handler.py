from asyncio import Queue

import aiohttp

from aiohttp import web

from server.data_structures import update_websocket_queue
from server.logger import get_logger
from server.socket_server.message_processor import agents

logger = get_logger()


async def websocket_handler(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return web.WebSocketReady(ok=False, protocol=None)

    await ws_current.prepare(request)

    await ws_current.send_json({'action': 'connect', 'agents': [a.__str__() for a in agents]})

    while True:
        msg = await update_websocket_queue.get()

        if msg:
            await ws_current.send_json({'action': 'update', 'agents': [a.__str__() for a in agents]})
        else:
            break

    await ws_current.send_json({'action': 'disconnect', 'agents': []})

    logger.info('ws disconnected.')

    return ws_current
