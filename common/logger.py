class Logger:
    def __init__(self, logName):
        self.logName = logName
        self.__debug = True

    # Log
    # Log
    # Log

    def debug(self):
        self.__debug = True

    def log(self, level: str, *message):
        if self.__debug:
            print(level, self.logName + " - ", message)

    def info(self, *message):
        self.log("Info: ", message)

    def error(self, *message):
        self.log("ERROR: ", message)
