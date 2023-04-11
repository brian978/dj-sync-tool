import struct

from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class LoopModel(BaseEntryModel):
    NAME = 'LOOP'
    FMT = '>cBII4s4sB?'
    FIELDS = ('field1', 'index', 'startposition', 'endposition', 'field5', 'field6', 'color', 'locked', 'name',)

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.NAME.encode('utf-8'),
            b'\x00',
        ))