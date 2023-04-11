import struct

from app.models.serato.EntryModel import EntryModel


class BpmLockModel(EntryModel):
    NAME = 'BPMLOCK'
    FIELDS = ('enabled',)
    FMT = '?'

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))
