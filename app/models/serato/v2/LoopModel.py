import struct

from app.models.HotCue import HotCue
from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class LoopModel(BaseEntryModel):
    NAME = 'LOOP'
    FMT = '>cBII4s4sB?'
    FIELDS = ('field1', 'index', 'startposition', 'endposition', 'field5', 'field6', 'color', 'locked', 'name',)

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)

        return cls(*[
            b'\x00',
            hot_cue.index,
            hot_cue.start,
            hot_cue.end,
            b'\xff\xff\xff\xff',
            b"\x00'\xaa\xe1",
            0,
            True,
            hot_cue.name
        ])

    def set_cue_loop(self, position_start: int, position_end: int):
        setattr(self, 'startposition', position_start)
        setattr(self, 'endposition', position_end)
        setattr(self, 'color', 0)

    def set_name(self, name: str):
        setattr(self, 'name', name)

    def lock(self):
        setattr(self, 'locked', True)

    def unlock(self):
        setattr(self, 'locked', False)

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.get_name().encode('utf-8'),
            b'\x00',
        ))