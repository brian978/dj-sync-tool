from app.models.serato.PlainEntry import PlainEntry


class UnknownPlainEntry(PlainEntry):
    NAME = None
    FIELDS = ('data',)