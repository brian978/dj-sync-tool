from app.models.serato.EntryModel import EntryModel


class UnknownEntry(EntryModel):
    NAME = None
    FIELDS = ('data',)