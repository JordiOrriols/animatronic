from socket import socket, AF_INET, SOCK_DGRAM

DISCOVERY_PORT = 50000
DISCOVERY_MAGIC = "jordiorriols-animatronic@"

class AutoDiscovery:
    def __init__(self):
        self.__current_ip = None
        self.__debug = False

        self.__socket = socket(AF_INET, SOCK_DGRAM) # create UDP socket
        self.__socket.bind(('', DISCOVERY_PORT))        

    def listen(self):
        self.__info('Listening for service')
        while self.__current_ip == None:
            
            data, addr = self.__socket.recvfrom(1024) # wait for a packet
            self.__info("Data", data, addr)

            if data.startswith(str.encode(DISCOVERY_MAGIC)):
                self.__info("Found service", data)
                self.__current_ip = data[len(DISCOVERY_MAGIC):].decode('utf-8')
                self.__info("Current IP", self.__current_ip)

        return self.get_current_ip()

    def get_current_ip(self):
        return self.__current_ip

    # Log
    # Log
    # Log

    def debug(self):
        self.__debug = True

    def __log(self, level: str, *message):
        if self.__debug:
            print(level, 'AutoDiscovery - ',
                  message,
                  '\n')

    def __info(self, *message):
        self.__log('Info: ', message)

    def __error(self, *message):
        self.__log('ERROR: ', message)