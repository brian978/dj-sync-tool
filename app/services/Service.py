import logging


class Service(object):
    @staticmethod
    def _logger() -> logging.Logger:
        return logging.getLogger(__name__)
