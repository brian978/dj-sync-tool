from app.models.serato.EntryModel import EntryModel


class BaseDecoder:
    """
    Each entry data looks something like (it's the same for CUE & LOOP):

    """
    FMT_VERSION = 'BB'

    def __init__(self, source: str):
        self._source: str = source