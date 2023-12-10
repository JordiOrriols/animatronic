class Logger:
    def __init__(self, logName):
        self.logName = logName
        self.__debug = False

    # Log
    # Log
    # Log

    def debug(self):
        self.__debug = True

    def __console(self, level: str, *message):
        print(level, self.logName + " - ", message)

    def log(self, *message):
        if self.__debug:
            self.__console("Log: ", message)

    def info(self, *message):
        self.__console("Info: ", message)

    def error(self, *message):
        self.__console("ERROR: ", message)
