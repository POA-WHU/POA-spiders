import logging
from config import Log


class Logger(logging.Logger):
    def __init__(self, name: str):
        config = Log()
        super().__init__(name)
        formatter = logging.Formatter(fmt=config.format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(config.level)
        self.addHandler(handler)
        self.setLevel(config.level)
