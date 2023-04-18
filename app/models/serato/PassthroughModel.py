import struct

from app.models.HotCue import HotCue
from app.models.serato.EntryType import EntryType
from app.utils.serato.encoder import encode
from app.models.serato.ColorMap import ColorMap


class PassthroughModel(object):
    FMT = '>B4sB4s6s4sBB'
    FIELDS = (
        'field0',
        'field1',
        'field2',
        'field3',
        'field4',
        'field5',
        'field6',
        'field7'
    )

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

        setattr(self, 'type', EntryType.PASSTHROUGH)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name)) for name in self.FIELDS)
        )

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)
        raise NotImplementedError(f"Method not implemented in {cls}")

    def lock(self):
        pass

    def unlock(self):
        pass

    @staticmethod
    def locked():
        return True

    @staticmethod
    def is_empty():
        return False

    def dump(self):
        entry_data = []
        for field in self.FIELDS:
            value = getattr(self, field)
            entry_data.append(value)

        return struct.pack(self.FMT, *entry_data)