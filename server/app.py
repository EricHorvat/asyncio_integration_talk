import asyncio
import json
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web

from server.data_structures import agents
from server.logger import get_logger, setup_logging
from server.socket_server.server import start_socket_server
from server.utils import json_payload
from server.websockets.handler import websocket_handler

setup_logging()
logger = get_logger()

routes = web.RouteTableDef()

app = web.Application()
messages_list = []


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


@aiohttp_jinja2.template('messages.html')
async def reset(request):
    messages_list.clear()
    return dict(messages=['Cleaned'])


async def add_messages(request):

    raw_data = await request.read()  # Raises 400 if malformed data is passed
    data = json_payload(raw_data)

    import random

    messages_list.extend([data] * random.randint(1,3))

    logger.info(messages_list)

    return "OK"


async def run_agent(request):

    raw_data = await request.read()  # Raises 400 if malformed data is passed
    data = json_payload(raw_data)
    logger.info(f"Running {data}")

    if "name" not in data or "code_executor" not in data or "args" not in data:
        return web.Response(status=400)

    data["args"] = json.loads(data['args'])

    for agent in agents:
        if agent.name == data["name"]:
            await agent.queue.put(dict(action="RUN", code_executor=data['code_executor'], args=data['args']))
            return web.Response()

    return web.Response(status=400)


@aiohttp_jinja2.template('messages.html')
def get_messages(request):
    return dict(messages=messages_list)


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


if __name__ == '__main__':
    templates_folder = Path(__file__).parent / 'templates'
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates_folder))
    app.add_routes([
        web.get('/', index),
        web.get('/reset', reset),
        web.get('/messages', get_messages),
        web.post('/messages', add_messages),
        web.get('/ws', websocket_handler),
        web.post('/run', run_agent),
    ])
    app['websockets'] = {}
    app.on_shutdown.append(shutdown)

    start_socket_server()
    web.run_app(app)

