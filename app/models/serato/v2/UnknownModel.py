from app.models.serato.EntryModel import EntryModel


class UnknownModel(EntryModel):
    NAME = None
    FIELDS = ('data',)