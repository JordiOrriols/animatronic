class Logger:
    """Logger class to handle printing messages."""

    def __init__(self, log_name):
        self.log_name = log_name
        self.__debug = False

    # Log
    # Log
    # Log

    def debug(self):
        """Enable debug mode."""
        self.__debug = True

    def __console(self, level: str, *message):
        print(level, self.log_name + " - ", message)

    def log(self, *message):
        """Log any message. Will be only logged if debug mode."""
        if self.__debug:
            self.__console("Log: ", message)

    def info(self, *message):
        """Log any message."""
        self.__console("Info: ", message)

    def error(self, *message):
        """Log any error."""
        self.__console("ERROR: ", message)
