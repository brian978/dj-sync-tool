import struct

from app.models.serato.EntryType import EntryType
from app.utils.serato.encoder import encode


class Entry(object):
    FMT = '>B4sB4s6s4sBB'
    FIELDS = (
        'start_position_set',
        'start_position',
        'end_position_set',
        'end_position',
        'field5',
        'color',
        'type',
        'is_locked'
    )

    @classmethod
    def format(cls):
        return cls.FMT

    @classmethod
    def fields(cls):
        return cls.FIELDS

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name)) for name in self.FIELDS)
        )

    def add_hot_cue(self, position: int, color: str):
        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position)
        setattr(self, 'type', EntryType.CUE)
        setattr(self, 'color', bytes.fromhex(color))

    def set_cue_loop(self, position_start: int, position_end: int):
        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position_start)
        setattr(self, 'end_position_set', True)
        setattr(self, 'end_position', position_end)
        setattr(self, 'type', EntryType.LOOP)
        setattr(self, 'color', bytes.fromhex("27AAE1"))

    def lock(self):
        setattr(self, 'is_locked', 1)

    def unlock(self):
        setattr(self, 'is_locked', 0)

    def dump(self):
        entry_data = []
        for field in self.FIELDS:
            value = getattr(self, field)
            if field == 'start_position_set':
                value = 0x7F if not value else 0x00
            elif field == 'end_position_set':
                value = 0x7F if not value else 0x00
            elif field == 'color':
                value = encode(value)
            elif field == 'start_position':
                if value is None:
                    value = 0x7F7F7F7F.to_bytes(4, 'big')
                else:
                    value = encode(struct.pack('>I', value)[1:])
            elif field == 'end_position':
                if value is None:
                    value = 0x7F7F7F7F.to_bytes(4, 'big')
                else:
                    value = encode(struct.pack('>I', value)[1:])
            elif field == 'type':
                value = int(value)
            entry_data.append(value)

        return struct.pack(self.FMT, *entry_data)
