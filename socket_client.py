import asyncio
import json

# Based on echo server of asyncio documentation example
async def socket_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(f"{message}\n".encode())

    data = await reader.readline()
    print('Received: %r' % data.decode())
    await asyncio.sleep(i/100)

    print('Close the socket')
    writer.close()


if __name__ == '__main__':

    message_dict = {
        "action": "JOIN", # TODO SHOW WITH AND WITHOUT THIS LINE
        "name": "World",
        "executors": [
            {
                "name": "exe1",
                "args": {
                    "a1": True,
                    "a2": False
                },
            },
            {
                "name": "exe2",
                "args": {
                    "a1": True,
                },
            },
        ]
    }

    loop = asyncio.get_event_loop()
    loop.run_until_complete(socket_client(json.dumps(message_dict), loop))
    loop.close()
