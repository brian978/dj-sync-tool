import struct

from app.models.HotCue import HotCue
from app.models.serato.EntryType import EntryType
from app.models.serato.v2.BaseEntryModel import BaseEntryModel
from app.models.serato.ColorMap import ColorMap


class CueModel(BaseEntryModel):
    NAME = 'CUE'
    FMT = '>cBIc3s2s'
    FIELDS = ('index', 'start_position', 'color', 'is_locked', 'name', 'type')

    @classmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        assert isinstance(hot_cue, HotCue)

        return cls(*[
            hot_cue.index,
            hot_cue.start,
            bytes.fromhex(ColorMap.to_serato(hot_cue.hex_color())),
            b'\x00',
            hot_cue.name,
            EntryType.CUE
        ])

    def set_hot_cue(self, position: int, color: str):
        setattr(self, 'start_position', position / 100)
        setattr(self, 'color', bytes.fromhex(ColorMap.to_serato(color)))

    def set_name(self, name: str):
        if self.locked():
            return

        setattr(self, 'name', name)

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.get_name().encode('utf-8'),
            b'\x00',
        ))
