import logging

_FORMAT = '[%(name)-10s] %(levelname)-8s: %(message)s'
_LEVEL = logging.DEBUG


class Logger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        formatter = logging.Formatter(fmt=_FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(_LEVEL)
        self.addHandler(handler)
        self.setLevel(_LEVEL)
