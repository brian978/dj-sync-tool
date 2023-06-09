import struct

from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class ColorModel(BaseEntryModel):
    NAME = 'COLOR'
    FMT = 'c3s'
    FIELDS = ('color', 'type')

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))
