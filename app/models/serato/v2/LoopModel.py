import struct

from app.models.HotCue import HotCue
from app.models.serato.EntryType import EntryType
from app.models.serato.LockableModel import LockableModel
from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class LoopModel(BaseEntryModel, LockableModel):
    NAME = 'LOOP'
    FMT = '>cBII4s4sB?'
    FIELDS = ('index', 'start_position', 'end_position', 'color', 'is_locked', 'name', 'type')

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)

        return cls(*[
            hot_cue.index,
            hot_cue.start,
            hot_cue.end,
            b'\xaa\xe1',  # Color
            False,
            hot_cue.name,
            EntryType.LOOP
        ])

    def set_cue_loop(self, position_start: int, position_end: int):
        if self.locked():
            return

        setattr(self, 'start_position', position_start)
        setattr(self, 'end_position', position_end)

    def set_name(self, name: str):
        if self.locked():
            return

        setattr(self, 'name', name)

    def is_start_position_set(self):
        return getattr(self, 'start_position') != 4294967295

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.get_name().encode('utf-8'),
            b'\x00',
        ))
