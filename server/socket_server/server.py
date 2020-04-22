import asyncio
import json
from asyncio import StreamReader, StreamWriter, Queue

from server.data_structures import agents
from server.logger import get_logger
from server.socket_server.message_processor import process_message, disconnected_agent

logger = get_logger()


async def read_data(reader: StreamReader):
    data = await reader.readline()
    return json.loads(data) if len(data) > 0 else None


async def handle_write(writer: StreamWriter, queue: Queue, addr: tuple):
    message = await queue.get()
    while message is not None:
        logger.info("Send: %r" % message)
        data = json.dumps(message)
        writer.write(f"{data}\n".encode())
        await writer.drain()
        message = await queue.get()


async def handle_read(reader: StreamReader, queue: Queue, addr: tuple):
    message = await read_data(reader)
    while message:
        logger.info("Received %r from %r" % (message, addr))
        try:
            await process_message(message, queue, addr)
        except (ValueError, KeyError) as e:
            logger.debug("Error parsing socket data", exc_info=e)
        message = await read_data(reader)
    await queue.put(None)


async def handle(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    queue = Queue()

    await asyncio.gather(handle_read(reader=reader, queue=queue, addr=addr),
                         handle_write(writer=writer, queue=queue, addr=addr))

    await disconnected_agent(addr)
    logger.info("Close the client socket")
    writer.close()


def start_socket_server():

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))

    return server
