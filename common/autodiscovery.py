import threading
from time import sleep
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    SOL_SOCKET,
    SO_BROADCAST,
    gethostbyname,
    gethostname,
)

from common.logger import Logger
from common.config import DISCOVERY_PORT, DISCOVERY_MAGIC


class AutoDiscoveryClient(Logger):
    """AutoDiscovery Client Class to auto discover servers via UDP broadcasting."""

    def __init__(self):
        super().__init__("AutoDiscovery Client")

        self.__current_ip = None

        self.__socket = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        self.__socket.bind(("", DISCOVERY_PORT))

    def listen(self):
        """Listen for UDP messages on the local network."""
        self.info("Listening for service")
        while self.__current_ip == None:
            data, addr = self.__socket.recvfrom(1024)  # wait for a packet
            self.log("Data", data, addr)

            if data.startswith(str.encode(DISCOVERY_MAGIC)):
                self.info("Found service", data)
                self.__current_ip = data[len(DISCOVERY_MAGIC) :].decode("utf-8")
                self.log("Current IP", self.__current_ip)

        self.__socket.close()
        return self.__current_ip


class AutoDiscoveryServer(Logger):
    """AutoDiscovery Server Class to broadcast server IP via UDP."""

    def __init__(self):
        super().__init__("AutoDiscovery Server")

        self.__current_ip = None
        self.__auto_discovery = True

        self.__socket = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        self.__socket.bind(("", 0))
        self.__socket.setsockopt(
            SOL_SOCKET, SO_BROADCAST, 1
        )  # This is a broadcast socket

    def __get_local_ip(self):
        # Create a socket to get the local IP address
        with socket(AF_INET, SOCK_DGRAM) as skt:
            try:
                # Create UDP socket
                skt.connect(
                    ("8.8.8.8", 80)
                )  # Connect to a known external server (Google's public DNS)
                self.__current_ip = skt.getsockname()[0]

            except skt.error as e:
                self.error(f"Cannot get local IP address: {e}")
                self.__current_ip = gethostbyname(
                    gethostname()
                )  # get our IP. Be careful if you have multiple network interfaces or IPs

        self.info("Local IP address:", self.__current_ip)

    def __broadcast(self):
        self.info("Start broadcast")
        while True:
            if self.__auto_discovery == True:
                data = DISCOVERY_MAGIC + str(self.__current_ip)
                self.__socket.sendto(str.encode(data), ("<broadcast>", DISCOVERY_PORT))
                self.log("Sent service announcement", data)
                sleep(5)
            else:
                sleep(10)

    def start(self):
        """Start broadcasting server IP."""
        self.__get_local_ip()
        thread = threading.Thread(target=self.__broadcast)
        thread.start()

    def disable(self):
        """Disable temporally broadcasting server IP."""
        self.info("Disabled")
        self.__auto_discovery = False

    def enable(self):
        """Enable temporally broadcasting server IP."""
        self.info("Enabled")
        self.__auto_discovery = True

    def get_current_ip(self):
        """Get current network IP."""
        return self.__current_ip
