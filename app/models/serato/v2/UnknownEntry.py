from app.models.serato.PlainEntry import PlainEntry


class UnknownEntry(PlainEntry):
    NAME = None
    FIELDS = ('data',)