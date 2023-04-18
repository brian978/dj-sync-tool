from app.models.serato.EntryType import EntryType


class EntryData:
    """
    Raw representation of the Serato data so we can access it into a standardised way.
    The data is also assume to be decoded if it's the case
    """

    def __init__(self, entry_type: EntryType):
        assert isinstance(entry_type, EntryType)
        self.__type = entry_type

    def data_type(self):
        return self.__type.value

    def set(self, item, value):
        return setattr(self, item, value)

    def get(self, item):
        if item == 'type':
            return self.data_type()

        return getattr(self, item, None)
