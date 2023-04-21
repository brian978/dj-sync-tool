import logging


class BaseReader:
    @staticmethod
    def _logger() -> logging.Logger:
        return logging.getLogger(__name__)

    def read(self):
        raise NotImplementedError()
