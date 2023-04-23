import logging
import os


class BaseReader:
    def __init__(self, path):
        self._path = os.path.abspath(os.path.expanduser(path))

    @staticmethod
    def _logger() -> logging.Logger:
        return logging.getLogger(__name__)

    def read(self):
        raise NotImplementedError()
