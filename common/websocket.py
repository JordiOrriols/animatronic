
from websockets.sync.client import connect
from common.autodiscovery import AutoDiscovery
from logger import Logger

WEBSOCKET_PORT = 8765
messages = {
    "connected": 'client-connected',
    "ready": 'client-ready',
    "waiting": 'server-waiting',
    "play": 'play-animation',
    "finished": 'animation-finished',
    "exit": 'exit',
}

class WebSocketClient(Logger):
    def __init__(self):
        super(self, 'WebSocketClient')

        self.__continue_loop = True
        self.__websocket = None
        self.__autoDiscovery = AutoDiscovery()

    def connect(self):
        
        # Auto Discovery - UPD LISTENING
        self.info('Discovering servers...')

        current_ip = self.__autoDiscovery.listen()

        self.info('Server found at ', current_ip)
        self.info('Connecting...')

        with connect("ws://" + current_ip + ":" + str(WEBSOCKET_PORT)) as websocket:

            self.info("Connected successfully")
            self.__websocket = websocket
            self.send(messages['connected'])
        
    def ready(self, handler):

        self.send(messages['ready'])
        self.__continue_loop = True

        while self.__continue_loop:

            message = self.__websocket.recv()
            self.info(f"Message recieved: {message}")

            if message == messages['exit']:
                self.__continue_loop = False
            
            handler(message)

    # Send
    # Send
    # Send

    def send(self, msg):
        if self.__websocket != None:
            self.__websocket.send(msg)
            self.info('Message sent', msg)
        else:
            self.error('Cannot send message', msg)