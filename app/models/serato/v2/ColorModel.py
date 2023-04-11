import struct

from app.models.serato.EntryModel import EntryModel


class ColorModel(EntryModel):
    NAME = 'COLOR'
    FMT = 'c3s'
    FIELDS = ('field1', 'color',)

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))