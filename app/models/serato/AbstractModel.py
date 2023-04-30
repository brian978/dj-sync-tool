from abc import ABC

from app.models.serato.EntryType import EntryType


class AbstractModel(ABC):
    FIELDS: tuple = ()

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name)) for name in self.FIELDS)
        )

    def model_type(self) -> EntryType:
        return self.get('type', EntryType.INVALID)

    def get(self, item, default=None):
        return getattr(self, item, default)
