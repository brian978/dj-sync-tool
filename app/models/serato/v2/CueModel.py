import struct

from app.models.HotCue import HotCue
from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class CueModel(BaseEntryModel):
    NAME = 'CUE'
    FMT = '>cBIc3s2s'
    FIELDS = ('field1', 'index', 'position', 'field4', 'color', 'field6',
              'name',)

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)

        return cls(*[
            b'\x00',
            hot_cue.index,
            hot_cue.start,
            b'\x00',
            bytes.fromhex(hot_cue.hex_color()),
            b'\x00\x00',
            hot_cue.name
        ])

    def set_hot_cue(self, position: int, color: str):
        setattr(self, 'position', position / 100)
        setattr(self, 'color', bytes.fromhex(color))

    def set_name(self, name: str):
        setattr(self, 'name', name)

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.get_name().encode('utf-8'),
            b'\x00',
        ))
