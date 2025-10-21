import sys
import logging
from abc import ABC, abstractmethod


class BaseLogger(ABC):
    @abstractmethod
    def debug(self, msg):
        pass

    @abstractmethod
    def info(self, msg):
        pass

    @abstractmethod
    def warning(self, msg):
        pass

    @abstractmethod
    def error(self, msg):
        pass

    @abstractmethod
    def critical(self, msg):
        pass


logging_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

# Shared console handler (only created once)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging_formatter)


class DefaultLogger(BaseLogger):
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            if console_handler not in self.logger.handlers:
                self.logger.addHandler(console_handler)

            self.logger.setLevel(logging.INFO)

        self.logger.propagate = False

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


def get_logger(name: str):
    return DefaultLogger(name)
