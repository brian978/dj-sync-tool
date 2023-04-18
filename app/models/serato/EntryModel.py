import struct

from app.models.HotCue import HotCue
from app.models.serato.EntryType import EntryType
from app.models.serato.ColorMap import ColorMap


class EntryModel(object):
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

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)
        raise NotImplementedError(f"Method not implemented in {cls}")

    def get(self, item):
        return getattr(self, item, None)

    def model_type(self) -> EntryType:
        return getattr(self, 'type', EntryType.INVALID)

    def set_hot_cue(self, position: int, color: str):
        if self.locked():
            return

        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position)
        setattr(self, 'type', EntryType.CUE)
        setattr(self, 'color', bytes.fromhex(ColorMap.to_serato(color)))

    def set_cue_loop(self, position_start: int, position_end: int):
        if self.locked():
            return

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

    def locked(self):
        return getattr(self, 'is_locked') == 1

    def is_empty(self):
        return getattr(self, 'type') == EntryType.INVALID
