import logging
from config import Log


class Logger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        formatter = logging.Formatter(fmt=Log.format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(Log.level)
        self.addHandler(handler)
        self.setLevel(Log.level)
