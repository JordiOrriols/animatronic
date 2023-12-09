from socket import socket, AF_INET, SOCK_DGRAM

from logger import Logger

DISCOVERY_PORT = 50000
DISCOVERY_MAGIC = "jordiorriols-animatronic@"

class AutoDiscovery(Logger):
    def __init__(self):
        super(self, 'AutoDiscovery')
        
        self.__current_ip = None

        self.__socket = socket(AF_INET, SOCK_DGRAM) # create UDP socket
        self.__socket.bind(('', DISCOVERY_PORT))        

    def listen(self):
        self.info('Listening for service')
        while self.__current_ip == None:
            
            data, addr = self.__socket.recvfrom(1024) # wait for a packet
            self.info("Data", data, addr)

            if data.startswith(str.encode(DISCOVERY_MAGIC)):
                self.info("Found service", data)
                self.__current_ip = data[len(DISCOVERY_MAGIC):].decode('utf-8')
                self.info("Current IP", self.__current_ip)

        return self.get_current_ip()

    def get_current_ip(self):
        return self.__current_ip