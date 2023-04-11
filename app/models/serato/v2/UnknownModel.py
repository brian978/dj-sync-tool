from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class UnknownModel(BaseEntryModel):
    NAME = None
    FIELDS = ('data',)
