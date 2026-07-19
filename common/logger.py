"""Logger module to handle printing messages."""


class Logger:
    """Logger class to handle printing messages."""

    RESET = "\033[0m"
    RED = "\033[31m"
    ORANGE = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"

    def __init__(self, log_name):
        self.log_name = log_name
        self.__debug = False

    def debug(self):
        """Enable debug mode."""
        self.__debug = True

    def _color(self, text: str, color: str) -> str:
        return f"{color}{text}{self.RESET}"

    def __console(self, level: str, color: str, *message):
        print(self._color(level, color), self._color(self.log_name + " - ", color), *message)

    def log(self, *message):
        """Log any message. Will be only logged if debug mode is enabled."""
        if self.__debug:
            self.__console("Log:", self.BLUE, *message)

    def info(self, *message):
        """Log any message."""
        self.__console("Info:", self.BLUE, *message)

    def error(self, *message):
        """Log any error."""
        self.__console("ERROR:", self.RED, *message)

    def warning(self, *message):
        """Log any warning."""
        self.__console("Warning:", self.ORANGE, *message)

    def success(self, *message):
        """Log a success message."""
        self.__console("Success:", self.GREEN, *message)

    def input(self, *message):
        """Log an input prompt."""
        self.__console("Input:", self.WHITE, *message)
