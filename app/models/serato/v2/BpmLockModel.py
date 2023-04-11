import struct

from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class BpmLockModel(BaseEntryModel):
    NAME = 'BPMLOCK'
    FIELDS = ('enabled',)
    FMT = '?'

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))
