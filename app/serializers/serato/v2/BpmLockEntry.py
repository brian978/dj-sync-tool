import struct

from app.serializers.serato.EntrySerializer import EntrySerializer


class BpmLockEntry(EntrySerializer):
    NAME = 'BPMLOCK'
    FIELDS = ('enabled',)
    FMT = '?'

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))
