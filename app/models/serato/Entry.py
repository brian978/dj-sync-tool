from app.models.serato.EntryType import EntryType


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

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name)) for name in self.FIELDS)
        )

    def add_hot_cue(self, position, color):
        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position)
        setattr(self, 'type', EntryType.CUE)
        setattr(self, 'color', bytes.fromhex(color))

    def set_start_position(self, value):
        setattr(self, 'start_position', value)
