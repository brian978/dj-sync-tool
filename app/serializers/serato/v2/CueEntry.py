import struct

from app.serializers.serato.EntrySerializer import EntrySerializer


class CueEntry(EntrySerializer):
    NAME = 'CUE'
    FMT = '>cBIc3s2s'
    FIELDS = ('field1', 'index', 'position', 'field4', 'color', 'field6',
              'name',)

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''
        return cls(*info, name.decode('utf-8'))

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.name.encode('utf-8'),
            b'\x00',
        ))