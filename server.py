import asyncio
from websockets.server import serve
from playsound import playsound
from common.socket import url, port, messages

async def handler(websocket):
    try:
        async for message in websocket:

            print(message)
            await websocket.send(message)

            if message == messages.ready:
                await websocket.send(messages.waiting)
                input('Press any key to start')
                await websocket.send(messages.play)
                playsound('sound/background.mp3', False)
                playsound('sound/laugh.mp3', False)

    except websockets.ConnectionClosedOK:
        print('Server Closed')

async def main():
    async with serve(handler, url, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())

