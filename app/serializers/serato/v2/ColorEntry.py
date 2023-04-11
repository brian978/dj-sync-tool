import struct

from app.serializers.serato.EntrySerializer import EntrySerializer


class ColorEntry(EntrySerializer):
    NAME = 'COLOR'
    FMT = 'c3s'
    FIELDS = ('field1', 'color',)

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))