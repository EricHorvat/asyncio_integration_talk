import asyncio
import json
from asyncio import StreamReader, StreamWriter

from flask_server.logger import get_logger
from flask_server.socket_server.message_processor import process_message, disconnected_agent

logger = get_logger()


async def read_data(reader: StreamReader):
    data = await reader.readline()
    return json.loads(data) if len(data) > 0 else None


# Based on echo server of asyncio documentation example
async def handle(reader: StreamReader, writer: StreamWriter):
    message = await read_data(reader)
    addr = writer.get_extra_info('peername')

    while message:
        data = json.dumps(message)
        logger.info("Received %r from %r" % (message, addr))

        try:
            process_message(message, addr)

            logger.info("Send: %r" % message)
            writer.write(f"{data}\n".encode())
            await writer.drain()
        except (ValueError, KeyError) as e:
            logger.debug("Error parsing socket data", exc_info=e)

        message = await read_data(reader)

    disconnected_agent(addr)
    logger.info("Close the client socket")
    writer.close()


def start_socket_server():

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))

    return server
