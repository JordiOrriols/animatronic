
from websockets.sync.client import connect
from common.autodiscovery import AutoDiscovery

WEBSOCKET_PORT = 8765
messages = {
    "connected": 'client-connected',
    "ready": 'client-ready',
    "waiting": 'server-waiting',
    "play": 'play-animation',
    "finished": 'animation-finished',
    "exit": 'exit',
}

class WebSocketClient:
    def __init__(self):

        self.__continue_loop = True
        self.__websocket = None
        self.__autoDiscovery = AutoDiscovery()
        self.__debug = False

    def connect(self):
        
        # Auto Discovery - UPD LISTENING
        self.__info('Discovering servers...')

        current_ip = self.__autoDiscovery.listen()

        self.__info('Server found at ', current_ip)
        self.__info('Connecting...')

        with connect("ws://" + current_ip + ":" + str(WEBSOCKET_PORT)) as websocket:

            self.__info("Connected successfully")
            self.__websocket = websocket
            self.send(messages['connected'])
        
    def ready(self, handler):

        self.send(messages['ready'])
        self.__continue_loop = True

        while self.__continue_loop:

            message = self.__websocket.recv()
            self.__info(f"Message recieved: {message}")

            if message == messages['exit']:
                self.__continue_loop = False
            
            handler(message)

    # Send
    # Send
    # Send

    def send(self, msg):
        if self.__websocket != None:
            self.__websocket.send(msg)
            self.__info('Message sent', msg)
        else:
            self.__error('Cannot send message', msg)

    # Log
    # Log
    # Log

    def debug(self):
        self.__debug = True

    def __log(self, level: str, *message):
        if self.__debug:
            print(level, 'Websocket - ',
                  message,
                  '\n')

    def __info(self, *message):
        self.__log('Info: ', message)

    def __error(self, *message):
        self.__log('ERROR: ', message)